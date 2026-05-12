import json
from pathlib import Path
from math import sqrt
import pandas as pd

try:
    from scipy import stats
except ImportError:  # pragma: no cover - keeps descriptive analysis usable without SciPy.
    stats = None

REPO_ROOT = Path(__file__).resolve().parents[1]

def ci_crosses_zero(ci_dict):
    if ci_dict is None:
        return None

    mean = ci_dict.get("mean")
    half = ci_dict.get("half_width")

    if mean is None or half is None:
        return None

    lower = mean - half
    upper = mean + half
    return lower <= 0 <= upper

def classify_group(paired_summary: dict) -> str:
    n_pairs = paired_summary.get("n_pairs", 0)
    mean_delta = paired_summary.get("delta_total_per_event_mJ")
    std_delta = paired_summary.get("std_delta_total_per_event_mJ")
    ci95 = paired_summary.get("ci95_delta_total_per_event_mJ")
    tests = paired_summary.get("tests_delta_total_per_event_mJ", {})
    paired_t_p = tests.get("paired_t_p_two_sided")

    if n_pairs == 0 or mean_delta is None:
        return "insufficient_data"

    if n_pairs == 1:
        return "preliminary_single_pair"

    paired_snr = None
    if std_delta not in (None, 0):
        paired_snr = mean_delta / std_delta

    crosses_zero = ci_crosses_zero(ci95)

    if paired_t_p is not None and paired_t_p < 0.05:
        if mean_delta > 0:
            return "formal_positive_signal"
        if mean_delta < 0:
            return "formal_negative_signal"

    if mean_delta > 0 and paired_snr is not None and abs(paired_snr) >= 1.0:
        return "positive_noise_floor_signal"

    if mean_delta < 0 and paired_snr is not None and abs(paired_snr) >= 1.0:
        return "negative_noise_floor_signal"

    if crosses_zero is True:
        if paired_snr is not None and abs(paired_snr) < 1.0:
            return "below_noise_floor"
        return "directionally_unresolved"

    if crosses_zero is False:
        if mean_delta > 0:
            return "positive_detectable"
        if mean_delta < 0:
            return "negative_detectable"

    return "insufficient_data"

def load_summary_for_run(run_row: pd.Series, runs_root: str | None = None) -> dict | None:
    run_id = run_row["run_id"]

    if runs_root:
        run_base = resolve_input_path(runs_root) / run_id
    else:
        run_base = resolve_input_path(run_row["run_path"])

    summary_path = run_base / "analysis" / "summary.json"

    if not summary_path.exists():
        return None

    with open(summary_path, "r") as f:
        return json.load(f)


def resolve_input_path(path_value, search_subdirs=()):
    path = Path(path_value)

    if path.is_absolute():
        return path

    candidates = [path, REPO_ROOT / path]
    candidates.extend(REPO_ROOT / subdir / path for subdir in search_subdirs)

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return REPO_ROOT / path


def load_run_sheet(run_sheet_path: str) -> pd.DataFrame:
    path = resolve_input_path(run_sheet_path, search_subdirs=("docs",))
    df = pd.read_csv(path)

    required = {
        "run_id",
        "workload",
        "status",
        "comparison_group",
        "run_type",
        "interval_ms",
        "run_path",
        "replicate_id",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"run_sheet missing required columns: {sorted(missing)}")

    return df


def load_metrics_for_run(run_row: pd.Series, runs_root: str | None = None) -> dict | None:
    run_id = run_row["run_id"]

    if runs_root:
        run_base = resolve_input_path(runs_root) / run_id
    else:
        run_base = resolve_input_path(run_row["run_path"])

    metrics_path = run_base / "analysis" / "metrics.json"

    if not metrics_path.exists():
        return None

    with open(metrics_path, "r") as f:
        return json.load(f)


def safe_mean(values):
    vals = [v for v in values if v is not None and pd.notna(v)]
    if not vals:
        return None
    return float(pd.Series(vals).mean())


