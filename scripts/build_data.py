"""Build the app-ready files from the raw data.

Usage (from the project root):
    python -m scripts.build_data

Steps: load -> clean -> validate -> compute annual totals -> save.
The script exits with an error if a quality check fails
(useful in GitHub CI to detect a change in the source data).
"""
import json
import sys

from utils import constants as C
from utils import prep, validate


def main() -> int:
    C.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("1/4 Loading raw data...")
    raw = prep.load_raw()
    labels = prep.load_labels()

    print(f"2/4 Cleaning ({len(raw):,} rows)...")
    tidy = prep.clean(raw, labels)

    print("3/4 Quality checks...")
    results = validate.run_all(tidy)
    for r in results:
        print(f"   [{'OK' if r['ok'] else 'FAIL'}] {r['controle']} -- {r['detail']}")

    print("4/4 Annual totals and saving...")
    annual = prep.annual_table(tidy)
    tidy.to_parquet(C.TIDY_PARQUET, index=False)
    annual.to_parquet(C.ANNUAL_PARQUET, index=False)
    with open(C.QUALITY_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    with open(C.PIPELINE_JSON, "w", encoding="utf-8") as f:
        json.dump(prep.pipeline_summary(raw, tidy, annual), f, ensure_ascii=False, indent=2)

    print(f"Done: {len(tidy):,} clean rows, {len(annual):,} annual rows.")
    failed = [r for r in results if not r["ok"]]
    if failed:
        print(f"WARNING: {len(failed)} check(s) failed.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
