import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from paper_plot_style import apply_paper_style, save_paper_figure


OUT_DIR = Path("docs/paper_figures")


BLUE = "#EAF2F8"
ORANGE = "#FEF5E7"
GREEN = "#EAF7EA"
PURPLE = "#F4ECF7"
RED = "#FDEDEC"
GRAY = "#F7F7F7"
EDGE = "#333333"


def add_box(ax, xy, width, height, text, *, facecolor=GRAY, fontsize=8, lw=0.9):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        linewidth=lw,
        edgecolor=EDGE,
        facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(
        x + width / 2,
        y + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        linespacing=1.15,
    )
    return patch


def add_label(ax, x, y, text, *, fontsize=8, weight="normal"):
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, weight=weight)


def add_arrow(
    ax,
    start,
    end,
    *,
    label=None,
    label_offset=(0, 0),
    linestyle="-",
    color=EDGE,
    rad=0.0,
):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=0.9,
        linestyle=linestyle,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        shrinkA=3,
        shrinkB=3,
    )
    ax.add_patch(arrow)
    if label:
        mx = (start[0] + end[0]) / 2 + label_offset[0]
        my = (start[1] + end[1]) / 2 + label_offset[1]
        ax.text(
            mx,
            my,
            label,
            ha="center",
            va="center",
            fontsize=6.5,
            bbox={"facecolor": "white", "edgecolor": "none", "pad": 0.5, "alpha": 0.9},
        )


def setup_axis(width=12.0, height=7.0, figsize=(7.2, 4.2)):
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def draw_system_architecture():
    fig, ax = setup_axis(figsize=(7.4, 4.5))

    add_label(ax, 1.55, 6.55, "IoT nodes", fontsize=8.5, weight="bold")
    add_label(ax, 4.45, 6.55, "Protocol gateways", fontsize=8.5, weight="bold")
    add_label(ax, 7.25, 6.55, "Controller / broker", fontsize=8.5, weight="bold")
    add_label(ax, 10.2, 6.55, "External logger", fontsize=8.5, weight="bold")

    add_box(ax, (0.35, 5.35), 2.35, 0.72, "ESP32 Wi-Fi\nMQTT node", facecolor=BLUE)
    add_box(ax, (0.35, 4.15), 2.35, 0.72, "Tuya TS0001\nZigbee device", facecolor=BLUE)
    add_box(ax, (0.35, 2.95), 2.35, 0.72, "ESP32 BLE\nadvertiser", facecolor=BLUE)
    add_box(ax, (0.35, 1.35), 2.35, 0.72, "INA231 + ESP32\npower path", facecolor=RED)

    add_box(ax, (3.45, 5.35), 2.0, 0.72, "Wi-Fi AP\n2.4 GHz", facecolor=ORANGE)
    add_box(ax, (3.45, 4.15), 2.0, 0.72, "Sonoff Zigbee\ncoordinator", facecolor=ORANGE)
    add_box(ax, (3.45, 2.95), 2.0, 0.72, "BLE scanner\non logger", facecolor=ORANGE)
    add_box(ax, (3.45, 1.35), 2.0, 0.72, "USB-UART\nserial only", facecolor=ORANGE)

    ha = add_box(ax, (6.25, 4.75), 2.05, 0.86, "Raspberry Pi\nHome Assistant", facecolor=GREEN, fontsize=7.4)
    mqtt = add_box(ax, (6.25, 3.45), 2.05, 0.86, "Mosquitto MQTT\nbroker", facecolor=GREEN, fontsize=7.4)

    logger = add_box(ax, (9.25, 3.0), 2.45, 1.0, "Python event loggers\nEthernet-connected", facecolor=PURPLE, fontsize=7.3)
    analysis = add_box(ax, (9.25, 1.35), 2.45, 0.86, "Run artifacts\nCSV / JSON / figures", facecolor=PURPLE, fontsize=7.4)

    add_arrow(ax, (2.7, 5.71), (3.45, 5.71), label="MQTT", label_offset=(0, 0.16))
    add_arrow(ax, (5.45, 5.71), (6.25, 5.18))
    add_arrow(ax, (2.7, 4.51), (3.45, 4.51), label="802.15.4", label_offset=(0, 0.16))
    add_arrow(ax, (5.45, 4.51), (6.25, 5.18), label="ZHA", label_offset=(0.15, -0.05))
    add_arrow(ax, (2.7, 3.31), (3.45, 3.31))
    add_arrow(ax, (2.7, 1.71), (3.45, 1.71))

    add_arrow(ax, (7.27, 4.75), (7.27, 4.31), label="events", label_offset=(0.42, 0))
    add_arrow(ax, (8.3, 3.88), (9.25, 3.65))
    add_arrow(ax, (5.45, 3.31), (9.25, 3.35))
    add_arrow(ax, (5.45, 1.71), (9.25, 1.78), rad=0.04)
    add_arrow(ax, (10.48, 3.0), (10.48, 2.21), label="analysis", label_offset=(0.42, 0))

    outputs = save_paper_figure(fig, OUT_DIR / "fig01_system_architecture")
    plt.close(fig)
    return outputs


