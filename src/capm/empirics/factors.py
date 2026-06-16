"""Factor premiums: market, size (SMB), value (HML) and momentum (WML).

Reproduces the paper's headline numbers -- for 1927-2003 the market premium is
about 8.3% per year (3.5 standard errors from zero), SMB about 3.6% and HML
about 5.0% -- and extends them to the present, where the size and value
premiums have notably weakened. All premiums are annualized arithmetic means
in decimal form, with t-statistics and annualized Sharpe ratios.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from capm.data import french as fr


def _summary(series: pd.Series) -> dict:
    s = series.dropna()
    n = len(s)
    mean_m = s.mean()
    se_m = s.std(ddof=1) / np.sqrt(n)
    return {
        "mean_ann": float(mean_m * 12),
        "vol_ann": float(s.std(ddof=1) * np.sqrt(12)),
        "t_stat": float(mean_m / se_m),
        "sharpe_ann": float(mean_m / s.std(ddof=1) * np.sqrt(12)),
        "n_months": n,
    }


def factor_premia(period: str) -> pd.DataFrame:
    """Annualized premium, volatility, t-stat and Sharpe for each factor."""
    fac = fr.factors()
    mom = fr.momentum_factor()
    series = {
        "Mkt-RF": fr.slice_period(fac["Mkt-RF"], period),
        "SMB": fr.slice_period(fac["SMB"], period),
        "HML": fr.slice_period(fac["HML"], period),
        "WML (Mom)": fr.slice_period(mom, period),
    }
    return pd.DataFrame({name: _summary(s) for name, s in series.items()}).T


def factor_cumulative(period: str) -> pd.DataFrame:
    """Cumulative compounded growth of $1 in each long-short factor (for charts)."""
    fac = fr.factors()
    mom = fr.momentum_factor()
    df = pd.concat(
        [fac[["Mkt-RF", "SMB", "HML"]], mom.rename("WML (Mom)")], axis=1
    )
    df = fr.slice_period(df, period).dropna()
    return (1.0 + df).cumprod()
