"""
api.py (Core API Module)

Overview:
  This module provides a non-interactive, programmatic API for ingesting, managing, and retrieving time-series data in TimescaleDB, designed for use in CLI tools, automation scripts, and data pipelines. It integrates with:

    - TimescaleDB for hypertable creation and data insertion via PostgreSQL COPY
    - PostgREST for efficient data retrieval
    - Grafana for generating visualization URLs
    - `.env` for dynamic configuration of database and service credentials

  It serves as the backend for the interactive CLI (`cli.py`), providing robust, reusable functions for data ingestion, schema inference, metadata management, and export.

Key Features:
  - Dynamic configuration via `.env`, eliminating reliance on cached `config.toml`
  - File ingestion support for CSV, TXT, and HDF5 formats
  - Automatic detection with optional overrides:
      - File delimiters (CSV/TXT: e.g., ',', ';', '\\t')
      - HDF5 dataset keys (auto-selects filename stem, '/data', or sole dataset)
      - Datetime columns and formats
      - SQL schema from pandas DataFrame dtypes
  - Table management:
      - Creates PostgreSQL tables and converts them to TimescaleDB hypertables
      - Infers and validates schemas
      - Supports per-table JSON config files for reuse
  - Data insertion:
      - Bulk inserts via PostgreSQL COPY for high performance
      - Single-row inserts for live feeds (e.g., sensor data)
      - Duplicate time-range detection and prevention
  - Metadata system:
      - Automatically tracks table metadata (row count, time range, sampling period, schema)
      - Supports metadata updates, retrieval, and validation
      - Centralized in `_timeseries_metadata` table for CLI and API consistency
  - Data retrieval:
      - Fetches data via PostgREST with optional row limits
      - Exports to CSV, JSON, XLSX, TXT, or HDF5 formats
      - Auto-generates output paths or accepts user-defined paths
  - Grafana integration:
      - Generates Grafana Explore URLs for ad-hoc visualization
      - Auto-infers datetime, value, and label columns

Core API Functions:
  - File Reading & Parsing:
      - read_csv(file_path, delimiter): Reads CSV/TXT files into a pandas DataFrame
      - read_h5(file_path, key): Reads HDF5 files, normalizing DatetimeIndex and multi-index columns
      - detect_datetime_column(df, datetime_col): Auto-detects or validates datetime column
      - parse_datetime_column(df, datetime_col, format, timezone): Parses and localizes timestamps
      - infer_schema(df): Maps pandas dtypes to PostgreSQL types
      - get_file_time_range(df, datetime_col): Extracts min/max timestamps
  - Table Management:
      - create_table_df(df, schema_map, table_name, datetime_col, chunk_days): Creates hypertables
      - list_table_columns(table_name): Lists column names
      - get_table_schema(table_name): Retrieves column names and SQL types
  - Data Insertion:
      - insert_data_df(df, table_name): Inserts DataFrame via COPY
      - insert_single_row(table_name, row_dict, ...): Inserts a single row
      - check_duplicates(table_name, datetime_col, file_min, file_max): Checks for time-range overlaps
  - Metadata Management:
      - query_table_metadata(table_name, datetime_col): Retrieves table stats (row count, time range, etc.)
      - _refresh_or_create_metadata(df, table_name, datetime_col, schema): Updates or creates metadata
      - save_metadata(meta), load_metadata(table_name), etc.: Metadata CRUD operations
  - Data Retrieval:
      - get_data(table_name, row_limit): Fetches raw JSON via PostgREST
      - retrieve_data(table_name, row_limit, output_format, output_path, hdf_key, hdf_mode): Exports to file
      - write_h5(df, file_path, key, mode): Saves DataFrame to HDF5
  - Grafana Integration:
      - get_grafana_url(table_name, value_col, ...): Builds Grafana Explore URL
      - infer_plot_columns(table_name, max_metric_cardinality): Infers columns for visualization
  - Utilities:
      - validate_table_name(name): Ensures PostgreSQL-compliant table names
      - table_exists(table_name): Checks if a table exists
      - drop_table(table_name): Drops a table and its metadata
      - save_config_file(cfg, table_name, path): Saves JSON config for reuse

Wrapper Functions:
  - create_table_from_row(row: dict, table_name, ...): Creates a table from a single row
  - create_table_from_file(file_path, table_name, ...): Full pipeline for table creation
  - insert_data(file_path, table_name, ...): Inserts data into existing tables
  - insert_data_from_file(file_path, table_name, ...): Creates table and inserts data

Dependencies & Environment:
  - Standard Library: os, re, json, logging, pathlib, urllib.parse, typing
  - Third-Party: pandas, requests, python-dotenv, SQLAlchemy, dateutil
  - Internal: exceptions, metadata, config modules
  - Requires Python 3.10+ with type hints
  - Configured via `.env` for DB, PostgREST, and Grafana settings
  - Dynamic host resolution to avoid `localhost` issues (Issue 4 fix)
  - Debug logging toggled via `DEBUG=true` in `.env` (Issue 3 fix)
  - Terminal- and automation-friendly with minimal dependencies
"""

# -----------------------------------------------------------------------------
# Imports & Dependencies
# -----------------------------------------------------------------------------

# === Standard Library ===
import os
import re
import json
import sys
from io import StringIO
from enum import Enum
from pathlib import Path
from urllib.parse import quote
from typing import Dict, Any
import datetime

# === Third-Party Libraries ===
import pandas as pd
from dateutil.parser import parse
from sqlalchemy import create_engine, text, Engine
from sqlalchemy.exc import OperationalError

# === Internal Modules ===
from .exceptions import (
    InvalidDelimiterError,
    DatetimeDetectionError,
    DatetimeParsingError,
    TableNameError,
)
from .metadata import (
    TableMetadata,
    load_metadata,
    save_metadata,
    drop_metadata,
    compute_sampling_period,
    ensure_meta_table,
    pretty_print_metadata,
    Units,
)
from .config import DBConfig, get_db_config, get_config_file_path
from .exceptions import DatabaseUnavailableError
from .logger import logger

# re-exports (not necessary but to make the usage explicit)
load_metadata = load_metadata
get_config_file_path = get_config_file_path

# -----------------------------------------------------------------------
# Database Engine (Reusable SQLAlchemy Connector)
# -----------------------------------------------------------------------


def pg_engine(
    cfg: "DBConfig | None" = None,
    *,
    probe: bool = True,  # set False only if you really want to skip the ping
    quiet: bool = False,  # suppress the print & exit (rarely needed)
) -> Engine:
    """
    Return a SQLAlchemy engine and (by default) verify the database is reachable.

    If the TCP connection fails, raise `DatabaseUnavailableError` with a concise
    message instead of the long SQLAlchemy traceback.

    Parameters
    ----------
    cfg     : DBConfig | None
        Explicit config (else resolved via get_db_config()).
    probe  : bool  (default True)
        Perform a quick connect/close to ensure the server is up.  Set False if
        you need to create an engine even when the DB may be offline (rare).
    """
    cfg = cfg or get_db_config()
    eng = create_engine(cfg.pg_dsn(), pool_pre_ping=True)

    if probe:
        try:
            with eng.connect():
                pass
        except OperationalError:
            msg = (
                "\nERROR: Database server is unreachable.\n"
                f"  Host: {cfg.host}\n"
                f"  Port: {cfg.postgres_port}\n"
                "Please check that Timescale/Postgres is running "
                "and network‑reachable.\n"
            )
            if quiet:
                # give calling code a chance to handle it
                raise DatabaseUnavailableError(msg) from None
            # otherwise: show message and exit (no traceback)
            print(msg, file=sys.stderr)
            sys.exit(1)

    # Metadata Table Bootstrapping
    try:
        ensure_meta_table(cfg=cfg)
    except Exception as exc:
        logger.error("Could not verify metadata table at import-time: %s", exc)

    return eng


