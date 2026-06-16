"""Shared helpers for the empirical studies.

Conventions used everywhere:
    * returns are monthly simple returns in **decimal** form;
    * "excess" means net of the risk-free rate ``RF``;
    * alphas/means tagged ``_ann`` are annualized (x12) and still in decimal.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from capm.stats import time_series_regression


def excess(portfolios: pd.DataFrame, rf: pd.Series) -> pd.DataFrame:
    """Subtract the risk-free rate from every portfolio return column."""
    return portfolios.sub(rf.reindex(portfolios.index), axis=0)


def capm_stats(
    portfolios: pd.DataFrame, market_excess: pd.Series, rf: pd.Series, *, hac_lags="auto"
) -> pd.DataFrame:
    """Per-portfolio CAPM statistics: beta, alpha and average excess return.

    Returns one row per portfolio with mean excess return, market beta, CAPM
    alpha (monthly and annualized, decimal) and the alpha t-statistic. Also
    includes the CAPM-predicted average excess return ``beta * E[Mkt-RF]`` so
    the realized-vs-predicted gap can be charted directly.
    """
    exc = excess(portfolios, rf)
    market = market_excess.rename("Mkt-RF").to_frame()
    mkt_mean = float(market_excess.reindex(exc.index).mean())

    rows = {}
    for name in portfolios.columns:
        reg = time_series_regression(exc[name], market, hac_lags=hac_lags, annualize_alpha=False)
        beta = reg.coef("Mkt-RF")
        rows[name] = {
            "mean_excess": float(exc[name].mean()),
            "mean_excess_ann": float(exc[name].mean() * 12),
            "beta": beta,
            "alpha": reg.coef("alpha"),
            "alpha_ann": reg.coef("alpha") * 12,
            "t_alpha": reg.tstat("alpha"),
            "predicted_excess": float(beta * mkt_mean),
            "predicted_excess_ann": float(beta * mkt_mean * 12),
            "r_squared": reg.r_squared,
            "n_obs": reg.n_obs,
        }
    return pd.DataFrame(rows).T


def multifactor_alpha(
    portfolios: pd.DataFrame, factors: pd.DataFrame, rf: pd.Series, *, hac_lags="auto"
) -> pd.DataFrame:
    """Per-portfolio multifactor alpha and loadings for an arbitrary factor set."""
    exc = excess(portfolios, rf)
    rows = {}
    for name in portfolios.columns:
        reg = time_series_regression(exc[name], factors, hac_lags=hac_lags, annualize_alpha=False)
        row = {"alpha": reg.coef("alpha"), "alpha_ann": reg.coef("alpha") * 12, "t_alpha": reg.tstat("alpha")}
        for fac in factors.columns:
            row[f"b_{fac}"] = reg.coef(fac)
        row["r_squared"] = reg.r_squared
        rows[name] = row
    return pd.DataFrame(rows).T


def fit_line(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Simple OLS fit returning (intercept, slope)."""
    coef = np.polyfit(np.asarray(x, float), np.asarray(y, float), 1)
    return float(coef[1]), float(coef[0])
