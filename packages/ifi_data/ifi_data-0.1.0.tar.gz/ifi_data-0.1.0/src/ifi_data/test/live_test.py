# live_test.py

from pathlib import Path
from ..api import create_table_from_file, insert_single_row, query_table_metadata
import random
from datetime import datetime
from typing import Iterator, Dict


## Generate the data
def single_sensor(sensor_id: str, n: int) -> Iterator[Dict]:
    """
    Yield `n` readings for one sensor:
      - Date-Time (string)
      - Sensor_ID (string)
      - Cloud_Coverage (float 0–100)
    """
    for _ in range(n):
        ts = datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S.%f")[:-3]
        yield {
            "Date-Time": ts,
            "Sensor_ID": sensor_id,
            "Cloud_Coverage": round(random.uniform(0, 100), 2),
        }


def multi_sensor(sensor_ids: list[str], n: int) -> Iterator[Dict]:
    """
    Over `n` ticks, yield one reading per sensor.
    Total rows = len(sensor_ids) × n.
    """
    for _ in range(n):
        for sid in sensor_ids:
            yield from single_sensor(sid, 1)


# Sample for the table
FILE = "C:/Users/Moosa/Desktop/api-main/V5/sample/cloud_coverage.txt"
TABLE = "cloud_data_multi"


def setup_table():
    create_table_from_file(file_path=str(FILE), table_name=TABLE, config=False)


def run_single():
    print("→ Single-sensor stream")
    total = 0
    for row in single_sensor("camera_1", 10):
        insert_single_row(
            table_name=TABLE, row=row, timezone="UTC", allow_duplicates=False
        )
        total += 1
        meta = query_table_metadata(TABLE)
        print(f"{total:2d} rows in table now")


def run_multi():
    print("→ 5-sensor stream")
    sensors = [f"camera_{i}" for i in range(1, 6)]
    total = 0
    for row in multi_sensor(sensors, 5):
        insert_single_row(
            table_name=TABLE, row=row, timezone="UTC", allow_duplicates=False
        )
        total += 1
        meta = query_table_metadata(TABLE)
        print(f"{total:2d} rows in table now")


if __name__ == "__main__":
    setup_table()
    choice = input("Mode [1=single, 2=multi]? ").strip()
    (run_single if choice == "1" else run_multi)()
