import json
from pathlib import Path
import pandas as pd

from version_info import build_metadata, display_path

SCRIPT_NAME = "python/summarize_w3_run.py"


def ensure_analysis_dir(run_dir):
    analysis_dir = Path(run_dir).parent / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    return analysis_dir


def read_csv_if_exists(path):
    path = Path(path)
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


def has_mqtt_metric_rows(events):
    if events.empty:
        return False
    if "type" not in events.columns:
        return False
    return events["type"].isin(["event", "rtt"]).any()


def load_events(run_dir, run_id):
    run_dir = Path(run_dir)
    mqtt_events = read_csv_if_exists(run_dir / f"{run_id}_mqtt_events.csv")
    ble_events = read_csv_if_exists(run_dir / f"{run_id}_ble_events.csv")

    if has_mqtt_metric_rows(mqtt_events) or ble_events.empty:
        return mqtt_events, "mqtt_events"

    return ble_events, "ble_events"


def load_csvs(run_dir, run_id):
    run_dir = Path(run_dir)
    power_path = run_dir / f"{run_id}_power_samples.csv"
    power = read_csv_if_exists(power_path)
    events, event_source = load_events(run_dir, run_id)
    return power, events, event_source


def select_main_boot_segment(events):
    """
    W3 reset-safe selection.

    If boot_id exists:
      select the boot_id with the largest number of event rows.
      Prefer boot_ids whose event seq starts at 1.

    If boot_id does not exist:
      fallback to the latest sequence segment starting from seq=1.
    """
    if events.empty:
        return events

    df = events.copy()

    if "type" not in df.columns or "seq" not in df.columns:
        return df

    df["seq_num"] = pd.to_numeric(df["seq"], errors="coerce")
    df["pi_rx_time_ns_num"] = pd.to_numeric(df.get("pi_rx_time_ns"), errors="coerce")

    # Preferred modern path: boot_id-aware selection
    if "boot_id" in df.columns:
        event_rows = df[df["type"] == "event"].dropna(subset=["boot_id", "seq_num"]).copy()

        if not event_rows.empty:
            boot_stats = (
                event_rows
                .groupby("boot_id")
                .agg(
                    event_count=("seq_num", "count"),
                    min_seq=("seq_num", "min"),
                    max_seq=("seq_num", "max"),
                    first_pi_rx_time_ns=("pi_rx_time_ns_num", "min"),
                )
                .reset_index()
            )

            # Prefer complete/reset-started boot segments
            boot_stats["starts_at_1"] = boot_stats["min_seq"] == 1

            candidates = boot_stats[boot_stats["starts_at_1"]].copy()
            if candidates.empty:
                candidates = boot_stats.copy()

            candidates = candidates.sort_values(
                ["event_count", "max_seq", "first_pi_rx_time_ns"],
                ascending=[False, False, False],
            )

            selected_boot = candidates.iloc[0]["boot_id"]

            selected = df[df["boot_id"] == selected_boot].copy()
            selected = selected.drop(columns=["seq_num", "pi_rx_time_ns_num"], errors="ignore")
            return selected.reset_index(drop=True)

    # Fallback: latest segment beginning at event seq=1
    event_rows = df[df["type"] == "event"].copy()
    event_rows = event_rows.dropna(subset=["seq_num", "pi_rx_time_ns_num"])
    event_rows = event_rows.sort_values("pi_rx_time_ns_num")

    reset_points = event_rows.index[event_rows["seq_num"] == 1].tolist()
    if not reset_points:
        return df.drop(columns=["seq_num", "pi_rx_time_ns_num"], errors="ignore").reset_index(drop=True)

    start_idx = reset_points[-1]
    start_time = df.loc[start_idx, "pi_rx_time_ns_num"]

    selected = df[df["pi_rx_time_ns_num"] >= start_time].copy()
    selected = selected.drop(columns=["seq_num", "pi_rx_time_ns_num"], errors="ignore")
    return selected.reset_index(drop=True)


def deduplicate_mqtt_payloads(events):
    if "type" not in events.columns:
        return events

    dedupe_columns_by_type = {
        "event": [
            "topic", "type", "node", "protocol", "exp", "boot_id", "seq",
            "trigger", "t_local_us", "wifi_rssi", "event_id",
            "ha_context_id", "ha_time", "old_state", "new_state",
        ],
        "rtt": ["topic", "type", "node", "protocol", "exp", "boot_id", "seq", "rtt_us"],
    }

    parts = []
    used_indexes = set()

    for msg_type, columns in dedupe_columns_by_type.items():
        subset = [col for col in columns if col in events.columns]
        typed = events[events["type"] == msg_type].copy()
        if typed.empty:
            continue
        parts.append(typed.drop_duplicates(subset=subset, keep="first"))
        used_indexes.update(typed.index)

    remaining = events[~events.index.isin(used_indexes)].copy()
    if not remaining.empty:
        parts.append(remaining)

    if not parts:
        return events

    return pd.concat(parts).sort_values("pi_rx_time_ns").reset_index(drop=True)


