"""
+ creates a tiny hypertable
+ verifies the _timeseries_metadata row
+ prints the stored metadata as JSON
"""

from pathlib import Path
from datetime import timezone
import pandas as pd
from sqlalchemy import text

from ...api import create_table_from_file
from ...metadata import (
    ensure_meta_table,
    load_metadata,
    meta_engine,
)

TMP_TABLE = "tmp_1"


def main(csv) -> None:
    ensure_meta_table()

    # ── create hypertable + metadata row ─────────────────────────────────
    create_table_from_file(
        file_path=csv,
        table_name=TMP_TABLE,
    )

    # ── fetch & show metadata ────────────────────────────────────────────
    meta = load_metadata(TMP_TABLE)
    assert meta is not None, "Metadata row not found!"

    print("\n--- Metadata row ------------------------------")
    print(meta.to_json())

    # ── cleanup (drop table + meta row) ──────────────────────────────────
    eng = meta_engine()
    with eng.begin() as conn:
        conn.execute(text(f'DROP TABLE IF EXISTS "{TMP_TABLE}"'))
        conn.execute(
            text("DELETE FROM _timeseries_metadata WHERE table_name = :t"),
            {"t": TMP_TABLE},
        )
    print("\nCleanup done.")


if __name__ == "__main__":
    csv = Path("sample") / "energy_dummy_data.txt"
    assert csv.exists(), f"CSV file not found: {csv}"
    main(csv)