def list_tables(
    *, include_meta: bool = False, cfg: DBConfig | None = None
) -> list[str]:
    """
    Returns a list of public-schema tables.

    Parameters:
    include_meta : bool
        * False (default) – hides the internal “_timeseries_metadata” table
        * True            – return *all* tables, including the registry
    """

    query = text(f"""
        SELECT table_name
          FROM information_schema.tables
         WHERE table_schema = 'public'
           AND table_type   = 'BASE TABLE'
           {"AND table_name <> '_timeseries_metadata'" if not include_meta else ""}
         ORDER BY table_name;
    """)

    with pg_engine(cfg=cfg).connect() as conn:
        return [r[0] for r in conn.execute(query)]


# -----------------------------------------------------------------------
# File-format detection
# -----------------------------------------------------------------------


def get_file_format(file_path: str) -> str:
    """
    Returns 'csv' or 'h5' based on the file extension.

    * .csv  .txt  -> 'csv'
    * .h5   .hdf  .hdf5 -> 'h5'

    Args:
        file_path: Path to the file.

    Returns:
        str: File format ('csv' or 'h5').

    Raises:
        ValueError: If the file extension is unsupported.
    """

    ext = Path(file_path).suffix.lower()
    if ext in (".csv", ".txt"):
        return "csv"
    if ext in (".h5", ".hdf", ".hdf5"):
        return "h5"
    raise ValueError(
        f"Unsupported file extension '{ext}'. "
        "Currently accepted: .csv, .txt, .h5, .hdf, .hdf5"
    )


# -----------------------------------------------------------------------
# Grafana Integration: Plot Column Inference & URL Builder
# -----------------------------------------------------------------------


def infer_plot_columns(
    table_name: str,
    max_metric_cardinality: int = 7,
    cfg: DBConfig | None = None,
) -> tuple[str, str, str | None]:
    """
    Infers columns for plotting from table metadata or schema.

    Selects:
      - Datetime column (TIMESTAMPTZ)
      - Numeric value column (integer or double precision)
      - Label column (text with ≤ `max_metric_cardinality` unique values, if any)

    Args:
        table_name: Name of the TimescaleDB table.
        max_metric_cardinality: Maximum unique values for a text column to be considered a label (default: 7).

    Returns:
        tuple[str, str, str | None]: (datetime_col, value_col, label_col), where label_col may be None.

    Raises:
        RuntimeError: If suitable datetime or value columns are not found.
    """

    # === try metadata first ===
    meta = load_metadata(table_name, cfg=cfg)
    if meta:
        datetime_col = meta.datetime_col
        numeric_cols = [
            c for c, t in meta.schema.items() if t in ("integer", "double precision")
        ]
        value_col = numeric_cols[0] if numeric_cols else None

        # simple heuristic for label: first TEXT column ≤ max_metric_cardinality
        label_col = None
        for col, dtype in meta.schema.items():
            if dtype == "text":
                uniq_sql = text(f'SELECT COUNT(DISTINCT "{col}") FROM "{table_name}"')
                with pg_engine(cfg=cfg).connect() as conn:
                    if conn.execute(uniq_sql).scalar() <= max_metric_cardinality:
                        label_col = col
                        break

        if datetime_col and value_col:
            return datetime_col, value_col, label_col

    # === fallback to original information_schema logic ===
    engine = pg_engine(cfg=cfg)
    sql = text("""
        SELECT column_name, data_type
          FROM information_schema.columns
         WHERE table_name = :tbl
         ORDER BY ordinal_position;
    """)

    datetime_col = value_col = label_col = None
    text_candidates = []

    with engine.connect() as conn:
        rows = conn.execute(sql, {"tbl": table_name}).fetchall()

        for col, dtype in rows:
            if dtype == "timestamp with time zone" and not datetime_col:
                datetime_col = col
            elif dtype in ("integer", "double precision") and not value_col:
                value_col = col
            elif dtype == "text":
                text_candidates.append(col)

        for col in text_candidates:
            count_sql = text(f'SELECT COUNT(DISTINCT "{col}") FROM "{table_name}"')
            if conn.execute(count_sql).scalar() <= max_metric_cardinality:
                label_col = col
                break

    if not datetime_col or not value_col:
        raise RuntimeError(
            f"Could not find suitable time/value columns in '{table_name}'"
        )

    return datetime_col, value_col, label_col


def get_grafana_url(
    table_name: str,
    value_col: str,
    from_time=None,
    to_time=None,
    limit: int = 1000,
    datasource: str = "TimescaleDB",
    org_id: int = 1,
    cfg: DBConfig | None = None,
) -> str:
    """
    Constructs a Grafana Explore URL for a single numeric column against the time column.

    Parameters:
      table_name  : Name of the hypertable.
      value_col   : Numeric column to plot on the Y-axis.
      from_time   : Start of time range (datetime or ISO string). If None, auto-uses min time in table.
      to_time     : End of time range. If None, auto-uses max time in table.
      limit       : Max rows to include in the query (default 1000).
      datasource  : Grafana datasource name (default "TimescaleDB").
      org_id      : Grafana organization ID (default 1).

    Returns:
      A full Grafana Explore URL string with the encoded SQL query.
    """
    # get config parameters
    cfg = cfg or get_db_config()

    # set the Grafana base URL
    GRAFANA_BASE_URL = cfg.grafana_base_url

    datetime_col, _, _ = infer_plot_columns(table_name, cfg=cfg)
    schema = get_table_schema(table_name, cfg=cfg)
    if value_col not in schema or schema[value_col] not in (
        "integer",
        "double precision",
    ):
        raise RuntimeError(
            f"Column '{value_col}' is not a numeric column in '{table_name}'."
        )

    # Time bonds
    if from_time is None or to_time is None:
        meta = query_table_metadata(table_name, datetime_col, cfg=cfg)
        from_time = from_time or meta["min_time"]
        to_time = to_time or meta["max_time"]

    # Build query
    raw_sql = (
        f'SELECT "{datetime_col}" AS time, "{value_col}" AS value '
        f'FROM "{table_name}" '
        f"WHERE \"{datetime_col}\" BETWEEN '{from_time}' AND '{to_time}' "
        f'ORDER BY "{datetime_col}" '
        f"LIMIT {limit};"
    )

    # The URL
    payload = {
        "datasource": datasource,
        "queries": [{"refId": value_col, "rawSql": raw_sql, "format": "time_series"}],
        "range": {"from": str(from_time), "to": str(to_time)},
    }
    encoded = quote(json.dumps(payload))
    return f"{GRAFANA_BASE_URL}/explore?orgId={org_id}&limit={limit}&left={encoded}"


# -----------------------------------------------------------------------
# Input Validation & Config Handling
# -----------------------------------------------------------------------

# --- Table name validator regex (PostgreSQL-safe) ---
_TABLE_NAME_PATTERN = re.compile(r"^[a-z_][a-z0-9_]*$")


def validate_table_name(name: str) -> None:
    """
    Validates whether the given table name conforms to PostgreSQL naming rules.

    Allowed format:
      - Starts with a lowercase letter or underscore.
      - Contains only lowercase letters, numbers, and underscores.

    Parameters:
      name : str - Table name to validate.
    """

    if not _TABLE_NAME_PATTERN.match(name):
        raise TableNameError(
            f"Invalid table name '{name}'. "
            "Names must start with lowercase letter/_ and contain only lowercase letters, digits, or underscores."
        )


# --- Default config directory ---
DEFAULT_CONFIG_DIR = Path.cwd() / "configs"
DEFAULT_CONFIG_DIR.mkdir(exist_ok=True, parents=True)


