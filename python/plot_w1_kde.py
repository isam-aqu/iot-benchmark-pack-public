import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from paper_plot_style import apply_paper_style, save_paper_figure


apply_paper_style()


def load_series(path: Path, column: str) -> np.ndarray:
    df = pd.read_csv(path)
    values = pd.to_numeric(df[column], errors="coerce").dropna().values
    if len(values) == 0:
        raise ValueError(f"No valid values found in {path} column {column}")
    return values


def normalize_median(data: np.ndarray) -> np.ndarray:
    return data - np.median(data)


def kde_manual(data: np.ndarray, x_grid: np.ndarray, bandwidth: float) -> np.ndarray:
    kde = np.zeros_like(x_grid, dtype=float)
    for value in data:
        kde += np.exp(-0.5 * ((x_grid - value) / bandwidth) ** 2)
    kde /= len(data) * bandwidth * np.sqrt(2 * np.pi)
    return kde


def main():
    repo = Path(".")

    wifi_path = repo / "experiments/runs/R106/derived/W1_wifi_near_quiet_v6_wifi_rtt_core.csv"
    zigbee_path = repo / "experiments/runs/R204/derived/W1_zigbee_near_quiet_v3_zigbee_events_processed.csv"
    ble_path = repo / "experiments/runs/R303/derived/W1_ble_near_quiet_v3_ble_events_processed.csv"

    wifi = normalize_median(load_series(wifi_path, "rtt_ms"))
    zigbee = load_series(zigbee_path, "norm_delay_ms")
    ble = load_series(ble_path, "norm_delay_ms")

    xmin = min(wifi.min(), zigbee.min(), ble.min())
    xmax = max(wifi.max(), zigbee.max(), ble.max())
    x_grid = np.linspace(xmin, xmax, 1000)

    kde_wifi = kde_manual(wifi, x_grid, bandwidth=5)
    kde_zigbee = kde_manual(zigbee, x_grid, bandwidth=8)
    kde_ble = kde_manual(ble, x_grid, bandwidth=12)

    print("Loaded datasets:")
    print(f"  Wi-Fi  : {wifi_path} ({len(wifi)} samples, median-normalized from rtt_ms)")
    print(f"  Zigbee : {zigbee_path} ({len(zigbee)} samples, norm_delay_ms)")
    print(f"  BLE    : {ble_path} ({len(ble)} samples, norm_delay_ms)")

    plt.figure(figsize=(10, 5))
    plt.plot(x_grid, kde_wifi, linewidth=2, label="Wi-Fi (R106)")
    plt.plot(x_grid, kde_zigbee, linewidth=2, label="Zigbee (R204)")
    plt.plot(x_grid, kde_ble, linewidth=2, linestyle="--", label="BLE (R303)")

    plt.xlabel("Median-normalized latency (ms)")
    plt.ylabel("Probability density")
    plt.title("W1 latency density estimates")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    fig = plt.gcf()
    analysis_base = repo / "analysis/w1/figures/w1_latency_kde"
    paper_base = repo / "docs/paper_figures/fig07_w1_latency_kde"
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
