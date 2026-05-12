import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from paper_plot_style import apply_paper_style, save_paper_figure


apply_paper_style()


def load_series(path: Path, column: str) -> np.ndarray:
    df = pd.read_csv(path)
    values = pd.to_numeric(df[column], errors="coerce").dropna().values
    if len(values) == 0:
        raise ValueError(f"No valid values found in {path} column {column}")
    return values


def cdf(data: np.ndarray):
    sorted_data = np.sort(data)
    y = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    return sorted_data, y


def main():
    repo = Path(".")

    # Final W1 baselines:
    # Wi-Fi  -> R106 / W1_wifi_near_quiet_v6
    # Zigbee -> R204 / W1_zigbee_near_quiet_v3
    # BLE    -> R303 / W1_ble_near_quiet_v3

    # Input files
    wifi_path = repo / "experiments/runs/R106/derived/W1_wifi_near_quiet_v6_wifi_rtt_core.csv"
    zigbee_path = repo / "experiments/runs/R204/derived/W1_zigbee_near_quiet_v3_zigbee_events_processed.csv"
    ble_path = repo / "experiments/runs/R303/derived/W1_ble_near_quiet_v3_ble_events_processed.csv"

    # Load data
    wifi = load_series(wifi_path, "rtt_ms")
    zigbee = load_series(zigbee_path, "norm_delay_ms")
    ble = load_series(ble_path, "norm_delay_ms")

    # Median-normalize Wi-Fi too, so all three series are comparable
    wifi = wifi - np.median(wifi)

    # Summary printout
    print("Loaded datasets:")
    print(f"  Wi-Fi  : {wifi_path} ({len(wifi)} samples)")
    print(f"  Zigbee : {zigbee_path} ({len(zigbee)} samples)")
    print(f"  BLE    : {ble_path} ({len(ble)} samples)")
    print()

    print("Median-normalized summary:")
    for label, data in [("Wi-Fi", wifi), ("Zigbee", zigbee), ("BLE", ble)]:
        print(f"{label}:")
        print(f"  Mean   = {np.mean(data):.3f} ms")
        print(f"  Median = {np.median(data):.3f} ms")
        print(f"  Std    = {np.std(data, ddof=1):.3f} ms")
        print(f"  P95    = {np.percentile(data, 95):.3f} ms")
        print(f"  Min    = {np.min(data):.3f} ms")
        print(f"  Max    = {np.max(data):.3f} ms")
        print()

    plt.figure(figsize=(8, 5.5))

    series = [
        (wifi, "Wi-Fi", "-"),
        (zigbee, "Zigbee", "--"),
        (ble, "BLE", ":"),
    ]

    # All labels start at the same height, to the right of the P95 line
    p95_label_y = 0.20
    p95_label_x_offset = 2.0

    max_p95 = None

    for data, label, linestyle in series:
        x, y = cdf(data)

        line, = plt.plot(
            x,
            y,
            linestyle=linestyle,
            linewidth=2.2,
            label=label,
        )

        color = line.get_color()
        p95 = np.percentile(data, 95)

        if max_p95 is None or p95 > max_p95:
            max_p95 = p95

        plt.axvline(
            p95,
            linestyle=linestyle,
            linewidth=1.0,
            color=color,
            alpha=0.8,
        )

        plt.text(
            p95 + p95_label_x_offset,
            p95_label_y,
            f"{label} P95",
            rotation=90,
            fontsize=8,
            color=color,
            ha="left",
            va="bottom",
        )

    plt.xlabel("Median-normalized latency (ms)")
    plt.ylabel("Empirical CDF")
    plt.title("W1 median-normalized latency CDF")
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Keep some room on the right so the right-side P95 labels do not clip
    x_left = -120
    x_right = max(200, max_p95 + 18)
    plt.xlim(x_left, x_right)
    plt.ylim(0, 1.0)

    fig = plt.gcf()
    analysis_base = repo / "analysis/w1/figures/w1_cdf_comparison"
    paper_base = repo / "docs/paper_figures/fig05_w1_latency_empirical_cdf"
    analysis_outputs = save_paper_figure(fig, analysis_base)
    paper_outputs = save_paper_figure(fig, paper_base)
    plt.close()

    print("[OK] Saved analysis figure:")
    for path in analysis_outputs.values():
        print(f"  {path}")
    print("[OK] Saved paper figure:")
    for path in paper_outputs.values():
        print(f"  {path}")


if __name__ == "__main__":
    main()
