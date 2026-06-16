"""Ordinary least squares with optional Newey-West (HAC) standard errors.

Asset returns are heteroskedastic and serially correlated, so the time-series
regressions used to estimate Jensen's alpha and factor loadings report
heteroskedasticity- and autocorrelation-consistent (HAC) standard errors by
default (Newey & West, 1987). This keeps the t-statistics on alpha honest.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats

MONTHS_PER_YEAR = 12


@dataclass(frozen=True)
class OLSResult:
    """Coefficients and inference for a single linear regression."""

    names: list[str]
    params: np.ndarray
    std_errors: np.ndarray
    tstats: np.ndarray
    pvalues: np.ndarray
    resid: np.ndarray
    r_squared: float
    adj_r_squared: float
    n_obs: int
    hac_lags: int | None

    def coef(self, name: str) -> float:
        return float(self.params[self.names.index(name)])

    def tstat(self, name: str) -> float:
        return float(self.tstats[self.names.index(name)])


def _newey_west_lags(n_obs: int) -> int:
    """Automatic Bartlett lag length L = floor(4 * (T/100)^(2/9))."""
    return int(np.floor(4.0 * (n_obs / 100.0) ** (2.0 / 9.0)))


def _hac_cov(x: np.ndarray, resid: np.ndarray, xtx_inv: np.ndarray, lags: int) -> np.ndarray:
    """Newey-West HAC sandwich covariance of the OLS coefficients."""
    n, k = x.shape
    scores = x * resid[:, None]  # (n, k)
    meat = scores.T @ scores  # lag 0
    for lag in range(1, lags + 1):
        weight = 1.0 - lag / (lags + 1.0)  # Bartlett kernel
        gamma = scores[lag:].T @ scores[:-lag]
        meat += weight * (gamma + gamma.T)
    return xtx_inv @ meat @ xtx_inv


def ols(y: np.ndarray, x: np.ndarray, *, hac_lags: int | None = "auto", names: list[str] | None = None) -> OLSResult:
    """Fit ``y = x @ params + e``. ``x`` must already include an intercept column.

    ``hac_lags="auto"`` uses the Newey-West rule; ``None`` gives classical
    homoskedastic standard errors; an int fixes the Bartlett lag length.
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    n, k = x.shape
    xtx_inv = np.linalg.inv(x.T @ x)
    params = xtx_inv @ x.T @ y
    resid = y - x @ params

    if hac_lags is None:
        sigma2 = resid @ resid / (n - k)
        cov = sigma2 * xtx_inv
        used_lags = None
    else:
        lags = _newey_west_lags(n) if hac_lags == "auto" else int(hac_lags)
        cov = _hac_cov(x, resid, xtx_inv, lags)
        used_lags = lags

    std_errors = np.sqrt(np.diag(cov))
    tstats = params / std_errors
    pvalues = 2.0 * stats.t.sf(np.abs(tstats), df=n - k)

    tss = np.sum((y - y.mean()) ** 2)
    rss = resid @ resid
    r2 = 1.0 - rss / tss
    adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / (n - k)

    if names is None:
        names = ["const"] + [f"x{i}" for i in range(1, k)]
    return OLSResult(names, params, std_errors, tstats, pvalues, resid, r2, adj_r2, n, used_lags)


def time_series_regression(
    excess_asset: pd.Series,
    factors: pd.DataFrame,
    *,
    hac_lags: int | None = "auto",
    annualize_alpha: bool = True,
) -> OLSResult:
    """Regress an asset's excess return on factor returns (intercept = alpha).

    Both inputs are aligned on their common dates. With monthly data and
    ``annualize_alpha=True`` the reported intercept and its standard error are
    scaled by 12 so alpha is expressed in annual percentage points; the
    t-statistic is unchanged by the rescaling.
    """
    df = pd.concat([excess_asset.rename("y"), factors], axis=1).dropna()
    y = df["y"].to_numpy()
    factor_names = list(factors.columns)
    x = np.column_stack([np.ones(len(df)), df[factor_names].to_numpy()])
    result = ols(y, x, hac_lags=hac_lags, names=["alpha", *factor_names])

    if annualize_alpha:
        params = result.params.copy()
        std_errors = result.std_errors.copy()
        params[0] *= MONTHS_PER_YEAR
        std_errors[0] *= MONTHS_PER_YEAR
        result = OLSResult(
            result.names, params, std_errors, result.tstats, result.pvalues,
            result.resid, result.r_squared, result.adj_r_squared, result.n_obs, result.hac_lags,
        )
    return result
