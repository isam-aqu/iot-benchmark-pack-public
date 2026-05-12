import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from version_info import build_metadata, display_path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = REPO_ROOT / "analysis" / "w3" / "aggregates" / "w3_replicates.json"
SCRIPT_NAME = "python/plot_w3_results.py"

OUTPUT_FIGURES_DIR = REPO_ROOT / "analysis" / "w3" / "figures"
OUTPUT_WIFI_LATENCY = OUTPUT_FIGURES_DIR / "w3_latency_plot_ci.png"
OUTPUT_WIFI_ROBUST = OUTPUT_FIGURES_DIR / "w3_mad_drop_plot_ci.png"
OUTPUT_PROTOCOL_P95 = OUTPUT_FIGURES_DIR / "w3_protocol_p95_comparison_ci.png"
OUTPUT_PROTOCOL_ROBUST = OUTPUT_FIGURES_DIR / "w3_protocol_mad_anomaly_comparison_ci.png"

LOADS = ["baseline", "light", "moderate", "heavy"]
LOAD_LABELS = ["Baseline", "Light", "Moderate", "Heavy"]
PROTOCOLS = [
    {
        "slug": "wifi",
        "label": "Wi-Fi",
        "comparison_group": "W3_wifi_auto",
        "color": "tab:blue",
        "marker": "o",
        "anomaly_metric": "drop_rate",
        "anomaly_label": "Wi-Fi missing events",
    },
    {
        "slug": "zigbee",
        "label": "Zigbee",
        "comparison_group": "W3_zigbee_auto",
        "color": "tab:green",
        "marker": "s",
        "anomaly_metric": "extra_event_rate",
        "anomaly_label": "Zigbee extra state events",
    },
    {
        "slug": "ble",
        "label": "BLE",
        "comparison_group": "W3_ble_auto",
        "color": "tab:purple",
        "marker": "^",
        "anomaly_metric": "drop_rate",
        "anomaly_label": "BLE missed advertisements",
    },
]


def group_key(protocol, load_level):
    return f"{protocol['slug']}_{load_level}_{protocol['comparison_group']}"


def metric_values(aggregate, metric_name):
    metric = aggregate[metric_name]
    mean = metric["mean"]
    ci_low = metric["ci_low"]
    ci_high = metric["ci_high"]

    if mean is None or ci_low is None or ci_high is None:
        raise ValueError(f"Missing aggregate value for {metric_name}")

    return mean, ci_low, ci_high


def available_protocols(data):
    available = []
    for protocol in PROTOCOLS:
        if all(group_key(protocol, load) in data for load in LOADS):
            available.append(protocol)
    return available


def collect_metric(data, protocol, metric_name, multiplier=1.0):
    values, ci_low, ci_high = [], [], []

    for load in LOADS:
        key = group_key(protocol, load)
        agg = data[key]["aggregate"]
        mean, low, high = metric_values(agg, metric_name)

        values.append(mean * multiplier)
        ci_low.append(low * multiplier)
        ci_high.append(high * multiplier)

    return values, ci_low, ci_high


def asymmetric_error(values, ci_low, ci_high):
    return [
        [value - low for value, low in zip(values, ci_low)],
        [high - value for value, high in zip(values, ci_high)],
    ]


def write_plot_metadata(output_path, plot_name, metrics, source_metadata=None):
    meta_path = output_path.with_name(f"{output_path.name}.meta.json")
    payload = {
        "metadata": build_metadata(
            SCRIPT_NAME,
            inputs=[INPUT_PATH],
            outputs=[output_path, meta_path],
            extra={
                "plot_name": plot_name,
                "metrics": metrics,
            },
        )
    }
    if source_metadata:
        payload["source_metadata"] = source_metadata

    meta_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Saved plot metadata -> {display_path(meta_path)}")


