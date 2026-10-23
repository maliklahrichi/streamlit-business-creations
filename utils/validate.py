"""Data-quality checks on the cleaned data.

Each check returns a dictionary:
    {"controle": name, "ok": True/False, "detail": explanation}
The results are shown in the "Data quality" section of the app.
"""
import json

import pandas as pd

from utils import constants as C
from utils.prep import monthly_raw


def _res(name: str, ok: bool, detail: str) -> dict:
    return {"controle": name, "ok": bool(ok), "detail": detail}


def check_no_missing(tidy: pd.DataFrame) -> dict:
    n = int(tidy["creations"].isna().sum())
    return _res("No missing values", n == 0, f"{n} missing value(s)")


def check_no_duplicates(tidy: pd.DataFrame) -> dict:
    keys = ["niveau", "code_geo", "code_secteur", "code_forme",
            "frequence", "brut", "periode"]
    n = int(tidy.duplicated(subset=keys).sum())
    return _res("No duplicates on the key (place, sector, legal form, period)",
                n == 0, f"{n} duplicate(s)")


def check_non_negative(tidy: pd.DataFrame) -> dict:
    n = int((tidy["creations"] < 0).sum())
    return _res("No negative values", n == 0, f"{n} negative value(s)")


def check_france_months_complete(tidy: pd.DataFrame) -> dict:
    """No missing month in the France series (total, raw)."""
    m = monthly_raw(tidy)
    f = m[(m["niveau"] == "FRANCE") & (m["code_secteur"] == "_T")
          & (m["code_forme"] == "_T")]
    expected = pd.date_range(f["date"].min(), f["date"].max(), freq="MS")
    missing = expected.difference(pd.DatetimeIndex(f["date"]))
    return _res(
        "No missing month in the France series",
        len(missing) == 0,
        f"{len(f)} months from {f['date'].min():%Y-%m} to {f['date'].max():%Y-%m}; "
        f"{len(missing)} missing",
    )


def check_departments_sum_to_france(tidy: pd.DataFrame, tol: float = 0.0) -> dict:
    """The sum of the 101 départements must equal the France total, month by month."""
    m = monthly_raw(tidy)
    base = m[(m["code_secteur"] == "_T") & (m["code_forme"] == "_T")]
    dep = base[base["niveau"] == "DEP"].groupby("date")["creations"].sum()
    fra = base[base["niveau"] == "FRANCE"].set_index("date")["creations"]
    common = dep.index.intersection(fra.index)
    diff = (dep.loc[common] - fra.loc[common]).abs()
    bad = diff[diff > tol * fra.loc[common]]
    worst = int(diff.max()) if len(diff) else 0
    return _res(
        "Sum of départements = France total (monthly)",
        len(bad) == 0,
        f"{len(common)} months compared; {len(bad)} mismatch(es); max gap = {worst}",
    )


def check_legal_forms_add_up(tidy: pd.DataFrame) -> dict:
    """Micro + companies + sole proprietors excl. micro = total (France, monthly raw)."""
    m = monthly_raw(tidy)
    f = m[(m["niveau"] == "FRANCE") & (m["code_secteur"] == "_T")]
    p = f.pivot_table(index="date", columns="code_forme",
                      values="creations", aggfunc="sum")
    parts = p[C.LEGAL_FORM_PARTS].sum(axis=1)
    diff = (parts - p["_T"]).abs()
    bad = int((diff > 0).sum())
    return _res(
        "Micro + companies + sole proprietors (excl. micro) = total (France)",
        bad == 0,
        f"{len(p)} months compared; {bad} mismatch(es); max gap = {int(diff.max())}",
    )


def check_geo_codes(tidy: pd.DataFrame, geojson_path=C.GEOJSON) -> dict:
    """Département codes in the data must exist in the map file."""
    with open(geojson_path, encoding="utf-8") as f:
        geo_codes = {ft["properties"]["code"] for ft in json.load(f)["features"]}
    data_codes = set(tidy.loc[tidy["niveau"] == "DEP", "code_geo"])
    unknown = sorted(data_codes - geo_codes - set(C.OVERSEAS_DEPS))
    return _res(
        "Département codes covered by the map file",
        len(unknown) == 0,
        f"{len(geo_codes)} outlines; overseas excluded on purpose; "
        f"unknown codes: {unknown or 'none'}",
    )


def _norm(text: str) -> str:
    """Lower-case, no accents, no punctuation (to compare place names)."""
    import re
    import unicodedata

    t = unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def check_geo_names(tidy: pd.DataFrame, geojson_path=C.GEOJSON) -> dict:
    """Each département name in the data must match the name in the map file."""
    with open(geojson_path, encoding="utf-8") as f:
        geo_names = {ft["properties"]["code"]: ft["properties"]["nom"]
                     for ft in json.load(f)["features"]}
    dep = tidy.loc[tidy["niveau"] == "DEP", ["code_geo", "lieu"]].drop_duplicates()
    dep = dep[dep["code_geo"].isin(geo_names)]
    bad = [(r.code_geo, r.lieu, geo_names[r.code_geo]) for r in dep.itertuples()
           if _norm(r.lieu) != _norm(geo_names[r.code_geo])]
    return _res(
        "Département names match the map file",
        len(bad) == 0,
        f"{len(dep)} départements compared; {len(bad)} mismatch(es)"
        + (f": {bad[:3]}" if bad else ""),
    )


def reliability_share(tidy: pd.DataFrame) -> dict:
    """Information (not a test): share of low-reliability / revised observations."""
    s = tidy["statut"].value_counts(normalize=True) * 100
    return _res(
        "Share of low-reliability observations (status U)",
        True,
        f"low reliability: {s.get('U', 0):.1f}%; "
        f"revised: {s.get('R', 0):.1f}%; normal: {s.get('A', 0):.1f}%",
    )


def run_all(tidy: pd.DataFrame) -> list:
    """Run every check and return the list of results."""
    return [
        check_no_missing(tidy),
        check_no_duplicates(tidy),
        check_non_negative(tidy),
        check_france_months_complete(tidy),
        check_departments_sum_to_france(tidy),
        check_legal_forms_add_up(tidy),
        check_geo_codes(tidy),
        check_geo_names(tidy),
        reliability_share(tidy),
    ]
