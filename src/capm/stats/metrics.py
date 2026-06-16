"""Performance metrics for monthly return streams.

Used to describe the tradeable factor and Betting-Against-Beta portfolios with
the same vocabulary as a trading backtest: annualized return and volatility,
Sharpe and Sortino ratios, maximum drawdown and Calmar ratio.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class PerformanceMetrics:
    n_months: int
    ann_return: float  # geometric, decimal
    ann_arith_return: float  # arithmetic mean * 12, decimal
    ann_vol: float
    sharpe: float
    sortino: float
    max_drawdown: float  # negative decimal
    calmar: float
    hit_rate: float  # fraction of positive months
    skew: float
    worst_month: float
    best_month: float


def equity_curve(returns: pd.Series, initial: float = 1.0) -> pd.Series:
    """Compound a monthly return series into a growth-of-1 equity curve."""
    return initial * (1.0 + returns.fillna(0.0)).cumprod()


def max_drawdown(returns: pd.Series) -> float:
    curve = equity_curve(returns)
    running_peak = curve.cummax()
    drawdown = curve / running_peak - 1.0
    return float(drawdown.min())


def performance_metrics(returns: pd.Series, *, risk_free: pd.Series | None = None) -> PerformanceMetrics:
    """Compute annualized performance statistics from monthly simple returns.

    If ``risk_free`` is provided, Sharpe/Sortino use excess returns; otherwise
    the input is assumed to already be an excess (e.g. long-short) return.
    """
    r = returns.dropna()
    n = len(r)
    excess = r - risk_free.reindex(r.index).fillna(0.0) if risk_free is not None else r

    ann_arith = float(r.mean() * MONTHS_PER_YEAR)
    growth = float((1.0 + r).prod())
    ann_geom = growth ** (MONTHS_PER_YEAR / n) - 1.0 if n > 0 and growth > 0 else float("nan")
    ann_vol = float(r.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR))

    sharpe = float(excess.mean() / excess.std(ddof=1) * np.sqrt(MONTHS_PER_YEAR)) if excess.std(ddof=1) > 0 else float("nan")
    downside = excess[excess < 0]
    downside_dev = float(downside.std(ddof=1)) if len(downside) > 1 else float("nan")
    sortino = float(excess.mean() * MONTHS_PER_YEAR / (downside_dev * np.sqrt(MONTHS_PER_YEAR))) if downside_dev and downside_dev > 0 else float("nan")

    mdd = max_drawdown(r)
    calmar = float(ann_geom / abs(mdd)) if mdd < 0 else float("nan")

    return PerformanceMetrics(
        n_months=n,
        ann_return=ann_geom,
        ann_arith_return=ann_arith,
        ann_vol=ann_vol,
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown=mdd,
        calmar=calmar,
        hit_rate=float((r > 0).mean()),
        skew=float(r.skew()),
        worst_month=float(r.min()),
        best_month=float(r.max()),
    )
