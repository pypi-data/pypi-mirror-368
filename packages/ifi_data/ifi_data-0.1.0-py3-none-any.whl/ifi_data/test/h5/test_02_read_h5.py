"""
Tests for the read_h5 function.

This test suite verifies that the read_h5 function correctly reads datasets from
the multi-key HDF5 file *low_freq.h5* and handles error cases.

Test coverage:
- Reading three representative datasets (one per building) and checking row count.
- Ensuring that calling read_h5 with no key raises an error because the file
  contains many datasets and none match the filename stem.

Dataset keys sampled in these tests
    /building6/elec/meter1
    /building5/elec/meter8
    /building3/elec/meter12
Each dataset in low_freq.h5 holds exactly two rows.
"""

from pathlib import Path
import pytest
import pandas as pd
from ...api import read_h5 

TEST_H5 = Path(r"C:\Users\Moosa\Desktop\api\sample\low_freq.h5")

@pytest.fixture(scope="module")
def lowfreq_h5():
    """Return Path to the low-frequency test file."""
    return TEST_H5


# ---------- Test reads ----------

def test_read_building6_meter1(lowfreq_h5):
    df = read_h5(lowfreq_h5, key="building6/elec/meter1")
    assert isinstance(df, pd.DataFrame)
    assert df.shape[0] == 887457               # every dataset has 887457 rows


def test_read_building5_meter8(lowfreq_h5):
    df = read_h5(lowfreq_h5, key="building5/elec/meter8")
    assert df.shape[0] == 80417


def test_read_building3_meter12(lowfreq_h5):
    df = read_h5(lowfreq_h5, key="building3/elec/meter12")
    assert df.shape[0] == 404107


# ---------- error case: no key given ----------

def test_read_no_key_raises(lowfreq_h5):
    # stem name is low_freq, which doesnt exist = error!
    with pytest.raises(ValueError):       # read_h5 raises ValueError
        read_h5(lowfreq_h5)