def compute_duplicate_payload_counts(events):
    if "type" not in events.columns:
        ble_identity = [
            col for col in ("address", "company_id", "version", "node_num", "exp_code", "seq", "t_local_us")
            if col in events.columns
        ]
        if ble_identity:
            unique_rows = events.drop_duplicates(subset=ble_identity, keep="first")
            return {
                "total_rows": int(len(events)),
                "unique_payload_rows": int(len(unique_rows)),
                "duplicate_payload_rows": int(len(events) - len(unique_rows)),
            }
        return {}

    deduped = deduplicate_mqtt_payloads(events)

    counts = {
        "total_rows": int(len(events)),
        "unique_payload_rows": int(len(deduped)),
        "duplicate_payload_rows": int(len(events) - len(deduped)),
    }

    for msg_type in ("event", "rtt"):
        before = int((events["type"] == msg_type).sum())
        after = int((deduped["type"] == msg_type).sum())
        counts[f"{msg_type}_duplicate_payload_rows"] = int(before - after)

    return counts


def compute_boot_selection_info(original_events, selected_events):
    info = {
        "original_rows": int(len(original_events)),
        "selected_rows": int(len(selected_events)),
    }

    if "boot_id" in selected_events.columns and not selected_events.empty:
        boot_ids = selected_events["boot_id"].dropna().unique().tolist()
        info["selected_boot_id"] = boot_ids[0] if len(boot_ids) == 1 else boot_ids

    if "boot_id" in original_events.columns and "type" in original_events.columns and "seq" in original_events.columns:
        tmp = original_events.copy()
        tmp["seq_num"] = pd.to_numeric(tmp["seq"], errors="coerce")
        event_rows = tmp[tmp["type"] == "event"].dropna(subset=["boot_id", "seq_num"])

        if not event_rows.empty:
            boot_table = (
                event_rows
                .groupby("boot_id")["seq_num"]
                .agg(["count", "min", "max"])
                .reset_index()
                .to_dict("records")
            )
            info["boot_candidates"] = boot_table

    return info


def extract_latency_series(events):
    def get(col):
        if col not in events.columns:
            return None
        s = pd.to_numeric(events[col], errors="coerce").dropna()
        return s if not s.empty else None

    rtt_rows = events
    if "type" in events.columns:
        rtt_rows = events[events["type"] == "rtt"].copy()

    rtt = get_from_df(rtt_rows, "rtt_us")
    if rtt is not None:
        return rtt / 1000.0, "rtt_us"

    raw = get("raw_delay_ms")
    if raw is not None:
        return raw, "raw_delay_ms"

    norm = get("norm_delay_ms")
    if norm is not None:
        return norm, "norm_delay_ms"

    return None, None


def get_from_df(df, col):
    if col not in df.columns:
        return None
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    return s if not s.empty else None


def unwrap_uint32_us(series):
    values = pd.to_numeric(series, errors="coerce").reset_index(drop=True)
    unwrapped = []
    offset = 0.0
    previous = None
    wrap = float(2 ** 32)
    half_wrap = wrap / 2.0

    for value in values:
        if pd.isna(value):
            unwrapped.append(float("nan"))
            continue

        current = float(value)
        if previous is not None and current + offset < previous - half_wrap:
            offset += wrap

        adjusted = current + offset
        unwrapped.append(adjusted)
        previous = adjusted

    return pd.Series(unwrapped)


