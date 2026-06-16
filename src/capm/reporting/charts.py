"""Generate every figure used in the study and the README.

Each function writes one PNG into the figures directory. ``generate_all_figures``
runs them all. Charts read straight from the empirical modules, so they always
reflect the current data and code.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from capm.data import french as fr
from capm.empirics import (
    betting_against_beta,
    factor_premia,
    grs_panel,
    momentum_study,
    security_market_line,
    sorted_decile_study,
)
from capm.empirics._common import fit_line
from capm.empirics.factors import factor_cumulative
from capm.reporting.style import COLORS, apply_style

PERIOD_LABELS = {
    "full": "Full sample",
    "paper_1927_2003": "Paper window 1927-2003",
    "paper_1963_2003": "Paper window 1963-2003",
    "modern_2004_now": "Out-of-sample 2004-present",
}


def _save(fig: plt.Figure, figdir: Path, name: str) -> Path:
    path = figdir / name
    fig.savefig(path)
    plt.close(fig)
    return path


# --------------------------------------------------------------------------- #
# 1. Conceptual efficient frontier + capital market line (paper Figure 1)
# --------------------------------------------------------------------------- #
def fig_efficient_frontier(figdir: Path) -> Path:
    rets = fr.industry_portfolios(17).dropna()
    rf = fr.factors()["RF"].reindex(rets.index).mean() * 12
    mu = rets.mean().to_numpy() * 12
    cov = rets.cov().to_numpy() * 12
    inv = np.linalg.inv(cov)
    ones = np.ones(len(mu))

    a = ones @ inv @ ones
    b = ones @ inv @ mu
    c = mu @ inv @ mu
    targets = np.linspace(mu.min() * 0.6, mu.max() * 1.05, 120)
    variances = (a * targets**2 - 2 * b * targets + c) / (a * c - b**2)
    sigmas = np.sqrt(np.clip(variances, 0, None))

    w_tan = inv @ (mu - rf * ones)
    w_tan /= ones @ w_tan
    ret_tan = float(mu @ w_tan)
    sig_tan = float(np.sqrt(w_tan @ cov @ w_tan))

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.plot(sigmas * 100, targets * 100, color=COLORS["navy"], lw=2, label="Minimum-variance frontier")
    ax.scatter(np.sqrt(np.diag(cov)) * 100, mu * 100, s=22, color=COLORS["grey"], alpha=0.8, label="17 industry portfolios", zorder=3)
    cml_x = np.array([0, sig_tan * 1.7])
    ax.plot(cml_x * 100, (rf + (ret_tan - rf) / sig_tan * cml_x) * 100, color=COLORS["orange"], lw=2, ls="--", label="Capital market line")
    ax.scatter([sig_tan * 100], [ret_tan * 100], marker="*", s=260, color=COLORS["red"], zorder=5, label="Tangency portfolio T")
    ax.scatter([0], [rf * 100], marker="o", s=60, color=COLORS["teal"], zorder=5, label="Risk-free rate $R_f$")
    ax.set_xlabel("Annualized standard deviation (%)")
    ax.set_ylabel("Annualized return (%)")
    ax.set_title("Investment opportunities: efficient frontier and the CAPM tangency portfolio")
    ax.set_xlim(left=0)
    ax.legend(loc="lower right")
    fig.text(0.01, -0.02, "Built from 17 value-weighted industry portfolios, full sample. Mirrors Figure 1 of Fama & French (2004).", fontsize=8, color=COLORS["grey"])
    return _save(fig, figdir, "01_efficient_frontier.png")


# --------------------------------------------------------------------------- #
# 2/3/4. Security market line scatter (realized vs CAPM-predicted)
# --------------------------------------------------------------------------- #
def _sml_panel(ax, table: pd.DataFrame, mkt_mean_ann: float, title: str, *, point_color: str) -> None:
    beta = table["beta"].to_numpy()
    ret = table["mean_excess_ann"].to_numpy() * 100
    grid = np.linspace(min(beta.min(), 0.0), beta.max() * 1.05, 50)

    ax.plot(grid, grid * mkt_mean_ann * 100, color=COLORS["grey"], lw=1.8, ls="--", label="CAPM prediction")
    inter, slope = fit_line(beta, table["mean_excess"].to_numpy())
    ax.plot(grid, (inter + slope * grid) * 12 * 100, color=COLORS["red"], lw=2, label="Realized fit (too flat)")
    ax.scatter(beta, ret, s=60, color=point_color, zorder=4, edgecolor="white", linewidth=0.6)
    for i, (bx, ry) in enumerate(zip(beta, ret), start=1):
        ax.annotate(str(i), (bx, ry), fontsize=7, color="#333", xytext=(3, 3), textcoords="offset points")
    ax.set_xlabel(r"Market beta $\beta$")
    ax.set_ylabel("Avg. annualized excess return (%)")
    ax.set_title(title)
    ax.legend(loc="upper left")


def fig_flat_sml(figdir: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    for ax, period in zip(axes, ["paper_1963_2003", "modern_2004_now"]):
        s = security_market_line(period)
        _sml_panel(ax, s.table, s.capm_slope_ann, f"Beta-sorted deciles - {PERIOD_LABELS[period]}", point_color=COLORS["navy"])
    fig.suptitle("The flat Security Market Line (replicating Fama & French 2004, Figure 2)", fontsize=14, fontweight="bold", color=COLORS["navy"])
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save(fig, figdir, "02_flat_sml.png")


def fig_value_size_sml(figdir: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2))
    v = sorted_decile_study("beme", "paper_1963_2003")
    z = sorted_decile_study("me", "paper_1963_2003", long_minus_short=False)
    mkt_mean = fr.slice_period(fr.factors()["Mkt-RF"], "paper_1963_2003").mean() * 12
    _sml_panel(axes[0], v.table, mkt_mean, "Book-to-market deciles (1=growth -> 10=value)", point_color=COLORS["teal"])
    _sml_panel(axes[1], z.table, mkt_mean, "Size deciles (1=small -> 10=big)", point_color=COLORS["orange"])
    fig.suptitle("Value and size: high average returns unrelated to beta (Figure 3 of the paper)", fontsize=14, fontweight="bold", color=COLORS["navy"])
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    return _save(fig, figdir, "03_value_size_sml.png")


# --------------------------------------------------------------------------- #
# 5. CAPM alphas by decile
# --------------------------------------------------------------------------- #
def fig_capm_alphas(figdir: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.0))
    specs = [("beta", "Beta-sorted deciles", COLORS["navy"]), ("beme", "Book-to-market deciles", COLORS["teal"])]
    for ax, (kind, title, color) in zip(axes, specs):
        s = sorted_decile_study(kind, "paper_1963_2003", long_minus_short=(kind != "me"))
        alpha = s.table["alpha_ann"] * 100
        t = s.table["t_alpha"]
        colors = [COLORS["green"] if a >= 0 else COLORS["red"] for a in alpha]
        bars = ax.bar(range(1, 11), alpha, color=colors, alpha=0.85)
        for rect, tv in zip(bars, t):
            ax.annotate(f"{tv:.1f}", (rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        ha="center", va="bottom" if rect.get_height() >= 0 else "top", fontsize=7, color="#555")
        ax.axhline(0, color=COLORS["grey"], lw=1)
        ax.set_xticks(range(1, 11))
        ax.set_xlabel("Decile (low -> high)")
        ax.set_ylabel("CAPM alpha (% / year)")
        ax.set_title(title)
    fig.suptitle("CAPM alphas: positive where beta is low, negative where beta is high (t-stats labelled)", fontsize=13, fontweight="bold", color=COLORS["navy"])
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return _save(fig, figdir, "04_capm_alphas.png")


# --------------------------------------------------------------------------- #
# 6/11. Factor premiums: paper window vs out-of-sample
# --------------------------------------------------------------------------- #
def fig_factor_premia(figdir: Path) -> Path:
    paper = factor_premia("paper_1927_2003")
    modern = factor_premia("modern_2004_now")
    names = list(paper.index)
    x = np.arange(len(names))
    w = 0.38

    fig, ax = plt.subplots(figsize=(9.5, 5.4))
    b1 = ax.bar(x - w / 2, paper["mean_ann"] * 100, w, color=COLORS["navy"], label="1927-2003 (paper)")
    b2 = ax.bar(x + w / 2, modern["mean_ann"] * 100, w, color=COLORS["orange"], label="2004-present (out-of-sample)")
    for bars, tbl in [(b1, paper), (b2, modern)]:
        for rect, tv in zip(bars, tbl["t_stat"]):
            ax.annotate(f"t={tv:.1f}", (rect.get_x() + rect.get_width() / 2, rect.get_height()),
                        ha="center", va="bottom" if rect.get_height() >= 0 else "top", fontsize=8, color="#555")
    ax.axhline(0, color=COLORS["grey"], lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.set_ylabel("Annualized premium (%)")
    ax.set_title("Factor premiums then and now: size and value have faded since the paper")
    ax.legend()
    return _save(fig, figdir, "05_factor_premia.png")


# --------------------------------------------------------------------------- #
# 7. Cumulative factor growth
# --------------------------------------------------------------------------- #
def fig_factor_cumulative(figdir: Path) -> Path:
    cum = factor_cumulative("full")
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for col, color in zip(cum.columns, [COLORS["navy"], COLORS["teal"], COLORS["orange"], COLORS["purple"]]):
        ax.plot(cum.index, cum[col], label=col, color=color, lw=1.6)
    ax.set_yscale("log")
    ax.set_ylabel("Growth of $1 (log scale)")
    ax.set_xlabel("")
    ax.axhline(1, color=COLORS["grey"], lw=0.8)
    ax.set_title("Cumulative growth of the long-short factor portfolios (full sample)")
    ax.legend(loc="upper left")
    return _save(fig, figdir, "06_factor_cumulative.png")


# --------------------------------------------------------------------------- #
# 8. GRS p-value heatmap
# --------------------------------------------------------------------------- #
def fig_grs_heatmap(figdir: Path) -> Path:
    panel = grs_panel("paper_1963_2003")
    pivot = panel.pivot(index="test_assets", columns="model", values="p_value")
    pivot = pivot[["CAPM", "FF3", "Carhart4"]]

    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    data = pivot.to_numpy()
    im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=0.10, aspect="auto")
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            val = data[i, j]
            txt = "n/a" if np.isnan(val) else f"{val:.3f}"
            ax.text(j, i, txt, ha="center", va="center", fontsize=9, color="black")
    ax.set_title("GRS test p-values (1963-2003): green = model not rejected, red = rejected")
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("GRS p-value (0.05 threshold)")
    fig.text(0.01, -0.02, "Joint test that all intercepts are zero. CAPM is rejected almost everywhere; FF3 rescues size/value; momentum needs the 4th factor.", fontsize=8, color=COLORS["grey"])
    return _save(fig, figdir, "07_grs_heatmap.png")


# --------------------------------------------------------------------------- #
# 9. Momentum alphas across models
# --------------------------------------------------------------------------- #
def fig_momentum_alphas(figdir: Path) -> Path:
    m = momentum_study("paper_1963_2003")
    x = np.arange(1, 11)
    w = 0.27
    fig, ax = plt.subplots(figsize=(10, 5.4))
    ax.bar(x - w, m.capm_alpha * 100, w, color=COLORS["red"], label="CAPM alpha")
    ax.bar(x, m.ff3_alpha * 100, w, color=COLORS["orange"], label="FF3 alpha")
    ax.bar(x + w, m.carhart_alpha * 100, w, color=COLORS["green"], label="Carhart 4-factor alpha")
    ax.axhline(0, color=COLORS["grey"], lw=1)
    ax.set_xticks(x)
    ax.set_xlabel("Momentum decile (1 = losers -> 10 = winners)")
    ax.set_ylabel("Alpha (% / year)")
    ax.set_title("Momentum breaks the CAPM and the three-factor model; the 4th factor absorbs it")
    ax.legend()
    return _save(fig, figdir, "08_momentum_alphas.png")


# --------------------------------------------------------------------------- #
# 10. Betting-Against-Beta equity curve and drawdown
# --------------------------------------------------------------------------- #
def fig_bab(figdir: Path) -> Path:
    b = betting_against_beta("full")
    curve = b.equity_curve
    drawdown = curve / curve.cummax() - 1.0

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.6), sharex=True, gridspec_kw={"height_ratios": [3, 1]})
    ax1.plot(curve.index, curve, color=COLORS["navy"], lw=1.6)
    ax1.set_yscale("log")
    ax1.set_ylabel("Growth of $1 (log)")
    ax1.set_title(f"Betting Against Beta: CAPM alpha {b.capm_alpha_ann*100:.1f}%/yr (t={b.capm_alpha_t:.1f}), beta {b.capm_beta:.2f}, Sharpe {b.metrics.sharpe:.2f}")
    ax2.fill_between(drawdown.index, drawdown * 100, 0, color=COLORS["red"], alpha=0.5)
    ax2.set_ylabel("Drawdown (%)")
    ax2.set_xlabel("")
    fig.tight_layout()
    return _save(fig, figdir, "09_bab_equity.png")


# --------------------------------------------------------------------------- #
# 12. Rolling 10-year factor premiums
# --------------------------------------------------------------------------- #
def fig_rolling_premia(figdir: Path) -> Path:
    fac = fr.factors()
    roll = (fac[["Mkt-RF", "SMB", "HML"]].rolling(120, min_periods=120).mean() * 12 * 100).dropna()
    fig, ax = plt.subplots(figsize=(10, 5.4))
    for col, color in zip(["Mkt-RF", "SMB", "HML"], [COLORS["navy"], COLORS["teal"], COLORS["orange"]]):
        ax.plot(roll.index, roll[col], label=col, color=color, lw=1.6)
    ax.axhline(0, color=COLORS["grey"], lw=1)
    ax.axvline(pd.Timestamp("2004-01-01"), color=COLORS["red"], lw=1, ls=":", label="Paper published (2004)")
    ax.set_ylabel("Trailing 10-year premium (% / year)")
    ax.set_title("Rolling 10-year factor premiums: the value and size premiums decay after 2004")
    ax.legend(loc="upper right", ncol=2)
    return _save(fig, figdir, "10_rolling_premia.png")


_FIGURES = [
    fig_efficient_frontier,
    fig_flat_sml,
    fig_value_size_sml,
    fig_capm_alphas,
    fig_factor_premia,
    fig_factor_cumulative,
    fig_grs_heatmap,
    fig_momentum_alphas,
    fig_bab,
    fig_rolling_premia,
]


def generate_all_figures(figdir: Path) -> list[Path]:
    """Generate every figure into ``figdir`` and return the written paths."""
    apply_style()
    figdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for func in _FIGURES:
        paths.append(func(figdir))
    return paths
