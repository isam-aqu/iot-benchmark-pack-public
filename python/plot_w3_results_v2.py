import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("analysis/w3/tables/w3_protocol_comparison.csv")

# Ensure order
order = ["Baseline", "Light", "Moderate", "Heavy"]
df["load"] = pd.Categorical(df["load"], categories=order, ordered=True)
df = df.sort_values(["protocol", "load"])

protocols = df["protocol"].unique()

# Create figure (3 panels)
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Panel A: P95 latency
for p in protocols:
    d = df[df["protocol"] == p]
    axes[0].plot(d["load"], d["p95_latency_ms"], marker='o', label=p)

axes[0].set_title("P95 Latency (ms)")
axes[0].set_ylabel("Latency (ms)")
axes[0].grid(True)

# Panel B: MAD (jitter)
for p in protocols:
    d = df[df["protocol"] == p]
    axes[1].plot(d["load"], d["mad_latency_ms"], marker='o', label=p)

axes[1].set_title("MAD (Jitter Robustness)")
axes[1].set_ylabel("MAD (ms)")
axes[1].grid(True)

# Panel C: Drop rate
for p in protocols:
    d = df[df["protocol"] == p]
    axes[2].plot(d["load"], d["drop_rate"] * 100, marker='o', label=p)

axes[2].set_title("Drop Rate (%)")
axes[2].set_ylabel("Drop Rate (%)")
axes[2].grid(True)

# Shared legend
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc='upper center', ncol=len(labels))

plt.tight_layout(rect=[0, 0, 1, 0.9])
plt.savefig("w3_protocol_comparison.png", dpi=300)
plt.savefig("w3_protocol_comparison.svg")
