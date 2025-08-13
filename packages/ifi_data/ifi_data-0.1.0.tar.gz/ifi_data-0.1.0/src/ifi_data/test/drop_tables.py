import os
import pandas as pd
from ..api import get_file_format, drop_table

# def test_h5():
#     fname = "test_file.h5"
#     pd.DataFrame({"a": [1, 2]}).to_hdf(fname, key="data")
#     assert get_file_format(fname) == "h5"
#     os.remove(fname)

# def test_csv():
#     fname = "test_file.csv"
#     pd.DataFrame({"a": [1, 2]}).to_csv(fname, index=False)
#     assert get_file_format(fname) == "csv"
#     os.remove(fname)

# def test_txt():
#     fname = "test_file.txt"
#     with open(fname, "w") as f:
#         f.write("hello world\n")
#     assert get_file_format(fname) == "csv"
#     os.remove(fname)

# if __name__ == "__main__":
#     test_h5()
#     test_csv()
#     test_txt()
#     print("All tests passed!")

# drop_table("test_table")
try:
    drop_table("tmp_b6_meter1")
except Exception as e:
    print(f"Error dropping tmp_b6_meter1: {e}")
try:
    drop_table("tmp_b3_meter12")
except Exception as e:
    print(f"Error dropping tmp_b3_meter12: {e}")
try:
    drop_table("tmp_b5_meter8")
except Exception as e:
    print(f"Error dropping tmp_b5_meter8: {e}")
print("Table dropped successfully.")
