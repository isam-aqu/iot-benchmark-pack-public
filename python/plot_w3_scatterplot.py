import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from paper_plot_style import apply_paper_style, save_paper_figure


apply_paper_style()

df = pd.read_csv("analysis/w3/tables/w3_experiment_summary.csv")

colors = {"wifi": "#0072B2", "zigbee": "#009E73", "ble": "#D55E00"}
markers = {"baseline": "o", "light": "s", "moderate": "^", "heavy": "D"}

fig, ax = plt.subplots(figsize=(8, 6))

# ---- MAIN SCATTER ----
for _, row in df.iterrows():
    ax.scatter(
        row["p95"],
        row["mad"],
        color=colors[row["protocol"]],
        marker=markers[row["load"]],
        alpha=0.7,
        edgecolors="k",
        s=45,
        linewidths=0.8,
    )

ax.set_xlabel("P95 latency (ms)")
ax.set_ylabel("Median absolute deviation, MAD (ms)")
ax.set_title("W3 latency-variability map")

# ---- CLUSTER ANNOTATIONS ----
ax.annotate(
    "Wi-Fi\nlow latency,\nhigher variability\nunder heavy load",
    xy=(24, 3.4),
    xytext=(35, 12),
    arrowprops=dict(arrowstyle="->", linewidth=1.0),
    fontsize=9,
)

ax.annotate(
    "Zigbee\nlow latency,\nstable tail",
    xy=(10.5, 2.0),
    xytext=(30, 25),
    arrowprops=dict(arrowstyle="->", linewidth=1.0),
    fontsize=9,
)

ax.annotate(
    "BLE\nhigh spread,\nadvertisement/scanner\ndominated",
    xy=(170, 85),
    xytext=(165, 45),
    arrowprops=dict(arrowstyle="->", linewidth=1.0),
    fontsize=9,
)

# ---- ZOOM INSET ----
axins = inset_axes(ax, width="38%", height="34%", loc="lower right", borderpad=1.25)
axins.set_facecolor("white")
axins.patch.set_alpha(1.0)
axins.set_zorder(6)

for _, row in df[df["protocol"] != "ble"].iterrows():
    axins.scatter(
        row["p95"],
        row["mad"],
        color=colors[row["protocol"]],
        marker=markers[row["load"]],
        alpha=0.7,
        edgecolors="k",
        s=35,
        linewidths=0.8,
    )

axins.set_xlim(0, 40)
axins.set_ylim(0, 5)
axins.set_title("Wi-Fi/Zigbee zoom", fontsize=8, pad=2)
axins.tick_params(labelsize=7)
axins.grid(True, linestyle="--", alpha=0.3)

# ---- CLEAN LEGENDS: BOTH LEFT ----
protocol_legend = [
    Line2D([0], [0], marker="o", color="w", label="Wi-Fi",
           markerfacecolor=colors["wifi"], markeredgecolor="k", markersize=8),
    Line2D([0], [0], marker="o", color="w", label="Zigbee",
           markerfacecolor=colors["zigbee"], markeredgecolor="k", markersize=8),
    Line2D([0], [0], marker="o", color="w", label="BLE",
           markerfacecolor=colors["ble"], markeredgecolor="k", markersize=8),
]

load_legend = [
    Line2D([0], [0], marker="o", color="black", label="Baseline",
           linestyle="None", markersize=7),
    Line2D([0], [0], marker="s", color="black", label="Light",
           linestyle="None", markersize=7),
    Line2D([0], [0], marker="^", color="black", label="Moderate",
           linestyle="None", markersize=7),
    Line2D([0], [0], marker="D", color="black", label="Heavy",
           linestyle="None", markersize=7),
]

leg1 = ax.legend(
    handles=protocol_legend,
    title="Protocol",
    loc="upper left",
    bbox_to_anchor=(0.01, 0.99),
    frameon=True,
)

ax.add_artist(leg1)

ax.legend(
    handles=load_legend,
    title="Load Level",
    loc="upper left",
    bbox_to_anchor=(0.01, 0.72),
    frameon=True,
)

ax.grid(True, linestyle="--", alpha=0.3)

analysis_outputs = save_paper_figure(fig, Path("analysis/w3/figures/w3_scatter"))
paper_outputs = save_paper_figure(
    fig, Path("docs/paper_figures/fig09_w3_latency_variability_map")
)
plt.close(fig)

print("[OK] Saved analysis figure:")
for path in analysis_outputs.values():
    print(f"  {path}")
print("[OK] Saved paper figure:")
for path in paper_outputs.values():
    print(f"  {path}")
