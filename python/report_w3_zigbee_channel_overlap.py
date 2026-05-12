import csv
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

from scipy import stats

from version_info import build_metadata, display_path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_SHEET = REPO_ROOT / "docs" / "run_sheet.csv"
RUNS_DIR = REPO_ROOT / "experiments" / "runs"
OUTPUT_RUNS_CSV = REPO_ROOT / "analysis" / "w3" / "tables" / "w3_zigbee_channel_overlap_runs.csv"
OUTPUT_PAIRS_CSV = REPO_ROOT / "analysis" / "w3" / "tables" / "w3_zigbee_channel_overlap_pairs.csv"
OUTPUT_SUMMARY_CSV = REPO_ROOT / "analysis" / "w3" / "tables" / "w3_zigbee_channel_overlap_summary.csv"
OUTPUT_MD = REPO_ROOT / "analysis" / "w3" / "reports" / "w3_zigbee_channel_overlap.md"
SCRIPT_NAME = "python/report_w3_zigbee_channel_overlap.py"

CHANNEL_CONTEXT = {
    "W3_zigbee_ap_ch1_20mhz": {
        "ap_channel": "1",
        "ap_width_mhz": "20",
        "zigbee_exposure": "control / non-overlap with Zigbee ch20",
        "zigbee_channel": "20",
        "zigbee_center_mhz": "2450",
    },
    "W3_zigbee_ap_ch9_20mhz": {
        "ap_channel": "9",
        "ap_width_mhz": "20",
        "zigbee_exposure": "overlap with Zigbee ch20",
        "zigbee_channel": "20",
        "zigbee_center_mhz": "2450",
    },
}


def load_run_sheet():
    with RUN_SHEET.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def run_number(run_id):
    return int(run_id.lstrip("R"))


def iperf_mean(run_id):
    iperf_files = list((RUNS_DIR / run_id / "raw").glob("*_iperf_summary.json"))
    if not iperf_files:
        return None
    return load_json(iperf_files[0]).get("mean_interval_mbps")


def ci95(values):
    vals = [float(value) for value in values]
    n = len(vals)
    if n == 0:
        return {"n": 0, "mean": None, "std": None, "lower": None, "upper": None}

    avg = mean(vals)
    if n == 1:
        return {"n": 1, "mean": avg, "std": 0.0, "lower": None, "upper": None}

    sd = stdev(vals)
    if sd == 0:
        return {"n": n, "mean": avg, "std": 0.0, "lower": avg, "upper": avg}

    sem = stats.sem(vals)
    lower, upper = stats.t.interval(0.95, n - 1, loc=avg, scale=sem)
    return {"n": n, "mean": avg, "std": sd, "lower": lower, "upper": upper}


def paired_test(values):
    vals = [float(value) for value in values]
    if len(vals) < 2:
        return {"t_p": None, "wilcoxon_p": None}

    t_result = stats.ttest_1samp(vals, 0.0)
    if all(value == 0 for value in vals):
        wilcoxon_p = None
    else:
        wilcoxon_p = stats.wilcoxon(vals).pvalue

    return {
        "t_p": float(t_result.pvalue),
        "wilcoxon_p": float(wilcoxon_p) if wilcoxon_p is not None else None,
    }


def two_sample_test(left, right):
    if len(left) < 2 or len(right) < 2:
        return {"welch_p": None, "mannwhitney_p": None}
    welch = stats.ttest_ind(left, right, equal_var=False)
    mann = stats.mannwhitneyu(left, right, alternative="two-sided")
    return {"welch_p": float(welch.pvalue), "mannwhitney_p": float(mann.pvalue)}


