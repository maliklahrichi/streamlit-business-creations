"""Project constants: paths, file names and labels."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"

# Raw files (downloaded by scripts/download_data.py)
SERIES_CSV = RAW_DIR / "DS_SIDE_CREA_ENT_SERIES_data.csv"
METADATA_CSV = RAW_DIR / "DS_SIDE_CREA_ENT_SERIES_metadata.csv"
GEOJSON = RAW_DIR / "departements.geojson"

# Files produced by scripts/build_data.py
TIDY_PARQUET = PROCESSED_DIR / "creations_tidy.parquet"
ANNUAL_PARQUET = PROCESSED_DIR / "creations_annual.parquet"
QUALITY_JSON = PROCESSED_DIR / "quality_report.json"
PIPELINE_JSON = PROCESSED_DIR / "pipeline_summary.json"

# Reference year for "base 100" indices
BASE_YEAR = 2019

# Series break: new "Guichet des formalités d'entreprises" (INSEE, 2023)
BREAK_YEAR = 2023

# Short English labels for legal forms (codes come from INSEE)
LEGAL_FORM_LABELS = {
    "_T": "Total",
    "MICRO": "Micro-entrepreneurs",
    "SOC": "Companies",
    "ENTIND_X_MICRO": "Sole proprietors (excl. micro)",
    "X_MICRO": "Excl. micro-entrepreneurs",
    "ENTIND": "Sole proprietors (incl. micro)",
}

# The three forms that add up exactly to the total
LEGAL_FORM_PARTS = ["MICRO", "SOC", "ENTIND_X_MICRO"]

# Geographic levels
GEO_LEVELS = {"FRANCE": "France", "REG": "Region", "DEP": "Département"}

# Overseas départements: not on the map (mainland France only)
OVERSEAS_DEPS = ["971", "972", "973", "974", "976"]

# Sectors at the A10 level (they add up exactly to the France total)
SECTOR_SHORT = {
    "BE": "Industry",
    "FZ": "Construction",
    "GI": "Trade, transport, accommodation & food",
    "JZ": "Information & communication",
    "KZ": "Finance & insurance",
    "LZ": "Real estate",
    "MN": "Professional, scientific, technical & support services",
    "OQ": "Public administration, education, health & social work",
    "RU": "Other services (arts, leisure, personal)",
}
