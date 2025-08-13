"""
Exports the two populated tables produced in test_ingest_h5.py:

    tmp_b3_meter12   -- 1 x dataset rows   (append was run)
    tmp_b5_meter8    -- 1 x dataset rows   (single insert)

Checks performed:
1. HDF5 export (mode="w")   — dataset name = table name
2. TXT  export
3. Second HDF5 export in append mode (mode="a", key="backup") for tmp_b3_meter12
"""

from pathlib import Path
import pandas as pd
from ...api import retrieve_data, OutputFormat, read_h5

# ----------------------------------------------------------------------
TEST_H5    = Path(r"C:\Users\Moosa\Desktop\api\sample\low_freq.h5")
EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)

TABLES = {
    "tmp_b3_meter12": "building3/elec/meter12",
    "tmp_b5_meter8" : "building5/elec/meter8",
}

def _expected_rows(hdf_key: str, multiplier: int = 1) -> int:
    """Utility: count rows in the original dataset, apply multiplier."""
    df = read_h5(TEST_H5, key=hdf_key)
    return df.shape[0] * multiplier


# ----------------------------------------------------------------------
# 1 & 2 – fresh exports for both tables
# ----------------------------------------------------------------------

def test_export_tables_to_h5_and_txt():
    for tbl, key in TABLES.items():
        mult = 1 if tbl == "tmp_b3_meter12" else 1
        expected = _expected_rows(key, mult)

        # ---- HDF5 export ----
        h5_path = EXPORT_DIR / f"{tbl}.h5"
        retrieve_data(
            table_name   = tbl,
            output_format= OutputFormat.HDF5,
            output_path  = h5_path,
            hdf_mode     = "w",
        )
        df_h5 = pd.read_hdf(h5_path, key=tbl)
        assert df_h5.shape[0] == expected

        # ---- TXT export ----
        txt_path = EXPORT_DIR / f"{tbl}.txt"
        retrieve_data(
            table_name   = tbl,
            output_format= OutputFormat.TXT,
            output_path  = txt_path,
        )
        df_txt = pd.read_csv(txt_path, sep="\t")
        assert df_txt.shape[0] == expected


# ----------------------------------------------------------------------
# 3 – append second dataset to tmp_b3_meter12.h5 only
# ----------------------------------------------------------------------

def test_append_backup_dataset_to_b3():
    tbl      = "tmp_b3_meter12"
    key      = TABLES[tbl]
    expected = _expected_rows(key)

    h5_path = EXPORT_DIR / f"{tbl}.h5"             # same file from test 1

    retrieve_data(
        table_name   = tbl,
        output_format= OutputFormat.HDF5,
        output_path  = h5_path,
        hdf_mode     = "a",
        hdf_key      = "backup",
    )

    with pd.HDFStore(h5_path, mode="r") as store:
        assert f"/{tbl}" in store.keys()
        assert "/backup" in store.keys()
        # both datasets should have identical row counts
        assert store[tbl].shape[0] == expected
        assert store["/backup"].shape[0] == expected