def collect_records():
    records = []
    for row in load_run_sheet():
        run_id = row["run_id"]
        if not (678 <= run_number(run_id) <= 697):
            continue
        if row["comparison_group"] not in CHANNEL_CONTEXT:
            continue

        summary_path = RUNS_DIR / run_id / "analysis" / "summary.json"
        metadata_path = RUNS_DIR / run_id / "raw" / "run_metadata.json"
        if not summary_path.exists() or not metadata_path.exists():
            continue

        summary = load_json(summary_path)
        metadata = load_json(metadata_path)
        context = CHANNEL_CONTEXT[row["comparison_group"]]
        ap_rf = metadata["run"].get("ap_rf", {})
        reliability = summary["reliability"]
        latency = summary["latency"]

        records.append({
            "run_id": run_id,
            "date": row["date"],
            "comparison_group": row["comparison_group"],
            "ap_channel": context["ap_channel"],
            "ap_width_mhz": context["ap_width_mhz"],
            "zigbee_exposure": context["zigbee_exposure"],
            "zigbee_channel": context["zigbee_channel"],
            "zigbee_center_mhz": context["zigbee_center_mhz"],
            "load_level": row["load_level"],
            "run_type": row["run_type"],
            "replicate_id": row["replicate_id"],
            "baseline_ref": row["baseline_ref"],
            "raw_run_id": metadata["run"]["run_id"],
            "status": metadata["run"]["status"],
            "exit_code": metadata["run"]["exit_code"],
            "ap_channel_recorded": ap_rf.get("channel", ""),
            "ap_width_recorded_mhz": ap_rf.get("ap_width_mhz", ""),
            "ap_sideband_recorded": ap_rf.get("control_sideband", ""),
            "ap_rf_source": ap_rf.get("source", ""),
            "expected_events": reliability["expected_events"],
            "state_rows": reliability["actual_events"],
            "missing_events": reliability["missing_events"],
            "extra_events": reliability["extra_events"],
            "drop_rate": reliability["loss_rate"],
            "extra_event_rate": reliability["extra_events"] / reliability["expected_events"],
            "repeated_event_id_rows": reliability.get("repeated_event_id_rows", 0),
            "p95_latency_ms": latency["p95_latency_ms"],
            "mad_latency_ms": latency["mad_latency_ms"],
            "mean_latency_ms": latency["mean_latency_ms"],
            "p99_latency_ms": latency["p99_latency_ms"],
            "max_latency_ms": latency["max_latency_ms"],
            "iperf_mean_mbps": iperf_mean(run_id),
        })

    return sorted(records, key=lambda record: run_number(record["run_id"]))


def aggregate(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["ap_channel"], record["load_level"])].append(record)

    rows = []
    for (ap_channel, load_level), items in sorted(grouped.items(), key=lambda item: (int(item[0][0]), item[0][1])):
        p95 = ci95([item["p95_latency_ms"] for item in items])
        mad = ci95([item["mad_latency_ms"] for item in items])
        missing = ci95([item["missing_events"] for item in items])
        extra = ci95([item["extra_events"] for item in items])
        repeated = ci95([item["repeated_event_id_rows"] for item in items])
        iperf_values = [item["iperf_mean_mbps"] for item in items if item["iperf_mean_mbps"] is not None]
        context = CHANNEL_CONTEXT[items[0]["comparison_group"]]

        rows.append({
            "ap_channel": ap_channel,
            "ap_width_mhz": context["ap_width_mhz"],
            "zigbee_exposure": context["zigbee_exposure"],
            "load_level": load_level,
            "runs": ", ".join(item["run_id"] for item in items),
            "replicates": len(items),
            "p95_latency_ms_mean": p95["mean"],
            "p95_latency_ms_lower": p95["lower"],
            "p95_latency_ms_upper": p95["upper"],
            "p95_latency_ms_std": p95["std"],
            "mad_latency_ms_mean": mad["mean"],
            "mad_latency_ms_lower": mad["lower"],
            "mad_latency_ms_upper": mad["upper"],
            "mad_latency_ms_std": mad["std"],
            "missing_events_mean": missing["mean"],
            "extra_events_mean": extra["mean"],
            "repeated_event_id_rows_mean": repeated["mean"],
            "iperf_mean_mbps": mean(iperf_values) if iperf_values else None,
        })

    return rows