def save_config_file(cfg: dict, table_name: str, path: Path | None = None) -> None:
    """
    Saves the given config dictionary to a JSON file under the /configs directory.

    If no explicit path is provided, the default location will be:
      ./configs/<table_name>.json

    """
    target = path or (DEFAULT_CONFIG_DIR / f"{table_name}.json")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w") as f:
            json.dump(cfg, f, indent=2)
        logger.info("Saved config to: %s", target)
    except Exception as e:
        logger.error("Failed to save config to %s: %s", target, e)
        raise


# -----------------------------------------------------------------------
# File Reading & Delimiter Detection
# -----------------------------------------------------------------------


def auto_detect_delimiter(file_path: str) -> str | None:
    """
    Auto-detects the delimiter used in a CSV/TXT file.

    Scans the first line for common delimiters: ',', ';', '\\t', '|'.

    Parameters:
      file_path : str - Path to the CSV or TXT file.

    Returns:
        A string delimiter (e.g. ',') or None if detection failed.
    """

    file_path = Path(file_path)

    try:
        test_df = pd.read_csv(file_path, sep=None, engine="python", nrows=5)
        if len(test_df.columns) > 1:
            delimiters = [",", ";", "\t", "|"]
            with file_path.open("r") as f:
                first_line = f.readline()
                for delim in delimiters:
                    if delim in first_line:
                        return delim
        return None
    except Exception as e:
        logger.error("Delimiter auto-detection failed: %s", e)
        return None


def read_csv(file_path: str, delimiter: str | None = None) -> pd.DataFrame:
    """
    Reads a CSV or TXT file into a pandas DataFrame.

    Parameters:
        file_path : Path to the file.
        delimiter : Optional override. If None, auto-detection is attempted.

    Returns:
        A pandas DataFrame.
    """
    file_path = Path(file_path)
    if delimiter is None:
        delimiter = auto_detect_delimiter(file_path)
        if delimiter:
            logger.info("Auto-detected delimiter: '%s'", delimiter)
        else:
            logger.error("Could not auto-detect delimiter for file: '%s'", file_path)
            raise InvalidDelimiterError(
                f"Delimiter could not be auto-detected for file '{file_path}'."
            )

    try:
        df = pd.read_csv(file_path, delimiter=delimiter)
        logger.info(
            "CSV file '%s' successfully read with delimiter '%s'.", file_path, delimiter
        )
        return df
    except Exception as e:
        logger.error("Error reading CSV file '%s': %s", file_path, e)
        raise


# -----------------------------------------------------------------------
# HDF5 reading helper (revised) - convert the time-index to a column
# -----------------------------------------------------------------------


def read_h5(file_path: str, key: str | None = None) -> pd.DataFrame:
    """
    Reads an HDF5 file into a clean DataFrame.

    Selection logic when *key* is omitted:
        1. dataset whose name matches the filename stem
        2. dataset "/data"
        3. the only dataset (if exactly one exists)
    Otherwise raises ValueError and lists available keys.

    After loading:
        * If the dataset is indexed by DatetimeIndex, it is reset to a column
          named 'timestamp'.
        * Tuple / multi-index column labels are flattened by joining their
          parts with '_' so they are SQL-safe.
    """
    file_path = Path(file_path)

    with pd.HDFStore(file_path, mode="r") as store:
        keys = store.keys()  # ['/group1', '/g2', …]

        # ---------- pick dataset ----------
        if key:
            # accept with or without leading slash
            k = key if key.startswith("/") else f"/{key}"
            if k in keys:
                df = store[k]
            else:
                raise ValueError(f"Dataset '{key}' not found in {keys}")
        else:
            stem_key = f"/{file_path.stem}"
            if stem_key in keys:
                df = store[stem_key]
            elif "/data" in keys:
                df = store["/data"]
            elif len(keys) == 1:
                df = store[keys[0]]
            else:
                raise ValueError(
                    f"HDF5 file '{file_path}' contains multiple datasets {keys}. "
                    "Specify the desired key."
                )

    # ---------- normalise dataframe ----------
    # 1) move DatetimeIndex into a column
    if isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index(names="timestamp")

    # 2) flatten tuple column names -> strings
    df.columns = [
        "_".join(map(str, c)) if isinstance(c, tuple) else str(c) for c in df.columns
    ]

    return df


# -----------------------------------------------------------------------
# Datetime Detection & Parsing
# -----------------------------------------------------------------------


def is_timestamp(series: pd.Series, threshold: float = 0.9) -> bool:
    """
    Determines if a Series likely contains datetime values.

    Checks up to 100 non-null samples, requiring `threshold` (90%) to parse as datetimes.
    Skips numeric columns and numeric strings (e.g., '123').

    Args:
        series: Pandas Series to check.
        threshold: Fraction of samples that must parse as datetimes (default: 0.9).

    Returns:
        bool: True if the Series is likely a datetime column.
    """

    # Native datetime -- Accept immediately
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    # Numeric or numeric-string -- Not a timestamp
    if pd.api.types.is_numeric_dtype(series):
        return False
    if pd.api.types.is_string_dtype(series):
        # Only call .str on string columns!
        try:
            if series.dropna().str.isnumeric().all():
                return False
        except AttributeError:
            return False

        # Now try parsing sample of string values as datetime
        successes = 0
        series_clean = series.dropna()
        total_samples = min(100, len(series_clean))
        if total_samples == 0:
            return False
        sample = (
            series_clean.sample(total_samples, random_state=42)
            if len(series_clean) > total_samples
            else series_clean
        )
        for val in sample:
            try:
                parse(str(val), fuzzy=False)
                successes += 1
            except:
                continue
        return (successes / total_samples) >= threshold
    return False


def auto_detect_datetime_cols(df: pd.DataFrame) -> list:
    """
    Scans all columns in a DataFrame and returns a list of likely datetime fields.

    Notes:
      - Uses `is_timestamp()` on each column to detect datetime-like values.
      - Returns multiple candidates.
      - Used internally by `detect_datetime_column()` when no explicit column is provided.
    """
    candidate_cols = [col for col in df.columns if is_timestamp(df[col])]
    return candidate_cols


def detect_datetime_column(
    df: pd.DataFrame,
    datetime_col: str | None = None,
    cfg: DBConfig | None = None,
) -> str:
    """
    Identifies the datetime column in a DataFrame.

    If `datetime_col` is given, validates it against the table schema. Otherwise, auto-detects.
    """

    if datetime_col:
        # Validate against table schema
        table_name = df.attrs.get(
            "table_name", None
        )  # Optional: store table_name in df.attrs
        if table_name:
            schema = get_table_schema(table_name, cfg=cfg)
            if (
                datetime_col in schema
                and schema[datetime_col].lower() == "timestamp with time zone"
            ):
                logger.info(
                    "Using explicitly provided datetime column: '%s'", datetime_col
                )
                return datetime_col

        # Fallback to checking if column exists in DataFrame
        if datetime_col in df.columns:
            logger.info("Using explicitly provided datetime column: '%s'", datetime_col)
            return datetime_col
        else:
            logger.error("Provided datetime column '%s' is not valid.", datetime_col)
            raise DatetimeDetectionError(
                f"Provided datetime column '{datetime_col}' is invalid."
            )

    detected_cols = auto_detect_datetime_cols(df)
    if len(detected_cols) == 1:
        logger.info("Datetime column auto-detected: '%s'", detected_cols[0])
        return detected_cols[0]
    elif len(detected_cols) == 0:
        logger.error("No datetime columns detected automatically.")
        raise DatetimeDetectionError("No datetime columns detected automatically.")
    else:
        logger.error("Multiple datetime columns detected: %s", detected_cols)
        raise DatetimeDetectionError(
            f"Multiple datetime columns detected: {detected_cols}"
        )


