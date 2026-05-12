import json
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

from version_info import build_metadata

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_NAME = "python/analyze_w3_replicates.py"


# ----------------------------
# Helpers
# ----------------------------

def resolve(path):
    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


def display_path(path):
    p = Path(path)
    try:
        return p.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return p


def load_run_sheet(path):
    p = Path(path)
    resolved = resolve(p)
    if resolved.exists():
        return pd.read_csv(resolved)

    if not p.is_absolute():
        docs_resolved = REPO_ROOT / "docs" / p
        if docs_resolved.exists():
            return pd.read_csv(docs_resolved)

    return pd.read_csv(resolved)


def load_summary(run_id):
    path = REPO_ROOT / "experiments" / "runs" / run_id / "analysis" / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def safe_get(summary, section, key):
    if not summary:
        return None
    if section not in summary:
        return None
    return summary[section].get(key)


def extract_metrics(summary):
    if not summary:
        return None

    reliability = summary.get("reliability", {})
    median = safe_get(summary, "latency", "median_latency_ms")
    p95 = safe_get(summary, "latency", "p95_latency_ms")

    tail_inflation = None
    if median not in (None, 0) and p95 is not None:
        tail_inflation = p95 / median

    actual = reliability.get("actual_events")
    expected = reliability.get("expected_events")
    missing = reliability.get("missing_events")
    extra = reliability.get("extra_events")
    duplicates = reliability.get("duplicates")
    repeated_event_id_rows = reliability.get("repeated_event_id_rows")

    if extra is None and actual is not None and expected is not None:
        extra = max(0, actual - expected)

    reliability_rate = None
    extra_event_rate = None
    duplicate_event_rate = None
    repeated_event_id_rate = None

    if expected not in (None, 0):
        if missing is not None:
            reliability_rate = max(0.0, (expected - missing) / expected)
        elif actual is not None:
            reliability_rate = min(actual, expected) / expected

        if extra is not None:
            extra_event_rate = extra / expected
        if duplicates is not None:
            duplicate_event_rate = duplicates / expected
        if repeated_event_id_rows is not None:
            repeated_event_id_rate = repeated_event_id_rows / expected

    return {
        "mean_latency_ms": safe_get(summary, "latency", "mean_latency_ms"),
        "median_latency_ms": median,
        "mad_latency_ms": safe_get(summary, "latency", "mad_latency_ms"),
        "p95_latency_ms": p95,
        "temporal_std_ms": safe_get(summary, "latency", "temporal_std_ms"),
        "drop_rate": safe_get(summary, "reliability", "loss_rate"),
        "reliability_rate": reliability_rate,
        "extra_event_rate": extra_event_rate,
        "duplicate_event_rate": duplicate_event_rate,
        "repeated_event_id_rate": repeated_event_id_rate,
        "tail_inflation_factor": tail_inflation,
    }


# ----------------------------
# Core statistics
# ----------------------------

NON_NEGATIVE_METRICS = {
    "mean_latency_ms",
    "median_latency_ms",
    "mad_latency_ms",
    "p95_latency_ms",
    "temporal_std_ms",
    "drop_rate",
    "reliability_rate",
    "extra_event_rate",
    "duplicate_event_rate",
    "repeated_event_id_rate",
    "tail_inflation_factor",
}

BOUNDED_METRIC_LIMITS = {
    "drop_rate": (0.0, 1.0),
    "reliability_rate": (0.0, 1.0),
}


def clamp_metric_ci(metric_name, mean, ci_low, ci_high):
    if metric_name in NON_NEGATIVE_METRICS:
        ci_low = max(0.0, ci_low)

    if metric_name in BOUNDED_METRIC_LIMITS:
        lower, upper = BOUNDED_METRIC_LIMITS[metric_name]
        mean = min(max(mean, lower), upper)
        ci_low = min(max(ci_low, lower), upper)
        ci_high = min(max(ci_high, lower), upper)

    return mean, ci_low, ci_high


def compute_ci(values, metric_name=None, confidence=0.95):
    values = [
        float(v) for v in values
        if v is not None and pd.notna(v) and np.isfinite(float(v))
    ]

    if len(values) == 0:
        return None, None, None

    if len(values) == 1:
        v = float(values[0])
        return clamp_metric_ci(metric_name, v, v, v)

    arr = np.array(values, dtype=float)
    mean = float(np.mean(arr))
    sem = stats.sem(arr)

    if not np.isfinite(sem):
        return mean, mean, mean

    margin = float(sem * stats.t.ppf((1 + confidence) / 2.0, len(arr) - 1))
    ci_low = mean - margin
    ci_high = mean + margin

    mean, ci_low, ci_high = clamp_metric_ci(metric_name, mean, ci_low, ci_high)

    return mean, float(ci_low), float(ci_high)


