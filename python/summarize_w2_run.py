import json
from pathlib import Path

import pandas as pd

MICROS_WRAP_US = 2**32


def ensure_analysis_dir(run_dir):
    analysis_dir = Path(run_dir).parent / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    return analysis_dir


def load_csvs(run_dir, run_id):
    power_path = Path(run_dir) / f"{run_id}_power_samples.csv"
    events_path = Path(run_dir) / f"{run_id}_mqtt_events.csv"

    power = pd.read_csv(power_path)
    events = pd.read_csv(events_path)

    return power, events


def compute_power_stats(df):
    return {
        "power_sample_count": len(df),
        "mean_power_mW": df["power_mW"].mean(),
        "median_power_mW": df["power_mW"].median(),
        "std_power_mW": df["power_mW"].std(),
        "min_power_mW": df["power_mW"].min(),
        "p95_power_mW": df["power_mW"].quantile(0.95),
        "max_power_mW": df["power_mW"].max(),
        "samples_above_500mW": int((df["power_mW"] > 500).sum()),
        "fraction_above_500mW": float((df["power_mW"] > 500).mean()),
        "mean_current_mA": df["current_mA"].mean(),
        "median_current_mA": df["current_mA"].median(),
        "max_current_mA": df["current_mA"].max(),
        "mean_bus_v": df["bus_v"].mean(),
        "min_bus_v": df["bus_v"].min(),
        "max_bus_v": df["bus_v"].max(),
    }


def compute_energy(df):
    dt_us = wrap_safe_time_diff_us(df["t_local_us"]).fillna(0)
    dt = dt_us / 1e6
    energy_mJ = (df["power_mW"] * dt).sum()
    return energy_mJ


def wrap_safe_time_diff_us(series):
    """Return positive local-clock deltas, correcting ESP32 micros() wrap."""
    values = pd.to_numeric(series, errors="coerce")
    dt = values.diff()
    return dt.where(dt >= 0, dt + MICROS_WRAP_US)


def _numeric_series_if_present(df, col):
    if col not in df.columns:
        return None
    s = pd.to_numeric(df[col], errors="coerce").dropna()
    if s.empty:
        return None
    return s.astype(float)


def _extract_latency_series(events):
    """
    Proper latency extraction policy for W2:
    1) Prefer rtt_us (device-measured RTT) -> ms
    2) Else use raw_delay_ms if already computed upstream
    3) Else use norm_delay_ms only as normalized/relative delay
    4) Otherwise latency is unavailable

    We do NOT derive latency from pi_rx_time_ns - t_local_us because
    those timestamps are from unsynchronized clocks.
    """
    rtt_us = _numeric_series_if_present(events, "rtt_us")
    if rtt_us is not None:
        return {
            "available": True,
            "source": "rtt_us",
            "kind": "absolute_rtt",
            "series_ms": rtt_us / 1000.0,
            "reason": None,
        }

    raw_delay_ms = _numeric_series_if_present(events, "raw_delay_ms")
    if raw_delay_ms is not None:
        return {
            "available": True,
            "source": "raw_delay_ms",
            "kind": "absolute_or_upstream_computed",
            "series_ms": raw_delay_ms,
            "reason": None,
        }

    norm_delay_ms = _numeric_series_if_present(events, "norm_delay_ms")
    if norm_delay_ms is not None:
        return {
            "available": True,
            "source": "norm_delay_ms",
            "kind": "normalized_relative",
            "series_ms": norm_delay_ms,
            "reason": "Normalized delay is available, but this is not absolute latency.",
        }

    # Diagnose why unavailable
    reason = "No recognized latency column with valid numeric samples."

    if "rtt_us" in events.columns:
        rtt_raw = pd.to_numeric(events["rtt_us"], errors="coerce")
        if rtt_raw.notna().sum() == 0:
            reason = "rtt_us column exists but has no valid samples; true RTT was not captured for this run."

    elif "pi_rx_time_ns" in events.columns and "t_local_us" in events.columns:
        reason = (
            "Logger and device timestamps are present but unsynchronized; "
            "latency cannot be derived safely from pi_rx_time_ns and t_local_us."
        )

    return {
        "available": False,
        "source": None,
        "kind": None,
        "series_ms": None,
        "reason": reason,
    }


