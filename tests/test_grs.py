"""Tests for the Gibbons-Ross-Shanken joint test."""

from __future__ import annotations

import numpy as np
import pandas as pd

from capm.stats import grs_test


def _make_panel(alphas, *, n=600, beta=1.0, seed=0):
    rng = np.random.default_rng(seed)
    idx = pd.date_range("1970-01-31", periods=n, freq="ME")
    mkt = pd.Series(rng.normal(0.005, 0.04, size=n), index=idx, name="Mkt-RF")
    cols = {}
    for i, a in enumerate(alphas):
        cols[f"P{i}"] = a + beta * mkt + rng.normal(0, 0.02, size=n)
    return pd.DataFrame(cols, index=idx), mkt.to_frame()


def test_grs_does_not_reject_when_alphas_are_zero():
    returns, factors = _make_panel([0.0, 0.0, 0.0, 0.0, 0.0], seed=1)
    result = grs_test(returns, factors)
    assert not result.rejects_at_5pct
    assert result.p_value > 0.05
    assert result.df1 == 5


def test_grs_rejects_with_large_common_alpha():
    returns, factors = _make_panel([0.01, 0.012, 0.011, 0.009, 0.013], seed=2)
    result = grs_test(returns, factors)
    assert result.rejects_at_5pct
    assert result.p_value < 0.01
    assert result.mean_abs_alpha_annual > 0.05  # ~ >5%/yr


def test_grs_requires_enough_observations():
    returns, factors = _make_panel([0.0] * 5, n=5)
    try:
        grs_test(returns, factors)
    except ValueError:
        return
    raise AssertionError("expected ValueError when T <= N + K")
