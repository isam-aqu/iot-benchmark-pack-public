import csv
import json
import os
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from version_info import build_metadata, display_path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_SHEET = REPO_ROOT / "docs" / "run_sheet.csv"
RUNS_DIR = REPO_ROOT / "experiments" / "runs"
OUTPUT_RUNS_CSV = REPO_ROOT / "analysis" / "w3" / "tables" / "w3_ble_channel_overlap_runs.csv"
OUTPUT_SUMMARY_CSV = REPO_ROOT / "analysis" / "w3" / "tables" / "w3_ble_channel_overlap_summary.csv"
OUTPUT_MD = REPO_ROOT / "analysis" / "w3" / "reports" / "w3_ble_channel_overlap.md"
OUTPUT_FIGURE = REPO_ROOT / "analysis" / "w3" / "figures" / "w3_ble_channel_overlap_p95_missing.png"
SCRIPT_NAME = "python/report_w3_ble_channel_overlap.py"

CHANNEL_CONTEXT = {
    "W3_ble_ap_ch1_20mhz": ("1", "37", "2402 MHz"),
    "W3_ble_ap_ch6_20mhz": ("6", "38", "2426 MHz"),
    "W3_ble_ap_ch13_20mhz": ("13", "39", "2480 MHz"),
}


def load_run_sheet():
    with RUN_SHEET.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def missing_sequences(run_id):
    ble_files = list((RUNS_DIR / run_id / "raw").glob("*_ble_events.csv"))
    if not ble_files:
        return []

    seqs = set()
    with ble_files[0].open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                seqs.add(int(float(row.get("seq", ""))))
            except ValueError:
                continue

    return [seq for seq in range(1, 101) if seq not in seqs]


def iperf_mean(run_id):
    iperf_files = list((RUNS_DIR / run_id / "raw").glob("*_iperf_summary.json"))
    if not iperf_files:
        return None
    return load_json(iperf_files[0]).get("mean_interval_mbps")


def rounded(value, digits=2):
    if value is None:
        return ""
    return round(float(value), digits)


def std(values):
    return stdev(values) if len(values) > 1 else 0.0


def collect_records():
    records = []
    for row in load_run_sheet():
        run_id = row["run_id"]
        if not ("R660" <= run_id <= "R677"):
            continue
        if row["comparison_group"] not in CHANNEL_CONTEXT:
            continue

        summary_path = RUNS_DIR / run_id / "analysis" / "summary.json"
        metadata_path = RUNS_DIR / run_id / "raw" / "run_metadata.json"
        if not summary_path.exists() or not metadata_path.exists():
            continue

        summary = load_json(summary_path)
        metadata = load_json(metadata_path)
        ap_channel, adv_channel, adv_freq = CHANNEL_CONTEXT[row["comparison_group"]]
        missing = missing_sequences(run_id)

        records.append({
            "run_id": run_id,
            "date": row["date"],
            "comparison_group": row["comparison_group"],
            "ap_channel": ap_channel,
            "ap_width_mhz": "20",
            "target_ble_adv_channel": adv_channel,
            "target_ble_adv_freq": adv_freq,
            "load_level": row["load_level"],
            "run_type": row["run_type"],
            "replicate_id": row["replicate_id"],
            "raw_run_id": metadata["run"]["run_id"],
            "status": metadata["run"]["status"],
            "exit_code": metadata["run"]["exit_code"],
            "expected_events": summary["reliability"]["expected_events"],
            "captured_events": summary["reliability"]["actual_events"],
            "missing_events": summary["reliability"]["missing_events"],
            "missing_sequences": ",".join(str(seq) for seq in missing),
            "drop_rate": summary["reliability"]["loss_rate"],
            "p95_latency_ms": summary["latency"]["p95_latency_ms"],
            "mad_latency_ms": summary["latency"]["mad_latency_ms"],
            "mean_latency_ms": summary["latency"]["mean_latency_ms"],
            "p99_latency_ms": summary["latency"]["p99_latency_ms"],
            "max_latency_ms": summary["latency"]["max_latency_ms"],
            "iperf_mean_mbps": iperf_mean(run_id),
        })

    return records


def aggregate(records):
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["ap_channel"], record["target_ble_adv_channel"], record["load_level"])].append(record)

    rows = []
    for key, items in sorted(grouped.items(), key=lambda item: (int(item[0][0]), item[0][2])):
        ap_channel, adv_channel, load_level = key
        rows.append({
            "ap_channel": ap_channel,
            "ap_width_mhz": "20",
            "target_ble_adv_channel": adv_channel,
            "load_level": load_level,
            "runs": ", ".join(item["run_id"] for item in items),
            "samples": len(items),
            "captured_events_mean": mean(item["captured_events"] for item in items),
            "missing_events_mean": mean(item["missing_events"] for item in items),
            "drop_rate_mean": mean(item["drop_rate"] for item in items),
            "p95_latency_ms_mean": mean(item["p95_latency_ms"] for item in items),
            "p95_latency_ms_std": std([item["p95_latency_ms"] for item in items]),
            "mad_latency_ms_mean": mean(item["mad_latency_ms"] for item in items),
            "mad_latency_ms_std": std([item["mad_latency_ms"] for item in items]),
            "iperf_mean_mbps": mean([item["iperf_mean_mbps"] for item in items if item["iperf_mean_mbps"] is not None]) if any(item["iperf_mean_mbps"] is not None for item in items) else None,
        })

    return rows


