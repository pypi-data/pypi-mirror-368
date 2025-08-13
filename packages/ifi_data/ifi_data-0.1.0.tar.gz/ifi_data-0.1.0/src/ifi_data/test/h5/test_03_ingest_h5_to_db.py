"""
Each run creates three fresh tables and LEAVES them in the database for
subsequent export tests.

Test coverage:
1. Creating a table from three representative datasets in low_freq.h5
     • /building6/elec/meter1   →  tmp_b6_meter1
     • /building5/elec/meter8   →  tmp_b5_meter8
     • /building3/elec/meter12  →  tmp_b3_meter12
2. Appending to an existing table with the same dataset (allow_duplicates=True).
3. Attempting to create/insert with a non-existent key (should raise).
4. Attempting to insert with no key at all (ambiguous file → should raise).
"""

from pathlib import Path
import pytest
from ...api import create_table_from_file, insert_data, insert_data_from_file, table_exists

TEST_H5 = Path(r"C:\Users\Moosa\Desktop\api\sample\low_freq.h5")

@pytest.fixture(scope="module")
def lowfreq_h5():
    """Return Path to the low-frequency test file."""
    return TEST_H5


TABLE_B6_M1   = "tmp_b6_meter1"
TABLE_B5_M8   = "tmp_b5_meter8"
TABLE_B3_M12  = "tmp_b3_meter12"
TABLE_FAKE    = "tmp_b99_m99" # does not exist

KEY_B6_M1     = "building6/elec/meter1"
KEY_B5_M8     = "building5/elec/meter8"
KEY_B3_M12    = "building3/elec/meter12"
KEY_FAKE      = "building1/elec/meter999" # does not exist


# -----------------------------------------------------------------------------
# 1–2 : Create one table per real dataset
# -----------------------------------------------------------------------------

def test_create_b6_meter1(lowfreq_h5):
    create_table_from_file(
        lowfreq_h5,
        TABLE_B6_M1,
        hdf_key=KEY_B6_M1,
        derive_stats=True,
    )
    assert table_exists(TABLE_B6_M1)

def test_create_b3_meter12(lowfreq_h5):
    create_table_from_file(
        lowfreq_h5,
        TABLE_B3_M12,
        hdf_key=KEY_B3_M12,
        derive_stats=True,
    )
    assert table_exists(TABLE_B3_M12)


# -----------------------------------------------------------------------------
# 3 : Append same dataset to existing table (allow_duplicates path)
# -----------------------------------------------------------------------------

def test_append_b3_meter12(lowfreq_h5):
    insert_data(
        lowfreq_h5,
        TABLE_B3_M12,
        hdf_key=KEY_B3_M12,
        allow_duplicates=True,
    )
    # table should still exist; row count check happens in export tests
    assert table_exists(TABLE_B3_M12)


# -----------------------------------------------------------------------------
# 4 : Create and insert data from file
# -----------------------------------------------------------------------------

def test_create_and_insert_b5_meter8(lowfreq_h5):
    insert_data_from_file(
        lowfreq_h5,
        TABLE_B5_M8,
        hdf_key=KEY_B5_M8,
        allow_duplicates=True,
    )
    
    assert table_exists(TABLE_B5_M8)

# -----------------------------------------------------------------------------
# 5 : Creating a table with a non-existent key should raise
# -----------------------------------------------------------------------------

def test_create_fake_key_raises(lowfreq_h5):
    with pytest.raises(Exception):
        create_table_from_file(
            lowfreq_h5,
            TABLE_FAKE,
            hdf_key=KEY_FAKE,
        )


# -----------------------------------------------------------------------------
# 6 : Inserting into an existing table with a non-existent key should raise
# -----------------------------------------------------------------------------

def test_insert_fake_key_raises(lowfreq_h5):
    with pytest.raises(Exception):
        insert_data(
            lowfreq_h5,
            TABLE_B6_M1,
            hdf_key=KEY_FAKE,
            allow_duplicates=True,
        )


# -----------------------------------------------------------------------------
# 7 : Inserting with *no* key should raise (file has many datasets ⇒ ambiguous)
# -----------------------------------------------------------------------------

def test_insert_no_key_raises(lowfreq_h5):
    with pytest.raises(Exception):
        insert_data(
            lowfreq_h5,
            TABLE_B6_M1,          # no key provided
            allow_duplicates=True,
        )
