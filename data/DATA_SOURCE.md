# Data source

- **Dataset:** Créations d'entreprises – séries longues (business creations, long series)
- **Producer:** INSEE (SIDE system)
- **Portal:** data.gouv.fr — https://www.data.gouv.fr/datasets/creations-dentreprises-series-longues
- **Licence:** Open Licence 2.0 (Etalab)
- **Files used:** `DS_SIDE_CREA_ENT_SERIES_data.csv` (184,293 rows) and
  `DS_SIDE_CREA_ENT_SERIES_metadata.csv` (code → label dictionary)
- **Direct download:** https://www.data.gouv.fr/api/1/datasets/r/c1bafe65-e6a5-49f9-a5ce-bf75a6875ef5
- **How to get the raw files:** `python -m scripts.download_data` (cached: files already present are
  not downloaded again). The raw CSV is not committed (12.5 MB); the prepared Parquet files in
  `data/processed/` are committed so the app starts immediately.
- **Map outlines (complement):** `data/raw/departements.geojson`, from
  https://github.com/gregoiredavid/france-geojson (IGN Admin Express COG 2018, Open Licence).
