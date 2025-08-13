from pathlib import Path
import json
from ..api import create_table_from_file

sample_file = "C:/Users/Moosa/Desktop/v3.5/sample/energy_dummy_data.csv"
table_name = "test_create_table"
config_path = Path("configs") / f"{table_name}.json"

# Step 1: Run table creation with config save
create_table_from_file(file_path=sample_file, table_name=table_name, config=True)

# Step 2: Check if config file exists
assert config_path.exists(), f"Config file not found at {config_path}"

# Step 3: Verify contents
with config_path.open() as f:
    cfg = json.load(f)
    for key in ["file_path", "delimiter", "datetime_col", "timezone"]:
        assert key in cfg, f"Missing '{key}' in config"

print("test_create_table passed.")