def parse_datetime_column(
    df: pd.DataFrame,
    datetime_col: str,
    format: str | None = None,
    timezone: str = "UTC",
) -> pd.DataFrame:
    """
    Parses and localizes a datetime column in a pandas DataFrame.

    Processes the specified column to convert its values to datetime objects and applies
    the given timezone. Supports explicit format strings, including 'ISO8601', or auto-detects
    the format with a preference for ISO8601 if the pattern is detected.

    Args:
        df: The pandas DataFrame containing the datetime column.
        datetime_col: The name of the column to parse as datetime.
        format: Optional datetime format string (e.g., '%Y-%m-%d %H:%M:%S' or 'ISO8601').
                If None, attempts automatic parsing, prioritizing ISO8601 if detected.
        timezone: Timezone to localize the datetime column to (default: 'UTC').

    Returns:
        pd.DataFrame: The modified DataFrame with the parsed and localized datetime column.

    Raises:
        DatetimeParsingError: If parsing or timezone localization fails.
    """

    try:
        series_str = df[datetime_col].astype(str)
        if format and format.upper() == "ISO8601":
            df[datetime_col] = pd.to_datetime(series_str, format="ISO8601")
            logger.info("Datetime column '%s' parsed as ISO8601.", datetime_col)

        elif format:
            df[datetime_col] = pd.to_datetime(series_str, format=format, errors="raise")
            logger.info(
                "Datetime column '%s' parsed using format '%s'.", datetime_col, format
            )

        else:
            # If ISO8601 pattern detected, use it. (Fast path for your case!)
            if series_str.str.contains(r"T\d{2}:\d{2}:\d{2}", regex=True).any():
                df[datetime_col] = pd.to_datetime(series_str, format="ISO8601")
                logger.info(
                    "Datetime column '%s' parsed as ISO8601 (auto).", datetime_col
                )

            else:
                # Fall back to pandas' default auto-detect with dayfirst True
                df[datetime_col] = pd.to_datetime(
                    series_str, errors="raise", dayfirst=True
                )
                logger.info(
                    "Datetime column '%s' parsed automatically (dayfirst).",
                    datetime_col,
                )

        # Timezone conversion/localization as before...
        if df[datetime_col].dt.tz is not None:
            df[datetime_col] = df[datetime_col].dt.tz_convert(timezone)

        else:
            df[datetime_col] = df[datetime_col].dt.tz_localize(
                timezone, ambiguous="raise", nonexistent="raise"
            )

        logger.info(
            "Datetime column '%s' localized to timezone '%s'.", datetime_col, timezone
        )
        return df

    except Exception as e:
        logger.error(
            "Failed to parse/localize datetime column '%s': %s", datetime_col, e
        )
        raise DatetimeParsingError(
            f"Parsing datetime column '{datetime_col}' failed: {e}"
        )


# -----------------------------------------------------------------------
# Table Schema Utilities
# -----------------------------------------------------------------------


def list_table_columns(table_name: str, cfg: DBConfig | None = None) -> list[str]:
    """
    Returns a list of column names for `table_name` in the public schema.

    Parameters:
        table_name : str - Table name to inspect.

    Returns:
        List of column names in ordinal order.
    """
    validate_table_name(table_name)
    engine = pg_engine(cfg=cfg)
    sql = text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = :tbl
        ORDER BY ordinal_position;
    """)
    with engine.connect() as conn:
        return [row[0] for row in conn.execute(sql, {"tbl": table_name}).fetchall()]


def get_table_schema(table_name: str, cfg: DBConfig | None = None) -> dict[str, str]:
    """
    Returns a mapping of column_name -> data_type for an existing table.

    Example output:
        {
            'time': 'timestamp with time zone',
            'temperature': 'double precision',
            ...
        }
    """
    validate_table_name(table_name)
    engine = pg_engine(cfg=cfg)
    sql = text("""
        SELECT column_name, data_type
          FROM information_schema.columns
         WHERE table_schema='public'
           AND table_name = :tbl
         ORDER BY ordinal_position;
    """)
    with engine.connect() as conn:
        return {row[0]: row[1] for row in conn.execute(sql, {"tbl": table_name})}


def infer_schema(df: pd.DataFrame) -> Dict[str, str]:
    """
    Infers PostgreSQL-compatible SQL types from a pandas DataFrame.

    Mapping:
        - int      -> INT
        - float    -> DOUBLE PRECISION
        - bool     -> BOOLEAN
        - datetime -> TIMESTAMPTZ
        - other    -> TEXT

    Returns:
        Dict[str, str] mapping of column names to SQL types.
    """
    schema_map = {}
    for col in df.columns:
        dtype_str = str(df[col].dtype)
        # Map pandas types to PostgreSQL-compatible types
        if "int" in dtype_str:
            schema_map[col] = "INT"
        elif "float" in dtype_str:
            schema_map[col] = "DOUBLE PRECISION"
        elif "bool" in dtype_str:
            schema_map[col] = "BOOLEAN"
        elif "datetime64[ns, UTC]" in dtype_str:
            schema_map[col] = "TIMESTAMPTZ"
        else:
            schema_map[col] = "TEXT"
    logger.info("Schema inferred: %s", schema_map)
    return schema_map


# -----------------------------------------------------------------------
# Table Creation (Hypertable Initialization)
# -----------------------------------------------------------------------


def create_table_df(
    schema_map: Dict[str, str],
    table_name: str,
    datetime_col: str,
    chunk_days: int = 1,
    cfg: DBConfig | None = None,
) -> None:
    """
    Creates a new SQL table and transforms it into a TimescaleDB hypertable.

    Parameters:
        schema_map   : Dict of column_name → SQL type (from `infer_schema`)
        table_name   : Target name of the table
        datetime_col : Column to use as time axis
        chunk_days   : Hypertable partition size (in days)
    """
    engine = pg_engine(cfg)

    # Check if the table already exists.
    check_sql = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = :tbl
        );
    """)

    with engine.connect() as conn:
        exists = conn.execute(check_sql, {"tbl": table_name}).scalar()
        if exists:
            raise ValueError(
                f"Table '{table_name}' already exists. Aborting to avoid overwriting."
            )

    # Build CREATE TABLE SQL
    col_defs = ",\n  ".join([f'"{col}" {dtype}' for col, dtype in schema_map.items()])
    create_sql = f'CREATE TABLE "{table_name}" (\n  {col_defs}\n);'

    # Execute table + hypertable creation
    with engine.begin() as conn:
        conn.execute(text(create_sql))
        logger.info("Table '%s' created successfully.", table_name)

        # Create a TimescaleDB hypertable on "<table_name>" using "<datetime_col>" and chunk interval.
        hypertable_sql = (
            "SELECT create_hypertable("
            f"'{table_name}', '{datetime_col}', "
            f"chunk_time_interval => interval '{chunk_days} day', "
            "if_not_exists => true);"
        )
        conn.execute(text(hypertable_sql))
        logger.info(
            "Hypertable created on '%s' (time column: '%s', chunk: %d day).",
            table_name,
            datetime_col,
            chunk_days,
        )


# -----------------------------------------------------------------------
# Data Insertion -- Dataframe
# -----------------------------------------------------------------------


