"""Download, cache and parse datasets from the Kenneth R. French Data Library.

The library publishes plain-text CSV files (zipped) with a fixed but quirky
layout: a few lines of preamble, then one or more *sections* (e.g. "Value
Weighted Returns -- Monthly", "Equal Weighted Returns -- Annual", "Number of
Firms in Portfolios", ...). Each section is a title line, a column-header line
that starts with a comma, and a block of `period,value,value,...` rows
terminated by a blank line.

This module turns that into tidy pandas frames:
    * returns are converted from percent to **decimal** (e.g. 2.89 -> 0.0289);
    * the missing-value sentinels (-99.99, -999) become NaN;
    * monthly frames are indexed by a month-end ``DatetimeIndex``.

Raw files are cached under ``data/cache/`` so the study is reproducible offline
after the first run. The cache is reproducible (re-downloadable) and therefore
git-ignored.
"""

from __future__ import annotations

import io
import re
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

_BASE_URL = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
_CACHE_DIR = Path(__file__).resolve().parents[3] / "data" / "cache"
_MISSING = (-99.99, -999.0, -99.0)
_HEADERS = {"User-Agent": "Mozilla/5.0 (capm-study; research/educational)"}

# Sample windows used throughout the study. The paper reports the equity
# premium and factor premiums for 1927-2003 and the value/beta figures for
# 1963-2003; "modern" is the out-of-sample extension after the paper.
PERIODS: dict[str, tuple[str | None, str | None]] = {
    "full": (None, None),
    "paper_1927_2003": ("1927-01", "2003-12"),
    "paper_1963_2003": ("1963-07", "2003-12"),
    "modern_2004_now": ("2004-01", None),
}


@dataclass(frozen=True)
class _Table:
    title: str
    freq: str  # "M" or "A"
    frame: pd.DataFrame


