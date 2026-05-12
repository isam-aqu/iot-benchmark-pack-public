import os
import sys
from pathlib import Path
import numpy as np
import pandas as pd

DEFAULT_RUN_PATH = Path("experiments/runs/R303/derived/W1_ble_near_quiet_v3_ble_events_processed.csv")

# How aggressively to merge nearby values into the same cluster
ROUND_DECIMALS = 0   # 0 => 1 ms buckets, 1 => 0.1 ms buckets

# Minimum jump size to consider "between clusters"
MIN_JUMP_MS = 8.0

run_path_arg = sys.argv[1] if len(sys.argv) > 1 else os.getenv("BLE_RUN_PATH", "").strip()
RUN_PATH = Path(run_path_arg) if run_path_arg else DEFAULT_RUN_PATH

df = pd.read_csv(RUN_PATH)

vals = pd.to_numeric(df["norm_delay_ms"], errors="coerce").dropna().to_numpy()
vals = np.sort(vals)

print(f"Loaded {len(vals)} BLE core samples from {RUN_PATH}")
print()

# 1) Show rounded value frequencies
rounded = np.round(vals, ROUND_DECIMALS)
freq = pd.Series(rounded).value_counts().sort_index()

print(f"Top rounded latency buckets (rounded to {ROUND_DECIMALS} decimals):")
print(freq.sort_values(ascending=False).head(20).to_string())
print()

# 2) Find unique rounded levels and jumps between them
levels = np.array(sorted(freq.index.to_numpy()))
level_diffs = np.diff(levels)

print("Unique rounded levels (first 40):")
print(levels[:40])
print()

large_jumps = level_diffs[level_diffs >= MIN_JUMP_MS]
print(f"Jumps between adjacent rounded levels >= {MIN_JUMP_MS} ms:")
print(large_jumps if len(large_jumps) else "None")
print()

if len(large_jumps):
    print("Jump statistics:")
    print(f"Count:  {len(large_jumps)}")
    print(f"Mean:   {np.mean(large_jumps):.3f} ms")
    print(f"Median: {np.median(large_jumps):.3f} ms")
    print(f"Min:    {np.min(large_jumps):.3f} ms")
    print(f"Max:    {np.max(large_jumps):.3f} ms")
    print()

# 3) Very simple cluster extraction based on large jumps
clusters = []
start = 0
for i, d in enumerate(np.diff(vals)):
    if d >= MIN_JUMP_MS:
        clusters.append(vals[start:i+1])
        start = i + 1
clusters.append(vals[start:])

print(f"Detected {len(clusters)} clusters using raw sorted data and MIN_JUMP_MS={MIN_JUMP_MS}")
print()

for idx, c in enumerate(clusters, start=1):
    print(
        f"Cluster {idx:02d}: "
        f"n={len(c):2d}, "
        f"min={np.min(c):8.3f}, "
        f"max={np.max(c):8.3f}, "
        f"median={np.median(c):8.3f}, "
        f"mean={np.mean(c):8.3f}"
    )
print()

# 4) Estimate representative cluster centers and spacing
centers = np.array([np.median(c) for c in clusters if len(c) > 0])
if len(centers) > 1:
    center_diffs = np.diff(centers)
    print("Cluster center medians:")
    print(np.round(centers, 3))
    print()
    print("Differences between cluster centers:")
    print(np.round(center_diffs, 3))
    print()
    print("Cluster-center spacing statistics:")
    print(f"Mean:   {np.mean(center_diffs):.3f} ms")
    print(f"Median: {np.median(center_diffs):.3f} ms")
    print(f"Min:    {np.min(center_diffs):.3f} ms")
    print(f"Max:    {np.max(center_diffs):.3f} ms")
    print()
    print(
        "Interpretation: use this as a descriptive clustering aid, not as proof "
        "of strict fixed-period quantization."
    )