def insert_data_df(
    df: pd.DataFrame,
    table_name: str,
    datetime_col: str | None = None,
    cfg: DBConfig | None = None,
) -> None:
    """
    Inserts a DataFrame into an existing table using PostgreSQL's COPY.

    Parameters:
        df         : Data to insert
        table_name : Existing TimescaleDB table

    Skips insert if DataFrame is empty.
    Raises exceptions on COPY failure.
    """
    if df.empty:
        raise ValueError("DataFrame is empty")

    buffer = StringIO()
    df.to_csv(buffer, index=False, header=False)
    buffer.seek(0)

    columns_str = ",".join([f'"{col}"' for col in df.columns])
    copy_sql = f'COPY "{table_name}" ({columns_str}) FROM STDIN WITH (FORMAT csv)'

    engine = pg_engine(cfg)
    raw_conn = engine.raw_connection()

    try:
        cur = raw_conn.cursor()
        cur.copy_expert(copy_sql, buffer)
        cur.close()
        raw_conn.commit()
        logger.info(
            "Successfully inserted %d rows into table '%s'.", len(df), table_name
        )
    except Exception as e:
        raw_conn.rollback()
        raise ValueError("Error inserting data into table '%s': %s", table_name, e)
    finally:
        raw_conn.close()

    if datetime_col is None:
        datetime_col = detect_datetime_column(df, cfg=cfg)
    _refresh_or_create_metadata(
        df,
        table_name=table_name,
        datetime_col=datetime_col,
        schema=get_table_schema(table_name, cfg=cfg),
        cfg=cfg,
    )


# -----------------------------------------------------------------------
# Metadata Helpers (Duplicate Check, Stats, Metadata Maintenance)
# -----------------------------------------------------------------------


def get_file_time_range(df: pd.DataFrame, datetime_col: str) -> tuple:
    """
    Returns the (min, max) timestamps from a datetime column.

    Parameters:
        df           : pandas DataFrame
        datetime_col : Name of the datetime column

    Returns:
        (file_min, file_max)
    """
    file_min = df[datetime_col].min()
    file_max = df[datetime_col].max()
    return file_min, file_max


def check_duplicates(
    table_name: str, datetime_col: str, file_min, file_max, cfg: DBConfig | None = None
) -> bool:
    """
    Checks whether the target table already contains rows within the given time range.

    Parameters:
        table_name   : TimescaleDB table
        datetime_col : Column used for time comparisons
        file_min     : Start of input data range
        file_max     : End of input data range

    Returns:
        True if overlap exists, False otherwise.
    """
    engine = pg_engine(cfg=cfg)
    query_sql = text(f"""
        SELECT COUNT(*) FROM "{table_name}" 
        WHERE "{datetime_col}" BETWEEN :file_min AND :file_max;
    """)
    with engine.connect() as conn:
        count = conn.execute(
            query_sql, {"file_min": file_min, "file_max": file_max}
        ).scalar()
    logger.info(
        "Found %d rows in table '%s' with %s between %s and %s.",
        count,
        table_name,
        datetime_col,
        file_min,
        file_max,
    )
    return count > 0


def query_table_metadata(
    table_name: str,
    datetime_col: str | None = None,
    cfg: DBConfig | None = None,
) -> dict:
    """
    Returns basic stats for a table, using metadata if available.

    Output:
        {
            "row_count": int,
            "min_time": datetime,
            "max_time": datetime,
            "sampling_period_ms": float | None,
            "datetime_col": str
        }
    """
    # === fast-path : cached row ===
    meta = load_metadata(table_name, cfg=cfg)
    # if meta and (datetime_col is None or datetime_col == meta.datetime_col):
    #     return {
    #         "row_count": meta.row_count,
    #         "min_time": meta.min_time,
    #         "max_time": meta.max_time,
    #         "sampling_period_ms": meta.sampling_period_ms,
    #         "datetime_col": meta.datetime_col,
    #     }

    # === slow-path : live SQL ===
    # either no row yet or caller wants stats on another column
    if datetime_col is None:
        # need a column to query – reuse infer_plot_columns helper
        datetime_col, _, _ = infer_plot_columns(table_name, cfg=cfg)

    engine = pg_engine(cfg=cfg)
    sql = text(f"""
        SELECT COUNT(*)        AS row_count,
               MIN("{datetime_col}") AS min_time,
               MAX("{datetime_col}") AS max_time
          FROM "{table_name}";
    """)
    with engine.connect() as conn:
        row = conn.execute(sql).first()

    stats = {
        "row_count": row._mapping["row_count"],
        "min_time": row._mapping["min_time"],
        "max_time": row._mapping["max_time"],
        "sampling_period_ms": None,  # filled below
        "datetime_col": datetime_col,
    }

    # try to derive sampling period when there are enough points
    stats["sampling_period_ms"] = compute_sampling_period(
        stats["row_count"], stats["min_time"], stats["max_time"]
    )

    # write (or refresh) the metadata row so next call is instant
    # if meta is None or meta.datetime_col == datetime_col:
    schema = get_table_schema(table_name, cfg=cfg)
    save_metadata(
        TableMetadata(
            table_name=table_name,
            schema=schema,
            datetime_col=datetime_col,
            row_count=stats["row_count"],
            min_time=stats["min_time"],
            max_time=stats["max_time"],
            sampling_period_ms=stats["sampling_period_ms"],
        ),
        cfg=cfg,
    )
    return stats


def _refresh_or_create_metadata(
    df: pd.DataFrame,
    *,
    table_name: str,
    datetime_col: str,
    schema: dict[str, str],
    cfg: DBConfig | None = None,
) -> None:
    """
    Updates or creates the _timeseries_metadata row for a table after data insert.

    - If table is new, creates a full metadata record
    - If table exists, patches row count, time bounds, and recomputes sampling
    """

    # basic stats for this batch
    batch_rows = len(df)
    batch_min, batch_max = df[datetime_col].min(), df[datetime_col].max()
    meta = load_metadata(table_name, cfg=cfg)

    # first time this table shows up -> create full record
    if meta is None:
        meta = TableMetadata(
            table_name=table_name,
            schema=schema,
            datetime_col=datetime_col,
            row_count=batch_rows,
            min_time=batch_min,
            max_time=batch_max,
            sampling_period_ms=compute_sampling_period(
                batch_rows, batch_min, batch_max
            ),
            units=None,  # user can update later
            notes=None,  # user can update later
        )
        save_metadata(meta, cfg=cfg)
        logger.info("Metadata row created for '%s'.", table_name)
        return

    # table already registered -> patch evolving fields
    if meta.min_time is not None:
        tz = meta.min_time.tzinfo
        if batch_min.tzinfo is None:
            # tz-naive -> tz_localize
            batch_min = batch_min.tz_localize(tz)
            batch_max = batch_max.tz_localize(tz)
        else:
            # tz-aware -> tz_convert
            batch_min = batch_min.tz_convert(tz)
            batch_max = batch_max.tz_convert(tz)

    meta.row_count = (meta.row_count or 0) + batch_rows
    meta.min_time = min(meta.min_time, batch_min) if meta.min_time else batch_min
    meta.max_time = max(meta.max_time, batch_max) if meta.max_time else batch_max
    meta.sampling_period_ms = compute_sampling_period(
        meta.row_count, meta.min_time, meta.max_time
    )

    save_metadata(meta, cfg=cfg)
    logger.info("Metadata row updated for '%s'.", table_name)


# -----------------------------------------------------------------------------
# Wrapper Functions (Public Ingestion API)
# -----------------------------------------------------------------------------


