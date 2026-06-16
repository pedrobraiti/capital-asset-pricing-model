"""Fama & MacBeth (1973) two-pass cross-sectional regression.

The CAPM predicts that, across assets, average excess returns line up with
market betas: the cross-sectional slope on beta should equal the average excess
market return and the intercept should be zero (excess-return form). Fama &
MacBeth estimate this with month-by-month cross-sectional regressions and base
inference on the time-series of the monthly slopes, which sidesteps the
residual-correlation problem the paper describes.

First pass : estimate each asset's beta from a full-sample time-series
             regression of its excess return on the factor(s).
Second pass: for every month, regress the cross-section of excess returns on
             those betas; average the monthly coefficients and form t-statistics
             from their time-series standard deviation.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FamaMacBethResult:
    factor_names: list[str]
    betas: pd.DataFrame  # asset x factor
    gamma_mean: pd.Series  # average monthly premium per regressor (incl. intercept)
    gamma_tstat: pd.Series
    gamma_mean_annual: pd.Series  # premiums annualized (x12), in percent
    n_obs: int
    n_assets: int


def fama_macbeth(excess_returns: pd.DataFrame, factors: pd.DataFrame) -> FamaMacBethResult:
    """Two-pass cross-section regression on ``factors`` (usually just Mkt-RF).

    ``excess_returns`` is T x N; ``factors`` is T x K. The reported intercept is
    labelled ``const`` and the betas are estimated full-sample (a standard choice
    for portfolio test assets, whose betas are stable).
    """
    df = pd.concat([excess_returns, factors], axis=1).dropna()
    r = df[excess_returns.columns]
    f = df[factors.columns]
    t = len(df)
    factor_names = list(f.columns)

    # First pass: full-sample betas per asset.
    x_ts = np.column_stack([np.ones(t), f.to_numpy()])
    betas = {}
    for asset in r.columns:
        coef = np.linalg.lstsq(x_ts, r[asset].to_numpy(), rcond=None)[0]
        betas[asset] = coef[1:]
    beta_df = pd.DataFrame(betas, index=factor_names).T  # asset x factor

    # Second pass: monthly cross-sectional regressions of returns on betas.
    b = np.column_stack([np.ones(len(beta_df)), beta_df.to_numpy()])  # N x (K+1)
    btb_inv = np.linalg.inv(b.T @ b)
    gammas = []
    for _, row in r.iterrows():
        y = row[beta_df.index].to_numpy()
        gammas.append(btb_inv @ b.T @ y)
    gammas = np.asarray(gammas)  # T x (K+1)

    cols = ["const", *factor_names]
    gamma_mean = pd.Series(gammas.mean(axis=0), index=cols)
    gamma_se = pd.Series(gammas.std(axis=0, ddof=1) / np.sqrt(t), index=cols)
    gamma_tstat = gamma_mean / gamma_se

    return FamaMacBethResult(
        factor_names=factor_names,
        betas=beta_df,
        gamma_mean=gamma_mean,
        gamma_tstat=gamma_tstat,
        gamma_mean_annual=gamma_mean * 12 * 100,
        n_obs=t,
        n_assets=len(beta_df),
    )