def draw_measurement_models():
    fig, ax = setup_axis(figsize=(7.4, 4.8))
    ROW_SHADE = "#FAFAFA"
    VALIDATION_SHADE = "#F1F1F1"
    ANALYSIS_SHADE = "#FFFFFF"
    CLAIM_SHADE = "#F7F7F7"

    ax.text(
        6.0,
        6.62,
        "Measurement-aware evaluation framework",
        ha="center",
        va="center",
        fontsize=9.2,
        weight="bold",
    )

    headers = [
        (0.45, "Protocol and\nworkload semantics"),
        (3.2, "Measurement\nboundary validation"),
        (6.05, "Common analysis\nlayer"),
        (8.9, "Interpretation\nboundary"),
    ]
    for x, text in headers:
        add_box(ax, (x, 5.82), 2.35, 0.52, text, facecolor=VALIDATION_SHADE, fontsize=7.3)

    protocol_rows = [
        (
            4.82,
            "Wi-Fi W1/W3\nESP32 MQTT RTT\nsingle device clock",
            "Validated logger path\nEthernet event capture\nremoves Wi-Fi coupling",
            "RTT distribution\nP95, MAD, KS\nmissing ACKs",
            "System-level Wi-Fi\nresponsiveness and\ntail robustness",
        ),
        (
            3.62,
            "Zigbee W1/W3\nHA trigger to\nlogger receive",
            "Boundary includes\nZHA, state update,\nMQTT forward",
            "Median normalization\nP95, MAD, KS\nextra state events",
            "Automation-path\nlatency and state\naccounting",
        ),
        (
            2.42,
            "BLE W1/W3\nadvertiser timestamp\nto scanner receive",
            "Cross-device clocks\nand scanner timing\nmade explicit",
            "Median normalization\nmulti-modal shape\nmissed advertisements",
            "Advertisement-mode\ndetection behavior,\nnot connection latency",
        ),
        (
            1.22,
            "W2 energy\nESP32 Wi-Fi MQTT\ntelemetry node",
            "Serial-only power log\nseparates measurement\nfrom MQTT workload",
            "Matched pairs\n95% CI / Wilcoxon\nnoise-floor check",
            "Node-local telemetry\nenergy detectability,\nnot protocol ranking",
        ),
    ]

    x_positions = [0.35, 3.12, 5.96, 8.85]
    widths = [2.55, 2.6, 2.6, 2.75]
    height = 0.78
    column_shades = [ROW_SHADE, VALIDATION_SHADE, ANALYSIS_SHADE, CLAIM_SHADE]

    for y, *texts in protocol_rows:
        for x, width, text, facecolor in zip(x_positions, widths, texts, column_shades):
            add_box(ax, (x, y), width, height, text, facecolor=facecolor, fontsize=6.6)
        row_mid_y = y + height / 2
        add_arrow(ax, (x_positions[0] + widths[0], row_mid_y), (x_positions[1], row_mid_y))
        add_arrow(ax, (x_positions[1] + widths[1], row_mid_y), (x_positions[2], row_mid_y))
        add_arrow(ax, (x_positions[2] + widths[2], row_mid_y), (x_positions[3], row_mid_y))

    add_box(
        ax,
        (0.45, 0.18),
        5.25,
        0.74,
        "Validation guard:\ntiming anchors, logging transport, event accounting,\nand power-measurement path are checked",
        facecolor=VALIDATION_SHADE,
        fontsize=6.3,
    )
    add_box(
        ax,
        (6.18, 0.18),
        5.35,
        0.74,
        "Claim guard:\ncompare shape, tails, anomalies, and detectability\nwithin stated boundaries",
        facecolor=GRAY,
        fontsize=6.3,
    )
    add_arrow(ax, (5.7, 0.55), (6.18, 0.55))

    outputs = save_paper_figure(fig, OUT_DIR / "fig02_measurement_models")
    plt.close(fig)
    return outputs


