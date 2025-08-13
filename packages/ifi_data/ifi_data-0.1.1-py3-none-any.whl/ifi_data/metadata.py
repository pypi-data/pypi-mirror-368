"""
metadata.py (Metadata Registry Module)

Overview:
  This module manages a metadata registry for TimescaleDB hypertables, storing descriptive
  metadata not natively tracked by PostgreSQL. Metadata is maintained in a dedicated
  `_timeseries_metadata` table, with one row per hypertable, and is automatically updated
  by `api.py` during table creation and data insertion. It supports the CLI (`cli.py`) and
  API (`api.py`) by providing table statistics, schema validation, and defaults.

Key Features:
  - Stores metadata in `_timeseries_metadata` table with fields:
      - table_name, schema (JSONB), datetime_col, row_count, min_time, max_time,
        sampling_period_ms, units (JSONB), notes
  - Tracks:
      - Schema (column names and SQL types)
      - Datetime column for time-series indexing
      - Row count, time range, and sampling frequency
      - Optional engineering units and user notes
  - Automatically computes sampling interval from row count and time span
  - Supports metadata export to JSON for inspection or backup
  - Rebuilds metadata from live SQL queries if missing or outdated
  - Integrates with `.env` for dynamic configuration, avoiding `localhost` issues
  - Debug logging toggled via `DEBUG=true` in `.env` for troubleshooting

Core Metadata Functions:
  - save_metadata(meta): Inserts or updates a metadata row
  - load_metadata(table_name): Retrieves metadata for a table (or None if missing)
  - update_metadata(table_name, ...): Patches specific metadata fields
  - rebuild_metadata_row(table_name): Regenerates metadata from live DB stats
  - compute_sampling_period(row_count, min_ts, max_ts): Estimates milliseconds per sample
  - drop_metadata(table_name): Deletes a table's metadata row

Export Functions:
  - export_meta(table_name, path): Exports a table's metadata to a JSON file
  - export_all_metadata(path): Dumps all metadata rows to a JSON file

Utilities:
  - ensure_meta_table(): Creates `_timeseries_metadata` table if missing
  - pretty_print_metadata(meta): Pretty-prints metadata to stdout
  - TableMetadata: Dataclass for metadata rows with JSON serialization

Dependencies:
  - Standard Library: json, sys, os, logging, datetime, pathlib, dataclasses, typing
  - Third-Party: sqlalchemy, python-dotenv (via `config.py`)
  - Internal: config, api (for schema and stats in rebuild_metadata_row)
  - Requires Python 3.10+ with type annotations
  - Configured via `.env` for database settings
"""

# -----------------------------------------------------------------------
# Imports and Logging Setup
# -----------------------------------------------------------------------

# === Standard Library ===
import json
import sys
from datetime import datetime
from pathlib import Path
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

# === Third-Party Libraries ===
from sqlalchemy import create_engine, inspect, text, Engine
from sqlalchemy.exc import OperationalError
from .config import get_db_config, DBConfig
from .logger import logger

# === Type Aliases ===
Units = Dict[str, str | None]

# -----------------------------------------------------------------------
# Engine Helper: Create SQLAlchemy Connection
# -----------------------------------------------------------------------


def meta_engine(*, probe: bool = True, cfg: DBConfig | None = None) -> Engine:
    """
    Creates a SQLAlchemy engine for metadata operations.

    Args:
        probe: If True (default), verifies database connectivity.

    Returns:
        Engine: SQLAlchemy engine for database operations.

    Exits:
        If database is unreachable and `probe` is True, prints error and exits with status 1.
    """
    cfg = cfg or get_db_config()
    eng = create_engine(cfg.pg_dsn(), pool_pre_ping=True)

    if probe:
        try:
            with eng.connect():
                pass
        except OperationalError:
            print(
                "\nERROR: Database server is unreachable.\n"
                f"  Host: {cfg.host}\n"
                f"  Port: {cfg.postgres_port}\n"
                "Please check that Timescale/Postgres is running "
                "and network‑reachable.\n",
                file=sys.stderr,
            )
            sys.exit(1)

    return eng


