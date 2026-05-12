import json
from pathlib import Path
import pandas as pd

from version_info import build_metadata

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_NAME = "python/analyze_w3_run.py"


# -----------------------
# PATH RESOLUTION
# -----------------------

def resolve(path):
    p = Path(path)
    if p.is_absolute():
        return p
    return REPO_ROOT / p


def display_path(path):
    p = Path(path)
    try:
        return p.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return p


# -----------------------
# LOAD HELPERS
# -----------------------

def load_summary(run_dir):
    path = resolve(run_dir).parent / "analysis" / "summary.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


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


def get_row(run_sheet, run_id):
    row = run_sheet[run_sheet["run_id"] == run_id]
    if row.empty:
        raise ValueError(f"Run ID {run_id} not found in run_sheet")
    return row.iloc[0]


def load_baseline_summary(run_sheet, row):
    baseline_id = row.get("baseline_ref")

    if pd.isna(baseline_id) or not baseline_id:
        return None, None

    base_dir = resolve("experiments/runs") / baseline_id / "analysis" / "summary.json"

    if not base_dir.exists():
        return baseline_id, None

    return baseline_id, json.loads(base_dir.read_text())


# -----------------------
# METRIC EXTRACTION
# -----------------------

def extract_metrics(summary):
    if summary is None:
        return None

    latency = summary.get("latency", {})
    reliability = summary.get("reliability", {})
    timing = summary.get("timing", {})

    actual = reliability.get("actual_events")
    expected = reliability.get("expected_events")
    missing = reliability.get("missing_events")
    extra = reliability.get("extra_events")
    duplicates = reliability.get("duplicates")

    reliability_rate = None
    if expected not in (None, 0):
        if missing is not None:
            reliability_rate = max(0.0, (expected - missing) / expected)
        elif actual is not None:
            reliability_rate = min(actual, expected) / expected

    extra_event_rate = None
    duplicate_event_rate = None
    if expected not in (None, 0):
        if extra is not None:
            extra_event_rate = extra / expected
        if duplicates is not None:
            duplicate_event_rate = duplicates / expected

    temporal_std_ms = latency.get("temporal_std_ms")
    if temporal_std_ms is None:
        temporal_std_ms = timing.get("jitter_ms")

    return {
        "mean_latency_ms": latency.get("mean_latency_ms"),
        "std_latency_ms": latency.get("std_latency_ms"),
        "p95_latency_ms": latency.get("p95_latency_ms"),
        "temporal_std_ms": temporal_std_ms,

        "drop_rate": reliability.get("loss_rate"),
        "reliability_rate": reliability_rate,
        "extra_event_rate": extra_event_rate,
        "duplicate_event_rate": duplicate_event_rate,
    }


# -----------------------
# DELTA COMPUTATION
# -----------------------

def compute_delta(current, baseline):
    if baseline is None:
        return {}

    def delta(a, b):
        return None if a is None or b is None else a - b

    def pct(a, b):
        if a is None or b in (None, 0):
            return None
        return (a - b) / b * 100.0

    return {
        # absolute
        "delta_mean_latency_ms": delta(current["mean_latency_ms"], baseline["mean_latency_ms"]),
        "delta_std_latency_ms": delta(current["std_latency_ms"], baseline["std_latency_ms"]),
        "delta_p95_latency_ms": delta(current["p95_latency_ms"], baseline["p95_latency_ms"]),
        "delta_temporal_std_ms": delta(current["temporal_std_ms"], baseline["temporal_std_ms"]),
        "delta_drop_rate": delta(current["drop_rate"], baseline["drop_rate"]),
        "delta_reliability_rate": delta(current["reliability_rate"], baseline["reliability_rate"]),
        "delta_extra_event_rate": delta(current["extra_event_rate"], baseline["extra_event_rate"]),
        "delta_duplicate_event_rate": delta(current["duplicate_event_rate"], baseline["duplicate_event_rate"]),

        # normalized (CRITICAL for W3 paper)
        "pct_mean_latency_increase": pct(current["mean_latency_ms"], baseline["mean_latency_ms"]),
        "pct_p95_latency_increase": pct(current["p95_latency_ms"], baseline["p95_latency_ms"]),
    }


def classify_impact(delta):
    if not delta:
        return "baseline"

    d = delta.get("pct_mean_latency_increase")

    if d is None:
        return "unknown"

    if d < 5:
        return "negligible"
    elif d < 20:
        return "moderate"
    elif d < 50:
        return "high"
    else:
        return "severe"


def json_safe(value):
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]

    if pd.isna(value):
        return None

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    if hasattr(value, "item"):
        try:
            return json_safe(value.item())
        except (TypeError, ValueError):
            pass

    return value


# -----------------------
# MAIN ANALYSIS
# -----------------------

def analyze(run_dir, run_id, run_sheet_path):
    summary_path = resolve(run_dir).parent / "analysis" / "summary.json"
    out = resolve(run_dir).parent / "analysis" / "metrics.json"

    summary = load_summary(run_dir)
    if summary is None:
        raise FileNotFoundError(f"Current run summary not found: {summary_path}")

    run_sheet = load_run_sheet(run_sheet_path)
    row = get_row(run_sheet, run_id)

    baseline_id, baseline_summary = load_baseline_summary(run_sheet, row)

    current_metrics = extract_metrics(summary)
    baseline_metrics = extract_metrics(baseline_summary) if baseline_summary else None

    delta = compute_delta(current_metrics, baseline_metrics)
    impact = classify_impact(delta)

    metrics = {
        "metadata": build_metadata(
            SCRIPT_NAME,
            inputs=[summary_path, run_sheet_path],
            outputs=[out],
            extra={"run_id": run_id},
        ),
        "run_id": run_id,
        "baseline_run_id": baseline_id,

        # W3 context (NEW, important)
        "w3_context": {
            "comparison_group": row.get("comparison_group"),
            "load_level": row.get("load_level"),
            "interference": row.get("interference"),
            "iperf_profile": row.get("iperf_profile"),
            "interval_nominal_ms": row.get("interval_nominal_ms"),
            "interval_jitter_ms": row.get("interval_jitter_ms"),
            "ap_model": row.get("ap_model"),
            "ap_firmware": row.get("ap_firmware"),
            "ap_channel_mode": row.get("ap_channel_mode"),
            "ap_channel": row.get("ap_channel"),
            "ap_width_mhz": row.get("ap_width_mhz", row.get("ap_channel_width_mhz")),
            "ap_control_sideband": row.get("ap_control_sideband"),
            "ap_rf_source": row.get("ap_rf_source"),
        },

        # raw metrics
        "w3": current_metrics,

        # baseline
        "baseline": baseline_metrics,

        # deltas
        "w3_delta": delta,

        # interpretation
        "impact_label": impact,
    }

    with open(out, "w") as f:
        json.dump(json_safe(metrics), f, indent=2, allow_nan=False)

    print(f"[OK] Saved metrics → {display_path(out)}")


# -----------------------
# CLI
# -----------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-sheet", required=True)

    args = parser.parse_args()

    analyze(args.run_dir, args.run_id, args.run_sheet)
