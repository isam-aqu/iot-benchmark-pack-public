import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from paper_plot_style import apply_paper_style, save_paper_figure


apply_paper_style()


def main():
    repo = Path(".")

    # Final W1 BLE baseline under corrected measurement setup
    path = repo / "experiments/runs/R303/derived/W1_ble_near_quiet_v3_ble_events_processed.csv"

    df = pd.read_csv(path)
    data = pd.to_numeric(df["norm_delay_ms"], errors="coerce").dropna().values

    if len(data) == 0:
        raise ValueError(f"No valid BLE samples found in {path}")

    print(f"Loaded {len(data)} BLE samples")
    print("BLE normalized latency summary:")
    print(f"  Mean   = {np.mean(data):.3f} ms")
    print(f"  Median = {np.median(data):.3f} ms")
    print(f"  Std    = {np.std(data, ddof=1):.3f} ms")
    print(f"  P95    = {np.percentile(data, 95):.3f} ms")
    print(f"  Min    = {np.min(data):.3f} ms")
    print(f"  Max    = {np.max(data):.3f} ms")

    plt.figure(figsize=(8, 5.5))

    # 5 ms bins give enough detail to reveal multi-modal structure
    bins = np.arange(-160, 220, 5)
    plt.hist(data, bins=bins)

    plt.xlabel("Median-normalized latency (ms)")
    plt.ylabel("Count")
    plt.title("W1 BLE median-normalized latency distribution")
    plt.grid(True, alpha=0.3)

    fig = plt.gcf()
    analysis_base = repo / "analysis/w1/figures/ble_latency_histogram"
    paper_base = repo / "docs/paper_figures/fig06_w1_ble_latency_histogram"
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
