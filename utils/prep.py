"""Cleaning and preparation of the INSEE business-creation data.

Input : the raw INSEE CSV (one row = one measure: a place, a sector,
        a legal form and a period).
Output: a tidy table with readable column names, English labels and real
        dates, plus an annual table ready for the charts.
"""
import pandas as pd

from utils import constants as C

# Column names: INSEE -> readable names
RENAME = {
    "GEO_OBJECT": "niveau",
    "GEO": "code_geo",
    "ACTIVITY": "code_secteur",
    "LEGAL_FORM": "code_forme",
    "FREQ": "frequence",
    "SEASONAL_ADJUST": "cvs",
    "TIME_PERIOD": "periode",
    "OBS_VALUE": "creations",
    "OBS_STATUS": "statut",
}


def load_labels(metadata_path=C.METADATA_CSV) -> dict:
    """Read the metadata file and return {variable: {code: label}}.

    Geography is special: the same code can be a region AND a département
    (e.g. "75" = Nouvelle-Aquitaine as a region, Paris as a département).
    So the GEO labels are keyed by (level, code), never by code alone.
    """
    meta = pd.read_csv(metadata_path, sep=";", dtype=str)
    labels = {}
    for var, sub in meta.groupby("COD_VAR"):
        if var == "GEO":
            labels[var] = dict(zip(zip(sub["GEO_OBJECT"], sub["COD_MOD"]), sub["LIB_MOD"]))
        else:
            labels[var] = dict(zip(sub["COD_MOD"], sub["LIB_MOD"]))
    return labels


def load_raw(path=C.SERIES_CSV) -> pd.DataFrame:
    """Load the raw CSV as-is (everything as text so nothing breaks)."""
    return pd.read_csv(path, sep=";", dtype=str)


def clean(raw: pd.DataFrame, labels: dict) -> pd.DataFrame:
    """Turn the raw CSV into a tidy table.

    Steps:
      1. keep and rename the useful columns;
      2. convert values to numbers;
      3. convert periods to real dates (monthly) or quarters;
      4. add labels;
      5. drop exact duplicates.
    """
    df = raw[list(RENAME)].rename(columns=RENAME).copy()

    # 2. Numeric values (errors become NaN, caught by validate.py)
    df["creations"] = pd.to_numeric(df["creations"], errors="coerce")

    # 3. Periods: "2024-03" (month) or "2024-Q1" (quarter)
    is_month = df["frequence"] == "M"
    df["annee"] = df["periode"].str[:4].astype(int)
    df["mois"] = pd.NA
    df.loc[is_month, "mois"] = df.loc[is_month, "periode"].str[5:7].astype(int)
    df["mois"] = df["mois"].astype("Int64")
    df["trimestre"] = pd.NA
    df.loc[~is_month, "trimestre"] = df.loc[~is_month, "periode"].str[-1].astype(int)
    df["trimestre"] = df["trimestre"].astype("Int64")
    df["date"] = pd.NaT
    df.loc[is_month, "date"] = pd.to_datetime(
        df.loc[is_month, "periode"] + "-01", format="%Y-%m-%d"
    )
    df["date"] = pd.to_datetime(df["date"])

    # 4. Labels
    df["secteur"] = df["code_secteur"].map(labels["ACTIVITY"])
    df["forme_legale"] = df["code_forme"].map(C.LEGAL_FORM_LABELS)
    df["lieu"] = pd.Series(list(zip(df["niveau"], df["code_geo"])),
                           index=df.index).map(labels["GEO"])
    df["statut_libelle"] = df["statut"].map(labels["OBS_STATUS"])
    df["brut"] = df["cvs"] == "N"  # True = raw figures, False = seasonally adjusted

    # 5. Exact duplicates
    df = df.drop_duplicates()

    cols = [
        "niveau", "code_geo", "lieu", "code_secteur", "secteur",
        "code_forme", "forme_legale", "frequence", "brut",
        "periode", "date", "annee", "mois", "trimestre",
        "creations", "statut", "statut_libelle",
    ]
    return df[cols].reset_index(drop=True)


def monthly_raw(tidy: pd.DataFrame) -> pd.DataFrame:
    """Keep the raw monthly series (the only ones we add up)."""
    return tidy[(tidy["frequence"] == "M") & (tidy["brut"])]