def create_table_from_file(
    file_path: str,
    table_name: str,
    delimiter: str | None = None,
    datetime_col: str | None = None,
    format: str | None = None,
    timezone: str = "UTC",
    chunk_days: int = 7,
    config: bool = False,
    config_path: Path | None = None,
    derive_stats: bool = False,
    units: Units | None = None,
    hdf_key: str | None = None,
    cfg: DBConfig | None = None,
) -> None:
    """
    Reads a file, infers schema, creates a hypertable, and writes metadata.

     This function performs the full pipeline:
       - Reads the input file using the specified or auto-detected delimiter.
       - Detects (or validates) the datetime column for time-series indexing.
       - Parses and localizes the datetime values to the given timezone.
       - Infers a PostgreSQL-compatible schema based on DataFrame dtypes.
       - Creates the table in the database and converts it to a hypertable using TimescaleDB.
       - Registers an initial metadata row in `_timeseries_metadata`.
       - Optionally saves a configuration file with all settings for reuse.

     Parameters:
       file_path     : Path to the input file (.csv or .txt).
       table_name    : Name of the new table to create (must follow PostgreSQL naming rules).
       delimiter     : Optional column separator (e.g., ',', ';', '\\t'); auto-detected if None.
       datetime_col  : Optional name of the timestamp column; auto-detected if not provided.
       format        : Optional datetime format string; uses pandas auto-parsing if omitted.
       timezone      : Timezone for localizing datetime values (default: 'UTC').
       chunk_days    : Chunk size in days for hypertable partitioning (default: 7).
       config        : If True, saves a JSON file with these settings under `configs/` (default: False).
       config_path   : Optional custom path to save the config JSON instead of default location.
       derive_stats  : False read only header + one row; write a metadata stub with. (default)
                       True  read *all* rows, compute row-count, min/max time, sampling period.
        units        : Optional units for metadata (e.g., Units.VOLTS).
        hdf_key      : Dataset key for HDF5 files; auto-detected if None.


     Raises:
       TableNameError         : If `table_name` is invalid.
       InvalidDelimiterError  : If no suitable delimiter is provided or detected.
       DatetimeDetectionError : If no suitable datetime column can be determined.
       DatetimeParsingError   : If parsing or timezone localization fails.
       ValueError             : If a table with the same name already exists in the DB.
    """

    validate_table_name(table_name)

    # File format detection
    fmt = get_file_format(file_path)

    if fmt == "csv":
        df = read_csv(file_path, delimiter=delimiter)
    elif fmt == "h5":
        df = read_h5(file_path, key=hdf_key)

    else:
        raise ValueError(f"Unsupported file format '{fmt}'")

    datetime_col = detect_datetime_column(df, datetime_col, cfg=cfg)
    df = parse_datetime_column(df, datetime_col, format=format, timezone=timezone)
    schema = infer_schema(df)
    create_table_df(schema, table_name, datetime_col, chunk_days, cfg=cfg)

    # create a bare metadata record for this table
    if derive_stats:
        row_count = len(df)
        file_min, file_max = get_file_time_range(df, datetime_col)
        sampling = compute_sampling_period(row_count, file_min, file_max)
    else:
        row_count = 0
        file_min = file_max = None

    meta = TableMetadata(
        table_name=table_name,
        schema=schema,
        datetime_col=datetime_col,
        row_count=row_count,
        min_time=file_min,
        max_time=file_max,
        sampling_period_ms=compute_sampling_period(row_count, file_min, file_max),
        units=units,
        notes=None,  # user can update later
    )
    save_metadata(meta, cfg=cfg)
    logger.info("Metadata row written for '%s'.", table_name)
    pretty_print_metadata(meta)

    if config:
        _cfg = {
            "file_path": str(file_path),
            "delimiter": delimiter,
            "datetime_col": datetime_col,
            "datetime_format": format,
            "timezone": timezone,
            "chunk_days": chunk_days,
            "allow_duplicates": False,
        }
        save_config_file(_cfg, table_name, path=config_path)


def insert_data(
    file_path: str,
    table_name: str,
    delimiter: str | None = None,
    datetime_col: str | None = None,
    format: str | None = None,
    timezone: str = "UTC",
    allow_duplicates: bool = False,
    config: bool = False,
    config_path: Path | None = None,
    hdf_key: str | None = None,
    cfg: DBConfig | None = None,
) -> None:
    """
    Simplified wrapper to insert file data into an *existing* table.

    Skips insertion if duplicate timestamps are detected (unless overridden).

    This function:
      - Loads and parses the file.
      - Detects the datetime column and localizes timestamps.
      - Verifies that the target table exists.
      - Skips insertion if overlapping data is already present (unless `allow_duplicates=True`).
      - Inserts the data using PostgreSQL COPY.
      - Logs final row count and time range after insertion.

    Parameters:
      file_path        : Path to the CSV or TXT file.
      table_name       : Name of the existing table to insert into.
      delimiter        : Optional file delimiter; auto-detected if None.
      datetime_col     : Optional datetime column name; auto-detected if None.
      format           : Optional format for datetime parsing.
      timezone         : Timezone to localize timestamps (default: 'UTC').
      allow_duplicates : Whether to skip duplicate checks (default: False).

    Raises:
      Exception if table doesn't exist or insertion fails.
    """

    validate_table_name(table_name)

    # File format detection
    fmt = get_file_format(file_path)

    if fmt == "csv":
        df = read_csv(file_path, delimiter=delimiter)
    elif fmt == "h5":
        df = read_h5(file_path, key=hdf_key)

    else:
        raise ValueError(f"Unsupported file format '{fmt}'")

    col = detect_datetime_column(df, datetime_col, cfg=cfg)
    df = parse_datetime_column(df, col, format=format, timezone=timezone)

    engine = pg_engine(cfg=cfg)
    exists = (
        engine.connect()
        .execute(
            text(
                "SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_schema='public' AND table_name=:tbl)"
            ),
            {"tbl": table_name},
        )
        .scalar()
    )

    if not exists:
        print(f"Table '{table_name}' not found.")
        print(
            f"  To create it, run:\n    create_table_from_file('{file_path}', '{table_name}')"
        )
        return

    print(f"Table '{table_name}' found. Inserting data…")

    if not allow_duplicates:
        file_min, file_max = get_file_time_range(df, col)
        if check_duplicates(table_name, col, file_min, file_max, cfg=cfg):
            print(
                f"Detected existing data in '{table_name}' between {file_min} and {file_max}. Skipping insert."
            )
            return

    insert_data_df(df, table_name, cfg=cfg)
    pretty_print_metadata(load_metadata(table_name, cfg=cfg))

    if config:
        _cfg = {
            "file_path": str(file_path),
            "delimiter": delimiter,
            "datetime_col": col,
            "datetime_format": format,
            "timezone": timezone,
            "chunk_days": None,
            "allow_duplicates": allow_duplicates,
        }
        save_config_file(_cfg, table_name, path=config_path)


def insert_data_from_file(
    file_path: str,
    table_name: str,
    delimiter: str | None = None,
    datetime_col: str | None = None,
    format: str | None = None,
    timezone: str = "UTC",
    allow_duplicates: bool = False,
    config: bool = False,
    config_path: Path | None = None,
    hdf_key: str | None = None,
    cfg: DBConfig | None = None,
) -> None:
    """
    Wrapper to create a table and insert data into it.

    Performs:
      - File reading, delimiter detection.
      - Datetime parsing and timezone localization.
      - Duplicate checking over the datetime range (optional).
      - PostgreSQL COPY-based data insertion.
      - Logs row count and time range post-insert.
      - Optionally writes a config file.

    Parameters:
      file_path        : Input file to insert.
      table_name       : Target table name (must exist).
      delimiter        : Optional field delimiter (auto-detected if None).
      datetime_col     : Optional datetime column name (auto-detected if None).
      format           : Optional datetime format string.
      timezone         : Timezone to localize timestamps (default: 'UTC').
      allow_duplicates : Whether to allow overlapping time range insertions (default: False).
      config           : Whether to save a reusable config file (default: False).
      config_path      : Optional override path for saving the config JSON.

    Raises:
      Exception if the insert fails or duplicate check blocks the operation.
    """
    validate_table_name(table_name)

    # File format detection
    fmt = get_file_format(file_path)

    if fmt == "csv":
        df = read_csv(file_path, delimiter=delimiter)
    elif fmt == "h5":
        df = read_h5(file_path, key=hdf_key)

    else:
        raise ValueError(f"Unsupported file format '{fmt}'")

    datetime_col = detect_datetime_column(df, datetime_col, cfg=cfg)
    df = parse_datetime_column(df, datetime_col, format=format, timezone=timezone)

    if not table_exists(table_name, cfg=cfg):
        create_table_from_file(
            file_path=file_path,
            table_name=table_name,
            delimiter=delimiter,
            datetime_col=datetime_col,
            format=format,
            timezone=timezone,
            derive_stats=False,  # skeleton, refresh after COPY
            hdf_key=hdf_key,
            cfg=cfg,
        )

    file_min, file_max = get_file_time_range(df, datetime_col)

    # Check for duplicates using the datetime column as the primary key.
    if not allow_duplicates and check_duplicates(
        table_name, datetime_col, file_min, file_max, cfg=cfg
    ):
        logger.warning(
            "Data within the time range %s to %s already exists in table '%s'. Insertion aborted.",
            file_min,
            file_max,
            table_name,
        )
        return  # Skip insertion

    # Proceed to insert data.
    insert_data_df(df, table_name, cfg=cfg)
    pretty_print_metadata(load_metadata(table_name, cfg=cfg))

    if config:
        _cfg = {
            "file_path": str(file_path),
            "delimiter": delimiter,
            "datetime_col": datetime_col,
            "datetime_format": format,
            "timezone": timezone,
            "chunk_days": None,
            "allow_duplicates": allow_duplicates,
        }
        save_config_file(_cfg, table_name, path=config_path)


