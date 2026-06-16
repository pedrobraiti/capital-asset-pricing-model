"""Data ingestion from the Kenneth R. French Data Library."""

from capm.data.french import (
    PERIODS,
    REGION_ZIPS,
    factors,
    industry_portfolios,
    momentum_factor,
    portfolios_25_size_beme,
    portfolios_on_beme,
    portfolios_on_beta,
    portfolios_on_me,
    portfolios_on_momentum,
    regional_factors,
    slice_period,
)

__all__ = [
    "PERIODS",
    "REGION_ZIPS",
    "factors",
    "industry_portfolios",
    "momentum_factor",
    "portfolios_25_size_beme",
    "portfolios_on_beme",
    "portfolios_on_beta",
    "portfolios_on_me",
    "portfolios_on_momentum",
    "regional_factors",
    "slice_period",
]