def compute_ble_logger_latency(events):
    required = {"pi_rx_time_ns", "t_local_us", "address", "exp_code"}
    if not required.issubset(events.columns):
        return None, None

    df = events.copy()
    df["pi_rx_time_us"] = pd.to_numeric(df["pi_rx_time_ns"], errors="coerce") / 1000.0
    df["t_local_us_num"] = pd.to_numeric(df["t_local_us"], errors="coerce")

    if "seq" in df.columns:
        df["seq_num"] = pd.to_numeric(df["seq"], errors="coerce")
        df = df.sort_values(["seq_num", "pi_rx_time_us"])
    else:
        df = df.sort_values("pi_rx_time_us")

    df = df.dropna(subset=["pi_rx_time_us", "t_local_us_num"]).copy()
    if df.empty:
        return None, None

    df["t_local_us_unwrapped"] = unwrap_uint32_us(df["t_local_us_num"])
    raw_delay_ms = (df["pi_rx_time_us"].reset_index(drop=True) - df["t_local_us_unwrapped"]) / 1000.0
    raw_delay_ms = raw_delay_ms.dropna()

    if raw_delay_ms.empty:
        return None, None

    norm_delay_ms = raw_delay_ms - raw_delay_ms.median()
    return norm_delay_ms.reset_index(drop=True), "ble_t_local_pi_rx_median_normalized"


def compute_ha_logger_latency(events):
    if "ha_time" not in events.columns or "pi_rx_time_ns" not in events.columns:
        return None, None

    df = events.copy()
    if "type" in df.columns:
        df = df[df["type"] == "event"].copy()

    ha_time = pd.to_datetime(df["ha_time"], errors="coerce", utc=True)
    pi_rx_time_ns = pd.to_numeric(df["pi_rx_time_ns"], errors="coerce")
    valid = ha_time.notna() & pi_rx_time_ns.notna()

    if not valid.any():
        return None, None

    ha_time_ns = ha_time[valid].astype("int64")
    raw_delay_ms = (
        pi_rx_time_ns[valid].astype("float64").reset_index(drop=True)
        - ha_time_ns.astype("float64").reset_index(drop=True)
    ) / 1_000_000.0

    if raw_delay_ms.empty:
        return None, None

    norm_delay_ms = raw_delay_ms - raw_delay_ms.median()
    return norm_delay_ms.reset_index(drop=True), "ha_time_pi_rx_median_normalized"


def compute_latency(events):
    latency_ms, source = extract_latency_series(events)

    if latency_ms is None:
        latency_ms, source = compute_ble_logger_latency(events)

    if latency_ms is None:
        latency_ms, source = compute_ha_logger_latency(events)

    if latency_ms is None:
        return {
            "available": False,
            "reason": "No valid latency source"
        }

    latency_ms = latency_ms.reset_index(drop=True)

    window = max(10, int(len(latency_ms) / 10))
    chunks = [
        latency_ms.iloc[i:i + window]
        for i in range(0, len(latency_ms), window)
        if len(latency_ms.iloc[i:i + window]) == window
    ]

    chunk_means = [c.mean() for c in chunks]

    temporal_std = None
    if len(chunk_means) > 1:
        temporal_std = float(pd.Series(chunk_means).std())

    p95 = latency_ms.quantile(0.95)
    p99 = latency_ms.quantile(0.99)
    median = latency_ms.median()
    mad = (latency_ms - median).abs().median()

    outlier_threshold = p95 * 2 if p95 is not None else None
    outlier_rate = None
    if outlier_threshold is not None and pd.notna(outlier_threshold):
        outlier_rate = float((latency_ms > outlier_threshold).mean())

    tail_threshold = latency_ms.quantile(0.99)
    extreme_outliers = latency_ms[latency_ms > tail_threshold]

    def finite_float(value):
        return float(value) if pd.notna(value) else None

    return {
        "available": True,
        "source": source,
        "mean_latency_ms": finite_float(latency_ms.mean()),
        "std_latency_ms": finite_float(latency_ms.std()),
        "p95_latency_ms": finite_float(p95),
        "p99_latency_ms": finite_float(p99),
        "max_latency_ms": finite_float(latency_ms.max()),
        "temporal_std_ms": temporal_std,
        "outlier_rate": outlier_rate,
        "sample_count": int(len(latency_ms)),
        "median_latency_ms": finite_float(median),
        "mad_latency_ms": finite_float(mad),
        "p99_threshold_ms": finite_float(tail_threshold),
        "extreme_count": int(len(extreme_outliers)),
        "extreme_max_ms": finite_float(extreme_outliers.max()) if len(extreme_outliers) else None,
    }


