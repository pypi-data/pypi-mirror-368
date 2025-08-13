"""
+ creates a hypertable
+ appends the SAME file again (with allow_duplicates=True) just to bump the
  row-count
+ prints the metadata row before and after the second insert
"""

from pathlib import Path
import json
from datetime import datetime
from dataclasses import asdict


from ...api import (
    create_table_from_file,
    insert_data_from_file,
    table_exists,
    drop_table,
)
from ...metadata import (
    ensure_meta_table,
    load_metadata,
)

TABLE = "tmp_2"  # temp table name
SAMPLE_CSV = Path("sample") / "rainfall_dummy_data.txt"  # <— adjust if needed


def pprint_meta(stage: str) -> None:
    meta = load_metadata(TABLE)
    print(f"\n--- Metadata ({stage}) ----------------")
    if meta:
        # asdict() works for any dataclass, even with slots=True
        print(json.dumps(asdict(meta), default=str, indent=2))
    else:
        print("No metadata row found!")


if __name__ == "__main__":
    assert SAMPLE_CSV.exists(), f"Sample file not found: {SAMPLE_CSV}"
    file_path = str(SAMPLE_CSV.resolve())

    ensure_meta_table()

    if table_exists(TABLE):
        drop_table(TABLE)

    create_table_from_file(
        file_path=file_path,
        table_name=TABLE,
    )
    pprint_meta("after CREATE")

    insert_data_from_file(
        file_path=file_path,
        table_name=TABLE,
    )
    pprint_meta("after second INSERT")

    print("\nCleanup done.  Script finished at", datetime.utcnow().isoformat(), "UTC")
