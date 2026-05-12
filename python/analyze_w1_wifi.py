import os
import sys

import pandas as pd

from version_info import load_version_info
from path_utils import run_dir

VERSION_INFO = load_version_info()
PIPELINE_VERSION = VERSION_INFO.pipeline_version
SCRIPT_VERSION = VERSION_INFO.analysis_version

print(f"[INFO] Pipeline version: {PIPELINE_VERSION} | Analysis version: {SCRIPT_VERSION}")

DEFAULT_RUN_ID = "W1_wifi_near_quiet"
MAX_VALID_RTT_MS = 200.0

RUN_ID = sys.argv[1] if len(sys.argv) > 1 else os.getenv("RUN_ID", DEFAULT_RUN_ID)
EXP_RUN_ID = os.getenv("EXP_RUN_ID", "").strip() or (sys.argv[2] if len(sys.argv) > 2 else "")

if not EXP_RUN_ID:
    raise SystemExit("EXP_RUN_ID is required, e.g. EXP_RUN_ID=R102")

base = run_dir(EXP_RUN_ID)
raw_path = base / "raw" / f"{RUN_ID}_mqtt_events.csv"
derived_dir = base / "derived"
derived_dir.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(raw_path)

print(f"Loaded: {raw_path}")
print(f"Total rows: {len(df)}")
print()

print("Rows by type:")
print(df["type"].value_counts(dropna=False))
print()

wifi_df = df[df["protocol"] == "wifi"].copy()
event_df = wifi_df[wifi_df["type"] == "event"].copy()
rtt_df = wifi_df[wifi_df["type"] == "rtt"].copy()

print(f"Wi-Fi event rows: {len(event_df)}")
print(f"Wi-Fi RTT rows:   {len(rtt_df)}")
print()

for col in ["seq", "t_local_us", "wifi_rssi", "rtt_us", "pi_rx_time_ns"]:
    if col in wifi_df.columns:
        wifi_df[col] = pd.to_numeric(wifi_df[col], errors="coerce")
for col in ["seq", "t_local_us", "wifi_rssi", "pi_rx_time_ns"]:
    if col in event_df.columns:
        event_df[col] = pd.to_numeric(event_df[col], errors="coerce")
for col in ["seq", "rtt_us", "pi_rx_time_ns"]:
    if col in rtt_df.columns:
        rtt_df[col] = pd.to_numeric(rtt_df[col], errors="coerce")

event_seqs = set(event_df["seq"].dropna().astype(int))
rtt_seqs = set(rtt_df["seq"].dropna().astype(int))

print(f"Unique event seq count: {len(event_seqs)}")
print(f"Unique RTT seq count:   {len(rtt_seqs)}")
print(f"Missing RTT seqs:       {sorted(event_seqs - rtt_seqs)}")
print(f"Extra RTT seqs:         {sorted(rtt_seqs - event_seqs)}")
print()

event_dup = event_df["seq"].value_counts()
rtt_dup = rtt_df["seq"].value_counts()

print("Duplicate event seqs:")
print(event_dup[event_dup > 1] if not event_dup[event_dup > 1].empty else "None")
print()

print("Duplicate RTT seqs:")
print(rtt_dup[rtt_dup > 1] if not rtt_dup[rtt_dup > 1].empty else "None")
print()

rtt_df["rtt_ms"] = pd.to_numeric(rtt_df["rtt_us"], errors="coerce") / 1000.0

df_full = rtt_df.dropna(subset=["rtt_ms"]).copy()
df_core = df_full[(df_full["rtt_ms"] >= 0) & (df_full["rtt_ms"] <= MAX_VALID_RTT_MS)].copy()

print("--- DATASET SUMMARY ---")
print(f"Full samples:      {len(df_full)}")
print(f"Core samples:      {len(df_core)}")
print(f"Filtered outliers: {len(df_full) - len(df_core)}")
print()

def print_stats(label: str, data: pd.DataFrame):
    s = data["rtt_ms"].dropna()
    print(f"[{label}] RTT statistics (ms):")
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

rssi_series = event_df["wifi_rssi"].dropna()
if not rssi_series.empty:
    print("Wi-Fi RSSI statistics (dBm):")
    print(f"Mean:   {rssi_series.mean():.2f}")
    print(f"Median: {rssi_series.median():.2f}")
    print(f"Min:    {rssi_series.min():.2f}")
    print(f"Max:    {rssi_series.max():.2f}")
    print()

event_df["pipeline_version"] = PIPELINE_VERSION
df_full["pipeline_version"] = PIPELINE_VERSION
df_core["pipeline_version"] = PIPELINE_VERSION

event_df.to_csv(derived_dir / f"{RUN_ID}_events_only.csv", index=False)
df_full.to_csv(derived_dir / f"{RUN_ID}_wifi_rtt_full.csv", index=False)
df_core.to_csv(derived_dir / f"{RUN_ID}_wifi_rtt_core.csv", index=False)

print(f"Saved processed files to: {derived_dir}")