def compute_reliability(events, expected_events=None):
    if "type" in events.columns:
        events = events[events["type"] == "event"].copy()

    if "seq" not in events.columns:
        seq = pd.Series(dtype="float64")
    else:
        seq = pd.to_numeric(events["seq"], errors="coerce").dropna().astype(int)

    if len(events) == 0:
        return {
            "loss_rate": 0.0,
            "actual_events": 0,
            "expected_events": int(expected_events or 0),
            "missing_events": 0,
            "extra_events": 0,
            "duplicates": 0,
            "method": "empty",
        }

    repeated_event_id_rows = None
    if "event_id" in events.columns and events["event_id"].notna().any():
        event_ids = events["event_id"].dropna()
        repeated_event_id_rows = int(len(event_ids) - event_ids.nunique())

    if len(seq) > 0 and seq.nunique() > 1:
        inferred_expected = seq.max() - seq.min() + 1
        expected = int(expected_events or inferred_expected)
        actual_unique = len(seq.unique())
        duplicates = len(seq) - actual_unique
        method = "seq_range"
    elif any(col in events.columns for col in ("event_id", "ha_context_id", "ha_time")):
        identity_columns = [
            col for col in (
                "event_id",
                "ha_context_id",
                "ha_time",
                "old_state",
                "new_state",
            )
            if col in events.columns
        ]
        actual_unique = int(events.drop_duplicates(subset=identity_columns).shape[0])
        duplicates = int(len(events) - actual_unique)
        expected = int(expected_events or actual_unique)
        method = "event_identity_count"
    else:
        actual_unique = int(len(events))
        duplicates = 0
        expected = int(expected_events or actual_unique)
        method = "row_count"

    missing = max(expected - actual_unique, 0)
    extra = max(actual_unique - expected, 0)

    result = {
        "loss_rate": float(missing / expected) if expected > 0 else 0.0,
        "actual_events": int(actual_unique),
        "expected_events": int(expected),
        "missing_events": int(missing),
        "extra_events": int(extra),
        "duplicates": int(duplicates),
        "method": method,
    }

    if repeated_event_id_rows is not None:
        result["repeated_event_id_rows"] = repeated_event_id_rows

    return result


def compute_timing(events):
    if "type" in events.columns:
        events = events[events["type"] == "event"].copy()

    def summarize_intervals(series, source):
        if len(series) < 2:
            return {}
        intervals = series.diff().dropna() / 1000.0
        return {
            "mean_interval_ms": float(intervals.mean()),
            "std_interval_ms": float(intervals.std()),
            "jitter_ms": float(intervals.std()),
            "source": source,
        }

    if "t_local_us" in events.columns:
        local_events = events.copy()
        local_events["t_local_us_num"] = pd.to_numeric(local_events["t_local_us"], errors="coerce")
        local_events = local_events.dropna(subset=["t_local_us_num"]).copy()

        if local_events["t_local_us_num"].nunique() > 1:
            if "seq" in local_events.columns:
                local_events["seq_num"] = pd.to_numeric(local_events["seq"], errors="coerce")
                local_events = local_events.sort_values(["seq_num", "t_local_us_num"])
            else:
                local_events = local_events.sort_values("t_local_us_num")
            return summarize_intervals(unwrap_uint32_us(local_events["t_local_us_num"]), "t_local_us")

    if "pi_rx_time_ns" not in events.columns:
        return {}

    rx_events = events.copy()
    rx_events["pi_rx_time_us"] = pd.to_numeric(rx_events["pi_rx_time_ns"], errors="coerce") / 1000.0
    rx_events = rx_events.dropna(subset=["pi_rx_time_us"]).sort_values("pi_rx_time_us")

    return summarize_intervals(rx_events["pi_rx_time_us"], "pi_rx_time_ns")


def summarize(run_dir, run_id, expected_events=None):
    power, raw_events, event_source = load_csvs(run_dir, run_id)

    selected_events = select_main_boot_segment(raw_events)
    metric_events = deduplicate_mqtt_payloads(selected_events)

    summary = {
        "run_id": run_id,
        "event_source": event_source,
        "boot_selection": compute_boot_selection_info(raw_events, selected_events),
        "latency": compute_latency(metric_events),
        "reliability": compute_reliability(metric_events, expected_events=expected_events),
        "timing": compute_timing(metric_events),
        "data_quality": compute_duplicate_payload_counts(selected_events),
    }

    return summary


def save(summary, run_dir):
    analysis_dir = ensure_analysis_dir(run_dir)
    path = analysis_dir / "summary.json"
    payload = {
        "metadata": build_metadata(
            SCRIPT_NAME,
            inputs=[Path(run_dir)],
            outputs=[path],
            extra={"run_id": summary.get("run_id")},
        ),
        **summary,
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[OK] Saved summary → {display_path(path)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--expected-events", type=int)

    args = parser.parse_args()

    summary = summarize(args.run_dir, args.run_id, expected_events=args.expected_events)
    save(summary, args.run_dir)