def heavy_delta(summary_rows):
    by_channel = defaultdict(dict)
    for row in summary_rows:
        by_channel[row["ap_channel"]][row["load_level"]] = row

    deltas = []
    for ap_channel, loads in sorted(by_channel.items(), key=lambda item: int(item[0])):
        baseline = loads.get("baseline")
        heavy = loads.get("heavy")
        if not baseline or not heavy:
            continue
        p95_delta = heavy["p95_latency_ms_mean"] - baseline["p95_latency_ms_mean"]
        mad_delta = heavy["mad_latency_ms_mean"] - baseline["mad_latency_ms_mean"]
        missing_delta = heavy["missing_events_mean"] - baseline["missing_events_mean"]
        p95_pct = p95_delta / baseline["p95_latency_ms_mean"] * 100.0
        deltas.append({
            "ap_channel": ap_channel,
            "target_ble_adv_channel": baseline["target_ble_adv_channel"],
            "baseline_p95": baseline["p95_latency_ms_mean"],
            "heavy_p95": heavy["p95_latency_ms_mean"],
            "p95_delta": p95_delta,
            "p95_pct": p95_pct,
            "baseline_mad": baseline["mad_latency_ms_mean"],
            "heavy_mad": heavy["mad_latency_ms_mean"],
            "mad_delta": mad_delta,
            "baseline_missing": baseline["missing_events_mean"],
            "heavy_missing": heavy["missing_events_mean"],
            "missing_delta": missing_delta,
        })
    return deltas


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_figure(summary_rows, source_metadata=None):
    by_channel = defaultdict(dict)
    for row in summary_rows:
        by_channel[row["ap_channel"]][row["load_level"]] = row

    channels = ["1", "6", "13"]
    labels = [f"ch{ch}\nadv{by_channel[ch]['baseline']['target_ble_adv_channel']}" for ch in channels]
    x = list(range(len(channels)))
    width = 0.34

    baseline_p95 = [by_channel[ch]["baseline"]["p95_latency_ms_mean"] for ch in channels]
    heavy_p95 = [by_channel[ch]["heavy"]["p95_latency_ms_mean"] for ch in channels]
    baseline_p95_err = [by_channel[ch]["baseline"]["p95_latency_ms_std"] for ch in channels]
    heavy_p95_err = [by_channel[ch]["heavy"]["p95_latency_ms_std"] for ch in channels]
    baseline_missing = [by_channel[ch]["baseline"]["missing_events_mean"] for ch in channels]
    heavy_missing = [by_channel[ch]["heavy"]["missing_events_mean"] for ch in channels]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 6.0), sharex=True)
    ax1.bar([pos - width / 2 for pos in x], baseline_p95, width, yerr=baseline_p95_err, capsize=4, label="Baseline", color="tab:blue", alpha=0.85)
    ax1.bar([pos + width / 2 for pos in x], heavy_p95, width, yerr=heavy_p95_err, capsize=4, label="Heavy 50 Mbps TCP", color="tab:red", alpha=0.82)
    ax1.set_ylabel("P95 latency (ms)")
    ax1.set_title("BLE AP-Channel Extension: P95 and Missing Advertisements")
    ax1.grid(axis="y", alpha=0.3)
    ax1.legend()

    ax2.bar([pos - width / 2 for pos in x], baseline_missing, width, label="Baseline", color="tab:blue", alpha=0.85)
    ax2.bar([pos + width / 2 for pos in x], heavy_missing, width, label="Heavy 50 Mbps TCP", color="tab:red", alpha=0.82)
    ax2.set_ylabel("Missing events / 100")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    OUTPUT_FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT_FIGURE, dpi=300)
    plt.close(fig)

    meta_path = OUTPUT_FIGURE.with_name(f"{OUTPUT_FIGURE.name}.meta.json")
    payload = {
        "metadata": build_metadata(
            SCRIPT_NAME,
            inputs=[OUTPUT_SUMMARY_CSV],
            outputs=[OUTPUT_FIGURE, meta_path],
            extra={
                "plot_name": "W3 BLE AP-channel P95 and missing advertisements",
                "metrics": ["p95_latency_ms_mean", "missing_events_mean"],
            },
        )
    }
    if source_metadata:
        payload["source_metadata"] = source_metadata
    meta_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def fmt_ms(value):
    return f"{value:.1f} ms"


