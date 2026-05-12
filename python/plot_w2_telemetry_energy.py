import csv
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/iotbench_mplconfig")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/iotbench_xdg_cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd

from paper_plot_style import apply_paper_style, save_paper_figure


apply_paper_style()

try:
    from scipy import stats
except ImportError:  # pragma: no cover
    stats = None


ROOT = Path(__file__).resolve().parents[1]
PRIMARY_DIR = ROOT / "analysis" / "w2" / "primary_fw05"
PRIMARY_CSV = PRIMARY_DIR / "tables" / "groups.csv"
PRIMARY_JSON = PRIMARY_DIR / "tables" / "groups.json"
RUN_SHEET = ROOT / "docs" / "run_sheet.csv"
OUTPUT_DIR = PRIMARY_DIR / "figures"
OUTPUT_STEM = "w2_energy_delta_power_fw05_primary"

LOW_RATE_GROUPS = ["W2_7s", "W2_8s", "W2_9s", "W2_10s"]


def t_critical(n: int) -> float:
    if n <= 1:
        return float("nan")
    if stats is None:
        return 1.96
    return float(stats.t.ppf(0.975, n - 1))


def paired_summary(values, label="paired deltas"):
    vals = [float(v) for v in values]
    n = len(vals)
    if n == 0:
        raise ValueError(f"No values available for {label}; cannot compute paired summary.")
    mean = sum(vals) / n
    if n <= 1:
        return {
            "n": n,
            "mean": mean,
            "lower": None,
            "upper": None,
            "p": None,
        }
    variance = sum((v - mean) ** 2 for v in vals) / (n - 1)
    sd = math.sqrt(variance)
    half = t_critical(n) * sd / math.sqrt(n)
    p_value = None
    if stats is not None:
        p_value = float(stats.ttest_1samp(vals, 0.0).pvalue)
    return {
        "n": n,
        "mean": mean,
        "lower": mean - half,
        "upper": mean + half,
        "p": p_value,
    }


def bh_adjust(p_values):
    indexed = [(idx, float(p)) for idx, p in enumerate(p_values)]
    ordered = sorted(indexed, key=lambda item: item[1])
    adjusted = [None] * len(indexed)
    running = 1.0
    m = len(indexed)
    for rank, (idx, p_value) in reversed(list(enumerate(ordered, start=1))):
        running = min(running, p_value * m / rank)
        adjusted[idx] = running
    return adjusted


def load_primary_rows():
    df = pd.read_csv(PRIMARY_CSV).sort_values("interval_s").reset_index(drop=True)
    q_values = bh_adjust(df["paired_t_p_delta_mean_power_mW_two_sided"])
    df["bh_q_delta_power"] = q_values
    df["is_formal_power"] = (
        (df["paired_ci95_delta_mean_power_mW_low"] > 0)
        & (df["bh_q_delta_power"] < 0.05)
    )
    df["delta_energy_norm_mJ"] = (
        df["paired_delta_mean_power_mW"] * df["interval_s"]
    )
    df["delta_energy_norm_low_mJ"] = (
        df["paired_ci95_delta_mean_power_mW_low"] * df["interval_s"]
    )
    df["delta_energy_norm_high_mJ"] = (
        df["paired_ci95_delta_mean_power_mW_high"] * df["interval_s"]
    )
    return df


def load_primary_pairs_by_group():
    with open(PRIMARY_JSON, "r") as f:
        groups = json.load(f)
    result = {}
    for group_name, group in groups.items():
        pairs = group["paired"]["pairs"]
        result[group_name] = [p["delta_mean_power_mW"] for p in pairs]
    return result


def load_run_sheet_rows():
    with open(RUN_SHEET, newline="") as f:
        return {row["run_id"]: row for row in csv.DictReader(f)}


