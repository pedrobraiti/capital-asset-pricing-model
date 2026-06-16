"""GRS panel: which model prices which set of test assets?

For several sets of test portfolios we run the Gibbons-Ross-Shanken test under
the CAPM (market only), the Fama-French three-factor model and the Carhart
four-factor model (adding momentum). The story the paper tells falls straight
out of the table: the CAPM is rejected almost everywhere, the three-factor
model rescues the size/value sorts but is itself rejected by momentum, and the
four-factor model handles momentum.
"""

from __future__ import annotations

import pandas as pd

from capm.data import french as fr
from capm.empirics._common import excess
from capm.stats import grs_test


def _test_asset_sets() -> dict[str, pd.DataFrame]:
    return {
        "10 B/M deciles": fr.portfolios_on_beme(),
        "10 size deciles": fr.portfolios_on_me(),
        "10 beta deciles": fr.portfolios_on_beta(),
        "10 momentum deciles": fr.portfolios_on_momentum(),
        "25 size-B/M": fr.portfolios_25_size_beme(),
        "17 industries": fr.industry_portfolios(17),
    }


def _model_factors() -> dict[str, list[str]]:
    return {
        "CAPM": ["Mkt-RF"],
        "FF3": ["Mkt-RF", "SMB", "HML"],
        "Carhart4": ["Mkt-RF", "SMB", "HML", "WML"],
    }


def grs_panel(period: str) -> pd.DataFrame:
    """Run GRS for every (test-asset set, model) pair in ``period``.

    Returns a tidy frame with the F-statistic, p-value and annualized mean
    absolute alpha (decimal) for each cell.
    """
    fac = fr.factors()
    rf = fac["RF"]
    all_factors = pd.concat([fac[["Mkt-RF", "SMB", "HML"]], fr.momentum_factor().rename("WML")], axis=1)

    rows = []
    for set_name, portfolios in _test_asset_sets().items():
        exc = fr.slice_period(excess(portfolios, rf), period)
        for model_name, cols in _model_factors().items():
            facs = fr.slice_period(all_factors[cols], period)
            try:
                result = grs_test(exc, facs)
            except ValueError:
                continue
            rows.append({
                "test_assets": set_name,
                "model": model_name,
                "n_assets": result.n_assets,
                "grs_F": result.statistic,
                "p_value": result.p_value,
                "rejects_5pct": result.rejects_at_5pct,
                "mean_abs_alpha_ann": result.mean_abs_alpha_annual,
                "n_obs": result.n_obs,
            })
    return pd.DataFrame(rows)
