"""Empirical studies that reproduce and extend Fama & French (2004)."""

from capm.empirics.bab import betting_against_beta
from capm.empirics.factors import factor_premia
from capm.empirics.grs_panel import grs_panel
from capm.empirics.momentum import momentum_study
from capm.empirics.sml import security_market_line
from capm.empirics.sorts import sorted_decile_study

__all__ = [
    "betting_against_beta",
    "factor_premia",
    "grs_panel",
    "momentum_study",
    "security_market_line",
    "sorted_decile_study",
]
