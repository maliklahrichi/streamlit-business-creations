"""Download the raw data into data/raw/ (with caching: files already present
are not downloaded again).

Usage: python -m scripts.download_data

NOTE: this script could not be tested from the development environment
(limited network access). If a download fails, download the files manually
from the links below and place them in data/raw/.
"""
import io
import sys
import urllib.request
import zipfile

from utils import constants as C

SERIES_URL = "https://www.data.gouv.fr/api/1/datasets/r/c1bafe65-e6a5-49f9-a5ce-bf75a6875ef5"
GEOJSON_URL = ("https://raw.githubusercontent.com/gregoiredavid/france-geojson/"
               "master/departements-version-simplifiee.geojson")


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "streamlit-creations-entreprises"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def main() -> int:
    C.RAW_DIR.mkdir(parents=True, exist_ok=True)

    if C.SERIES_CSV.exists() and C.METADATA_CSV.exists():
        print("INSEE series: already present, nothing to do.")
    else:
        print("Downloading the INSEE series (data.gouv.fr)...")
        content = fetch(SERIES_URL)
        if content[:2] == b"PK":  # it is a zip file
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                z.extractall(C.RAW_DIR)
        else:
            C.SERIES_CSV.write_bytes(content)

    if C.GEOJSON.exists():
        print("Département outlines: already present, nothing to do.")
    else:
        print("Downloading the département outlines (GitHub)...")
        C.GEOJSON.write_bytes(fetch(GEOJSON_URL))

    missing = [p.name for p in (C.SERIES_CSV, C.METADATA_CSV, C.GEOJSON) if not p.exists()]
    if missing:
        print("Missing files:", missing)
        return 1
    print("OK: raw data ready in", C.RAW_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
