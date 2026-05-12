from pathlib import Path
import os
import sys

import pandas as pd

from version_info import load_version_info
from path_utils import run_dir

VERSION_INFO = load_version_info()
PIPELINE_VERSION = VERSION_INFO.pipeline_version
SCRIPT_VERSION = VERSION_INFO.analysis_version

print(f"[INFO] Pipeline version: {PIPELINE_VERSION} | Analysis version: {SCRIPT_VERSION}")

DEFAULT_RUN_ID = "W1_ble_near_quiet"
MAX_VALID_DELAY_MS = 200.0

RUN_ID = sys.argv[1] if len(sys.argv) > 1 else os.getenv("RUN_ID", DEFAULT_RUN_ID)
EXP_RUN_ID = os.getenv("EXP_RUN_ID", "").strip() or (sys.argv[2] if len(sys.argv) > 2 else "")

if not EXP_RUN_ID:
    raise SystemExit("EXP_RUN_ID is required, e.g. EXP_RUN_ID=R301")

base = run_dir(EXP_RUN_ID)
raw_path = base / "raw" / f"{RUN_ID}_ble_events.csv"
derived_dir = base / "derived"
derived_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(raw_path)

df["pi_time_us"] = pd.to_numeric(df["pi_rx_time_ns"], errors="coerce") / 1000.0
df["t_local_us"] = pd.to_numeric(df["t_local_us"], errors="coerce")

df["raw_delay_ms"] = (df["pi_time_us"] - df["t_local_us"]) / 1000.0
median_offset = df["raw_delay_ms"].median()
df["norm_delay_ms"] = df["raw_delay_ms"] - median_offset

df_full = df.copy()
df_core = df[(df["norm_delay_ms"] >= -MAX_VALID_DELAY_MS) & (df["norm_delay_ms"] <= MAX_VALID_DELAY_MS)].copy()

print("=== BLE DATASET SUMMARY ===")
print("Median offset removed (ms):", median_offset)
print(f"Full samples:      {len(df_full)}")
print(f"Core samples:      {len(df_core)}")
print(f"Filtered outliers: {len(df_full) - len(df_core)}")
print()

def print_stats(label: str, data: pd.DataFrame):
    s = data["norm_delay_ms"].dropna()
    print(f"[{label}] BLE normalized delay statistics (ms):")
    print(f"Count:   {len(s)}")
    print(f"Mean:    {s.mean():.3f}")
    print(f"Median:  {s.median():.3f}")
    print(f"Min:     {s.min():.3f}")
    print(f"Max:     {s.max():.3f}")
    print(f"Std:     {s.std():.3f}")
    print(f"P95:     {s.quantile(0.95):.3f}")
    print()

print_stats("FULL", df_full)
print_stats("CORE (filtered)", df_core)

print("RSSI mean:", df["rssi"].mean())

df_full["pipeline_version"] = PIPELINE_VERSION
df_core["pipeline_version"] = PIPELINE_VERSION

df_full.to_csv(derived_dir / f"{RUN_ID}_ble_events_processed_full.csv", index=False)
df_core.to_csv(derived_dir / f"{RUN_ID}_ble_events_processed.csv", index=False)

print(f"Saved processed files to: {derived_dir}")