def load_run_delta_inputs(run_id, rows):
    row = rows[run_id]
    run_path = ROOT / row["run_path"]
    with open(run_path / "analysis" / "summary.json", "r") as f:
        summary = json.load(f)
    with open(run_path / "analysis" / "metrics.json", "r") as f:
        metrics = json.load(f)
    return {
        "run_id": run_id,
        "comparison_group": row["comparison_group"],
        "run_type": row["run_type"],
        "replicate_id": row["replicate_id"],
        "mean_power_mW": summary["power"]["mean_power_mW"],
        "actual_events": metrics["reliability"]["actual_events"],
    }


def load_confirmation_pairs():
    rows = load_run_sheet_rows()
    records = []
    for run_id, row in rows.items():
        if row.get("plan_id") != "W2_EVENT_NORM_CONFIRM":
            continue
        if row.get("status") != "complete":
            continue
        if row.get("comparison_group") not in LOW_RATE_GROUPS:
            continue
        records.append(load_run_delta_inputs(run_id, rows))

    by_group = {group: {} for group in LOW_RATE_GROUPS}
    for record in records:
        group = record["comparison_group"]
        rep = record["replicate_id"]
        by_group.setdefault(group, {}).setdefault(rep, {})[record["run_type"]] = record

    pairs_by_group = {}
    event_ranges = {}
    for group in LOW_RATE_GROUPS:
        deltas = []
        event_counts = []
        for rep, members in sorted(by_group.get(group, {}).items()):
            if "control" not in members or "telemetry" not in members:
                continue
            control = members["control"]
            telemetry = members["telemetry"]
            deltas.append(telemetry["mean_power_mW"] - control["mean_power_mW"])
            event_counts.extend([control["actual_events"], telemetry["actual_events"]])
        pairs_by_group[group] = deltas
        if event_counts:
            event_ranges[group] = (min(event_counts), max(event_counts))
    return pairs_by_group, event_ranges


def interval_label(value):
    if float(value).is_integer():
        return str(int(value))
    return str(value)


def draw_primary_panel(ax, df):
    noise_floor = float(df["control_std_power_mW"].mean())
    ax.axhspan(
        -noise_floor,
        noise_floor,
        facecolor="0.96",
        edgecolor="0.78",
        hatch="///",
        linewidth=0.0,
        zorder=0,
        label="Mean control sigma",
    )
    ax.axhline(0, color="0.25", linestyle=":", linewidth=1.2, zorder=1)

    ax.plot(
        df["interval_s"],
        df["paired_delta_mean_power_mW"],
        color="0.35",
        linestyle="-",
        linewidth=1.1,
        zorder=2,
    )

    for _, row in df.iterrows():
        formal = bool(row["is_formal_power"])
        marker = "o" if formal else "s"
        face = "0.05" if formal else "white"
        edge = "0.05" if formal else "0.35"
        yerr = [
            [row["paired_delta_mean_power_mW"] - row["paired_ci95_delta_mean_power_mW_low"]],
            [row["paired_ci95_delta_mean_power_mW_high"] - row["paired_delta_mean_power_mW"]],
        ]
        ax.errorbar(
            row["interval_s"],
            row["paired_delta_mean_power_mW"],
            yerr=yerr,
            fmt=marker,
            markersize=6.5,
            markerfacecolor=face,
            markeredgecolor=edge,
            markeredgewidth=1.3,
            ecolor=edge,
            elinewidth=1.2,
            capsize=3.5,
            linestyle="None",
            zorder=3,
        )

    ax.set_title("(a) Primary fixed-duration runs", loc="left", fontsize=10)
    ax.set_ylabel(r"Paired $\Delta P$ (mW)")
    ax.set_xlabel("Reporting interval (s)")
    ax.set_xticks(df["interval_s"])
    ax.set_xticklabels([interval_label(v) for v in df["interval_s"]])
    ax.grid(True, axis="y", color="0.88", linewidth=0.8)
    ax.set_axisbelow(True)

    formal_handle = mlines.Line2D(
        [],
        [],
        color="0.05",
        marker="o",
        markerfacecolor="0.05",
        markeredgecolor="0.05",
        linestyle="None",
        label="Formal positive",
    )
    unresolved_handle = mlines.Line2D(
        [],
        [],
        color="0.35",
        marker="s",
        markerfacecolor="white",
        markeredgecolor="0.35",
        linestyle="None",
        label="Unresolved / below noise floor",
    )
    noise_handle = mpatches.Patch(
        facecolor="0.96",
        edgecolor="0.70",
        hatch="///",
        label="Mean control sigma band",
    )
    ax.legend(
        handles=[formal_handle, unresolved_handle, noise_handle],
        loc="lower right",
        frameon=True,
        fontsize=8.5,
    )


