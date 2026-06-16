"""Tests for the OLS / Newey-West regression engine."""

from __future__ import annotations

import numpy as np
import pandas as pd

from capm.stats import ols, time_series_regression


def test_ols_recovers_known_coefficients():
    rng = np.random.default_rng(0)
    n = 2000
    x1 = rng.normal(size=n)
    x2 = rng.normal(size=n)
    y = 1.5 + 2.0 * x1 - 0.5 * x2 + rng.normal(scale=0.1, size=n)
    x = np.column_stack([np.ones(n), x1, x2])

    result = ols(y, x, hac_lags=None, names=["const", "x1", "x2"])
    assert np.isclose(result.coef("const"), 1.5, atol=0.02)
    assert np.isclose(result.coef("x1"), 2.0, atol=0.02)
    assert np.isclose(result.coef("x2"), -0.5, atol=0.02)
    assert result.r_squared > 0.99


def test_hac_standard_errors_are_positive_and_finite():
    rng = np.random.default_rng(1)
    n = 500
    x1 = rng.normal(size=n)
    y = 0.3 + 0.8 * x1 + rng.normal(size=n)
    x = np.column_stack([np.ones(n), x1])
    result = ols(y, x, hac_lags="auto")
    assert np.all(result.std_errors > 0)
    assert np.all(np.isfinite(result.tstats))
    assert result.hac_lags is not None and result.hac_lags >= 1


def test_time_series_alpha_annualization_scales_intercept_not_tstat():
    rng = np.random.default_rng(2)
    idx = pd.date_range("1990-01-31", periods=360, freq="ME")
    mkt = pd.Series(rng.normal(0.005, 0.04, size=360), index=idx, name="Mkt-RF")
    # asset with a true monthly alpha of 0.004 and beta 1.1
    asset = 0.004 + 1.1 * mkt + pd.Series(rng.normal(0, 0.01, size=360), index=idx)

    monthly = time_series_regression(asset, mkt.to_frame(), annualize_alpha=False)
    annual = time_series_regression(asset, mkt.to_frame(), annualize_alpha=True)

    assert np.isclose(annual.coef("alpha"), monthly.coef("alpha") * 12)
    assert np.isclose(annual.tstat("alpha"), monthly.tstat("alpha"))
    assert np.isclose(monthly.coef("Mkt-RF"), 1.1, atol=0.03)
