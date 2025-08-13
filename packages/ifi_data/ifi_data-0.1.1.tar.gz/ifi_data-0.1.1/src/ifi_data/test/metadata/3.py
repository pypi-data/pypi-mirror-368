"""
+ creates a hypertable from an existing sample file
+ appends the SAME file again (with allow_duplicates=True) just to bump the
  row-count - no extra temp CSVs, no pytest, no fixtures
+ prints the metadata row before and after the second insert
+ Adds Units
"""

from pathlib import Path
import json
from datetime import datetime, timezone
from dataclasses import asdict

import pytest

from ...api import (
    create_table_from_file,
    insert_data_from_file,
    table_exists,
    drop_table,
)
from ...metadata import (
    ensure_meta_table,
    load_metadata,
    meta_engine,
    TableMetadata,
    save_metadata,
)

TABLE = "tmp_meta_3"  # temp table name
SAMPLE_CSV = Path("sample") / "rainfall_dummy_data.txt"  # <— adjust if needed


def pprint_meta(stage: str) -> None:
    meta = load_metadata(TABLE)
    print(f"\n--- Metadata ({stage}) ----------------")
    if meta:
        # asdict() works for any dataclass, even with slots=True
        print(json.dumps(asdict(meta), default=str, indent=2))
    else:
        print("No metadata row found!")


def test_meta_case3():
    assert SAMPLE_CSV.exists(), f"Sample file not found: {SAMPLE_CSV}"
    file_path = str(SAMPLE_CSV.resolve())

    ensure_meta_table()

    if table_exists(TABLE):
        print(f"Table {TABLE} already exists. Dropping it.")
        drop_table(TABLE)

    create_table_from_file(
        file_path=file_path,
        table_name=TABLE,
        units={
            "Rainfall": "cm",  # millimeters for rainfall
            "Date-Time": "Eurpe/Berlin",  # timezone for datetime
            "Sensor_ID": None,  # no units for ID
        },
    )

    meta = load_metadata(TABLE)
    assert meta is not None
    assert meta.table_name == TABLE
    assert meta.units["Rainfall"] == "cm"
    assert meta.units["Date-Time"] == "Eurpe/Berlin"

    # Update metadata with units after creation
    meta.units = {
        "Rainfall": "mm",
        "Date-Time": "UTC",
        "Sensor_ID": None,
    }
    save_metadata(meta)
    assert meta.units["Rainfall"] == "mm"
    assert meta.units["Date-Time"] == "UTC"

    pprint_meta("after CREATE")

    insert_data_from_file(
        file_path=file_path,
        table_name=TABLE,
    )
    pprint_meta("after INSERT")

    insert_data_from_file(
        file_path=file_path,
        table_name=TABLE,
        allow_duplicates=True,
    )
    pprint_meta("after 2. INSERT")

    print("\nCleanup done.  finished at", datetime.now(timezone.utc).isoformat(), "UTC")


if __name__ == "__main__":
    test_meta_case3()
