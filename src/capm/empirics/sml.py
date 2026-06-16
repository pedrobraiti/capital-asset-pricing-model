"""The flat Security Market Line (Fama & French 2004, Figure 2).

The Sharpe-Lintner CAPM predicts that average excess returns line up on a line
through the origin with slope equal to the average excess market return. The
paper's Figure 2 shows that, for beta-sorted portfolios, the realized relation
is far too flat: low-beta portfolios earn more than the CAPM predicts and
high-beta portfolios earn less.

This module reproduces that picture with the library's beta-sorted deciles and
backs it with a Fama-MacBeth cross-sectional regression over a broad set of test
portfolios (beta, size, B/M and momentum deciles), which is the cross-section
test described in the paper.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from capm.data import french as fr
from capm.empirics._common import capm_stats, fit_line
from capm.stats import fama_macbeth


@dataclass
class SMLResult:
    period: str
    table: pd.DataFrame  # per beta-decile: beta, mean excess, predicted, alpha
    realized_intercept_ann: float  # decimal, annualized
    realized_slope_ann: float
    capm_intercept_ann: float  # 0 in excess form
    capm_slope_ann: float  # average excess market return
    fm_intercept_ann: float
    fm_intercept_t: float
    fm_slope_ann: float
    fm_slope_t: float
    fm_n_assets: int


def _broad_test_assets(rf: pd.Series) -> pd.DataFrame:
    """A wide cross-section of decile portfolios for the Fama-MacBeth regression."""
    parts = {
        "beta": fr.portfolios_on_beta(),
        "me": fr.portfolios_on_me(),
        "bm": fr.portfolios_on_beme(),
        "mom": fr.portfolios_on_momentum(),
    }
    frames = [df.rename(columns=lambda c, p=key: f"{p}_{c}") for key, df in parts.items()]
    return pd.concat(frames, axis=1)


def security_market_line(period: str) -> SMLResult:
    fac = fr.factors()
    rf, mkt = fac["RF"], fac["Mkt-RF"]

    beta_dec = fr.slice_period(fr.portfolios_on_beta(), period)
    mkt_p = fr.slice_period(mkt, period)
    rf_p = fr.slice_period(rf, period)

    table = capm_stats(beta_dec, mkt_p, rf_p)
    realized_int, realized_slope = fit_line(table["beta"].to_numpy(), table["mean_excess"].to_numpy())

    capm_slope = float(mkt_p.reindex(beta_dec.index).mean())

    broad = fr.slice_period(_broad_test_assets(rf), period)
    fm = fama_macbeth(broad.sub(rf_p, axis=0), mkt_p.to_frame("Mkt-RF"))

    return SMLResult(
        period=period,
        table=table,
        realized_intercept_ann=realized_int * 12,
        realized_slope_ann=realized_slope * 12,
        capm_intercept_ann=0.0,
        capm_slope_ann=capm_slope * 12,
        fm_intercept_ann=float(fm.gamma_mean_annual["const"]) / 100,
        fm_intercept_t=float(fm.gamma_tstat["const"]),
        fm_slope_ann=float(fm.gamma_mean_annual["Mkt-RF"]) / 100,
        fm_slope_t=float(fm.gamma_tstat["Mkt-RF"]),
        fm_n_assets=fm.n_assets,
    )
