"""
fastapi_app.py (FastAPI Interface Module)

Overview:
  This module provides a FastAPI-based RESTful interface for the TimescaleDB ingestion suite,
  enabling programmatic insertion of time-series data into hypertables. It integrates with
  `api.py` for core database operations and `config.py` for dynamic configuration, offering
  a lightweight API for automation, external services, or web-based clients.

  The API supports single-row insertions and health checks, with robust error handling
  for invalid table names, datetime issues, and database connectivity.

Key Features:
  - RESTful endpoints for:
      - Health checking of database connectivity
      - Single-row data insertion into TimescaleDB hypertables
  - Integrates with `api.py` for data insertion logic (e.g., `insert_single_row`)
  - Uses `config.py` for dynamic `.env`-based configuration of database and service endpoints
  - Validates input data via Pydantic models
  - Handles errors with descriptive HTTP responses
  - Supports dynamic host resolution to avoid `localhost` issues
  - Debug logging toggled via `DEBUG=true` in `.env` for troubleshooting

Endpoints:
  - GET /health:
      - Checks database connectivity using `pg_engine` from `api.py`
      - Returns status and database connection state
  - POST /insert/{table_name}:
      - Inserts a single row into the specified hypertable
      - Accepts JSON payload with column-value pairs (validated via Pydantic)
      - Leverages `insert_single_row` for auto-detection of datetime columns and parsing
      - Supports UTC timezone and duplicate checking

Core Components:
  - RowData (Pydantic Model): Validates JSON payload for row insertion
  - app (FastAPI): Main application instance with endpoint definitions
  - Integration with:
      - `api.py`: For database operations (`insert_single_row`, `pg_engine`, `table_exists`)
      - `config.py`: For configuration via `get_db_config`
      - `exceptions.py`: For error handling (TableNameError, DatetimeDetectionError, etc.)

Dependencies:
  - Standard Library: None
  - Third-Party: fastapi, pydantic, sqlalchemy (via `api.py`)
  - Internal: api, config, exceptions
  - Requires Python 3.10+ with type annotations
  - Configured via `.env` for database and service settings
"""

import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from sqlalchemy import text
from .api import insert_single_row, pg_engine
from .config import DBConfig

app = FastAPI(title="Timescale Ingestion Suite API")

# if running inside a container -> get pgsql connection info from env
cfg = DBConfig.from_env()
possible_pgsql_host = os.getenv("PGRST_HOST")
if possible_pgsql_host:
    cfg.host = possible_pgsql_host
    cfg.postgres_port = os.getenv("PGRST_PORT")


# Pydantic model for the JSON payload
class RowData(BaseModel):
    data: Dict[str, Any]


@app.get("/health")
async def health_check():
    try:
        # Use pg_engine() to get a SQLAlchemy engine
        engine = pg_engine(cfg)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.post("/insert/{table_name}")
async def insert_row(table_name: str, row: RowData):
    try:
        insert_single_row(
            table_name=table_name,
            row=row.data,
            datetime_col=None,  # Auto-detect
            format=None,  # Auto-parse
            timezone="UTC",
            allow_duplicates=False,
            cfg=cfg,
        )
        return {"status": "success", "message": f"Row inserted into {table_name}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
