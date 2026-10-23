"""Data loading for the app (cached).

Search order:
  1. files already prepared in data/processed/ (fast, normal case);
  2. otherwise: download the raw data (scripts/download_data.py)
     then prepare it (scripts/build_data.py).
"""
import json

import pandas as pd
import streamlit as st

from utils import constants as C

DATA_SOURCE = (
    "Business creations – long series (INSEE), published on data.gouv.fr "
    "— Open Licence 2.0"
)
GEO_SOURCE = (
    "département outlines from IGN Admin Express COG (2018 edition, Open Licence), "
    "simplified GeoJSON from github.com/gregoiredavid/france-geojson"
)


def ensure_data() -> None:
    """Prepare the files if needed (download + cleaning)."""
    if C.ANNUAL_PARQUET.exists() and C.TIDY_PARQUET.exists():
        return
    from scripts import build_data, download_data

    if download_data.main() != 0:
        raise RuntimeError("Raw data not found: see the README.")
    build_data.main()


@st.cache_data(show_spinner="Loading data…")
def load_tables():
    """Return (annual table, quality report, full tidy table)."""
    ensure_data()
    annual = pd.read_parquet(C.ANNUAL_PARQUET)
    tidy = pd.read_parquet(C.TIDY_PARQUET)
    with open(C.QUALITY_JSON, encoding="utf-8") as f:
        quality = json.load(f)
    return annual, quality, tidy


@st.cache_data(show_spinner=False)
def load_geojson() -> dict:
    with open(C.GEOJSON, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def load_trend() -> pd.DataFrame:
    """Seasonally adjusted monthly series (France), see prep.monthly_trend."""
    from utils import prep

    return prep.monthly_trend(load_tables()[2])


@st.cache_data(show_spinner=False)
def load_summary() -> dict:
    """Before/after figures of the data preparation (empty if the file is absent)."""
    if not C.PIPELINE_JSON.exists():
        return {}
    with open(C.PIPELINE_JSON, encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(show_spinner=False)
def annual_csv() -> bytes:
    """Clean annual table as CSV bytes (download button)."""
    from utils import prep

    return prep.export_annual(load_tables()[0]).to_csv(index=False).encode("utf-8")
