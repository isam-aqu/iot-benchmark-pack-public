import csv
import json
from pathlib import Path

from version_info import build_metadata, display_path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "analysis" / "w3" / "aggregates" / "w3_replicates.json"
OUTPUT_MD = REPO_ROOT / "analysis" / "w3" / "reports" / "w3_protocol_comparison.md"
OUTPUT_CSV = REPO_ROOT / "analysis" / "w3" / "tables" / "w3_protocol_comparison.csv"
SCRIPT_NAME = "python/report_w3_protocol_comparison.py"

LOADS = ["baseline", "light", "moderate", "heavy"]
LOAD_LABELS = {
    "baseline": "Baseline",
    "light": "Light",
    "moderate": "Moderate",
    "heavy": "Heavy",
}
PROTOCOLS = {
    "wifi": {
        "label": "Wi-Fi",
        "comparison_group": "W3_wifi_auto",
        "run_range": "R600-R619",
        "latency_model": "ESP32 MQTT publish-to-ACK RTT",
        "reliability_metric": "missing event/drop rate",
    },
    "zigbee": {
        "label": "Zigbee",
        "comparison_group": "W3_zigbee_auto",
        "run_range": "R620-R639",
        "latency_model": "Home Assistant state-change time to logger receive time, median-normalized",
        "reliability_metric": "extra state-event rate",
    },
    "ble": {
        "label": "BLE",
        "comparison_group": "W3_ble_auto",
        "run_range": "R640-R659",
        "latency_model": "ESP32 advertiser timestamp to logger receive time, median-normalized",
        "reliability_metric": "missed advertisement/drop rate",
    },
}


def group_key(protocol, load):
    config = PROTOCOLS[protocol]
    return f"{protocol}_{load}_{config['comparison_group']}"


def metric(group, name):
    return group["aggregate"][name]


def mean(group, name):
    return metric(group, name)["mean"]


def runs(group):
    return ", ".join(f"`{run_id}`" for run_id in group["runs"])


def fmt_ms(value):
    if value is None:
        return "n/a"
    if abs(value) < 0.005:
        return "0.00 ms"
    return f"{value:.2f} ms"


def fmt_rate(value):
    if value is None:
        return "n/a"
    return f"{value * 100.0:.1f}%"


def fmt_pct_delta(value):
    if value is None:
        return "n/a"
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.1f}%"


def pct_change(value, baseline):
    if value is None or baseline in (None, 0):
        return None
    return 100.0 * (value - baseline) / baseline


def protocol_group(data, protocol, load):
    return data[group_key(protocol, load)]


def available_protocols(data):
    return [
        protocol for protocol in PROTOCOLS
        if all(group_key(protocol, load) in data for load in LOADS)
    ]


def build_rows(data):
    rows = []
    for protocol in available_protocols(data):
        config = PROTOCOLS[protocol]
        baseline_group = protocol_group(data, protocol, "baseline")
        baseline_p95 = mean(baseline_group, "p95_latency_ms")
        baseline_mad = mean(baseline_group, "mad_latency_ms")

        for load in LOADS:
            group = protocol_group(data, protocol, load)
            drop_rate = mean(group, "drop_rate")
            extra_event_rate = mean(group, "extra_event_rate")
            row = {
                "protocol": config["label"],
                "load": LOAD_LABELS[load],
                "runs": ", ".join(group["runs"]),
                "median_latency_ms": mean(group, "median_latency_ms"),
                "p95_latency_ms": mean(group, "p95_latency_ms"),
                "mad_latency_ms": mean(group, "mad_latency_ms"),
                "drop_rate": drop_rate,
                "extra_event_rate": extra_event_rate,
                "p95_pct_vs_baseline": pct_change(mean(group, "p95_latency_ms"), baseline_p95),
                "mad_pct_vs_baseline": pct_change(mean(group, "mad_latency_ms"), baseline_mad),
            }
            rows.append(row)

    return rows