def compute_latency(events):
    extracted = _extract_latency_series(events)

    if not extracted["available"]:
        return {
            "available": False,
            "source": None,
            "kind": None,
            "sample_count": 0,
            "reason": extracted["reason"],
        }

    latency_ms = extracted["series_ms"]

    return {
        "available": True,
        "source": extracted["source"],
        "kind": extracted["kind"],
        "sample_count": int(len(latency_ms)),
        "reason": extracted["reason"],
        "mean_latency_ms": latency_ms.mean(),
        "median_latency_ms": latency_ms.median(),
        "std_latency_ms": latency_ms.std(),
        "latency_jitter_ms": latency_ms.std(),
        "min_latency_ms": latency_ms.min(),
        "p95_latency_ms": latency_ms.quantile(0.95),
        "p99_latency_ms": latency_ms.quantile(0.99),
        "max_latency_ms": latency_ms.max(),
        "fraction_above_10ms": float((latency_ms > 10).mean()),
        "fraction_above_50ms": float((latency_ms > 50).mean()),
        "fraction_above_100ms": float((latency_ms > 100).mean()),
    }


def compute_timing(events):
    if len(events) < 2:
        return {}

    intervals = wrap_safe_time_diff_us(events["t_local_us"]).dropna() / 1000.0

    return {
        "mean_interval_ms": intervals.mean(),
        "median_interval_ms": intervals.median(),
        "std_interval_ms": intervals.std(),
        "jitter_ms": intervals.std(),
        "max_interval_ms": intervals.max(),
        "min_interval_ms": intervals.min(),
    }


def compute_reliability(events):
    if "seq" not in events.columns:
        return {}

    seq = events["seq"].dropna().astype(int)
    actual = len(seq)

    if actual == 0:
        return {
            "expected_events": 0,
            "actual_events": 0,
            "missing_events": 0,
            "loss_rate": 0.0,
            "duplicates": 0,
        }

    expected = seq.max() - seq.min() + 1
    missing = expected - actual
    duplicates = actual - len(seq.unique())

    return {
        "expected_events": int(expected),
        "actual_events": int(actual),
        "missing_events": int(missing),
        "loss_rate": float(missing / expected) if expected > 0 else 0.0,
        "duplicates": int(duplicates),
    }


def compute_event_stats(events):
    stats = {
        "event_count": len(events),
    }

    if len(events) < 2:
        return stats

    intervals = wrap_safe_time_diff_us(events["t_local_us"]).dropna() / 1000.0

    stats.update({
        "mean_event_interval_ms": intervals.mean(),
        "median_event_interval_ms": intervals.median(),
        "max_event_interval_ms": intervals.max(),
    })

    return stats


def summarize(run_dir, run_id):
    power, events = load_csvs(run_dir, run_id)

    power_stats = compute_power_stats(power)
    energy_mJ = compute_energy(power)
    latency = compute_latency(events)
    timing = compute_timing(events)
    reliability = compute_reliability(events)
    event_stats = compute_event_stats(events)

    summary = {
        "run_id": run_id,
        "power": power_stats,
        "energy_mJ": energy_mJ,
        "latency": latency,
        "timing": timing,
        "reliability": reliability,
        "events": event_stats,
    }

    return summary


def save_outputs(summary, run_dir):
    analysis_dir = ensure_analysis_dir(run_dir)

    json_path = analysis_dir / "summary.json"
    md_path = analysis_dir / "summary.md"

    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    with open(md_path, "w") as f:
        f.write(f"# Summary for {summary['run_id']}\n\n")

        f.write("## Energy\n")
        f.write(f"- energy_mJ: {summary['energy_mJ']}\n")

        f.write("\n## Power\n")
        for k, v in summary["power"].items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## Latency\n")
        for k, v in summary["latency"].items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## Timing\n")
        for k, v in summary["timing"].items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## Reliability\n")
        for k, v in summary["reliability"].items():
            f.write(f"- {k}: {v}\n")

        f.write("\n## Events\n")
        for k, v in summary["events"].items():
            f.write(f"- {k}: {v}\n")

    print(f"[OK] Saved summary to {json_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--run-id", required=True)

    args = parser.parse_args()

    summary = summarize(args.run_dir, args.run_id)
    save_outputs(summary, args.run_dir)
