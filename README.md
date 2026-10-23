# Business creations in France: who drove the boom?

[![tests](https://github.com/maliklahrichi/streamlit-business-creations/actions/workflows/tests.yml/badge.svg)](https://github.com/maliklahrichi/streamlit-business-creations/actions/workflows/tests.yml)

Data-storytelling web app built with Streamlit (EFREI Paris – *Data Analysis & Visualization*,
Individual Project: Streamlit Dashboard 2026).

**Question:** between two chosen years, how did business creations in France change, which
legal forms, sectors and territories drove the increase, and is the momentum continuing?
**Intended audience:** local elected officials and economic-development officers.

**Answer (default view, 2019 → 2025):** creations rose from 864,557 to 1,165,795 (+35%);
micro-entrepreneurs explain 86% of the increase, while classic sole proprietorships fell by 26%;
96 of 96 mainland départements saw creations rise; and in the first 9 months of 2026 the
seasonally adjusted monthly level is +12% above 2025.

**Author:** Malik Lahrichi (student no. 20231512, group DE1) ·
[LinkedIn](https://www.linkedin.com/in/malik-lahrichi-585a18291/) ·
[GitHub](https://github.com/maliklahrichi) · Instructor: Prof. Mano Mathew

## Story told by the app
Opening: the answer in a few sentences and four KPIs, all tied to the sidebar filters.
Each section is titled by its finding, which updates with the filters:
- **Legal forms**: base-100 index by legal form, 2023 series break marked
- **Monthly momentum**: seasonally adjusted monthly trend up to September 2026, lockdown and 2023 break marked
- **Sectors**: change in creations by activity sector
- **Territories**: département map and rankings by % or by number of creations
- **Can you trust these numbers?**: quality checks, what was done to the data, CSV download, limitations
- **What to remember**: finding, implication, next steps

Every figure sits next to a short reading note (chart type, axes, units, key values) that also serves
as its text alternative.

## Design choices
- **Typography:** headlines in Archivo (wide, bold); text in Atkinson Hyperlegible Next, a typeface
  designed for legibility (its zero is slashed on purpose, to tell 0 from O). Both fonts are
  embedded in `static/fonts/` (SIL Open Font Licence), so the app sends no request to a third party.
- **Colour:** the interface is neutral (ink on white); a colour only ever means a legal form
  (amber = micro-entrepreneurs, blue = companies, brick = sole proprietors excl. micro, dashed ink = total).
  The three hues were checked with a colour-blind simulation on all pairs and have at least 3:1
  contrast on white. The direction of a change is shown by position, never by a second colour code.
- **Layout:** no coloured call-out boxes; figure on the left, reading note on the right; stacks on mobile.

## Quick start (easiest)
Requirement: **Python 3.11 or newer** (https://www.python.org/downloads/; on Windows tick "Add Python to PATH").
- **Windows**: double-click `run.bat`
- **Mac / Linux**: double-click `run.command` (or run `bash run.command` in a terminal)

The launcher creates a `.venv` environment, installs the packages and opens the app in your browser
(http://localhost:8501). To stop it, close the black window. The map needs an Internet connection
(Plotly loads its world base layer from cdn.plot.ly).

## Run manually
```bash
pip install -r requirements.txt   # Python 3.11 or newer
python -m scripts.download_data   # download raw data (cached)
python -m scripts.build_data      # clean, validate, write data/processed/
python -m pytest -q               # 24 tests, including headless runs of the app
streamlit run app.py
```
Prepared files (`data/processed/`) are included, so the app starts without downloading anything.
If they are missing, the app downloads and prepares the data on first launch.
The large raw CSV (12.5 MB) is not committed: `scripts/download_data.py` fetches it and skips
files already present (caching).

## Data
- **Dataset:** *Créations d'entreprises – séries longues* (business creations, long series), INSEE,
  published on [data.gouv.fr](https://www.data.gouv.fr/datasets/creations-dentreprises-series-longues).
  Open Licence 2.0 (Etalab). France, region and département levels; sectors and legal forms;
  monthly and quarterly; raw and seasonally adjusted. 184,293 rows, January 2000 to September 2026.
- **Base map:** mainland département outlines (simplified GeoJSON,
  [gregoiredavid/france-geojson](https://github.com/gregoiredavid/france-geojson)), derived from
  IGN Admin Express COG (2018 edition), Open Licence. See "Limitations".
- **Raw vs adjusted:** annual totals add up the 12 raw months (they match INSEE's official annual
  figures); the monthly trend uses the seasonally adjusted series so that months can be compared.
- Cleaning never alters values: it renames, converts types and dates, and adds labels.

## Structure
```
app.py              Streamlit app
utils/constants.py  paths, labels, constants
utils/prep.py       cleaning, annual totals, monthly trend, export
utils/validate.py   quality checks
utils/viz.py        charts (consistent style)
utils/style.py      injects assets/style.css (visual identity)
utils/io.py         cached data loading
utils/profile.py    identity block (name, links, course)
scripts/            download_data.py, build_data.py
tests/              pytest tests (preparation, checks, app)
data/processed/     Parquet files + quality and preparation reports, ready for the app
assets/             EFREI logo, style.css
static/fonts/       embedded fonts (WOFF2) and their licences
.streamlit/         theme (colours, fonts) and server settings
.github/workflows/  continuous integration (pytest on every push)
docs/STORYBOARD.md  storyboard of the app
```

## Quality checks (run by `build_data.py`)
Missing values, duplicates, negative values, missing months, sum of départements = France total,
micro + companies + sole proprietors (excl. micro) = total, département codes and names matching the map file.
Result: all checks pass on the data downloaded on 23/10/2026. A bug found along the way
(the same code designates a region and a département, 9 départements got a region's name) is
covered by a dedicated check and test.

## Limitations
- A business creation is not a job creation; micro-enterprises weigh heavily in the figures.
- Series break in 2023 (new business-formalities portal): read that year with caution.
- Annual figures are raw (not seasonally adjusted); 2026 excluded from annual comparisons
  (incomplete year) and shown only in the monthly trend, where INSEE still revises recent months.
- By département, only the total (and legal forms) is used, not the sector detail.
- Overseas départements are not on the map (shown in a table).
- Correlations, not causation. The dataset says nothing about the survival of these businesses.
  Aggregated data only, no personal data.
- The département GeoJSON comes from an external GitHub repository (IGN Admin Express tracing,
  Open Licence), not from one of the three approved portals. It is only a cartographic
  complement; all analysed figures come from the INSEE dataset on data.gouv.fr.

## Licences
Data: Open Licence 2.0. Map outlines: IGN Admin Express, Open Licence. Code: MIT (see `LICENSE`).
