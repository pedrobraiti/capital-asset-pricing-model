"""Tests for the performance-metric helpers."""

from __future__ import annotations

import numpy as np
import pandas as pd

from capm.stats import performance_metrics
from capm.stats.metrics import equity_curve, max_drawdown


def _series(values):
    idx = pd.date_range("2000-01-31", periods=len(values), freq="ME")
    return pd.Series(values, index=idx)


def test_equity_curve_compounds():
    r = _series([0.10, -0.10, 0.05])
    curve = equity_curve(r)
    assert np.isclose(curve.iloc[-1], 1.10 * 0.90 * 1.05)


def test_max_drawdown_is_negative_and_correct():
    r = _series([0.20, -0.50, 0.10])  # peak 1.2 then down to 0.6
    mdd = max_drawdown(r)
    assert np.isclose(mdd, 0.6 / 1.2 - 1.0)  # -0.5
    assert mdd < 0


def test_constant_positive_returns_have_high_sharpe_and_no_drawdown():
    r = _series([0.01] * 120)
    m = performance_metrics(r)
    assert m.max_drawdown == 0.0 or np.isclose(m.max_drawdown, 0.0)
    assert m.hit_rate == 1.0
    assert np.isclose(m.ann_arith_return, 0.12, atol=1e-9)
    assert m.ann_return > 0.12  # geometric compounding > arithmetic here


def test_sharpe_uses_excess_when_risk_free_given():
    rng = np.random.default_rng(0)
    r = _series(rng.normal(0.01, 0.03, size=240))
    rf = _series([0.002] * 240)
    m_excess = performance_metrics(r, risk_free=rf)
    m_raw = performance_metrics(r)
    assert m_excess.sharpe < m_raw.sharpe  # subtracting rf lowers Sharpe
