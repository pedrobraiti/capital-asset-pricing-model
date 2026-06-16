"""The publication effect: do anomalies decay after they are published?

McLean & Pontiff (2016, *Journal of Finance*) show that the average anomaly's
return falls by more than half once the academic paper documenting it is in
print -- consistent with arbitrageurs trading the signal away. Fama & French
(2004) raised exactly this worry ("publication-hungry researchers ... unearthing
contradictions ... as a result of chance") but could not test it forward in time.

This module splits each factor's monthly premium at the publication date of its
seminal paper and compares the pre- and post-publication means, the percentage
decay, and a Welch t-test of the difference. The market premium is included as a
control: it was never an "anomaly", so it should not decay.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from capm.data import french as fr

# Factor -> (series-getter key, seminal publication year, citation).
PUBLICATIONS: dict[str, tuple[str, int, str]] = {
    "SMB (size)": ("SMB", 1981, "Banz (1981)"),
    "HML (value)": ("HML", 1985, "Rosenberg, Reid & Lanstein (1985)"),
    "WML (momentum)": ("WML", 1993, "Jegadeesh & Titman (1993)"),
    "Mkt-RF (control)": ("Mkt-RF", 1964, "Sharpe (1964) - not an anomaly"),
}


def _factor_series() -> dict[str, pd.Series]:
    fac = fr.factors()
    return {
        "Mkt-RF": fac["Mkt-RF"],
        "SMB": fac["SMB"],
        "HML": fac["HML"],
        "WML": fr.momentum_factor(),
    }


def _stats(series: pd.Series) -> tuple[float, float, int]:
    s = series.dropna()
    mean_ann = s.mean() * 12
    t = s.mean() / (s.std(ddof=1) / np.sqrt(len(s)))
    return float(mean_ann), float(t), len(s)


def publication_effect() -> pd.DataFrame:
    """Pre- vs post-publication premium, decay and significance for each factor."""
    series = _factor_series()
    rows = []
    for label, (key, year, cite) in PUBLICATIONS.items():
        s = series[key].dropna()
        split = f"{year}-12"
        pre, post = s.loc[:split], s.loc[f"{year + 1}-01":]
        pre_mean, pre_t, pre_n = _stats(pre)
        post_mean, post_t, post_n = _stats(post)
        decay = (post_mean - pre_mean) / abs(pre_mean) if pre_mean != 0 else np.nan
        welch = stats.ttest_ind(pre.to_numpy(), post.to_numpy(), equal_var=False)
        rows.append({
            "factor": label,
            "publication": cite,
            "pub_year": year,
            "pre_mean_ann": pre_mean,
            "pre_t": pre_t,
            "pre_n": pre_n,
            "post_mean_ann": post_mean,
            "post_t": post_t,
            "post_n": post_n,
            "decay_pct": decay * 100,
            "diff_t": float(welch.statistic),
            "diff_p": float(welch.pvalue),
        })
    return pd.DataFrame(rows).set_index("factor")