def create_table_from_row(
    row: dict,
    table_name: str,
    datetime_col: str = None,
    timezone: str = "UTC",
    chunk_days: int = 7,
    cfg: DBConfig | None = None,
) -> None:
    """
    Creates a TimescaleDB hypertable from a single row dictionary.

    Args:
        row: Dictionary with column names as keys and row values.
        table_name: Name of the hypertable to create (PostgreSQL-compliant).
        datetime_col: Datetime column name; auto-detected if None.
        timezone: Timezone for datetime parsing (default: 'UTC').
        chunk_days: TimescaleDB chunk interval in days (default: 7).

    Returns:
        None

    Raises:
        TableNameError: If table name is invalid.
        DatetimeDetectionError: If datetime column detection fails.
        ValueError: If row or datetime parsing is invalid.
    """

    # Validate table name
    validate_table_name(table_name)

    # Convert row to DataFrame
    df = pd.DataFrame([row])

    # Detect and parse datetime column
    datetime_col = detect_datetime_column(df, datetime_col, cfg=cfg)
    df = parse_datetime_column(df, datetime_col, timezone=timezone)

    # Infer schema and create table
    schema = infer_schema(df)
    create_table_df(schema, table_name, datetime_col, chunk_days, cfg=cfg)


def insert_single_row(
    table_name: str,
    row: Dict[str, Any],
    datetime_col: str | None = None,
    format: str | None = None,
    timezone: str = "UTC",
    allow_duplicates: bool = False,
    chunk_days: int = 7,
    cfg: DBConfig | None = None,
) -> None:
    """
    Inserts a single row (dict of values) into a hypertable.

    This is intended for live-sensor or manual single-point ingestion without
    writing/reading an external file.

    Steps performed:
      1. Validates `table_name` against Postgres naming rules.
      2. Wraps the single `row` (a dict) in a one-row pandas DataFrame.
      3. Auto-detects or validates the datetime column.
      4. Parses and localizes the timestamp.
      5. Optionally checks for duplicates by timestamp (skips insert if found).
      6. Leverages the high-performance `insert_data_df()` COPY path to inject the row.

    Parameters:
      table_name       : Name of the existing hypertable to insert into.
      row              : Dict mapping column names -> values for the new row.
      datetime_col     : Optional explicit name of the timestamp column; if None, auto-detected.
      format           : Optional `strftime` format for parsing the timestamp; if None, auto-parsed.
      timezone         : Timezone for localization (default: 'UTC').
      allow_duplicates : If False (default), skips insertion when a row with the same timestamp exists.
      chunk_days       : Hypertable chunk interval in days if table is created (default: 7).

    Raises:
      TableNameError           : If `table_name` is invalid.
      DatetimeDetectionError   : If the datetime column cannot be determined.
      DatetimeParsingError     : If timestamp parsing/localization fails.
      Exception                : If the COPY insertion fails.
    """

    validate_table_name(table_name)

    # If datetime_col not given, try to auto-detect later
    # Convert datetime-like value to ISO string if needed (prevents parse errors in DF)
    _row = row.copy()
    target_col = datetime_col or None  # let detection fallback work
    if target_col is None and len(row) == 1:
        # Only one key? Probably the datetime
        target_col = next(iter(row))

    if target_col is not None and target_col in _row:
        v = _row[target_col]
        if isinstance(v, (datetime.datetime, pd.Timestamp)):
            _row[target_col] = v.isoformat()

    df = pd.DataFrame([_row])
    col = detect_datetime_column(df, datetime_col, cfg=cfg)
    df = parse_datetime_column(df, col, format=format, timezone=timezone)

    # ---- Step 2: Auto-create table if missing ----
    if not table_exists(table_name, cfg=cfg):
        schema = infer_schema(df)
        create_table_df(schema, table_name, col, chunk_days, cfg=cfg)
        logger.info("Table '%s' auto-created before inserting row.", table_name)

    if not allow_duplicates:
        tmin, tmax = get_file_time_range(df, col)
        if check_duplicates(table_name, col, tmin, tmax, cfg=cfg):
            logger.info(
                "Skipping insert: row with timestamp %s already exists in '%s'.",
                tmin,
                table_name,
            )
            return

    insert_data_df(df, table_name, cfg=cfg)
    logger.info(
        "Single row inserted into '%s' (timestamp column: '%s').", table_name, col
    )


# -----------------------------------------------------------------------
# Data Retrieval via PostgREST
# -----------------------------------------------------------------------


# ------------------------ HDF5 writing helper ------------------------
def write_h5(
    df: pd.DataFrame,
    file_path: str | Path,
    *,
    key: str | None = None,
    mode: str = "w",
) -> None:
    """
    Save *df* to *file_path* under *key*.

    Parameters:
    df         : DataFrame to write
    file_path  : target *.h5* path
    key        : dataset name (e.g. "power_log") -- If *key* is None → uses Path(file_path).stem  (e.g. 'energy_data')
    mode       : "w" = overwrite file (default)
                 "a" = append or create key inside existing file

    Notes:
    * Uses `format="table"` so you can append more rows later.
    * Compression BLOSC-9: good ratio & fast even on a Pi.
    * Any other mode raises `ValueError`.
    """
    file_path = Path(file_path)
    if file_path.suffix.lower() not in (".h5", ".hdf", ".hdf5"):
        raise ValueError("File path must have .h5, .hdf, or .hdf5 extension")
    if mode not in ("w", "a"):
        raise ValueError('mode must be "w" (write) or "a" (append)')

    if key is None:
        key = file_path.stem

    df.to_hdf(
        file_path,
        key=key,
        mode=mode,
        format="table",
        complib="blosc",
        complevel=9,
        append=(mode == "a"),
    )


class OutputFormat(Enum):
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"
    TXT = "txt"
    HDF5 = "h5"


def get_data(
    table_name: str,
    row_limit: int | None = None,
    cfg: DBConfig | None = None,
) -> list[dict]:
    """
    Fetch raw data from the database for a specific table using SQLAlchemy.

    Parameters:
      table_name : Name of the TimescaleDB table to retrieve.
      row_limit  : Optional integer row limit for pagination or previewing.

    Returns:
      List of rows (as dictionaries) for further processing.
    """

    engine = pg_engine(cfg=cfg)
    sql = f'SELECT * FROM "{table_name}"'
    if row_limit is not None:
        sql += f" LIMIT {row_limit}"

    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql))
            rows = [dict(row._mapping) for row in result]
    except Exception as exc:
        print(
            f"\nERROR: Failed to fetch data from table '{table_name}': {exc}\n",
            file=sys.stderr,
        )
        sys.exit(1)

    if not rows:
        print(f"\nINFO: No data returned from table '{table_name}'.\n")
        sys.exit(0)

    return rows


