"""Tests for data preparation and validation, on a tiny dataset."""
import pandas as pd
import pytest

from utils import prep, validate

LABELS = {
    "ACTIVITY": {"_T": "Total"},
    "GEO": {("FRANCE", "FR"): "France", ("DEP", "01"): "Ain",
            ("DEP", "75"): "Paris", ("REG", "75"): "Nouvelle-Aquitaine"},
    "OBS_STATUS": {"A": "Normale"},
}


def make_raw(rows):
    cols = ["ACTIVITY", "FREQ", "GEO", "GEO_OBJECT", "LEGAL_FORM",
            "SEASONAL_ADJUST", "SIDE_MEASURE", "UNIT_MEASURE", "DECIMALS",
            "OBS_STATUS", "UNIT_MULT", "TIME_PERIOD", "OBS_VALUE"]
    return pd.DataFrame(rows, columns=cols)


def row(period, value, form="_T", geo="FR", level="FRANCE", cvs="N"):
    return ["_T", "M", geo, level, form, cvs, "BURE", "_Z", "0", "A", "0",
            period, str(value)]


def test_clean_converts_types_and_dates():
    raw = make_raw([row("2024-03", 100)])
    tidy = prep.clean(raw, LABELS)
    assert tidy.loc[0, "creations"] == 100
    assert tidy.loc[0, "annee"] == 2024
    assert tidy.loc[0, "mois"] == 3
    assert tidy.loc[0, "date"] == pd.Timestamp("2024-03-01")
    assert tidy.loc[0, "forme_legale"] == "Total"


def test_clean_removes_exact_duplicates():
    raw = make_raw([row("2024-03", 100), row("2024-03", 100)])
    assert len(prep.clean(raw, LABELS)) == 1


def test_annual_table_flags_incomplete_year_and_index():
    rows = [row(f"2019-{m:02d}", 10) for m in range(1, 13)]      # 120 in 2019
    rows += [row(f"2020-{m:02d}", 12) for m in range(1, 13)]     # 144 in 2020
    rows += [row("2021-01", 5)]                                   # partial year
    tidy = prep.clean(make_raw(rows), LABELS)
    a = prep.annual_table(tidy).set_index("annee")
    assert a.loc[2019, "indice_base100"] == pytest.approx(100)
    assert a.loc[2020, "indice_base100"] == pytest.approx(120)
    assert a.loc[2020, "croissance_pct"] == pytest.approx(20)
    assert not a.loc[2021, "annee_complete"]
    assert pd.isna(a.loc[2021, "indice_base100"])


def test_validation_detects_missing_value():
    raw = make_raw([row("2024-03", "abc")])  # non-numeric -> NaN
    tidy = prep.clean(raw, LABELS)
    assert not validate.check_no_missing(tidy)["ok"]


def test_validation_detects_negative_value():
    tidy = prep.clean(make_raw([row("2024-03", -5)]), LABELS)
    assert not validate.check_non_negative(tidy)["ok"]


def test_validation_departments_must_sum_to_france():
    rows = [row("2024-03", 100),                                        # France
            row("2024-03", 60, geo="01", level="DEP"),
            row("2024-03", 30, geo="02", level="DEP")]                  # 90 != 100
    tidy = prep.clean(make_raw(rows), LABELS)
    assert not validate.check_departments_sum_to_france(tidy)["ok"]


def test_same_code_for_region_and_departement_gets_the_right_label():
    rows = [row("2024-03", 10, geo="75", level="DEP"),
            row("2024-03", 20, geo="75", level="REG")]
    tidy = prep.clean(make_raw(rows), LABELS).set_index("niveau")
    assert tidy.loc["DEP", "lieu"] == "Paris"
    assert tidy.loc["REG", "lieu"] == "Nouvelle-Aquitaine"


def test_validation_detects_wrong_departement_name(tmp_path):
    geo = tmp_path / "geo.json"
    geo.write_text('{"features":[{"properties":{"code":"75","nom":"Paris"}}]}', encoding="utf-8")
    good = prep.clean(make_raw([row("2024-03", 10, geo="75", level="DEP")]), LABELS)
    assert validate.check_geo_names(good, geo)["ok"]
    bad = good.assign(lieu="Nouvelle-Aquitaine")
    assert not validate.check_geo_names(bad, geo)["ok"]


def test_monthly_trend_keeps_only_seasonally_adjusted_france_series():
    rows = [row("2024-03", 100, cvs="Y"),                      # kept
            row("2024-03", 90, cvs="N"),                       # raw: dropped
            row("2024-03", 7, geo="01", level="DEP", cvs="Y")]  # département: dropped
    tidy = prep.clean(make_raw(rows), LABELS)
    trend = prep.monthly_trend(tidy)
    assert len(trend) == 1
    assert trend.loc[0, "creations"] == 100


def test_export_annual_uses_english_column_names():
    rows = [row(f"2019-{m:02d}", 10) for m in range(1, 13)]
    annual = prep.annual_table(prep.clean(make_raw(rows), LABELS))
    out = prep.export_annual(annual)
    assert list(out.columns) == list(prep.EXPORT_COLUMNS.values())
    assert out.loc[0, "creations"] == 120


def test_pipeline_summary_counts_rows_and_duplicates():
    raw = make_raw([row("2024-03", 100), row("2024-03", 100), row("2024-04", 50)])
    tidy = prep.clean(raw, LABELS)
    annual = prep.annual_table(tidy)
    s = prep.pipeline_summary(raw, tidy, annual)
    assert s["raw_rows"] == 3 and s["clean_rows"] == 2
    assert s["duplicates_removed"] == 1
    assert s["dropped_are_constant"]
    assert s["first_month"] == "2024-03" and s["last_month"] == "2024-04"