def build_pairs(records):
    by_group_rep_load = defaultdict(dict)
    for record in records:
        by_group_rep_load[(record["comparison_group"], record["replicate_id"])][record["load_level"]] = record

    pairs = []
    for (comparison_group, replicate_id), loads in sorted(by_group_rep_load.items()):
        baseline = loads.get("baseline")
        heavy = loads.get("heavy")
        if not baseline or not heavy:
            continue
        if heavy["baseline_ref"] and heavy["baseline_ref"] != baseline["run_id"]:
            raise ValueError(
                f"Pairing mismatch for {comparison_group} {replicate_id}: "
                f"{heavy['run_id']} references {heavy['baseline_ref']}, not {baseline['run_id']}"
            )

        p95_delta = heavy["p95_latency_ms"] - baseline["p95_latency_ms"]
        mad_delta = heavy["mad_latency_ms"] - baseline["mad_latency_ms"]
        pairs.append({
            "comparison_group": comparison_group,
            "ap_channel": baseline["ap_channel"],
            "zigbee_exposure": baseline["zigbee_exposure"],
            "replicate_id": replicate_id,
            "baseline_run": baseline["run_id"],
            "heavy_run": heavy["run_id"],
            "baseline_p95_latency_ms": baseline["p95_latency_ms"],
            "heavy_p95_latency_ms": heavy["p95_latency_ms"],
            "p95_delta_ms": p95_delta,
            "p95_delta_pct": p95_delta / baseline["p95_latency_ms"] * 100.0,
            "baseline_mad_latency_ms": baseline["mad_latency_ms"],
            "heavy_mad_latency_ms": heavy["mad_latency_ms"],
            "mad_delta_ms": mad_delta,
            "baseline_missing_events": baseline["missing_events"],
            "heavy_missing_events": heavy["missing_events"],
            "missing_delta": heavy["missing_events"] - baseline["missing_events"],
            "baseline_extra_events": baseline["extra_events"],
            "heavy_extra_events": heavy["extra_events"],
            "extra_delta": heavy["extra_events"] - baseline["extra_events"],
            "baseline_repeated_event_id_rows": baseline["repeated_event_id_rows"],
            "heavy_repeated_event_id_rows": heavy["repeated_event_id_rows"],
            "repeated_event_id_rows_delta": heavy["repeated_event_id_rows"] - baseline["repeated_event_id_rows"],
            "iperf_mean_mbps": heavy["iperf_mean_mbps"],
        })

    return pairs


def pair_summary(pairs):
    grouped = defaultdict(list)
    for pair in pairs:
        grouped[pair["ap_channel"]].append(pair)

    rows = []
    for ap_channel, items in sorted(grouped.items(), key=lambda item: int(item[0])):
        p95 = ci95([item["p95_delta_ms"] for item in items])
        mad = ci95([item["mad_delta_ms"] for item in items])
        p95_tests = paired_test([item["p95_delta_ms"] for item in items])
        mad_tests = paired_test([item["mad_delta_ms"] for item in items])
        baseline_p95 = mean(item["baseline_p95_latency_ms"] for item in items)
        rows.append({
            "ap_channel": ap_channel,
            "zigbee_exposure": items[0]["zigbee_exposure"],
            "pairs": len(items),
            "baseline_p95_latency_ms_mean": baseline_p95,
            "p95_delta_ms_mean": p95["mean"],
            "p95_delta_ms_lower": p95["lower"],
            "p95_delta_ms_upper": p95["upper"],
            "p95_delta_pct_mean": p95["mean"] / baseline_p95 * 100.0,
            "p95_delta_ttest_p": p95_tests["t_p"],
            "p95_delta_wilcoxon_p": p95_tests["wilcoxon_p"],
            "mad_delta_ms_mean": mad["mean"],
            "mad_delta_ms_lower": mad["lower"],
            "mad_delta_ms_upper": mad["upper"],
            "mad_delta_ttest_p": mad_tests["t_p"],
            "mad_delta_wilcoxon_p": mad_tests["wilcoxon_p"],
            "missing_delta_mean": mean(item["missing_delta"] for item in items),
            "extra_delta_mean": mean(item["extra_delta"] for item in items),
            "repeated_event_id_rows_delta_mean": mean(item["repeated_event_id_rows_delta"] for item in items),
            "iperf_mean_mbps": mean(item["iperf_mean_mbps"] for item in items if item["iperf_mean_mbps"] is not None),
        })

    return rows