# -----------------------------------------------------------------------
# Dataclass: TableMetadata + JSON Helpers
# -----------------------------------------------------------------------


@dataclass(slots=True)
class TableMetadata:
    """
    Represents a metadata row in `_timeseries_metadata`.

    Required fields: table_name, schema, datetime_col.
    Optional fields are auto-maintained or user-defined.

    Attributes:
        table_name: Name of the hypertable.
        schema: Dictionary of column names to SQL types.
        datetime_col: Name of the datetime column.
        row_count: Number of rows in the table (optional).
        min_time: Earliest timestamp (optional).
        max_time: Latest timestamp (optional).
        sampling_period_ms: Sampling interval in milliseconds (optional).
        units: Dictionary of column names to engineering units (optional).
        notes: User-defined notes (optional).
    """

    # required
    table_name: str
    schema: Dict[str, str]
    datetime_col: str

    # auto-maintained
    row_count: Optional[int] = None
    min_time: Optional[datetime] = None
    max_time: Optional[datetime] = None
    sampling_period_ms: Optional[int] = None  # ≈ seconds / sample

    # user-defined
    units: Optional[Units] = None
    notes: Optional[str] = None

    # JSON setting
    def to_json(self) -> str:
        def _ser(o: Any):
            if isinstance(o, datetime):
                return o.isoformat()
            raise TypeError(o)

        return json.dumps(asdict(self), default=_ser, indent=2, sort_keys=True)

    @staticmethod
    def from_row(row) -> "TableMetadata":
        d = dict(row._mapping)
        for col in ("schema", "units"):
            if d[col] and isinstance(d[col], str):
                d[col] = json.loads(d[col])
        return TableMetadata(**d)


# -----------------------------------------------------------------------
# Metadata Table Management
# -----------------------------------------------------------------------

_META_TABLE_DDL = """
CREATE TABLE IF NOT EXISTS _timeseries_metadata (
    table_name           TEXT     PRIMARY KEY,
    schema               JSONB    NOT NULL,
    datetime_col         TEXT     NOT NULL,
    row_count            BIGINT,
    min_time             TIMESTAMPTZ,
    max_time             TIMESTAMPTZ,
    sampling_period_ms   BIGINT,
    units                JSONB,
    notes                TEXT
);
"""


def ensure_meta_table(cfg: DBConfig | None = None) -> None:
    """
    Make sure the metadata registry exists.
    Creates `_timeseries_metadata` table if missing.

    """
    eng = meta_engine(cfg=cfg)
    insp = inspect(eng)

    if "_timeseries_metadata" not in insp.get_table_names():
        logger.debug("Creating _timeseries_metadata …")
        with eng.begin() as conn:
            conn.execute(text(_META_TABLE_DDL))
        logger.debug("Created _timeseries_metadata table")
    else:
        logger.debug("_timeseries_metadata already present.")


# -----------------------------------------------------------------------
# Metadata Write Operations
# -----------------------------------------------------------------------