def save_wifi_latency_plot(data):
    wifi = PROTOCOLS[0]
    median, median_ci_low, median_ci_high = collect_metric(data, wifi, "median_latency_ms")
    p95, p95_ci_low, p95_ci_high = collect_metric(data, wifi, "p95_latency_ms")

    median_err = asymmetric_error(median, median_ci_low, median_ci_high)
    p95_err = asymmetric_error(p95, p95_ci_low, p95_ci_high)

    plt.figure(figsize=(6, 4))
    plt.errorbar(
        LOAD_LABELS,
        median,
        yerr=median_err,
        marker="o",
        capsize=5,
        label="Median latency",
    )
    plt.errorbar(
        LOAD_LABELS,
        p95,
        yerr=p95_err,
        marker="s",
        linestyle="--",
        capsize=5,
        label="P95 latency",
    )

    plt.xlabel("Load level")
    plt.ylabel("Latency (ms)")
    plt.title("Wi-Fi Latency under Background Traffic (W3)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    OUTPUT_WIFI_LATENCY.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(OUTPUT_WIFI_LATENCY, dpi=300)
    plt.close()

    write_plot_metadata(
        OUTPUT_WIFI_LATENCY,
        "W3 Wi-Fi latency under background traffic",
        ["median_latency_ms", "p95_latency_ms"],
        source_metadata=data.get("metadata"),
    )
    print(f"[OK] Saved latency plot -> {display_path(OUTPUT_WIFI_LATENCY)}")


def save_wifi_robustness_plot(data):
    wifi = PROTOCOLS[0]
    mad, mad_ci_low, mad_ci_high = collect_metric(data, wifi, "mad_latency_ms")
    drop, drop_ci_low, drop_ci_high = collect_metric(data, wifi, "drop_rate", multiplier=100.0)

    mad_err = asymmetric_error(mad, mad_ci_low, mad_ci_high)
    drop_err = asymmetric_error(drop, drop_ci_low, drop_ci_high)
    x = list(range(len(LOAD_LABELS)))
    mad_x = [pos - 0.04 for pos in x]
    drop_x = [pos + 0.04 for pos in x]
    mad_color = "tab:blue"
    drop_color = "tab:orange"

    fig, ax1 = plt.subplots(figsize=(6, 4))
    ax1.errorbar(
        mad_x,
        mad,
        yerr=mad_err,
        marker="o",
        capsize=5,
        color=mad_color,
        ecolor=mad_color,
        label="MAD latency",
        zorder=3,
    )
    ax1.set_xlabel("Load level")
    ax1.set_ylabel("MAD latency (ms)")
    ax1.set_ylim(0, 5.5)
    ax1.set_xticks(x)
    ax1.set_xticklabels(LOAD_LABELS)
    ax1.grid(True)

    ax2 = ax1.twinx()
    ax2.errorbar(
        drop_x,
        drop,
        yerr=drop_err,
        marker="s",
        linestyle="--",
        capsize=5,
        color=drop_color,
        ecolor=drop_color,
        label="Drop rate",
        zorder=2,
    )
    ax2.set_ylabel("Drop rate (%)")
    ax2.set_ylim(0, 5.5)

    lines_1, labels_1 = ax1.get_legend_handles_labels()
    lines_2, labels_2 = ax2.get_legend_handles_labels()
    ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc="upper left")

    plt.title("Wi-Fi Variability and Reliability under Load (W3)")
    plt.tight_layout()
    plt.savefig(OUTPUT_WIFI_ROBUST, dpi=300)
    plt.close()

    write_plot_metadata(
        OUTPUT_WIFI_ROBUST,
        "W3 Wi-Fi variability and reliability under load",
        ["mad_latency_ms", "drop_rate"],
        source_metadata=data.get("metadata"),
    )
    print(f"[OK] Saved robustness plot -> {display_path(OUTPUT_WIFI_ROBUST)}")