def draw_confirmation_panel(ax, primary_pairs, confirmation_pairs):
    offsets = {
        "Fixed-duration": -0.16,
        "Event-normalized": 0.0,
        "Combined": 0.16,
    }
    styles = {
        "Fixed-duration": {
            "marker": "o",
            "face": "white",
            "edge": "0.15",
            "linestyle": "--",
            "linewidth": 1.0,
        },
        "Event-normalized": {
            "marker": "^",
            "face": "white",
            "edge": "0.45",
            "linestyle": ":",
            "linewidth": 1.1,
        },
        "Combined": {
            "marker": "D",
            "face": "0.05",
            "edge": "0.05",
            "linestyle": "-",
            "linewidth": 1.4,
        },
    }

    x_values = [7, 8, 9, 10]
    summaries = {name: [] for name in offsets}
    for interval in x_values:
        group = f"W2_{interval}s"
        fixed_values = primary_pairs[group]
        confirmation_values = confirmation_pairs[group]
        combined_values = fixed_values + confirmation_values
        summaries["Fixed-duration"].append(
            (interval, paired_summary(fixed_values, f"{group} fixed-duration pairs"))
        )
        summaries["Event-normalized"].append(
            (interval, paired_summary(confirmation_values, f"{group} event-normalized pairs"))
        )
        summaries["Combined"].append(
            (interval, paired_summary(combined_values, f"{group} combined pairs"))
        )

    ax.axhline(0, color="0.25", linestyle=":", linewidth=1.2, zorder=1)

    for name, entries in summaries.items():
        style = styles[name]
        xs = [interval + offsets[name] for interval, _ in entries]
        ys = [summary["mean"] for _, summary in entries]
        ax.plot(
            xs,
            ys,
            color=style["edge"],
            linestyle=style["linestyle"],
            linewidth=style["linewidth"],
            zorder=2,
        )
        for x, (_, summary) in zip(xs, entries):
            lower = summary["lower"]
            upper = summary["upper"]
            yerr = None
            if lower is not None and upper is not None:
                yerr = [[summary["mean"] - lower], [upper - summary["mean"]]]
            ax.errorbar(
                x,
                summary["mean"],
                yerr=yerr,
                fmt=style["marker"],
                markersize=6.2,
                markerfacecolor=style["face"],
                markeredgecolor=style["edge"],
                markeredgewidth=1.3,
                ecolor=style["edge"],
                elinewidth=1.1,
                capsize=3.2,
                linestyle="None",
                zorder=3,
            )

    ax.set_title("(b) Low-rate event-normalized confirmation", loc="left", fontsize=10)
    ax.set_ylabel(r"Paired $\Delta P$ (mW)")
    ax.set_xlabel("Reporting interval (s)")
    ax.set_xticks(x_values)
    ax.set_xticklabels([str(v) for v in x_values])
    ax.grid(True, axis="y", color="0.88", linewidth=0.8)
    ax.set_axisbelow(True)

    fixed_handle = mlines.Line2D(
        [],
        [],
        color="0.15",
        marker="o",
        markerfacecolor="white",
        markeredgecolor="0.15",
        linestyle="--",
        label="Fixed-duration",
    )
    confirmation_handle = mlines.Line2D(
        [],
        [],
        color="0.45",
        marker="^",
        markerfacecolor="white",
        markeredgecolor="0.45",
        linestyle=":",
        label="Event-normalized",
    )
    combined_handle = mlines.Line2D(
        [],
        [],
        color="0.05",
        marker="D",
        markerfacecolor="0.05",
        markeredgecolor="0.05",
        linestyle="-",
        label="Combined",
    )
    ax.legend(
        handles=[fixed_handle, confirmation_handle, combined_handle],
        loc="lower right",
        frameon=True,
        fontsize=8.5,
    )