def save_metadata(meta: TableMetadata, cfg: DBConfig | None = None) -> None:
    """
    Insert or update the registry row for `meta.table_name`.

    """

    if not isinstance(meta.schema, dict):
        raise ValueError("meta.schema must be a dictionary")
    if meta.units is not None and not isinstance(meta.units, dict):
        raise ValueError("meta.units must be a dictionary")

    sql = text("""
        INSERT INTO _timeseries_metadata (
            table_name,     schema,                datetime_col,
            row_count,      min_time,              max_time,
            sampling_period_ms,                   units,      notes)
        VALUES (
            :table_name,    CAST(:schema AS jsonb),:datetime_col,
            :row_count,     :min_time,             :max_time,
            :sampling_period_ms,  CAST(:units AS jsonb), :notes)
        ON CONFLICT (table_name) DO UPDATE SET
            schema               = EXCLUDED.schema,
            datetime_col         = EXCLUDED.datetime_col,
            row_count            = EXCLUDED.row_count,
            min_time             = EXCLUDED.min_time,
            max_time             = EXCLUDED.max_time,
            sampling_period_ms  = EXCLUDED.sampling_period_ms,
            units                = EXCLUDED.units,
            notes                = EXCLUDED.notes;
    """)

    # JSON-encode the dict fields before binding
    bind = {
        "table_name": meta.table_name,
        "schema": json.dumps(meta.schema) if meta.schema else None,
        "datetime_col": meta.datetime_col,
        "row_count": meta.row_count,
        "min_time": meta.min_time,
        "max_time": meta.max_time,
        "sampling_period_ms": meta.sampling_period_ms,
        "units": json.dumps(meta.units) if meta.units else None,
        "notes": meta.notes,
    }

    with meta_engine(cfg=cfg).begin() as conn:
        conn.execute(sql, bind)
    logger.debug("Saved metadata for table '%s'", meta.table_name)


# -----------------------------------------------------------------------
# Metadata Read & Update Operations
# -----------------------------------------------------------------------


def load_metadata(
    table_name: str,
    cfg: DBConfig | None = None,
) -> Optional[TableMetadata]:
    """
    Return metadata for `table_name` or **None** if not yet registered.
    """
    eng = meta_engine(cfg=cfg)
    with eng.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM _timeseries_metadata WHERE table_name = :tbl"),
            {"tbl": table_name},
        ).first()
    return TableMetadata.from_row(row) if row else None


def update_metadata(
    *,
    table_name: str,
    row_count: Optional[int] = None,
    min_time: Optional[datetime] = None,
    max_time: Optional[datetime] = None,
    units: Optional[Dict[str, str]] = None,
    notes: Optional[str] = None,
    cfg: DBConfig | None = None,
) -> None:
    """
    Patch *only* the provided fields; create the row if missing.

    Automatically recomputes `sampling_period_ms` when we have both
    `row_count` and a valid time span.
    """
    meta = load_metadata(table_name) or TableMetadata(
        table_name=table_name, schema={}, datetime_col=""
    )

    # apply patches
    if row_count is not None:
        meta.row_count = row_count
    if min_time is not None:
        meta.min_time = min_time
    if max_time is not None:
        meta.max_time = max_time
    if units is not None:
        if meta.units:
            # shallow merge
            merged = meta.units | units
        else:
            merged = units
        meta.units = merged
    if notes is not None:
        meta.notes = notes

    # recompute sampling
    if (
        meta.row_count is not None
        and meta.min_time is not None
        and meta.max_time is not None
    ):
        meta.sampling_period_ms = compute_sampling_period(
            meta.row_count, meta.min_time, meta.max_time
        )

    save_metadata(meta, cfg=cfg)


def drop_metadata(table_name: str, cfg: DBConfig | None = None) -> None:
    """
    Delete the metadata row for `table_name`.

    This does not delete the actual table, only its metadata.
    """
    eng = meta_engine(cfg=cfg)
    with eng.begin() as conn:
        conn.execute(
            text("DELETE FROM _timeseries_metadata WHERE table_name = :t"),
            {"t": table_name},
        )
    logger.debug("Dropped metadata for table '%s'", table_name)


# -----------------------------------------------------------------------
# Metadata Export Helpers
# -----------------------------------------------------------------------


def export_meta(
    table_name: str,
    path: Optional[Path] = None,
    cfg: DBConfig | None = None,
) -> str:
    """
    Pretty-print metadata; optionally save to a file.

    Returns the JSON string.
    """
    meta = load_metadata(table_name, cfg=cfg)
    if not meta:
        raise ValueError(f"No metadata found for table '{table_name}'.")
    js = meta.to_json()
    if path:
        path.write_text(js, encoding="utf-8")
        logger.info("Exported metadata to %s", path.resolve())
    return js


