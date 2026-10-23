"""Headless test of the Streamlit app (no browser needed)."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(scope="module")
def app():
    return AppTest.from_file(APP, default_timeout=180).run()


def test_app_runs_without_error(app):
    assert not app.exception


def test_kpi_header_is_displayed(app):
    labels = [m.label for m in app.metric]
    assert any(label.startswith("Creations in") for label in labels)
    assert "Micro-entrepreneur share" in labels


def test_changing_the_period_changes_the_kpis():
    at = AppTest.from_file(APP, default_timeout=180).run()
    before = at.metric[0].value
    at.select_slider[0].set_value((2021, 2024)).run()
    assert not at.exception
    assert at.metric[0].value != before


def test_ranking_can_switch_to_absolute_numbers():
    at = AppTest.from_file(APP, default_timeout=180).run()
    at.radio[1].set_value("Change (number of creations)").run()
    assert not at.exception


@pytest.mark.parametrize("form", ["Total", "Micro-entrepreneurs", "Companies"])
@pytest.mark.parametrize("period", [(2019, 2025), (2019, 2020), (2012, 2025)])
def test_every_legal_form_and_period_renders(form, period):
    """Includes periods where some départements decrease (diverging colour scale)."""
    at = AppTest.from_file(APP, default_timeout=180).run()
    at.select_slider[0].set_value(period)
    at.selectbox[0].set_value(form)
    at.run()
    assert not at.exception
