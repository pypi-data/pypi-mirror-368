from pathlib import Path
import json
from ..api import create_table_from_file, insert_data_from_file

sample_file = "C:/Users/Moosa/Desktop/v3.5/sample/energy_dummy_data.csv"
table_name = "test_1"

# Test 1: Default config save
create_table_from_file(file_path=sample_file, table_name=table_name, config=True)

expected_path = Path("configs") / f"{table_name}.json"
assert expected_path.exists(), f"Expected config file not found at {expected_path}"

# Test 2: Custom config path
custom_path = Path("configs/custom_test_config.json")
insert_data_from_file(
    file_path=sample_file, table_name=table_name, config=True, config_path=custom_path
)

assert custom_path.exists(), f"Custom config file not found at {custom_path}"

# Test 3: Content verification
with expected_path.open() as f:
    cfg = json.load(f)
    assert "file_path" in cfg
    assert "delimiter" in cfg
    assert "datetime_col" in cfg
    assert "timezone" in cfg

print("test passed")