def build_figure():
    df = load_primary_rows()
    primary_pairs = load_primary_pairs_by_group()
    confirmation_pairs, event_ranges = load_confirmation_pairs()

    missing_primary = [group for group in LOW_RATE_GROUPS if not primary_pairs.get(group)]
    if missing_primary:
        raise RuntimeError(f"Missing primary fixed-duration pairs: {missing_primary}")

    missing_confirmation = [
        group for group in LOW_RATE_GROUPS if not confirmation_pairs.get(group)
    ]
    if missing_confirmation:
        raise RuntimeError(
            f"Missing event-normalized confirmation pairs: {missing_confirmation}"
        )

    fig, (ax_primary, ax_confirmation) = plt.subplots(
        2,
        1,
        figsize=(7.2, 7.0),
        constrained_layout=False,
    )

    draw_primary_panel(ax_primary, df)
    draw_confirmation_panel(ax_confirmation, primary_pairs, confirmation_pairs)

    fig.suptitle(
        "W2 Telemetry Energy Detectability and Low-Rate Validation",
        fontsize=12,
        y=0.985,
    )
    fig.tight_layout(rect=[0, 0.02, 1, 0.96], h_pad=1.7)

    analysis_outputs = save_paper_figure(fig, OUTPUT_DIR / OUTPUT_STEM)
    paper_outputs = save_paper_figure(
        fig, ROOT / "docs" / "paper_figures" / "fig08_w2_telemetry_energy_detectability"
    )
    png_out = analysis_outputs["png"]
    pdf_out = analysis_outputs["pdf"]
    svg_out = analysis_outputs["svg"]

    meta = {
        "plot_name": "W2 telemetry energy detectability and low-rate validation",
        "primary_csv": str(PRIMARY_CSV.relative_to(ROOT)),
        "primary_json": str(PRIMARY_JSON.relative_to(ROOT)),
        "run_sheet": str(RUN_SHEET.relative_to(ROOT)),
        "output_png": str(png_out.relative_to(ROOT)),
        "output_pdf": str(pdf_out.relative_to(ROOT)),
        "output_svg": str(svg_out.relative_to(ROOT)),
        "paper_output_png": str(paper_outputs["png"].relative_to(ROOT)),
        "paper_output_pdf": str(paper_outputs["pdf"].relative_to(ROOT)),
        "paper_output_svg": str(paper_outputs["svg"].relative_to(ROOT)),
        "low_rate_groups": LOW_RATE_GROUPS,
        "event_ranges": event_ranges,
        "encoding": (
            "Formal/unresolved classes use marker shape and marker fill; "
            "low-rate series use marker shape and line style; noise band uses hatching."
        ),
    }
    with open(png_out.with_suffix(".png.meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    print(f"[OK] Saved {png_out}")
    print(f"[OK] Saved {pdf_out}")
    print(f"[OK] Saved {svg_out}")
    print(f"[OK] Saved {paper_outputs['png']}")
    print(f"[OK] Saved {paper_outputs['pdf']}")
    print(f"[OK] Saved {paper_outputs['svg']}")
    print(f"[OK] Saved {png_out.with_suffix('.png.meta.json')}")


if __name__ == "__main__":
    build_figure()
