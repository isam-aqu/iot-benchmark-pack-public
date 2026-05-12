from pathlib import Path

import matplotlib.pyplot as plt


PDF_METADATA = {
    "Creator": "iot-benchmark",
    "Producer": "Matplotlib",
    "CreationDate": None,
    "ModDate": None,
}

SVG_METADATA = {
    "Creator": "iot-benchmark",
    "Date": "2026-05-10T00:00:00",
}

PNG_METADATA = {
    "Software": "iot-benchmark",
}


def apply_paper_style() -> None:
    """Use a consistent, editable publication style for paper figures."""
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "legend.title_fontsize": 8,
            "figure.titlesize": 11,
            "axes.linewidth": 0.8,
            "grid.linewidth": 0.5,
            "lines.linewidth": 1.6,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "svg.hashsalt": "iot-benchmark",
            "savefig.dpi": 300,
        }
    )


def save_paper_figure(fig, base_path: Path, *, dpi: int = 300) -> dict[str, Path]:
    """Save PNG preview plus vector PDF/SVG versions using one filename stem."""
    base = Path(base_path)
    base.parent.mkdir(parents=True, exist_ok=True)
    outputs = {
        "png": base.with_suffix(".png"),
        "pdf": base.with_suffix(".pdf"),
        "svg": base.with_suffix(".svg"),
    }
    fig.savefig(outputs["png"], dpi=dpi, bbox_inches="tight", metadata=PNG_METADATA)
    fig.savefig(outputs["pdf"], bbox_inches="tight", metadata=PDF_METADATA)
    fig.savefig(outputs["svg"], bbox_inches="tight", metadata=SVG_METADATA)
    return outputs
