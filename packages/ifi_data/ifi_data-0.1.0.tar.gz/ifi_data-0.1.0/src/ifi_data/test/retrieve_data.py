from pathlib import Path
import json
from ..api import  retrieve_data, OutputFormat


table_name = "wall_plugs"

# # Test 1: retrieve data with 100 rows limit and output format as XLSX
# retrieve_data(table_name=table_name, row_limit=100, output_format="txt")

# # Test 2: retrieve data with 1000 rows limit and output format as CSV
# retrieve_data(table_name=table_name, row_limit=1000, output_format="csv")

# # Test 3: retrieve data with 10000 rows limit and output format as JSON and custom path
# retrieve_data(
#     table_name=table_name,
#     row_limit=10000,
#     output_format="json",
#     output_path=Path("export/temp.json"),
# )


# Test 4: retrieve data with all rows and output format as txt and cutsom path
retrieve_data(
    table_name=table_name, output_format="txt", output_path=Path("export/wall_plugs.txt")
)

# Test 5: retrieve data with all rows and output format as txt and cutsom path
retrieve_data(
    table_name=table_name, output_format=OutputFormat.TXT, output_path=Path("export/wall_plugg.txt")
)