def draw_ina231_wiring():
    fig, ax = setup_axis(figsize=(7.4, 4.4))

    supply = add_box(ax, (0.35, 4.95), 2.0, 0.72, "External\n5 V supply", facecolor=RED)
    ina = add_box(ax, (4.0, 3.65), 3.05, 1.9, "INA231 high-side\ncurrent / voltage monitor", facecolor=RED, fontsize=8.3)
    esp = add_box(ax, (9.0, 3.55), 2.55, 2.05, "ESP32 node\nWi-Fi telemetry\nfirmware", facecolor=BLUE, fontsize=8.2)
    uart = add_box(ax, (8.95, 1.05), 2.65, 0.9, "USB-UART adapter\nTX0 / RX0 / GND", facecolor=ORANGE, fontsize=8)
    laptop = add_box(ax, (4.2, 0.75), 2.55, 0.78, "Laptop logger\nserial capture", facecolor=PURPLE)

    ax.text(3.92, 5.0, "VIN+", fontsize=7, ha="right", va="center")
    ax.text(7.12, 5.18, "VIN-", fontsize=7, ha="left", va="center")
    ax.text(7.12, 4.62, "BUS", fontsize=7, ha="left", va="center")
    ax.text(5.52, 3.55, "GND", fontsize=7, ha="center", va="top")
    ax.text(7.12, 4.12, "SDA/SCL", fontsize=7, ha="left", va="center")

    add_arrow(ax, (2.35, 5.31), (4.0, 5.0))
    ax.text(3.1, 5.36, "5 V", fontsize=7, ha="center")
    add_arrow(ax, (7.05, 5.05), (9.0, 5.05))
    add_arrow(ax, (7.05, 4.5), (9.0, 4.72), linestyle="--")
    add_arrow(ax, (7.05, 3.95), (9.0, 4.25))

    ax.plot([0.65, 11.25], [2.55, 2.55], color=EDGE, linewidth=0.9)
    ax.text(0.72, 2.75, "common ground", fontsize=7, ha="left")
    ax.plot([1.35, 1.35], [4.95, 2.55], color=EDGE, linewidth=0.9)
    ax.plot([5.52, 5.52], [3.65, 2.55], color=EDGE, linewidth=0.9)
    ax.plot([10.25, 10.25], [3.55, 2.55], color=EDGE, linewidth=0.9)
    ax.plot([10.25, 10.25], [1.95, 2.55], color=EDGE, linewidth=0.9)

    add_arrow(ax, (10.25, 3.55), (10.25, 1.95), label="TX/RX/GND", label_offset=(0.65, 0))
    add_arrow(ax, (8.95, 1.5), (6.75, 1.14), label="serial power log")

    ax.text(
        6.0,
        6.25,
        "Power path and measurement path are separated for W2",
        ha="center",
        va="center",
        fontsize=9,
        weight="bold",
    )
    ax.text(
        6.0,
        0.28,
        "USB-UART is used for data only; the ESP32 is powered through the INA231 so node current is measured at the high side.",
        ha="center",
        va="center",
        fontsize=7.4,
    )

    outputs = save_paper_figure(fig, OUT_DIR / "fig03_w2_power_measurement_setup")
    plt.close(fig)
    return outputs


def main():
    apply_paper_style()
    generated = {
        "system_architecture": draw_system_architecture(),
        "measurement_models": draw_measurement_models(),
        "ina231_wiring": draw_ina231_wiring(),
    }
    for name, outputs in generated.items():
        print(f"[OK] {name}")
        for path in outputs.values():
            print(f"  {path}")


if __name__ == "__main__":
    main()
