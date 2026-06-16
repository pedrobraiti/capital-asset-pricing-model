"""Betting Against Beta -- the strategy implied by the flat Security Market Line.

If the SML is too flat, low-beta assets are underpriced (positive CAPM alpha)
and high-beta assets are overpriced (negative alpha). Frazzini & Pedersen (2014)
turn this into a tradeable, self-financing, ex-ante beta-neutral portfolio: lever
the low-beta leg up to a beta of one, delever the high-beta leg to a beta of one,
and go long the former / short the latter.

    r_BAB(t) = (r_L(t) - rf) / beta_L(t-1) - (r_H(t) - rf) / beta_H(t-1)

Betas are estimated on a trailing window (no lookahead). A positive CAPM alpha
on this portfolio is the direct, tradeable counterpart of Figure 2.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from capm.data import french as fr
from capm.stats import PerformanceMetrics, performance_metrics, time_series_regression

_BETA_WINDOW = 60
_BETA_MIN = 36


@dataclass
class BABResult:
    period: str
    returns: pd.Series  # monthly BAB return (decimal)
    equity_curve: pd.Series
    metrics: PerformanceMetrics
    capm_alpha_ann: float  # decimal annualized
    capm_alpha_t: float
    capm_beta: float
    long_leg_beta_avg: float
    short_leg_beta_avg: float


def _rolling_beta(leg_excess: pd.Series, market_excess: pd.Series) -> pd.Series:
    """Trailing-window beta of a leg vs the market, lagged one month (no lookahead)."""
    cov = leg_excess.rolling(_BETA_WINDOW, min_periods=_BETA_MIN).cov(market_excess)
    var = market_excess.rolling(_BETA_WINDOW, min_periods=_BETA_MIN).var()
    return (cov / var).shift(1)


def betting_against_beta(period: str) -> BABResult:
    fac = fr.factors()
    rf, mkt = fac["RF"], fac["Mkt-RF"]
    deciles = fr.portfolios_on_beta()

    low_leg = deciles[["D1", "D2", "D3", "D4", "D5"]].mean(axis=1)
    high_leg = deciles[["D6", "D7", "D8", "D9", "D10"]].mean(axis=1)
    low_excess = (low_leg - rf).dropna()
    high_excess = (high_leg - rf).dropna()

    beta_low = _rolling_beta(low_excess, mkt)
    beta_high = _rolling_beta(high_excess, mkt)

    bab = (low_excess / beta_low) - (high_excess / beta_high)
    bab = fr.slice_period(bab.dropna(), period)
    bab.name = "BAB"

    mkt_p = fr.slice_period(mkt, period)
    reg = time_series_regression(bab, mkt_p.to_frame("Mkt-RF"), annualize_alpha=False)

    return BABResult(
        period=period,
        returns=bab,
        equity_curve=(1.0 + bab).cumprod(),
        metrics=performance_metrics(bab),
        capm_alpha_ann=float(reg.coef("alpha") * 12),
        capm_alpha_t=float(reg.tstat("alpha")),
        capm_beta=float(reg.coef("Mkt-RF")),
        long_leg_beta_avg=float(beta_low.reindex(bab.index).mean()),
        short_leg_beta_avg=float(beta_high.reindex(bab.index).mean()),
    )