def aggregate_group(run_ids):
    data = []

    for rid in run_ids:
        summary = load_summary(rid)
        metrics = extract_metrics(summary)
        if metrics:
            metrics["run_id"] = rid
            data.append(metrics)

    if not data:
        return None

    df = pd.DataFrame(data)

    metric_columns = [
        "median_latency_ms",
        "mad_latency_ms",
        "p95_latency_ms",
        "tail_inflation_factor",
        "drop_rate",
        "reliability_rate",
        "extra_event_rate",
        "duplicate_event_rate",
        "repeated_event_id_rate",
        "mean_latency_ms",
        "temporal_std_ms",
    ]

    result = {}

    for col in metric_columns:
        clean_values = df[col].dropna().tolist()
        mean, ci_low, ci_high = compute_ci(clean_values, metric_name=col)

        result[col] = {
            "mean": mean,
            "ci_low": ci_low,
            "ci_high": ci_high,
            "samples": len(clean_values),
        }

    return result


# ----------------------------
# Grouping logic
# ----------------------------

def group_runs(run_sheet):
    groups = {}

    for _, row in run_sheet.iterrows():
        if row.get("workload") != "W3":
            continue
        if row.get("status") != "complete":
            continue

        key = (
            row.get("protocol"),
            row.get("load_level"),
            row.get("comparison_group"),
        )

        groups.setdefault(key, []).append(row.get("run_id"))

    return groups


# ----------------------------
# Baseline matching
# ----------------------------

def find_baseline_group(groups, protocol, comparison_group):
    for (p, load, comp), runs in groups.items():
        if p == protocol and load == "baseline" and comp == comparison_group:
            return runs
    return []


def pct_change(value, baseline):
    if value is None or baseline in (None, 0):
        return None
    return 100.0 * (value - baseline) / baseline


# ----------------------------
# Main analysis
# ----------------------------

def analyze(run_sheet_path, output_path):
    run_sheet = load_run_sheet(run_sheet_path)
    groups = group_runs(run_sheet)

    results = {}

    delta_metrics = [
        "median_latency_ms",
        "mad_latency_ms",
        "p95_latency_ms",
        "tail_inflation_factor",
        "drop_rate",
        "reliability_rate",
        "extra_event_rate",
        "duplicate_event_rate",
        "repeated_event_id_rate",
        "mean_latency_ms",
        "temporal_std_ms",
    ]

    primary_metrics = [
        "median_latency_ms",
        "mad_latency_ms",
        "p95_latency_ms",
        "tail_inflation_factor",
        "drop_rate",
        "reliability_rate",
        "extra_event_rate",
    ]

    secondary_metrics = [
        "mean_latency_ms",
        "temporal_std_ms",
        "duplicate_event_rate",
        "repeated_event_id_rate",
    ]

    for (protocol, load_level, comp_group), run_ids in groups.items():
        comp_key = comp_group if pd.notna(comp_group) and comp_group else "unscoped"
        key = f"{protocol}_{load_level}_{comp_key}"

        agg = aggregate_group(run_ids)

        baseline_ids = find_baseline_group(groups, protocol, comp_group)
        baseline_agg = aggregate_group(baseline_ids)

        delta = {}
        pct_delta = {}

        if agg and baseline_agg:
            for metric in delta_metrics:
                a = agg.get(metric, {}).get("mean")
                b = baseline_agg.get(metric, {}).get("mean")

                if a is not None and b is not None:
                    delta[metric] = a - b
                    pct_delta[metric] = pct_change(a, b)
                else:
                    delta[metric] = None
                    pct_delta[metric] = None

        results[key] = {
            "runs": run_ids,
            "primary_metrics": primary_metrics,
            "secondary_metrics": secondary_metrics,
            "aggregate": agg,
            "baseline_runs": baseline_ids,
            "baseline_aggregate": baseline_agg,
            "delta_vs_baseline": delta,
            "pct_delta_vs_baseline": pct_delta,
        }

    out = resolve(output_path)
    out.parent.mkdir(exist_ok=True, parents=True)
    payload = {
        "metadata": build_metadata(
            SCRIPT_NAME,
            inputs=[run_sheet_path],
            outputs=[out],
        ),
        **results,
    }

    with open(out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"[OK] W3 replicate analysis saved → {display_path(out)}")


# ----------------------------
# CLI
# ----------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--run-sheet", required=True)
    parser.add_argument("--output", default="analysis/w3/aggregates/w3_replicates.json")

    args = parser.parse_args()

    analyze(args.run_sheet, args.output)
