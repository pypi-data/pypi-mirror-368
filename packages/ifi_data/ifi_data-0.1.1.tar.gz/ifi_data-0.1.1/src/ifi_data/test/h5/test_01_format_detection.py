"""
Tests for the get_file_format function.

This test suite checks that get_file_format correctly identifies the format of HDF5, CSV, and TXT files.
Each test creates a temporary file of the appropriate type and asserts that the detected format matches expectations.

- test_h5_detection: Checks detection of HDF5 files.
- test_csv_detection: Checks detection of CSV files.
- test_txt_detection: Checks detection of TXT files.
"""

from pathlib import Path
import pandas as pd
from ...api import get_file_format

def test_h5_detection(tmp_path):
    # Create a temporary HDF5 file and check detection
    f = tmp_path / "x.h5"
    pd.DataFrame({"x": [1]}).to_hdf(f, key="data")
    assert get_file_format(str(f)) == "h5"

def test_csv_detection(tmp_path):
    # Create a temporary CSV file and check detection
    f = tmp_path / "x.csv"
    pd.DataFrame({"x": [1]}).to_csv(f, index=False)
    assert get_file_format(str(f)) == "csv"

def test_txt_detection(tmp_path):
    # Create a temporary TXT file and check detection
    f = tmp_path / "x.txt"
    f.write_text("hello")
    assert get_file_format(str(f)) == "csv"