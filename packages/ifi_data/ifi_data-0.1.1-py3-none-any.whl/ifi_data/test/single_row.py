# tests/test_insert_single_row.py

from pathlib import Path

from ..api import (
    create_table_from_file,
    insert_single_row,
    read_csv,
    detect_datetime_column,
    query_table_metadata,
    table_exists,
    drop_table,
)


def test():
    # --- Configuration for this test ---
    sample_file_path = Path("sample") / "energy_dummy_data.csv"
    assert sample_file_path.exists()
    sample_file = str(sample_file_path)

    table_name = "single_row"

    # Clenup: remove the table if it exists
    if table_exists(table_name):
        drop_table(table_name)

    # 1) create hyper table
    create_table_from_file(
        file_path=sample_file,
        table_name=table_name,
        config=False,  # we don't need a config file here
    )

    # 2) Read and detect datetime (Primary Key) column
    df = read_csv(sample_file, delimiter=None)
    datetime_col = detect_datetime_column(df)

    # 3) verify table empty
    meta0 = query_table_metadata(table_name, datetime_col)
    assert meta0["row_count"] == 0, f"Expected 0 rows, found {meta0['row_count']}"

    # 4) prepare one row from the CSV file
    row0 = df.iloc[1].to_dict()

    # 5) Insert that single row
    insert_single_row(
        table_name=table_name,
        row=row0,
        datetime_col=datetime_col,
        format=None,
        timezone="UTC",
        allow_duplicates=False,
    )

    # 6) After first insert, we expect exactly 1 row
    meta1 = query_table_metadata(table_name, datetime_col)
    assert meta1["row_count"] == 1, (
        f"Expected 1 row after insert, found {meta1['row_count']}"
    )

    # 7) Try inserting the *same* row again (duplicate timestamp) → should be skipped
    insert_single_row(
        table_name=table_name,
        row=row0,
        datetime_col=datetime_col,
        format=None,
        timezone="UTC",
        allow_duplicates=False,
    )

    # 8) Define one single row as a Python dict (matching your CSV schema)
    row1 = {
        "Date-Time": "18-05-2025 00:43:11",
        "Sensor_ID": "energy_sensor_1",
        "Voltage": 222.06,
        "Current": 2.04,
        "Power": 1610.57,
    }

    # 9) Insert the new row
    insert_single_row(
        table_name=table_name,
        row=row1,
        datetime_col=datetime_col,
        format=None,
        timezone="UTC",
        allow_duplicates=False,
    )

    # 10) Confirm the row count (+1)
    meta2 = query_table_metadata(table_name, datetime_col)
    assert meta2["row_count"] == 2, (
        f"Duplicate row was inserted unexpectedly; row_count={meta2['row_count']}"
    )

    print("test_insert_single_row passed")