def fmt_pct(value):
    return f"{value:+.1f}%"


def write_markdown(records, summary_rows, deltas):
    metadata = build_metadata(
        SCRIPT_NAME,
        inputs=[RUN_SHEET],
        outputs=[OUTPUT_RUNS_CSV, OUTPUT_SUMMARY_CSV, OUTPUT_MD, OUTPUT_FIGURE],
    )

    md = [
        "# W3 BLE AP-Channel Overlap Extension",
        "",
        f"Generated: {metadata['generated_at_local']}",
        "",
        "## Scope",
        "",
        "- Runs: `R660-R677`.",
        "- Protocol: BLE legacy advertising, logger-side advertisement capture.",
        "- AP settings: manually planned 20 MHz Wi-Fi channels 1, 6, and 13, targeting BLE advertising channels 37, 38, and 39 respectively.",
        "- Load levels: baseline and 50 Mbps TCP heavy load, three replicates per AP channel and load.",
        "- Caveat: AP channel/width is not independently encoded in the raw run metadata; channel labels are based on the manual/planned AP setting for each run block.",
        "",
        "## Aggregate Results",
        "",
        "| AP channel | Target BLE adv | Load | Runs | Captured mean | Missing mean | Drop mean | P95 mean | MAD mean | iPerf mean |",
        "|---:|---:|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for row in summary_rows:
        iperf = f"{row['iperf_mean_mbps']:.2f} Mbps" if row["iperf_mean_mbps"] is not None else "-"
        md.append(
            f"| {row['ap_channel']} | {row['target_ble_adv_channel']} | {row['load_level']} | `{row['runs']}` | "
            f"{row['captured_events_mean']:.2f}/100 | {row['missing_events_mean']:.2f} | "
            f"{row['drop_rate_mean'] * 100.0:.1f}% | {fmt_ms(row['p95_latency_ms_mean'])} | "
            f"{fmt_ms(row['mad_latency_ms_mean'])} | {iperf} |"
        )

    md.extend([
        "",
        "## Heavy-vs-Baseline Delta",
        "",
        "| AP channel | Target BLE adv | P95 delta | MAD delta | Missing-event delta |",
        "|---:|---:|---:|---:|---:|",
    ])

    for row in deltas:
        md.append(
            f"| {row['ap_channel']} | {row['target_ble_adv_channel']} | "
            f"{row['p95_delta']:+.1f} ms ({fmt_pct(row['p95_pct'])}) | "
            f"{row['mad_delta']:+.1f} ms | {row['missing_delta']:+.2f}/100 |"
        )

    md.extend([
        "",
        "## Interpretation",
        "",
        "- All 18 runs completed at the device side with 100 scheduled advertisements.",
        "- Logger capture remained high across the sweep, ranging from 94/100 to 100/100 per run.",
        "- No AP channel shows a clear heavy-load degradation pattern in BLE P95 latency. Channel 6 / advertising channel 38 shows a small mean P95 increase under heavy load, while channels 1 and 13 show lower mean P95 under heavy load than baseline.",
        "- The result is consistent with BLE advertisement/scanner timing variability dominating over a simple Wi-Fi-load monotonic effect in this setup.",
        "- The channel 13 baseline group has the highest mean missing-event count because `R672` missed 6 advertisements; this should be treated as a run-level capture anomaly unless repeated in additional data.",
        "",
        "## Generated Artifacts",
        "",
        f"- `{display_path(OUTPUT_RUNS_CSV)}`",
        f"- `{display_path(OUTPUT_SUMMARY_CSV)}`",
        f"- `{display_path(OUTPUT_FIGURE)}`",
    ])

    OUTPUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    meta_path = OUTPUT_MD.with_suffix(OUTPUT_MD.suffix + ".meta.json")
    meta_path.write_text(json.dumps({"metadata": metadata}, indent=2) + "\n", encoding="utf-8")


def main():
    records = collect_records()
    summary_rows = aggregate(records)
    deltas = heavy_delta(summary_rows)

    write_csv(OUTPUT_RUNS_CSV, records)
    write_csv(OUTPUT_SUMMARY_CSV, summary_rows)
    write_figure(summary_rows)
    write_markdown(records, summary_rows, deltas)

    print(f"[OK] Saved BLE channel-overlap run table -> {display_path(OUTPUT_RUNS_CSV)}")
    print(f"[OK] Saved BLE channel-overlap summary table -> {display_path(OUTPUT_SUMMARY_CSV)}")
    print(f"[OK] Saved BLE channel-overlap figure -> {display_path(OUTPUT_FIGURE)}")
    print(f"[OK] Saved BLE channel-overlap report -> {display_path(OUTPUT_MD)}")


if __name__ == "__main__":
    main()
