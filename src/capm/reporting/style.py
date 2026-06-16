"""Shared matplotlib styling for a consistent, professional look."""

from __future__ import annotations

import matplotlib as mpl

COLORS = {
    "navy": "#1f3b5c",
    "blue": "#2c6fbb",
    "teal": "#2a9d8f",
    "orange": "#e08a1e",
    "red": "#c0392b",
    "green": "#2e8b57",
    "purple": "#7d5ba6",
    "grey": "#8a8f98",
    "light": "#e9edf2",
}

# Ordered palette for categorical series.
PALETTE = [COLORS["navy"], COLORS["orange"], COLORS["teal"], COLORS["red"],
           COLORS["purple"], COLORS["green"], COLORS["blue"], COLORS["grey"]]


def apply_style() -> None:
    """Apply the project-wide matplotlib rcParams (call once before plotting)."""
    mpl.use("Agg")
    mpl.rcParams.update({
        "figure.dpi": 120,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": COLORS["grey"],
        "axes.grid": True,
        "axes.axisbelow": True,
        "grid.color": COLORS["light"],
        "grid.linewidth": 0.8,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.titlecolor": COLORS["navy"],
        "font.size": 10,
        "legend.frameon": False,
        "legend.fontsize": 9,
        "xtick.color": "#444",
        "ytick.color": "#444",
        "axes.prop_cycle": mpl.cycler(color=PALETTE),
    })
