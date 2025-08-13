from pathlib import Path
import json
from ..api import create_table_from_file, insert_data

sample_file = "C:/Users/Moosa/Desktop/v3.5/sample/energy_dummy_data.csv"
table_name = "test_insert_data"

# # ensure table exists
# create_table_from_file(
#     file_path=sample_file,
#     table_name=table_name,
#     config=False  # Skip saving config in this step
# )

# Insert data using new wrapper
insert_data(file_path=sample_file, table_name=table_name, config=True)

print("test_insert_data passed.")