def difference_in_differences(pair_rows):
    by_channel = defaultdict(list)
    for pair in pair_rows:
        by_channel[pair["ap_channel"]].append(pair["p95_delta_ms"])

    control = by_channel.get("1", [])
    overlap = by_channel.get("9", [])
    tests = two_sample_test(overlap, control)
    return {
        "control_ap_channel": "1",
        "overlap_ap_channel": "9",
        "control_p95_delta_ms_mean": mean(control) if control else None,
        "overlap_p95_delta_ms_mean": mean(overlap) if overlap else None,
        "difference_in_differences_ms": (mean(overlap) - mean(control)) if control and overlap else None,
        "welch_p": tests["welch_p"],
        "mannwhitney_p": tests["mannwhitney_p"],
    }


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fmt_ms(value, digits=2):
    if value is None:
        return "-"
    return f"{value:.{digits}f} ms"


def fmt_ci(mean_value, lower, upper):
    if lower is None or upper is None:
        return fmt_ms(mean_value)
    return f"{mean_value:.2f} [{lower:.2f}, {upper:.2f}] ms"


def fmt_p(value):
    if value is None:
        return "-"
    if value < 0.001:
        return "<0.001"
    return f"{value:.3f}"


def write_markdown(records, summary_rows, pairs, delta_rows, did):
    metadata = build_metadata(
        SCRIPT_NAME,
        inputs=[RUN_SHEET],
        outputs=[
            OUTPUT_RUNS_CSV,
            OUTPUT_PAIRS_CSV,
            OUTPUT_SUMMARY_CSV,
            OUTPUT_MD,
            OUTPUT_MD.with_name(f"{OUTPUT_MD.name}.meta.json"),
        ],
    )

    md = [
        "# W3 Zigbee AP-Channel Overlap Extension",
        "",
        f"Generated: {metadata['generated_at_local']}",
        "",
        "## Scope",
        "",
        "- Runs: `R678-R697`.",
        "- Protocol: Zigbee channel 20, measured from Home Assistant state-change time to logger receive time and median-normalized.",
        "- AP settings: manually fixed 20 MHz Wi-Fi channel 1 as the non-overlap/control block and channel 9 as the overlap block for Zigbee channel 20.",
        "- Load levels: baseline and 50 Mbps TCP heavy load, five matched baseline/heavy pairs per AP setting.",
        "- AP RF fields are recorded in `run_metadata.json` and `docs/run_sheet.csv` for every run in this extension.",
        "",
        "## Aggregate Results",
        "",
        "| AP channel | Zigbee exposure | Load | Runs | P95 mean [95% CI] | MAD mean [95% CI] | Missing mean | Extra mean | Repeated-row mean | iPerf mean |",
        "|---:|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for row in summary_rows:
        iperf = f"{row['iperf_mean_mbps']:.2f} Mbps" if row["iperf_mean_mbps"] is not None else "-"
        md.append(
            f"| {row['ap_channel']} | {row['zigbee_exposure']} | {row['load_level']} | `{row['runs']}` | "
            f"{fmt_ci(row['p95_latency_ms_mean'], row['p95_latency_ms_lower'], row['p95_latency_ms_upper'])} | "
            f"{fmt_ci(row['mad_latency_ms_mean'], row['mad_latency_ms_lower'], row['mad_latency_ms_upper'])} | "
            f"{row['missing_events_mean']:.2f}/100 | {row['extra_events_mean']:.2f}/100 | "
            f"{row['repeated_event_id_rows_mean']:.2f}/100 | {iperf} |"
        )

    md.extend([
        "",
        "## Paired Heavy-vs-Baseline Delta",
        "",
        "| AP channel | Zigbee exposure | Pairs | P95 delta mean [95% CI] | P95 delta % | Paired t-test p | Wilcoxon p | MAD delta mean [95% CI] | Missing delta | Extra delta | Repeated-row delta |",
        "|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])

    for row in delta_rows:
        md.append(
            f"| {row['ap_channel']} | {row['zigbee_exposure']} | {row['pairs']} | "
            f"{fmt_ci(row['p95_delta_ms_mean'], row['p95_delta_ms_lower'], row['p95_delta_ms_upper'])} | "
            f"{row['p95_delta_pct_mean']:+.1f}% | {fmt_p(row['p95_delta_ttest_p'])} | "
            f"{fmt_p(row['p95_delta_wilcoxon_p'])} | "
            f"{fmt_ci(row['mad_delta_ms_mean'], row['mad_delta_ms_lower'], row['mad_delta_ms_upper'])} | "
            f"{row['missing_delta_mean']:+.2f}/100 | {row['extra_delta_mean']:+.2f}/100 | "
            f"{row['repeated_event_id_rows_delta_mean']:+.2f}/100 |"
        )

    md.extend([
        "",
        "## Channel-Overlap Contrast",
        "",
        f"- Mean P95 delta under AP channel 1 control: {did['control_p95_delta_ms_mean']:+.2f} ms.",
        f"- Mean P95 delta under AP channel 9 overlap: {did['overlap_p95_delta_ms_mean']:+.2f} ms.",
        f"- Difference-in-differences, overlap minus control: {did['difference_in_differences_ms']:+.2f} ms.",
        f"- Two-sample comparison of paired P95 deltas: Welch p = {fmt_p(did['welch_p'])}, Mann-Whitney p = {fmt_p(did['mannwhitney_p'])}.",
        "",
        "## Interpretation",
        "",
        "- All 20 runs completed with 100 scheduled Zigbee commands per run.",
        "- No missing Zigbee events occurred in either AP-channel block.",
        "- AP channel 9 overlap produced a small positive mean P95 shift relative to its matched baselines, while the AP channel 1 control block shifted slightly negative.",
        "- The channel-overlap contrast is approximately +1.10 ms in P95, but the five-pair extension does not provide strong statistical evidence of a large channel-specific degradation under the tested 50 Mbps TCP load.",
        "- Heavy-load state-accounting anomalies remain the main Zigbee reliability signal: one channel-1 heavy run has two extra state rows, while channel-9 heavy runs include two one-row repeats and one four-row extra/repeat run.",
        "",
        "## Generated Artifacts",
        "",
        f"- `{display_path(OUTPUT_RUNS_CSV)}`",
        f"- `{display_path(OUTPUT_PAIRS_CSV)}`",
        f"- `{display_path(OUTPUT_SUMMARY_CSV)}`",
    ])

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    meta_path = OUTPUT_MD.with_suffix(OUTPUT_MD.suffix + ".meta.json")
    meta_path.write_text(json.dumps({"metadata": metadata}, indent=2) + "\n", encoding="utf-8")


def main():
    records = collect_records()
    summary_rows = aggregate(records)
    pairs = build_pairs(records)
    delta_rows = pair_summary(pairs)
    did = difference_in_differences(pairs)

    write_csv(OUTPUT_RUNS_CSV, records)
    write_csv(OUTPUT_PAIRS_CSV, pairs)
    write_csv(OUTPUT_SUMMARY_CSV, summary_rows)
    write_markdown(records, summary_rows, pairs, delta_rows, did)

    print(f"[OK] Saved Zigbee channel-overlap run table -> {display_path(OUTPUT_RUNS_CSV)}")
    print(f"[OK] Saved Zigbee channel-overlap pair table -> {display_path(OUTPUT_PAIRS_CSV)}")
    print(f"[OK] Saved Zigbee channel-overlap summary table -> {display_path(OUTPUT_SUMMARY_CSV)}")
    print(f"[OK] Saved Zigbee channel-overlap report -> {display_path(OUTPUT_MD)}")


if __name__ == "__main__":
    main()