def safe_std(values):
    vals = [v for v in values if v is not None and pd.notna(v)]
    if len(vals) < 2:
        return None
    return float(pd.Series(vals).std(ddof=1))


def ci95_of_mean(values):
    vals = [v for v in values if v is not None and pd.notna(v)]
    n = len(vals)
    if n == 0:
        return None
    if n == 1:
        value = float(vals[0])
        return {
            "n": 1,
            "mean": value,
            "half_width": None,
            "lower": None,
            "upper": None,
            "method": "single_sample",
        }
    s = float(pd.Series(vals).std(ddof=1))
    mean = float(pd.Series(vals).mean())
    critical = 1.96
    method = "normal_approx"
    if stats is not None:
        critical = float(stats.t.ppf(0.975, n - 1))
        method = "t"
    half = critical * s / sqrt(n)
    return {
        "n": n,
        "mean": mean,
        "half_width": half,
        "lower": mean - half,
        "upper": mean + half,
        "method": method,
    }


def paired_tests(values):
    vals = [float(v) for v in values if v is not None and pd.notna(v)]
    n = len(vals)
    result = {
        "n": n,
        "paired_t_p_two_sided": None,
        "paired_t_p_greater": None,
        "wilcoxon_p_two_sided": None,
        "wilcoxon_p_greater": None,
        "method": "scipy" if stats is not None else "unavailable_no_scipy",
    }

    if n < 2 or stats is None:
        return result

    series = pd.Series(vals)
    std = float(series.std(ddof=1))
    mean = float(series.mean())

    if std == 0:
        result["paired_t_p_two_sided"] = 0.0 if mean != 0 else 1.0
        result["paired_t_p_greater"] = 0.0 if mean > 0 else 1.0
    else:
        result["paired_t_p_two_sided"] = float(
            stats.ttest_1samp(vals, popmean=0.0, alternative="two-sided").pvalue
        )
        result["paired_t_p_greater"] = float(
            stats.ttest_1samp(vals, popmean=0.0, alternative="greater").pvalue
        )

    if any(v != 0 for v in vals):
        result["wilcoxon_p_two_sided"] = float(
            stats.wilcoxon(vals, zero_method="wilcox", alternative="two-sided").pvalue
        )
        result["wilcoxon_p_greater"] = float(
            stats.wilcoxon(vals, zero_method="wilcox", alternative="greater").pvalue
        )

    return result


def collect_metric(metrics: dict, path: list[str]):
    cur = metrics
    for key in path:
        if cur is None or key not in cur:
            return None
        cur = cur[key]
    return cur


def normalize_replicate_id(value) -> str:
    if value is None or pd.isna(value):
        return "primary"

    normalized = str(value).strip()
    return normalized or "primary"


def summarize_subset(records: list[dict]) -> dict:
    mean_power = [r["mean_power_mW"] for r in records]
    total_per_event = [r["total_per_event_mJ"] for r in records]
    incr_per_event = [r["incremental_per_event_mJ"] for r in records]
    jitter = [r["jitter_ms"] for r in records]
    reliability = [r["reliability_rate"] for r in records]
    latency_mean = [r["mean_latency_ms"] for r in records]
    latency_std = [r["std_latency_ms"] for r in records]
    latency_p95 = [r["p95_latency_ms"] for r in records]

    return {
        "n_runs": len(records),
        "run_ids": [r["run_id"] for r in records],
        "mean_power_mW": safe_mean(mean_power),
        "std_power_mW": safe_std(mean_power),
        "ci95_mean_power_mW": ci95_of_mean(mean_power),
        "total_per_event_mJ": safe_mean(total_per_event),
        "std_total_per_event_mJ": safe_std(total_per_event),
        "incremental_per_event_mJ": safe_mean(incr_per_event),
        "std_incremental_per_event_mJ": safe_std(incr_per_event),
        "jitter_ms": safe_mean(jitter),
        "std_jitter_ms": safe_std(jitter),
        "reliability_rate": safe_mean(reliability),
        "mean_latency_ms": safe_mean(latency_mean),
        "std_latency_ms": safe_std(latency_mean),  # variability across runs
        "p95_latency_ms": safe_mean(latency_p95),
    }