def annual_table(tidy: pd.DataFrame) -> pd.DataFrame:
    """Annual total per place, sector and legal form (sum of the 12 raw months).

    - A year is "complete" only if all 12 months are present.
    - Adds the base-100 index (reference year: constants.BASE_YEAR)
      and the year-on-year growth.
    """
    m = monthly_raw(tidy)
    keys = ["niveau", "code_geo", "lieu", "code_secteur", "secteur",
            "code_forme", "forme_legale"]
    g = (
        m.groupby(keys + ["annee"], observed=True)["creations"]
        .agg(creations="sum", nb_mois="count")
        .reset_index()
    )
    g["annee_complete"] = g["nb_mois"] == 12
    g = g.sort_values(keys + ["annee"])

    # Base-100 index on the reference year
    base = (
        g[g["annee"] == C.BASE_YEAR][keys + ["creations"]]
        .rename(columns={"creations": "base"})
    )
    g = g.merge(base, on=keys, how="left")
    g["indice_base100"] = g["creations"] / g["base"] * 100

    # Year-on-year growth (only between complete years)
    g["croissance_pct"] = g.groupby(keys)["creations"].pct_change() * 100
    g.loc[~g["annee_complete"], ["croissance_pct", "indice_base100"]] = pd.NA
    return g.drop(columns=["base"]).reset_index(drop=True)


def monthly_trend(tidy: pd.DataFrame) -> pd.DataFrame:
    """Seasonally adjusted monthly series for France (all sectors), by legal form.

    Seasonal adjustment removes the usual yearly pattern (e.g. quiet summers),
    so months can be compared with each other. That is why this series is used
    for the trend, while the annual totals use the raw figures.
    """
    codes = ["_T"] + C.LEGAL_FORM_PARTS
    t = tidy[
        (tidy["niveau"] == "FRANCE") & (tidy["code_secteur"] == "_T")
        & (tidy["frequence"] == "M") & (~tidy["brut"])
        & (tidy["code_forme"].isin(codes))
    ]
    cols = ["date", "annee", "code_forme", "forme_legale", "creations", "statut"]
    return t[cols].sort_values(["code_forme", "date"]).reset_index(drop=True)


# Column names of the CSV offered for download (English)
EXPORT_COLUMNS = {
    "niveau": "level", "code_geo": "geo_code", "lieu": "place",
    "code_secteur": "sector_code", "secteur": "sector",
    "code_forme": "legal_form_code", "forme_legale": "legal_form",
    "annee": "year", "creations": "creations", "nb_mois": "months_available",
    "annee_complete": "complete_year", "indice_base100": "index_base100",
    "croissance_pct": "growth_pct",
}


def export_annual(annual: pd.DataFrame) -> pd.DataFrame:
    """Clean annual table with English column names (for the CSV download)."""
    out = annual[list(EXPORT_COLUMNS)].rename(columns=EXPORT_COLUMNS).copy()
    out["index_base100"] = out["index_base100"].astype("float64").round(2)
    out["growth_pct"] = out["growth_pct"].astype("float64").round(2)
    return out


def pipeline_summary(raw: pd.DataFrame, tidy: pd.DataFrame, annual: pd.DataFrame) -> dict:
    """Before/after figures shown in the app ("What was done to the data")."""
    dropped = [c for c in raw.columns if c not in RENAME]
    places = tidy.drop_duplicates(["niveau", "code_geo"])["niveau"].value_counts()
    return {
        "raw_rows": int(len(raw)),
        "raw_columns": int(raw.shape[1]),
        "clean_rows": int(len(tidy)),
        "clean_columns": int(tidy.shape[1]),
        "duplicates_removed": int(len(raw) - len(tidy)),
        "invalid_numbers": int(tidy["creations"].isna().sum()),
        "dropped_columns": {c: sorted(raw[c].dropna().unique().tolist())[:3] for c in dropped},
        "dropped_are_constant": all(raw[c].nunique(dropna=False) == 1 for c in dropped),
        "annual_rows": int(len(annual)),
        "first_month": f"{tidy['date'].min():%Y-%m}",
        "last_month": f"{tidy['date'].max():%Y-%m}",
        "places": {k: int(v) for k, v in places.items()},
    }