def save_protocol_p95_plot(data):
    protocols = available_protocols(data)
    x = np.arange(len(LOAD_LABELS))
    width = min(0.28, 0.8 / max(len(protocols), 1))

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for idx, protocol in enumerate(protocols):
        p95, ci_low, ci_high = collect_metric(data, protocol, "p95_latency_ms")
        offset = (idx - (len(protocols) - 1) / 2.0) * width
        ax.bar(
            x + offset,
            p95,
            width,
            yerr=asymmetric_error(p95, ci_low, ci_high),
            capsize=4,
            color=protocol["color"],
            label=protocol["label"],
            alpha=0.88,
        )

    ax.set_xlabel("Load level")
    ax.set_ylabel("P95 latency (ms)")
    ax.set_title("Protocol Tail Latency under W3 Load")
    ax.set_xticks(x)
    ax.set_xticklabels(LOAD_LABELS)
    ax.grid(True, axis="y", alpha=0.35)
    ax.legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_PROTOCOL_P95, dpi=300)
    plt.close()

    write_plot_metadata(
        OUTPUT_PROTOCOL_P95,
        "W3 protocol P95 latency comparison",
        ["p95_latency_ms"],
        source_metadata=data.get("metadata"),
    )
    print(f"[OK] Saved protocol P95 plot -> {display_path(OUTPUT_PROTOCOL_P95)}")


def save_protocol_robustness_plot(data):
    protocols = available_protocols(data)
    x = np.arange(len(LOAD_LABELS))
    width = min(0.28, 0.8 / max(len(protocols), 1))

    fig, (ax_mad, ax_rel) = plt.subplots(1, 2, figsize=(10.2, 4.1))

    for protocol in protocols:
        mad, ci_low, ci_high = collect_metric(data, protocol, "mad_latency_ms")
        ax_mad.errorbar(
            LOAD_LABELS,
            mad,
            yerr=asymmetric_error(mad, ci_low, ci_high),
            marker=protocol["marker"],
            capsize=4,
            color=protocol["color"],
            label=protocol["label"],
        )

    ax_mad.set_xlabel("Load level")
    ax_mad.set_ylabel("MAD latency (ms)")
    ax_mad.set_title("Latency Variability")
    ax_mad.grid(True, axis="y", alpha=0.35)
    ax_mad.legend()

    reliability_specs = [
        (protocol, protocol["anomaly_metric"], protocol["anomaly_label"])
        for protocol in protocols
    ]

    for idx, (protocol, metric_name, label) in enumerate(reliability_specs):
        values, ci_low, ci_high = collect_metric(data, protocol, metric_name, multiplier=100.0)
        offset = (idx - (len(reliability_specs) - 1) / 2.0) * width
        ax_rel.bar(
            x + offset,
            values,
            width,
            yerr=asymmetric_error(values, ci_low, ci_high),
            capsize=4,
            color=protocol["color"],
            label=label,
            alpha=0.88,
        )

    ax_rel.set_xlabel("Load level")
    ax_rel.set_ylabel("Event anomaly rate (%)")
    ax_rel.set_title("Reliability Anomalies")
    ax_rel.set_xticks(x)
    ax_rel.set_xticklabels(LOAD_LABELS)
    ax_rel.grid(True, axis="y", alpha=0.35)
    ax_rel.legend()

    plt.suptitle("Protocol Robustness under W3 Load", y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_PROTOCOL_ROBUST, dpi=300, bbox_inches="tight")
    plt.close()

    write_plot_metadata(
        OUTPUT_PROTOCOL_ROBUST,
        "W3 protocol variability and reliability comparison",
        ["mad_latency_ms", "drop_rate", "extra_event_rate"],
        source_metadata=data.get("metadata"),
    )
    print(f"[OK] Saved protocol robustness plot -> {display_path(OUTPUT_PROTOCOL_ROBUST)}")


def main():
    with INPUT_PATH.open(encoding="utf-8") as f:
        data = json.load(f)

    save_wifi_latency_plot(data)
    save_wifi_robustness_plot(data)
    save_protocol_p95_plot(data)
    save_protocol_robustness_plot(data)


if __name__ == "__main__":
    main()