def build_record(run_row: pd.Series, metrics: dict, summary: dict) -> dict:
    actual = collect_metric(metrics, ["reliability", "actual_events"])
    expected = collect_metric(metrics, ["reliability", "expected_events"])
    replicate_id = normalize_replicate_id(run_row.get("replicate_id", None))

    reliability_rate = None
    if actual is not None and expected not in (None, 0):
        reliability_rate = actual / expected

    return {
        "run_id": run_row["run_id"],
        "comparison_group": run_row["comparison_group"],
        "run_type": run_row["run_type"],
        "replicate_id": replicate_id,
        "interval_ms": run_row["interval_ms"],
        
        # latency
        "latency_available": collect_metric(metrics, ["latency", "available"]),
        "mean_latency_ms": collect_metric(metrics, ["latency", "mean_latency_ms"]),
        "std_latency_ms": collect_metric(metrics, ["latency", "std_latency_ms"]),
        "p95_latency_ms": collect_metric(metrics, ["latency", "p95_latency_ms"]),

        # from summary.json
        "mean_power_mW": collect_metric(summary, ["power", "mean_power_mW"]),
        "std_power_mW": collect_metric(summary, ["power", "std_power_mW"]),
        "energy_mJ": summary.get("energy_mJ"),

        # from metrics.json
        "total_per_event_mJ": collect_metric(metrics, ["energy", "total_per_event_mJ"]),
        "incremental_per_event_mJ": collect_metric(metrics, ["energy", "incremental_per_event_mJ"]),
        "baseline_per_event_mJ": collect_metric(metrics, ["energy", "baseline_per_event_mJ"]),
        "jitter_ms": collect_metric(metrics, ["timing", "jitter_ms"]),
        "reliability_rate": reliability_rate,
        "baseline_run_id": metrics.get("baseline_run_id"),
    }


def records_by_replicate(records: list[dict], run_type: str) -> dict[str, dict]:
    by_rep = {}
    duplicates = []

    for record in records:
        replicate_id = normalize_replicate_id(record.get("replicate_id"))
        record["replicate_id"] = replicate_id

        if replicate_id in by_rep:
            duplicates.append({
                "comparison_group": record.get("comparison_group", "<unknown>"),
                "run_type": run_type,
                "replicate_id": replicate_id,
                "run_ids": [by_rep[replicate_id]["run_id"], record["run_id"]],
            })
            continue

        by_rep[replicate_id] = record

    if duplicates:
        details = "; ".join(
            f"{d['comparison_group']}/{d['run_type']}/{d['replicate_id']} -> "
            f"{', '.join(d['run_ids'])}"
            for d in duplicates
        )
        raise ValueError(
            "Duplicate W2 pairing key(s) found. Each completed W2 run must be "
            "unique by comparison_group, run_type, and replicate_id. "
            f"Duplicates: {details}"
        )

    return by_rep


def pair_records(control_recs: list[dict], telemetry_recs: list[dict]) -> list[dict]:
    control_by_rep = records_by_replicate(control_recs, "control")
    telemetry_by_rep = records_by_replicate(telemetry_recs, "telemetry")

    common_reps = sorted(set(control_by_rep.keys()) & set(telemetry_by_rep.keys()))
    pairs = []

    for rep in common_reps:
        c = control_by_rep[rep]
        t = telemetry_by_rep[rep]

        pairs.append({
            "replicate_id": rep,
            "control_run_id": c["run_id"],
            "telemetry_run_id": t["run_id"],
            "delta_mean_power_mW": (
                None if c["mean_power_mW"] is None or t["mean_power_mW"] is None
                else t["mean_power_mW"] - c["mean_power_mW"]
            ),
            "delta_total_per_event_mJ": (
                None if c["total_per_event_mJ"] is None or t["total_per_event_mJ"] is None
                else t["total_per_event_mJ"] - c["total_per_event_mJ"]
            ),
            "delta_jitter_ms": (
                None if c["jitter_ms"] is None or t["jitter_ms"] is None
                else t["jitter_ms"] - c["jitter_ms"]
            ),
            "delta_reliability_rate": (
                None if c["reliability_rate"] is None or t["reliability_rate"] is None
                else t["reliability_rate"] - c["reliability_rate"]
            ),
            "delta_latency_ms": (
                None if c["mean_latency_ms"] is None or t["mean_latency_ms"] is None
                else t["mean_latency_ms"] - c["mean_latency_ms"]
            ),
        })

    return pairs

