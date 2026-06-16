"""International evidence: is the US fade in value and size a global pattern?

Fama & French (1998) found the value premium in markets around the world, which
the paper cites as evidence the anomalies are not US sample-specific. Using
Kenneth French's international factor files (Bloomberg-derived, starting 1990),
this module measures the market, size and value premiums region by region and
splits each at the end of 2003 -- the paper's horizon -- to see whether the
post-publication decay we observe in the US also shows up abroad.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from capm.data import french as fr

_SPLIT = "2003-12"


def _premium(series: pd.Series) -> dict:
    s = series.dropna()
    if len(s) < 24:
        return {"mean_ann": np.nan, "t_stat": np.nan, "n": len(s)}
    return {
        "mean_ann": float(s.mean() * 12),
        "t_stat": float(s.mean() / (s.std(ddof=1) / np.sqrt(len(s)))),
        "n": len(s),
    }


def international_premia() -> pd.DataFrame:
    """Market/SMB/HML premiums by region, for the full sample and 1990-2003 vs 2004+.

    Returns a tidy frame indexed by region with annualized premiums (decimal)
    and t-statistics for each factor and sub-period.
    """
    rows = {}
    for region in fr.REGION_ZIPS:
        fac = fr.regional_factors(region)
        start = fac.dropna(how="all").index.min()
        row = {"start": start.strftime("%Y-%m")}
        for factor in ["Mkt-RF", "SMB", "HML"]:
            if factor not in fac.columns:
                continue
            series = fac[factor]
            full = _premium(series)
            pre = _premium(series.loc[:_SPLIT])
            post = _premium(series.loc["2004-01":])
            row[f"{factor}_full_ann"] = full["mean_ann"]
            row[f"{factor}_full_t"] = full["t_stat"]
            row[f"{factor}_pre_ann"] = pre["mean_ann"]
            row[f"{factor}_post_ann"] = post["mean_ann"]
        rows[region] = row
    return pd.DataFrame(rows).T
