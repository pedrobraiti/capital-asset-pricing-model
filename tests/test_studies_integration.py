"""Integration checks for the new studies, run against cached French data.

These touch the Ken French library (cached locally after the first run). If the
data cannot be reached -- e.g. a clean checkout with no network -- the tests
skip rather than fail, so the offline unit suite stays green.
"""

from __future__ import annotations

import urllib.error

import pytest


def _maybe(fn):
    try:
        return fn()
    except (urllib.error.URLError, OSError) as exc:  # no network / cache
        pytest.skip(f"French data unavailable: {exc}")


def test_publication_effect_anomalies_decay_more_than_control():
    from capm.empirics import publication_effect

    pe = _maybe(publication_effect)
    assert list(pe.index) == ["SMB (size)", "HML (value)", "WML (momentum)", "Mkt-RF (control)"]
    # Every anomaly premium decays after publication.
    for factor in ["SMB (size)", "HML (value)", "WML (momentum)"]:
        assert pe.loc[factor, "decay_pct"] < 0
    # The market control decays least (smallest absolute decay) and survives.
    control_decay = abs(pe.loc["Mkt-RF (control)", "decay_pct"])
    anomaly_decay = abs(pe.loc[["SMB (size)", "HML (value)", "WML (momentum)"], "decay_pct"]).mean()
    assert control_decay < anomaly_decay
    assert abs(pe.loc["Mkt-RF (control)", "post_t"]) > 2.0


def test_international_value_premium_is_broadly_positive_full_sample():
    from capm.empirics import international_premia

    ip = _maybe(international_premia)
    assert "Emerging" in ip.index and "Japan" in ip.index
    # Value premium is positive on the full sample in most regions.
    full = ip["HML_full_ann"].astype(float)
    assert (full > 0).mean() >= 0.8
