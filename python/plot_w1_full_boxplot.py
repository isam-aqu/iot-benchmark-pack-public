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


def normalize_median(x: np.ndarray) -> np.ndarray:
    return x - np.median(x)


def main():
    repo = Path(".")

    # Final W1 baselines:
    # Wi-Fi  -> R106 / W1_wifi_near_quiet_v6
    # Zigbee -> R204 / W1_zigbee_near_quiet_v3
    # BLE    -> R303 / W1_ble_near_quiet_v3

    wifi_path = repo / "experiments/runs/R106/derived/W1_wifi_near_quiet_v6_wifi_rtt_full.csv"
    zigbee_path = repo / "experiments/runs/R204/derived/W1_zigbee_near_quiet_v3_zigbee_events_processed_full.csv"
    ble_path = repo / "experiments/runs/R303/derived/W1_ble_near_quiet_v3_ble_events_processed_full.csv"

    # Load data
    wifi_raw = load_series(wifi_path, "rtt_ms")
    zigbee = load_series(zigbee_path, "norm_delay_ms")
    ble = load_series(ble_path, "norm_delay_ms")

    # Normalize Wi-Fi to match Zigbee/BLE methodology
    wifi = normalize_median(wifi_raw)

    print("Loaded datasets (normalized comparison):")
    print(f"  Wi-Fi  : {len(wifi)} samples (median-normalized)")
    print(f"  Zigbee : {len(zigbee)} samples (normalized)")
    print(f"  BLE    : {len(ble)} samples (normalized)")
    print()

    for label, data in [("Wi-Fi (norm)", wifi), ("Zigbee", zigbee), ("BLE", ble)]:
        print(label)
        print(f"  Mean   : {np.mean(data):.3f} ms")
        print(f"  Median : {np.median(data):.3f} ms")
        print(f"  Std    : {np.std(data, ddof=1):.3f} ms")
        print(f"  P95    : {np.percentile(data, 95):.3f} ms")
        print(f"  Min    : {np.min(data):.3f} ms")
        print(f"  Max    : {np.max(data):.3f} ms")
        print()

    fig, ax = plt.subplots(figsize=(8, 5.5))

    data = [wifi, zigbee, ble]
    labels = ["Wi-Fi", "Zigbee", "BLE"]

    # Boxplot (no fliers — we show all points)
    ax.boxplot(
        data,
        labels=labels,
        showfliers=False,
        whis=1.5,
        widths=0.55,
    )

    # Scatter overlay (ALL points)
    rng = np.random.default_rng(42)

    for i, y in enumerate(data, start=1):
        x = rng.normal(i, 0.04, size=len(y))

        if labels[i - 1] == "BLE":
            ax.plot(x, y, "o", alpha=0.45, markersize=4)
        else:
            ax.plot(x, y, "o", alpha=0.30, markersize=3)

    ax.set_title("W1 normalized latency distributions")
    ax.set_ylabel("Median-normalized latency (ms)")
    ax.grid(True, axis="y", alpha=0.3)

    analysis_base = repo / "analysis/w1/figures/w1_full_boxplot_normalized"
    paper_base = repo / "docs/paper_figures/fig04_w1_latency_boxplot_normalized"
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
