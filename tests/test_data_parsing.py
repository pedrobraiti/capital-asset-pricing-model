"""Tests for the Ken French CSV parser (offline, using a synthetic fixture)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from capm.data.french import _parse_tables, _standardize_deciles, _to_decimal

_SAMPLE = """This file was created using a test fixture.

  Value Weight Returns -- Monthly
,Lo 10,Dec 2,Dec 3,Dec 4,Dec 5,Dec 6,Dec 7,Dec 8,Dec 9,Hi 10
196307,    1.12,    0.21,   -1.30,   -0.93,   -0.49,    1.34,    0.76,   -0.24,    0.63,   -1.37
196308,    3.68,    4.91,    5.92,    6.34,   10.09,    3.55,    3.89,    4.70,    5.11,    4.78

  Annual Factors
,Lo 10,Dec 2,Dec 3,Dec 4,Dec 5,Dec 6,Dec 7,Dec 8,Dec 9,Hi 10
1963,   10.0,   -99.99,   2.0,   3.0,   4.0,   5.0,   6.0,   7.0,   8.0,   9.0
"""


def test_parse_tables_splits_sections_and_detects_frequency():
    tables = _parse_tables(_SAMPLE)
    assert len(tables) == 2
    monthly = [t for t in tables if t.freq == "M"]
    annual = [t for t in tables if t.freq == "A"]
    assert len(monthly) == 1 and len(annual) == 1
    assert "Value Weight" in monthly[0].title
    assert monthly[0].frame.shape == (2, 10)


def test_to_decimal_converts_percent_and_masks_missing():
    tables = _parse_tables(_SAMPLE)
    annual = [t for t in tables if t.freq == "A"][0]
    dec = _to_decimal(annual.frame)
    assert np.isclose(dec.iloc[0, 0], 0.10)  # 10.0% -> 0.10
    assert np.isnan(dec.iloc[0, 1])  # -99.99 sentinel -> NaN


def test_standardize_deciles_relabels_to_d1_d10():
    tables = _parse_tables(_SAMPLE)
    monthly = [t for t in tables if t.freq == "M"][0]
    std = _standardize_deciles(monthly.frame)
    assert list(std.columns) == [f"D{i}" for i in range(1, 11)]
    # D1 is the "Lo 10" column, preserved in order
    assert np.isclose(std.iloc[0, 0], monthly.frame.iloc[0, 0])
