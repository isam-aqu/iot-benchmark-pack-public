import json
from pathlib import Path
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]


# ---------------------------
# PATH RESOLUTION
# ---------------------------

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


# ---------------------------
# DATA LOADING
# ---------------------------

def load_data(run_dir, run_id):
    raw_dir = resolve_input_path(run_dir)
    analysis_dir = raw_dir.parent / "analysis"

    power = pd.read_csv(raw_dir / f"{run_id}_power_samples.csv")
    events = pd.read_csv(raw_dir / f"{run_id}_mqtt_events.csv")

    summary_path = analysis_dir / "summary.json"
    summary = json.loads(summary_path.read_text())

    return power, events, summary, analysis_dir


# ---------------------------
# RUN SHEET
# ---------------------------

def load_run_sheet(run_sheet_path):
    return pd.read_csv(resolve_input_path(run_sheet_path, search_subdirs=("docs",)))


def get_run_row(run_sheet, run_id):
    row = run_sheet[run_sheet["run_id"] == run_id]
    return row.iloc[0] if not row.empty else None


# ---------------------------
# BASELINE RESOLUTION
# ---------------------------

def find_baseline(run_sheet, run_id):
    row = get_run_row(run_sheet, run_id)

    if row is None:
        return None

    # Control runs have no baseline
    if row["run_type"] == "control":
        return None

    group = row["comparison_group"]
    interval = row["interval_ms"]

    candidates = run_sheet[
        (run_sheet["run_id"] != run_id) &
        (run_sheet["comparison_group"] == group) &
        (run_sheet["interval_ms"] == interval) &
        (run_sheet["run_type"] == "control") &
        (run_sheet["status"] == "complete")
    ]

    if candidates.empty:
        return None

    # Prefer primary baseline, fallback to first available
    primary = candidates[candidates["replicate_id"] == "primary"]

    if not primary.empty:
        return primary.iloc[0]["run_id"]

    return candidates.iloc[0]["run_id"]


def load_baseline_metrics(runs_root, baseline_run_id):
    if baseline_run_id is None:
        return None

    path = resolve_input_path(runs_root) / baseline_run_id / "analysis" / "metrics.json"

    if not path.exists():
        return None

    return json.loads(path.read_text())


# ---------------------------
# METRICS
# ---------------------------

def compute_energy_per_event(summary, baseline_metrics=None):
    total_energy = summary["energy_mJ"]
    event_count = summary["events"]["event_count"]

    if event_count == 0:
        return None

    total_per_event = total_energy / event_count

    if baseline_metrics is None:
        return {
            "total_per_event_mJ": total_per_event,
            "incremental_per_event_mJ": None
        }

    baseline_per_event = baseline_metrics["energy"]["total_per_event_mJ"]

    return {
        "total_per_event_mJ": total_per_event,
        "baseline_per_event_mJ": baseline_per_event,
        "incremental_per_event_mJ": total_per_event - baseline_per_event
    }


def compute_dt_since_event(power):
    if "dt_since_event_ms" not in power.columns:
        return {}

    series = pd.to_numeric(power["dt_since_event_ms"], errors="coerce").dropna()
    if series.empty:
        return {}

    return {
        "mean_dt_since_event_ms": series.mean(),
        "median_dt_since_event_ms": series.median(),
        "max_dt_since_event_ms": series.max(),
    }


def compute_power_vs_event_distance(power):
    if "dt_since_event_ms" not in power.columns:
        return {}

    dt = pd.to_numeric(power["dt_since_event_ms"], errors="coerce")
    p = pd.to_numeric(power["power_mW"], errors="coerce")
    valid = pd.DataFrame({"dt": dt, "power": p}).dropna()

    if len(valid) < 2:
        return {}

    return {
        "power_dt_correlation": valid["power"].corr(valid["dt"])
    }


def compute_quality_flags(summary):
    flags = {}

    reliability = summary.get("reliability", {})
    timing = summary.get("timing", {})
    latency = summary.get("latency", {})

    if reliability.get("loss_rate", 0) > 0:
        flags["event_loss"] = True

    std_interval_ms = timing.get("std_interval_ms")
    if std_interval_ms is not None and std_interval_ms > 5:
        flags["high_interval_jitter"] = True

    if latency.get("available") is False:
        flags["missing_latency"] = True

    std_latency_ms = latency.get("std_latency_ms")
    if std_latency_ms is not None and std_latency_ms > 50:
        flags["high_latency_jitter"] = True

    p95_latency_ms = latency.get("p95_latency_ms")
    if p95_latency_ms is not None and p95_latency_ms > 100:
        flags["high_p95_latency"] = True

    return flags


# ---------------------------
# MAIN ANALYSIS
# ---------------------------

def analyze(run_dir, run_id, run_sheet_path=None, runs_root=None):
    resolved_run_dir = resolve_input_path(run_dir)
    sheet_run_id = resolved_run_dir.parent.name  # R514, R515, etc.

    power, events, summary, analysis_dir = load_data(resolved_run_dir, run_id)

    baseline_id = None
    baseline_metrics = None

    if run_sheet_path and runs_root:
        run_sheet = load_run_sheet(run_sheet_path)
        baseline_id = find_baseline(run_sheet, sheet_run_id)
        baseline_metrics = load_baseline_metrics(runs_root, baseline_id)

    metrics = {
        "run_id": run_id,
        "run_sheet_id": sheet_run_id,
        "baseline_run_id": baseline_id,

        "energy": compute_energy_per_event(summary, baseline_metrics),

        "latency": summary.get("latency", {}),
        "timing": summary.get("timing", {}),
        "reliability": summary.get("reliability", {}),

        "event_coupling": compute_dt_since_event(power),
        "power_event_relation": compute_power_vs_event_distance(power),

        "quality_flags": compute_quality_flags(summary),
    }

    return metrics, analysis_dir


# ---------------------------
# SAVE
# ---------------------------

def save(metrics, analysis_dir):
    path = analysis_dir / "metrics.json"
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"[OK] Saved metrics → {path}")


# ---------------------------
# CLI
# ---------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-sheet", required=False)
    parser.add_argument("--runs-root", default="experiments/runs")

    args = parser.parse_args()

    metrics, analysis_dir = analyze(
        args.run_dir,
        args.run_id,
        run_sheet_path=args.run_sheet,
        runs_root=args.runs_root
    )

    save(metrics, analysis_dir)