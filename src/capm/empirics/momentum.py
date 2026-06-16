"""Momentum: the anomaly that breaks both the CAPM and the three-factor model.

Jegadeesh & Titman (1993) show that recent winners keep beating recent losers.
The paper flags momentum as the three-factor model's "most serious problem".
Here we show the momentum decile alphas under the CAPM and the three-factor
model (large and significant), and under the Carhart four-factor model that
adds the momentum factor (alphas collapse). The winner-minus-loser spread is the
tradeable expression of the effect.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from capm.data import french as fr
from capm.empirics._common import multifactor_alpha
from capm.stats import time_series_regression


@dataclass
class MomentumStudy:
    period: str
    capm_alpha: pd.Series  # per decile, annualized decimal
    ff3_alpha: pd.Series
    carhart_alpha: pd.Series
    wml_mean_ann: float
    wml_capm_alpha_ann: float
    wml_capm_alpha_t: float
    wml_ff3_alpha_ann: float
    wml_ff3_alpha_t: float


def momentum_study(period: str) -> MomentumStudy:
    fac = fr.factors()
    rf = fac["RF"]
    wml = fr.momentum_factor().rename("WML")
    deciles = fr.slice_period(fr.portfolios_on_momentum(), period)

    capm_f = fr.slice_period(fac[["Mkt-RF"]], period)
    ff3_f = fr.slice_period(fac[["Mkt-RF", "SMB", "HML"]], period)
    car_f = fr.slice_period(pd.concat([fac[["Mkt-RF", "SMB", "HML"]], wml], axis=1), period)

    capm = multifactor_alpha(deciles, capm_f, fr.slice_period(rf, period))
    ff3 = multifactor_alpha(deciles, ff3_f, fr.slice_period(rf, period))
    car = multifactor_alpha(deciles, car_f, fr.slice_period(rf, period))

    wml_p = fr.slice_period(wml, period).dropna()
    reg_capm = time_series_regression(wml_p, capm_f, annualize_alpha=False)
    reg_ff3 = time_series_regression(wml_p, ff3_f, annualize_alpha=False)

    return MomentumStudy(
        period=period,
        capm_alpha=capm["alpha_ann"],
        ff3_alpha=ff3["alpha_ann"],
        carhart_alpha=car["alpha_ann"],
        wml_mean_ann=float(wml_p.mean() * 12),
        wml_capm_alpha_ann=float(reg_capm.coef("alpha") * 12),
        wml_capm_alpha_t=float(reg_capm.tstat("alpha")),
        wml_ff3_alpha_ann=float(reg_ff3.coef("alpha") * 12),
        wml_ff3_alpha_t=float(reg_ff3.tstat("alpha")),
    )