def retrieve_data(
    table_name: str,
    row_limit: int | None = None,
    output_format: OutputFormat = OutputFormat.CSV,
    output_path: Path | None = None,
    hdf_key: str | None = None,
    hdf_mode: str = "w",
    force: bool = False,  # hidden/undocumented admin bypass
    cfg: DBConfig | None = None,
) -> Path:
    """
    Retrieves data from a table via PostgREST and exports it to file in the requested format.

    Parameters:
      table_name    : Name of the table to retrieve data from.
      row_limit     : Maximum number of rows to fetch; None retrieves all.
      output_format : One of ['csv', 'json', 'xlsx', 'txt'] (default: 'csv').
      output_path   : Optional full path to save output; defaults to ./<table>.<ext>.

    Returns:
      Path to the saved file.

    Raises:
      ValueError for unsupported formats or fetch/export failures.
    """

    MAX_ROWS = 250_000  # Default max rows for PostgREST queries

    # Check if the table exists
    if not table_exists(table_name, cfg=cfg):
        print(f"ERROR: Table '{table_name}' does not exist in the database.")
        return

    # Preview Table Metadata
    stats = query_table_metadata(table_name, cfg=cfg)
    total_rows = stats.get("row_count", 0)
    min_time = stats.get("min_time", None)
    max_time = stats.get("max_time", None)
    datetime_col = stats.get("datetime_col", None)
    print(f"\nTable: '{table_name}'")
    print(f"Total rows: {total_rows}")
    print(f"Columns: {list(get_table_schema(table_name, cfg=cfg).keys())}")
    if datetime_col:
        print(f"Time range: {min_time} -> {max_time}")

    preview_df = pd.DataFrame(get_data(table_name, row_limit=3, cfg=cfg))
    if not preview_df.empty:
        print("\nSample rows:")
        print(preview_df.head(3).to_markdown(index=False, tablefmt="grid"))
    else:
        print("Table is empty.")

    print(f"\nWARNING: Maximum allowed rows to export is {MAX_ROWS}.")
    requested = row_limit or total_rows
    print(f"Requested rows: {requested}")

    # Hard limit (non-admin)
    if requested > MAX_ROWS:
        # Only allow if both (a) force is set AND (b) IS_ADMIN=true
        is_admin = os.environ.get("IS_ADMIN", "false").lower() == "true"
        if not (force and is_admin):
            print(
                f"\nERROR: Refusing to export {requested:,} rows (max allowed is {MAX_ROWS:,}).\n"
                "Contact admin if you require a full export."
            )
            return
        else:
            print("[ADMIN] Force export authorized.")

    df = pd.DataFrame(get_data(table_name, row_limit=row_limit, cfg=cfg))

    supported_formats = [format.value for format in OutputFormat]

    # Normalize to OutputFormat Enum if needed
    if isinstance(output_format, str):
        output_format = OutputFormat(output_format.lower())
    ext = "xlsx" if output_format == OutputFormat.XLSX else output_format.value

    # if isinstance(output_format, str):
    #     try:
    #         output_format = OutputFormat(output_format.lower())
    #     except ValueError:
    #         raise ValueError(f"Unsupported export format: '{output_format}'")

    # if output_format.value not in [f.value for f in OutputFormat]:
    #     raise ValueError(f"Unsupported export format: '{output_format}'")

    # ext = "xlsx" if output_format == "xlsx" else output_format
    if output_path is None:
        output_path = Path(f"{table_name}.{ext}")
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if output_format == OutputFormat.CSV:
            df.to_csv(output_path, index=False)
        elif output_format == OutputFormat.JSON:
            df.to_json(output_path, orient="records", indent=2)
        elif output_format == OutputFormat.XLSX:
            df.to_excel(output_path, index=False)
        elif output_format == OutputFormat.TXT:
            df.to_csv(output_path, sep="\t", index=False)
        elif output_format == OutputFormat.HDF5:
            write_h5(
                df,
                output_path,
                key=hdf_key or table_name,
                mode=hdf_mode,
            )
    except Exception as e:
        logger.error("Error exporting data to %s: %s", output_format, e)
        raise

    logger.info("Exported %d rows from '%s' to '%s'.", len(df), table_name, output_path)
    return output_path


def table_exists(table_name: str, cfg: DBConfig | None = None) -> bool:
    """
    Checks if a table exists in the PostgreSQL database.

    Parameters:
        table_name : str - Name of the table to check.

    Returns:
        True if the table exists, False otherwise.
    """
    engine = pg_engine(cfg=cfg)
    sql = text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = :tbl
        );
    """)
    with engine.connect() as conn:
        return conn.execute(sql, {"tbl": table_name}).scalar()


def drop_table(table_name: str, cfg: DBConfig | None = None) -> None:
    """
    Drops a table from the PostgreSQL database.

    Parameters:
        table_name : str - Name of the table to drop.

    Raises:
        ValueError if the table does not exist.
    """
    if not table_exists(table_name, cfg=cfg):
        raise ValueError(f"Table '{table_name}' does not exist.")

    engine = pg_engine(cfg=cfg)
    sql = text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
    with engine.begin() as conn:
        conn.execute(sql)
    logger.info("Table '%s' dropped successfully.", table_name)
    drop_metadata(table_name, cfg=cfg)


# -----------------------------------------------------------------------------
# API-to-CLI Mapping Reference
#
# The CLI menu wraps around these core API functions. Each CLI option maps
# directly to one or more non-interactive API calls listed below.
#
# ┌──────────────────────────────────────────────┬─────────────────────────────────────────────────────────────┐
# │                   CLI Option                 │                        API Function(s)                      │
# ├──────────────────────────────────────────────┼─────────────────────────────────────────────────────────────┤
# │ 1. Create Table Only                         │ create_table_from_file(file_path, table_name, …)            │
# │ 2. Insert Data Only                          │ insert_data(file_path, table_name, …)                       │
# │ 3. Insert Single Row                         │ insert_single_row(table_name, row_dict, …)                  │
# │ 4. Create Table + Insert Data                │ create_table_from_file(…) + insert_data_from_file(…)        │
# │ 5. Create Table + Insert Data (1 func)       │ insert_data_from_file(file_path, table_name, config=True)   │
# │ 6. Retrieve Data                             │ retrieve_data(table_name, row_limit, output_format, …)      │
# │ 7. Generate Grafana Link                     │ get_grafana_url(table_name, value_col, …)                   │
# │ 8. Metadata Tools                            │ query_table_metadata(table_name, …), save_metadata(meta),   │
# │                                              │ load_metadata(table_name), drop_metadata(table_name), etc.  │
# └──────────────────────────────────────────────┴─────────────────────────────────────────────────────────────┘
#
# Notes:
# - Configs are saved per-table to ./configs/<table_name>.json unless overridden via `config_path`.
# - Configuration is loaded dynamically from `.env`, with no reliance on cached files.
# - Debug logging is toggled via `DEBUG=true` in `.env` for troubleshooting.
# - Dynamic host resolution in `.env` avoids `localhost` issues for DB and PostgREST connections.
# - retrieve_data() supports file formats: csv, json, xlsx, txt, hdf5.
# - retrieve_data() auto-generates output paths (e.g., <table_name>.<ext>) if none provided.
# - Output directory is created automatically if missing.
# - Grafana URL builder is standalone and works independently of data export.
# - Metadata is stored in the `_timeseries_metadata` table and updated automatically after table creation or data insertion.
# - Metadata tracks row count, datetime range, sampling period, and schema, used for CLI defaults, range checks, and validation.
# -----------------------------------------------------------------------------