def summarize_pairs(pairs: list[dict]) -> dict:
    delta_power = [p["delta_mean_power_mW"] for p in pairs]
    delta_total_per_event = [p["delta_total_per_event_mJ"] for p in pairs]
    delta_jitter = [p["delta_jitter_ms"] for p in pairs]
    delta_reliability = [p["delta_reliability_rate"] for p in pairs]
    
    delta_latency = [p["delta_latency_ms"] for p in pairs]

    mean_delta_power = safe_mean(delta_power)
    std_delta_power = safe_std(delta_power)
    ci95_delta_power = ci95_of_mean(delta_power)
    ci95_delta_total_per_event = ci95_of_mean(delta_total_per_event)

    paired_snr = None
    if mean_delta_power is not None and std_delta_power not in (None, 0):
        paired_snr = mean_delta_power / std_delta_power

    mean_delta_energy = safe_mean(delta_total_per_event)
    std_delta_energy = safe_std(delta_total_per_event)
    paired_energy_snr = None
    if mean_delta_energy is not None and std_delta_energy not in (None, 0):
        paired_energy_snr = mean_delta_energy / std_delta_energy

    crosses_zero = ci_crosses_zero(ci95_delta_power)
    energy_crosses_zero = ci_crosses_zero(ci95_delta_total_per_event)
    tests_delta_power = paired_tests(delta_power)
    tests_delta_total_per_event = paired_tests(delta_total_per_event)
    tests_delta_latency = paired_tests(delta_latency)

    summary = {
        "n_pairs": len(pairs),
        "pairs": pairs,

        "delta_mean_power_mW": mean_delta_power,
        "std_delta_mean_power_mW": std_delta_power,
        "ci95_delta_mean_power_mW": ci95_delta_power,
        "tests_delta_mean_power_mW": tests_delta_power,
        
        "delta_latency_ms": safe_mean(delta_latency),
        "std_delta_latency_ms": safe_std(delta_latency),
        "ci95_delta_latency_ms": ci95_of_mean(delta_latency),
        "tests_delta_latency_ms": tests_delta_latency,

        "delta_total_per_event_mJ": mean_delta_energy,
        "std_delta_total_per_event_mJ": std_delta_energy,
        "ci95_delta_total_per_event_mJ": ci95_delta_total_per_event,
        "tests_delta_total_per_event_mJ": tests_delta_total_per_event,

        "delta_jitter_ms": safe_mean(delta_jitter),
        "std_delta_jitter_ms": safe_std(delta_jitter),

        "delta_reliability_rate": safe_mean(delta_reliability),
        "std_delta_reliability_rate": safe_std(delta_reliability),

        "paired_snr": paired_snr,
        "paired_energy_snr": paired_energy_snr,
        "paired_ci_crosses_zero": crosses_zero,
        "paired_energy_ci_crosses_zero": energy_crosses_zero,
    }

    summary["interpretation_label"] = classify_group(summary)
    return summary