def export_all_metadata(path: Path, cfg: DBConfig | None = None) -> None:
    """
    Export every row from _timeseries_metadata into one pretty-printed JSON file.

    Parameters
    ----------
    path : Path
        Target file location (parent dirs are created automatically).

    The helper converts Timestamp / datetime objects to ISO-8601 strings and
    leaves nested dicts (e.g. “units”) intact.
    """

    eng = meta_engine(cfg=cfg)

    # --- pull the whole registry ----------------------------------------
    with eng.connect() as conn:
        rows = (
            conn.execute(
                text('SELECT * FROM "_timeseries_metadata" ORDER BY table_name;')
            )
            .mappings()
            .all()
        )

    if not rows:
        raise ValueError(
            "The _timeseries_metadata table is empty. Ensure tables are registered "
            "via `save_metadata` or `api.py` functions."
        )

    # --- ISO-convert and collect ----------------------------------------
    def iso(obj):
        return obj.isoformat() if hasattr(obj, "isoformat") else obj

    records = [{k: iso(v) for k, v in row.items()} for row in rows]

    # --- write out ------------------------------------------------------
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")

    logger.info("Exported full metadata registry to %s", path.resolve())


# -----------------------------------------------------------------------
# Re-build / reset a single metadata row
# -----------------------------------------------------------------------


def rebuild_metadata_row(table_name: str, cfg: DBConfig | None = None) -> None:
    """
    Regenerate any existing _timeseries_metadata row for *table_name*
    from live SQL statistics.

    The new row contains only the auto-derived core fields
    (schema, datetime_col, row_count, min/max/sampling_period).
    “units” and “notes” are left empty so the user can fill them later.
    """
    # === Internal Modules ===
    from .api import (
        get_table_schema,
        infer_plot_columns,
        query_table_metadata,
    )  # imported here to avoid circular deps

    # # Uncomment to allow this function to delete the existing row first
    # # (use with caution, e.g. if you want to reset the metadata)
    # with eng.begin() as conn:
    #     conn.execute(
    #         text('DELETE FROM _timeseries_metadata WHERE table_name = :t'),
    #         {"t": table_name},
    #     )

    # --- recompute live stats -----------------------------------------
    schema = get_table_schema(table_name)
    datetime_col, _, _ = infer_plot_columns(table_name)
    stats = query_table_metadata(table_name, datetime_col=datetime_col)

    meta = TableMetadata(
        table_name=table_name,
        schema=schema,
        datetime_col=datetime_col,
        row_count=stats["row_count"],
        min_time=stats["min_time"],
        max_time=stats["max_time"],
        sampling_period_ms=stats["sampling_period_ms"],
        units=None,
        notes=None,
    )
    save_metadata(meta, cfg=cfg)


# -----------------------------------------------------------------------
# Utility: Sampling Period, Pretty-Print
# -----------------------------------------------------------------------


def compute_sampling_period(
    row_count: int,
    min_ts: datetime,
    max_ts: datetime,
    *,
    min_rows: int = 50,
) -> Optional[int]:
    """
    Estimates sampling interval in milliseconds.

    Args:
        row_count: Number of rows in the table.
        min_ts: Earliest timestamp.
        max_ts: Latest timestamp.
        min_rows: Minimum rows required for calculation (default: 50).

    Returns:
        Optional[int]: Sampling interval in milliseconds, or None if row_count
                       is below min_rows or time span is invalid.
    """
    if row_count < min_rows:
        return None
    span = (max_ts - min_ts).total_seconds()
    if span <= 0:
        return None
    return int((span * 1000) / (row_count - 1))


def pretty_print_metadata(meta: "TableMetadata", *, stream=sys.stdout) -> None:
    """
    Pretty-prints a TableMetadata instance as JSON.

    Args:
        meta: TableMetadata object to print.
        stream: Output stream for printing (default: sys.stdout).
    """

    js = json.dumps(asdict(meta), indent=2, default=str)
    print(js, file=stream)