def _raw_text(zip_name: str) -> str:
    """Return the decoded CSV text for a French zip, downloading once and caching."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _CACHE_DIR / (zip_name.replace(".zip", "") + ".csv")
    if cache_file.exists():
        # Cache is normalized to LF on write, so default universal-newline read is safe.
        return cache_file.read_text(encoding="latin-1")

    request = urllib.request.Request(_BASE_URL + zip_name, headers=_HEADERS)
    payload = urllib.request.urlopen(request, timeout=60).read()  # noqa: S310 (trusted host)
    archive = zipfile.ZipFile(io.BytesIO(payload))
    text = archive.read(archive.namelist()[0]).decode("latin-1")
    # Normalize to LF and disable newline translation so the cache round-trips
    # byte-for-byte on Windows (text-mode translation otherwise doubles lines).
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    cache_file.write_text(text, encoding="latin-1", newline="\n")
    return text


_DATA_ROW = re.compile(r"^\s*(\d{4,6})\s*,")


def _parse_tables(text: str) -> list[_Table]:
    """Split a French CSV into its sections (title + frequency + frame)."""
    lines = text.splitlines()
    tables: list[_Table] = []
    last_title = ""
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip() == "":
            i += 1
            continue
        # A column-header line starts with a comma and names the columns.
        if line.lstrip().startswith(","):
            columns = [c.strip() for c in line.split(",")][1:]
            i += 1
            index: list[str] = []
            rows: list[list[float]] = []
            while i < n and _DATA_ROW.match(lines[i]):
                parts = [p.strip() for p in lines[i].split(",")]
                index.append(parts[0])
                values = [float(p) if p not in ("", "-") else np.nan for p in parts[1:]]
                # pad/truncate to the column count
                values = (values + [np.nan] * len(columns))[: len(columns)]
                rows.append(values)
                i += 1
            if rows:
                freq = "M" if len(index[0]) == 6 else "A"
                frame = pd.DataFrame(rows, columns=columns, index=index)
                tables.append(_Table(last_title.strip(), freq, frame))
            continue
        # Otherwise it is a (potential) section title; remember it.
        last_title = line
        i += 1
    return tables


def _to_decimal(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out = out.replace(list(_MISSING), np.nan)
    return out / 100.0


def _monthly_index(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()
    out.index = pd.to_datetime(out.index, format="%Y%m") + pd.offsets.MonthEnd(0)
    out.index.name = "date"
    return out


def _select(
    zip_name: str, *, title_contains: str | None, freq: str = "M"
) -> pd.DataFrame:
    tables = [t for t in _parse_tables(_raw_text(zip_name)) if t.freq == freq]
    if not tables:
        raise ValueError(f"No {freq} tables found in {zip_name}.")
    if title_contains is None:
        chosen = tables[0]
    else:
        key = title_contains.lower()
        matches = [t for t in tables if key in t.title.lower()]
        if not matches:
            raise ValueError(
                f"No section matching {title_contains!r} in {zip_name}. "
                f"Available: {[t.title for t in tables]}"
            )
        chosen = matches[0]
    frame = _to_decimal(chosen.frame)
    if freq == "M":
        frame = _monthly_index(frame)
    return frame


# --------------------------------------------------------------------------- #
# High-level dataset accessors
# --------------------------------------------------------------------------- #
def factors() -> pd.DataFrame:
    """Fama-French research factors (monthly, decimal): Mkt-RF, SMB, HML, RF."""
    return _select("F-F_Research_Data_Factors_CSV.zip", title_contains=None, freq="M")


def momentum_factor() -> pd.Series:
    """Momentum factor WML (monthly, decimal)."""
    frame = _select("F-F_Momentum_Factor_CSV.zip", title_contains=None, freq="M")
    series = frame.iloc[:, 0]
    series.name = "Mom"
    return series


def _standardize_deciles(frame: pd.DataFrame) -> pd.DataFrame:
    """Return the 10 decile columns relabelled ``D1`` (lowest) .. ``D10`` (highest).

    The library mixes naming conventions across files: deciles appear as
    ``Lo 10 / Dec 2..Dec 9 / Hi 10`` (beta), ``Lo 10 / 2-Dec..9-Dec / Hi 10``
    (B/M, size) or as a clean 10-column block (``Lo PRIOR..Hi PRIOR`` for
    momentum). Some files also interleave 30/40/30, quintile and ``<= 0`` columns
    that must be dropped.
    """
    cols = list(frame.columns)
    if len(cols) == 10:  # already a clean decile block, ordered low -> high
        out = frame.copy()
    else:
        middles = [c for c in cols if "Dec" in c]
        middles = sorted(middles, key=lambda c: int(re.search(r"(\d)", c).group(1)))
        chosen = ["Lo 10", *middles, "Hi 10"]
        missing = [c for c in chosen if c not in cols]
        if missing or len(chosen) != 10:
            raise ValueError(f"Could not isolate deciles; cols={cols}")
        out = frame[chosen].copy()
    out.columns = [f"D{i}" for i in range(1, 11)]
    return out


def _weight_title(weighting: str) -> str:
    # The library is inconsistent ("Value Weight" vs "Value Weighted" vs
    # "Average Value Weighted"); the common substring matches them all and the
    # first monthly match is always the returns table we want.
    return "Value Weight" if weighting == "VW" else "Equal Weight"


def portfolios_on_beta(weighting: str = "VW") -> pd.DataFrame:
    """Decile portfolios sorted on pre-ranking market beta (monthly returns)."""
    frame = _select("Portfolios_Formed_on_BETA_CSV.zip", title_contains=_weight_title(weighting))
    return _standardize_deciles(frame)


def portfolios_on_beme(weighting: str = "VW") -> pd.DataFrame:
    """Decile portfolios sorted on book-to-market equity (B/M), monthly returns."""
    frame = _select("Portfolios_Formed_on_BE-ME_CSV.zip", title_contains=_weight_title(weighting))
    return _standardize_deciles(frame)


def portfolios_on_me(weighting: str = "VW") -> pd.DataFrame:
    """Decile portfolios sorted on size (market equity), monthly returns."""
    frame = _select("Portfolios_Formed_on_ME_CSV.zip", title_contains=_weight_title(weighting))
    return _standardize_deciles(frame)


def portfolios_on_momentum(weighting: str = "VW") -> pd.DataFrame:
    """Decile portfolios sorted on prior 2-12 month return (momentum)."""
    frame = _select("10_Portfolios_Prior_12_2_CSV.zip", title_contains=_weight_title(weighting))
    return _standardize_deciles(frame)


def portfolios_25_size_beme(weighting: str = "VW") -> pd.DataFrame:
    """25 portfolios formed on the 5x5 intersection of size and B/M (monthly)."""
    return _select("25_Portfolios_5x5_CSV.zip", title_contains=_weight_title(weighting))


def industry_portfolios(n: int = 49, weighting: str = "VW") -> pd.DataFrame:
    """Industry portfolios (n in {17, 49}), value- or equal-weighted, monthly."""
    return _select(f"{n}_Industry_Portfolios_CSV.zip", title_contains=_weight_title(weighting))


# Kenneth French's international factor files (Bloomberg-derived). Developed
# regions start 1990-07; emerging starts 1989-07 (sparse early on).
REGION_ZIPS: dict[str, str] = {
    "Developed": "Developed_3_Factors_CSV.zip",
    "Developed ex-US": "Developed_ex_US_3_Factors_CSV.zip",
    "North America": "North_America_3_Factors_CSV.zip",
    "Europe": "Europe_3_Factors_CSV.zip",
    "Japan": "Japan_3_Factors_CSV.zip",
    "Asia Pacific ex-Japan": "Asia_Pacific_ex_Japan_3_Factors_CSV.zip",
    "Emerging": "Emerging_5_Factors_CSV.zip",
}


def regional_factors(region: str) -> pd.DataFrame:
    """International Mkt-RF, SMB, HML, RF (monthly, decimal) for a French region.

    ``region`` must be a key of :data:`REGION_ZIPS`. Emerging markets come from
    the 5-factor file; only the three shared factors are returned.
    """
    if region not in REGION_ZIPS:
        raise ValueError(f"Unknown region {region!r}. Options: {list(REGION_ZIPS)}")
    frame = _select(REGION_ZIPS[region], title_contains=None, freq="M")
    keep = [c for c in ["Mkt-RF", "SMB", "HML", "RF"] if c in frame.columns]
    return frame[keep]


def slice_period(
    frame: pd.DataFrame | pd.Series, period: str
) -> pd.DataFrame | pd.Series:
    """Restrict a monthly frame/series to one of the named ``PERIODS`` windows."""
    start, end = PERIODS[period]
    return frame.loc[start:end]