def write_csv(rows):
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "protocol",
                "load",
                "runs",
                "median_latency_ms",
                "p95_latency_ms",
                "mad_latency_ms",
                "drop_rate",
                "extra_event_rate",
                "p95_pct_vs_baseline",
                "mad_pct_vs_baseline",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(data, rows):
    metadata = build_metadata(
        SCRIPT_NAME,
        inputs=[INPUT_PATH],
        outputs=[OUTPUT_MD, OUTPUT_CSV, OUTPUT_MD.with_name(f"{OUTPUT_MD.name}.meta.json")],
    )

    md = []
    protocols = available_protocols(data)
    protocol_labels = [PROTOCOLS[protocol]["label"] for protocol in protocols]
    title = "W3 Protocol Comparison"
    if protocol_labels == ["Wi-Fi", "Zigbee"]:
        title = "W3 Wi-Fi vs Zigbee Comparison"

    md.append(f"# {title}")
    md.append("")
    md.append(f"Generated: {metadata['generated_at_local']}")
    md.append("")
    md.append("## Scope")
    md.append("")
    for protocol in protocols:
        config = PROTOCOLS[protocol]
        md.append(f"- {config['label']} W3 runs: `{config['run_range']}`, five replicates per load level.")
    md.append("- Load levels: baseline, 5 Mbps TCP, 20 Mbps TCP, and 50 Mbps TCP background traffic.")
    md.append("- Means are computed across completed W3 replicates; confidence intervals are in `analysis/w3/aggregates/w3_replicates.json` and the generated figures.")
    md.append("")
    md.append("## RF Channel Context")
    md.append("")
    md.append("- Wi-Fi AP: netis WF2419, firmware `V2.2.36123`.")
    md.append("- The AP was later found to use Auto channel selection, so the AP channel for `R600-R639` is unknown from preserved metadata and may have changed after restarts.")
    md.append("- During `R640-R659`, the AP was observed on channel 1, channel width 40 MHz, control sideband Upper.")
    md.append("- Zigbee: channel 20.")
    md.append("- BLE legacy advertising: primary advertising channels 37, 38, and 39 (`2402`, `2426`, and `2480 MHz`).")
    md.append("")
    md.append("The Wi-Fi and Zigbee W3 results therefore represent system-level robustness under the tested 2.4 GHz background-load condition, not a channel-specific Wi-Fi/Zigbee coexistence experiment. For BLE, the observed `R640-R659` channel-1 40 MHz upper-sideband setting likely overlaps advertising channels 37 and 38, so the BLE results should be treated as shared-load behavior rather than a clean single-advertising-channel overlap test.")
    md.append("")
    md.append("Focused AP-channel extensions were completed separately from the main W3 aggregate: BLE runs `R660-R677` use 20 MHz AP width on channels 1, 6, and 13 to target advertising channels 37, 38, and 39; Zigbee runs `R678-R697` use AP channel 1 as a 20 MHz non-overlap/control block and AP channel 9 as the Zigbee-channel-20 overlap block. Their dedicated analyses are in `analysis/w3/reports/w3_ble_channel_overlap.md` and `analysis/w3/reports/w3_zigbee_channel_overlap.md`.")
    md.append("")
    md.append("## Measurement Caveat")
    md.append("")
    caveats = [f"{PROTOCOLS[protocol]['label']} uses {PROTOCOLS[protocol]['latency_model']}." for protocol in protocols]
    md.append(" ".join(caveats) + " The comparison therefore emphasizes robustness trends, tail behavior, variability, and event reliability rather than absolute link-layer latency.")
    md.append("")
    md.append("## Aggregate Metrics")
    md.append("")
    md.append("| Protocol | Load | Runs | Median | P95 | MAD | Drop rate | Extra-event rate |")
    md.append("|---|---|---|---:|---:|---:|---:|---:|")

    for row in rows:
        md.append(
            "| {protocol} | {load} | {runs} | {median} | {p95} | {mad} | {drop} | {extra} |".format(
                protocol=row["protocol"],
                load=row["load"],
                runs=", ".join(f"`{run_id}`" for run_id in row["runs"].split(", ")),
                median=fmt_ms(row["median_latency_ms"]),
                p95=fmt_ms(row["p95_latency_ms"]),
                mad=fmt_ms(row["mad_latency_ms"]),
                drop=fmt_rate(row["drop_rate"]),
                extra=fmt_rate(row["extra_event_rate"]),
            )
        )

    md.append("")
    md.append("## Change vs Protocol Baseline")
    md.append("")
    md.append("| Protocol | Load | P95 change | MAD change |")
    md.append("|---|---|---:|---:|")
    for row in rows:
        if row["load"] == "Baseline":
            continue
        md.append(
            f"| {row['protocol']} | {row['load']} | "
            f"{fmt_pct_delta(row['p95_pct_vs_baseline'])} | "
            f"{fmt_pct_delta(row['mad_pct_vs_baseline'])} |"
        )

    md.append("")
    md.append("## Interpretation")
    md.append("")
    if "wifi" in protocols:
        wifi_heavy = protocol_group(data, "wifi", "heavy")
        wifi_moderate = protocol_group(data, "wifi", "moderate")
        md.append("- Wi-Fi W3 shows increasing tail latency and variability under load. P95 rises from "
                  f"{fmt_ms(mean(protocol_group(data, 'wifi', 'baseline'), 'p95_latency_ms'))} at baseline to "
                  f"{fmt_ms(mean(wifi_moderate, 'p95_latency_ms'))} at moderate load and "
                  f"{fmt_ms(mean(wifi_heavy, 'p95_latency_ms'))} at heavy load.")
    if "zigbee" in protocols:
        zigbee_heavy = protocol_group(data, "zigbee", "heavy")
        zigbee_moderate = protocol_group(data, "zigbee", "moderate")
        md.append("- Zigbee W3 remains tightly bounded across the same load levels. P95 stays near "
                  f"{fmt_ms(mean(protocol_group(data, 'zigbee', 'baseline'), 'p95_latency_ms'))} to "
                  f"{fmt_ms(mean(zigbee_heavy, 'p95_latency_ms'))}, with no missing events in the completed Zigbee runs.")
        md.append("- The main Zigbee quality signal is not event loss, but occasional extra state events: the moderate group averages "
                  f"{fmt_rate(mean(zigbee_moderate, 'extra_event_rate'))} and the heavy group averages "
                  f"{fmt_rate(mean(zigbee_heavy, 'extra_event_rate'))} extra events, driven by R627, R638, and R639.")
    if "ble" in protocols:
        ble_heavy = protocol_group(data, "ble", "heavy")
        md.append("- BLE W3 is interpreted through median-normalized advertisement capture latency and missed-advertisement rate. Heavy-load P95 is "
                  f"{fmt_ms(mean(ble_heavy, 'p95_latency_ms'))} with a drop rate of "
                  f"{fmt_rate(mean(ble_heavy, 'drop_rate'))}.")
    if "wifi" in protocols and "zigbee" in protocols:
        md.append("- Under this W3 setup, Zigbee is less sensitive to Wi-Fi iperf load in latency-tail terms, while Wi-Fi is more affected by shared-network contention at the tail and variability levels.")
    md.append("")
    md.append("## Generated Artifacts")
    md.append("")
    md.append("- `analysis/w3/aggregates/w3_replicates.json`")
    md.append("- `analysis/w3/figures/w3_latency_plot_ci.png`")
    md.append("- `analysis/w3/figures/w3_mad_drop_plot_ci.png`")
    md.append("- `analysis/w3/figures/w3_protocol_p95_comparison_ci.png`")
    md.append("- `analysis/w3/figures/w3_protocol_mad_anomaly_comparison_ci.png`")
    md.append("- `analysis/w3/tables/w3_protocol_comparison.csv`")
    md.append("")

    OUTPUT_MD.write_text("\n".join(md), encoding="utf-8")
    meta_path = OUTPUT_MD.with_name(f"{OUTPUT_MD.name}.meta.json")
    meta_path.write_text(
        json.dumps(
            {
                "metadata": metadata,
                "source_metadata": data.get("metadata"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def main():
    data = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    rows = build_rows(data)
    write_csv(rows)
    write_markdown(data, rows)
    print(f"[OK] Saved W3 comparison report -> {display_path(OUTPUT_MD)}")
    print(f"[OK] Saved W3 comparison CSV -> {display_path(OUTPUT_CSV)}")


if __name__ == "__main__":
    main()
