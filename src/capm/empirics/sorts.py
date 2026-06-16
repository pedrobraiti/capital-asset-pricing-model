"""Decile-sort studies: value (B/M), size and momentum.

For each decile portfolio this computes the average excess return, the market
beta, the CAPM-predicted excess return and the CAPM alpha. It reproduces the
paper's Figure 3 (B/M deciles) and the size effect, and quantifies the long-
short spread (D10 minus D1) together with the CAPM alpha of that spread -- the
part of the premium the market factor cannot explain.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from capm.data import french as fr
from capm.empirics._common import capm_stats
from capm.stats import time_series_regression

_LOADERS = {
    "beme": (fr.portfolios_on_beme, "Book-to-Market (value)"),
    "me": (fr.portfolios_on_me, "Size"),
    "momentum": (fr.portfolios_on_momentum, "Momentum"),
    "beta": (fr.portfolios_on_beta, "Pre-ranking beta"),
}


@dataclass
class DecileStudy:
    kind: str
    label: str
    period: str
    table: pd.DataFrame  # per decile: beta, mean_excess(_ann), predicted_excess(_ann), alpha(_ann), t_alpha
    spread_label: str  # e.g. "D10-D1"
    spread_mean_ann: float  # decimal annualized average spread return
    spread_alpha_ann: float  # CAPM alpha of the spread, decimal annualized
    spread_alpha_t: float
    spread_beta: float


def sorted_decile_study(kind: str, period: str, *, long_minus_short: bool = True) -> DecileStudy:
    loader, label = _LOADERS[kind]
    fac = fr.factors()
    rf, mkt = fac["RF"], fac["Mkt-RF"]

    deciles = fr.slice_period(loader(), period)
    mkt_p = fr.slice_period(mkt, period)
    rf_p = fr.slice_period(rf, period)

    table = capm_stats(deciles, mkt_p, rf_p)

    # Long-short spread: high decile minus low decile (value, small? -- see note).
    high, low = ("D10", "D1") if long_minus_short else ("D1", "D10")
    spread = (deciles[high] - deciles[low]).dropna()
    reg = time_series_regression(spread, mkt_p.to_frame("Mkt-RF"), annualize_alpha=False)

    return DecileStudy(
        kind=kind,
        label=label,
        period=period,
        table=table,
        spread_label=f"{high}-{low}",
        spread_mean_ann=float(spread.mean() * 12),
        spread_alpha_ann=float(reg.coef("alpha") * 12),
        spread_alpha_t=float(reg.tstat("alpha")),
        spread_beta=float(reg.coef("Mkt-RF")),
    )
