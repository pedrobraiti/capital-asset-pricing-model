"""Gibbons, Ross and Shanken (1989) test of the joint hypothesis a_i = 0.

The CAPM (and any factor model) implies that the intercepts of the time-series
regressions of test-asset excess returns on the factors are all zero. The GRS
statistic is the exact small-sample F-test of that joint restriction; Fama &
French (2004) cite it as the way to test whether a market proxy is on the
minimum-variance frontier spanned by the test assets.

    GRS = (T - N - K) / N
          * alpha' Sigma^{-1} alpha / (1 + mu' Omega^{-1} mu)
        ~ F(N, T - N - K)

where N test assets, K factors, T periods; Sigma is the residual covariance
matrix; mu and Omega are the factor mean vector and covariance matrix (MLE,
i.e. divided by T).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class GRSResult:
    statistic: float
    p_value: float
    df1: int  # N
    df2: int  # T - N - K
    n_assets: int
    n_factors: int
    n_obs: int
    alphas: np.ndarray  # monthly intercepts (decimal)
    mean_abs_alpha_annual: float  # mean |alpha| annualized, decimal
    sharpe_factors: float  # ex-post Sharpe of the tangency of the factors

    @property
    def rejects_at_5pct(self) -> bool:
        return self.p_value < 0.05


def grs_test(excess_returns: pd.DataFrame, factors: pd.DataFrame) -> GRSResult:
    """Run the GRS test for ``N`` test assets against ``K`` factors (monthly).

    ``excess_returns`` is T x N (returns already net of the risk-free rate);
    ``factors`` is T x K (e.g. just Mkt-RF for the CAPM, or Mkt-RF/SMB/HML).
    """
    df = pd.concat([excess_returns, factors], axis=1).dropna()
    r = df[excess_returns.columns].to_numpy()
    f = df[factors.columns].to_numpy()
    t, n = r.shape
    k = f.shape[1]
    if t - n - k <= 0:
        raise ValueError(
            f"GRS needs T > N + K; got T={t}, N={n}, K={k}. "
            "Use fewer test assets or a longer sample."
        )

    x = np.column_stack([np.ones(t), f])
    beta = np.linalg.lstsq(x, r, rcond=None)[0]  # (K+1, N)
    resid = r - x @ beta
    alpha = beta[0]  # (N,)

    sigma = resid.T @ resid / t  # residual covariance (MLE)
    mu = f.mean(axis=0)
    omega = np.cov(f, rowvar=False, bias=True)  # /T
    omega = np.atleast_2d(omega)

    sigma_inv = np.linalg.inv(sigma)
    sharpe2_factors = float(mu @ np.linalg.inv(omega) @ mu)
    a_sigma_a = float(alpha @ sigma_inv @ alpha)

    statistic = (t - n - k) / n * a_sigma_a / (1.0 + sharpe2_factors)
    df1, df2 = n, t - n - k
    p_value = float(stats.f.sf(statistic, df1, df2))

    return GRSResult(
        statistic=statistic,
        p_value=p_value,
        df1=df1,
        df2=df2,
        n_assets=n,
        n_factors=k,
        n_obs=t,
        alphas=alpha,
        mean_abs_alpha_annual=float(np.mean(np.abs(alpha)) * 12),
        sharpe_factors=float(np.sqrt(max(sharpe2_factors, 0.0))),
    )