def analyze_groups(run_sheet_path: str, runs_root: str | None = None) -> tuple[dict, pd.DataFrame]:
    df = load_run_sheet(run_sheet_path)

    w2 = df[
        (df["workload"] == "W2") &
        (df["status"] == "complete") &
        (df["comparison_group"].notna()) &
        (df["run_type"].isin(["control", "telemetry"]))
    ].copy()

    records = []

    for _, row in w2.iterrows():
        metrics = load_metrics_for_run(row, runs_root=runs_root)
        summary = load_summary_for_run(row, runs_root=runs_root)

        if metrics is None or summary is None:
            continue

        rec = build_record(row, metrics, summary)

        if rec["mean_power_mW"] is None:
            continue

        records.append(rec)

    rec_df = pd.DataFrame(records)
    if rec_df.empty:
        raise ValueError("No completed W2 metrics found.")

    groups_json = {}
    csv_rows = []

    for group_name, gdf in rec_df.groupby("comparison_group"):
        control_recs = gdf[gdf["run_type"] == "control"].to_dict("records")
        telemetry_recs = gdf[gdf["run_type"] == "telemetry"].to_dict("records")

        control = summarize_subset(control_recs)
        telemetry = summarize_subset(telemetry_recs)

        # Unpaired deltas
        delta_power = None
        if control["mean_power_mW"] is not None and telemetry["mean_power_mW"] is not None:
            delta_power = telemetry["mean_power_mW"] - control["mean_power_mW"]

        delta_total_per_event = None
        if control["total_per_event_mJ"] is not None and telemetry["total_per_event_mJ"] is not None:
            delta_total_per_event = telemetry["total_per_event_mJ"] - control["total_per_event_mJ"]

        snr = None
        if delta_power is not None and control["std_power_mW"] not in (None, 0):
            snr = delta_power / control["std_power_mW"]

        detectable = None
        if snr is not None:
            detectable = abs(snr) >= 1.0

        # Paired analysis
        pairs = pair_records(control_recs, telemetry_recs)
        paired = summarize_pairs(pairs)

        interval_ms = int(gdf["interval_ms"].iloc[0])

        result = {
            "comparison_group": group_name,
            "interval_ms": interval_ms,
            "interval_s": interval_ms / 1000.0,
            "control": control,
            "telemetry": telemetry,
            "delta": {
                "mean_power_mW": delta_power,
                "total_per_event_mJ": delta_total_per_event,
                "incremental_per_event_mJ": delta_total_per_event,
            },
            "latency": {
                "control_mean_latency_ms": control["mean_latency_ms"],
                "telemetry_mean_latency_ms": telemetry["mean_latency_ms"],
                "delta_mean_latency_ms": (
                    None if control["mean_latency_ms"] is None or telemetry["mean_latency_ms"] is None
                    else telemetry["mean_latency_ms"] - control["mean_latency_ms"]
                ),
                "paired_delta_latency_ms": paired["delta_latency_ms"],
            },
            "paired": paired,
            "detectability": {
                "snr_vs_control_std": snr,
                "detectable_abs_snr_ge_1": detectable,
                "paired_snr": paired["paired_snr"],
                "paired_energy_snr": paired["paired_energy_snr"],
                "paired_ci_crosses_zero": paired["paired_ci_crosses_zero"],
                "paired_energy_ci_crosses_zero": paired["paired_energy_ci_crosses_zero"],
                "interpretation_label": paired["interpretation_label"],
            },
        }

        groups_json[group_name] = result
        power_ci = paired.get("ci95_delta_mean_power_mW") or {}
        energy_ci = paired.get("ci95_delta_total_per_event_mJ") or {}
        power_tests = paired.get("tests_delta_mean_power_mW") or {}
        energy_tests = paired.get("tests_delta_total_per_event_mJ") or {}

        csv_rows.append({
            "comparison_group": group_name,
            "interval_ms": interval_ms,
            "interval_s": interval_ms / 1000.0,

            "n_control": control["n_runs"],
            "n_telemetry": telemetry["n_runs"],
            "n_pairs": paired["n_pairs"],

            "control_mean_latency_ms": control["mean_latency_ms"],
            "telemetry_mean_latency_ms": telemetry["mean_latency_ms"],
            "paired_delta_latency_ms": paired["delta_latency_ms"],
            "paired_std_delta_latency_ms": paired["std_delta_latency_ms"],

            "control_mean_power_mW": control["mean_power_mW"],
            "control_std_power_mW": control["std_power_mW"],
            "telemetry_mean_power_mW": telemetry["mean_power_mW"],
            "telemetry_std_power_mW": telemetry["std_power_mW"],

            "delta_mean_power_mW": delta_power,
            "paired_delta_mean_power_mW": paired["delta_mean_power_mW"],
            "paired_std_delta_mean_power_mW": paired["std_delta_mean_power_mW"],
            "paired_ci95_delta_mean_power_mW_low": power_ci.get("lower"),
            "paired_ci95_delta_mean_power_mW_high": power_ci.get("upper"),
            "paired_t_p_delta_mean_power_mW_two_sided": power_tests.get("paired_t_p_two_sided"),
            "paired_t_p_delta_mean_power_mW_greater": power_tests.get("paired_t_p_greater"),
            "wilcoxon_p_delta_mean_power_mW_two_sided": power_tests.get("wilcoxon_p_two_sided"),
            "wilcoxon_p_delta_mean_power_mW_greater": power_tests.get("wilcoxon_p_greater"),

            "delta_total_per_event_mJ": delta_total_per_event,
            "paired_delta_total_per_event_mJ": paired["delta_total_per_event_mJ"],
            "paired_std_delta_total_per_event_mJ": paired["std_delta_total_per_event_mJ"],
            "paired_ci95_delta_total_per_event_mJ_low": energy_ci.get("lower"),
            "paired_ci95_delta_total_per_event_mJ_high": energy_ci.get("upper"),
            "paired_t_p_delta_total_per_event_mJ_two_sided": energy_tests.get("paired_t_p_two_sided"),
            "paired_t_p_delta_total_per_event_mJ_greater": energy_tests.get("paired_t_p_greater"),
            "wilcoxon_p_delta_total_per_event_mJ_two_sided": energy_tests.get("wilcoxon_p_two_sided"),
            "wilcoxon_p_delta_total_per_event_mJ_greater": energy_tests.get("wilcoxon_p_greater"),

            "snr_vs_control_std": snr,
            "detectable_abs_snr_ge_1": detectable,

            "paired_snr": paired["paired_snr"],
            "paired_energy_snr": paired["paired_energy_snr"],
            "paired_ci_crosses_zero": paired["paired_ci_crosses_zero"],
            "paired_energy_ci_crosses_zero": paired["paired_energy_ci_crosses_zero"],
            "interpretation_label": paired["interpretation_label"],

            "control_jitter_ms": control["jitter_ms"],
            "telemetry_jitter_ms": telemetry["jitter_ms"],
            "paired_delta_jitter_ms": paired["delta_jitter_ms"],

            "control_reliability_rate": control["reliability_rate"],
            "telemetry_reliability_rate": telemetry["reliability_rate"],
            "paired_delta_reliability_rate": paired["delta_reliability_rate"],
        })

    out_df = pd.DataFrame(csv_rows).sort_values("interval_ms")
    return groups_json, out_df


def save_outputs(groups_json: dict, out_df: pd.DataFrame, out_dir: str):
    target = resolve_input_path(out_dir)
    target.mkdir(parents=True, exist_ok=True)

    json_path = target / "groups.json"
    csv_path = target / "groups.csv"

    with open(json_path, "w") as f:
        json.dump(groups_json, f, indent=2)

    out_df.to_csv(csv_path, index=False)

    print(f"[OK] Wrote {json_path}")
    print(f"[OK] Wrote {csv_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--run-sheet", required=True)
    parser.add_argument("--runs-root", default="experiments/runs")
    parser.add_argument("--out-dir", default="analysis/w2/tables")

    args = parser.parse_args()

    groups_json, out_df = analyze_groups(
        run_sheet_path=args.run_sheet,
        runs_root=args.runs_root,
    )
    save_outputs(groups_json, out_df, args.out_dir)
