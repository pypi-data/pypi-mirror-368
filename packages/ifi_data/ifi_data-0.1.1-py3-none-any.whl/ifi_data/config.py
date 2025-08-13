"""
config.py (Configuration Management Module)

Overview:
  This module manages configuration for PostgreSQL, PostgREST, and Grafana connections,
  providing a centralized, dynamic configuration system for the TimescaleDB ingestion suite.
  It is used by `api.py`, `metadata.py` and `fastapi_app.py` to ensure consistent access
  to database and service endpoints.

  Configurations are resolved dynamically from environment variables or interactive prompts,
  with no reliance on cached configuration files (e.g., `config.toml`). Optional overrides
  can be passed programmatically for flexibility in scripts or testing.

Resolution Order:
  1. Explicit keyword overrides (e.g., get_db_config(host="..."))
  2. Environment variables (POSTGRES_USER, POSTGRES_DB, etc.)
  3. Interactive prompt (if required fields are missing)

Key Features:
  - Loads credentials and network settings from `.env` or user input
  - Supports PostgreSQL, PostgREST, and Grafana connection details
  - Provides helper methods for:
      - Generating SQLAlchemy DSN for PostgreSQL
      - Constructing PostgREST and Grafana URLs
      - Exporting configuration as environment variables for subprocesses
  - Validates port inputs and ensures non-empty required fields
  - Dynamic host resolution to avoid `localhost` issues (e.g., Docker compatibility)
  - Debug logging toggled via `DEBUG=true` in `.env` for troubleshooting

Core Components:
  - DBConfig: Dataclass for storing configuration
      - Required: user, password, database, grafana_admin_user, grafana_admin_password
      - Optional (with defaults): host, port, postgrest_port, grafana_port
      - Methods:
          - pg_dsn(): Returns SQLAlchemy PostgreSQL DSN
          - postgrest_url: Property for PostgREST URL
          - grafana_base_url: Property for Grafana URL
          - to_env(): Exports config as environment variable dictionary
  - get_db_config(**overrides): Main entrypoint to load or prompt for config
  - Helper Methods:
      - _env_var(key, default): Retrieves environment variables with defaults
      - from_env(): Loads config from environment variables
      - prompt(): Collects config via interactive prompts

Environment Variables:
  - POSTGRES_USER: Database username (required)
  - POSTGRES_PASSWORD: Database password (required)
  - POSTGRES_DB: Database name (required)
  - GF_SECURITY_ADMIN_USER: Grafana admin username (required)
  - GF_SECURITY_ADMIN_PASSWORD: Grafana admin password (required)
  - HOST: Database host (default: localhost)
  - POSTGRES_PORT: Database port (default: 5433)
  - POSTGREST_PORT: PostgREST port (default: 3006)
  - GRAFANA_PORT: Grafana port (default: 3011)
  - DEBUG: Enable debug logging if 'true'

Dependencies:
  - Standard Library: getpass, os, logging, pathlib, platformdirs
  - Third-Party: tomli, tomli_w, python-dotenv (for potential future config saving)
  - Requires Python 3.10+ with type annotations
  - Configured via `.env` for all connection settings
"""

from __future__ import annotations
import getpass
from dataclasses import dataclass, asdict, replace
from pathlib import Path
from platformdirs import user_cache_dir
import tomli as tomllib
import tomli_w
from dotenv import dotenv_values

from .logger import logger

ENV_FILE_NAME = ".env"

# Cache file in OS-specific user cache directory
_CACHE = Path(user_cache_dir("timescale_ingest", "timescale")) / "config.toml"
_CACHE.parent.mkdir(parents=True, exist_ok=True)

# Default values for environment variables
_ENV_DEFAULTS = {
    "HOST": "localhost",
    "POSTGRES_PORT": "5433",
    "POSTGREST_PORT": "3006",
    "GRAFANA_PORT": "3011",
}


@dataclass(slots=True, frozen=False)
class DBConfig:
    """
    Stores configuration for PostgreSQL, PostgREST, and Grafana connections.

    Attributes:
        user: PostgreSQL username.
        password: PostgreSQL password.
        database: PostgreSQL database name.
        grafana_admin_user: Grafana admin username.
        grafana_admin_password: Grafana admin password.
        host: Database host (default: 'localhost').
        port: PostgreSQL port (default: 5433).
        postgrest_port: PostgREST port (default: 3006).
        grafana_port: Grafana port (default: 3011).
    """

    # Required fields
    postgres_user: str
    postgres_password: str
    postgres_database: str
    grafana_admin_user: str
    grafana_admin_password: str
    host: str = "localhost"
    postgres_port: int = 5433
    postgrest_port: int = 3006  # PostgREST port
    grafana_port: int = 3011  # Grafana port

    # Helpers
    def pg_dsn(self) -> str:
        """Returns SQLAlchemy DSN for Postgres."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.host}:{self.postgres_port}/{self.postgres_database}"

    @property
    def postgrest_url(self) -> str:
        """Returns PostgREST URL."""
        logger.debug(
            f"Building PostgREST URL with host={self.host}, port={self.postgrest_port}"
        )
        return f"http://{self.host}:{self.postgrest_port}"

    @property
    def grafana_base_url(self) -> str:
        """Returns Grafana URL."""
        return f"http://{self.host}:{self.grafana_port}"

    def to_env(self) -> dict[str, str]:
        """Returns environment variables for subprocesses."""
        return {
            "HOST": self.host,
            "POSTGRES_USER": self.postgres_user,
            "POSTGRES_PASSWORD": self.postgres_password,
            "POSTGRES_DB": self.postgres_database,
            "POSTGRES_PORT": str(self.postgres_port),
            "POSTGREST_URL": self.postgrest_url,
            "GRAFANA_BASE_URL": self.grafana_base_url,
            "GF_SECURITY_ADMIN_USER": self.grafana_admin_user,
            "GF_SECURITY_ADMIN_PASSWORD": self.grafana_admin_password,
            "PGRST_DB_URI": self.pg_dsn(),
        }

    @classmethod
    def _env_var(cls, key: str, default: str | None = None) -> str:
        """
        Gets environment variable or default if provided.
        """
        config = dotenv_values(ENV_FILE_NAME)
        envvars = config.get(key, default or _ENV_DEFAULTS.get(key, ""))
        if not envvars:
            raise ValueError(f"Missing environment variable: {key}")
        return envvars

    @classmethod
    def from_env(cls) -> "DBConfig | None":
        """
        Loads config from environment variables if all required fields are present.
        """
        config = dotenv_values(
            ENV_FILE_NAME
        )  # Auto-detect .env in current or parent directories
        required = [
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
            "GF_SECURITY_ADMIN_USER",
            "GF_SECURITY_ADMIN_PASSWORD",
        ]
        if not all(config.get(k) for k in required):
            logger.debug("Missing required environment variables: %s", required)
            return None

        try:
            postgres_port = config.get("POSTGRES_PORT", cls._env_var("POSTGRES_PORT"))
            if postgres_port is None:
                raise ValueError("Missing required environment variable: POSTGRES_PORT")

            postgrest_port = config.get(
                "POSTGREST_PORT", cls._env_var("POSTGREST_PORT")
            )
            if postgrest_port is None:
                raise ValueError(
                    "Missing required environment variable: POSTGREST_PORT"
                )

            grafana_port = config.get("GRAFANA_PORT", cls._env_var("GRAFANA_PORT"))
            if grafana_port is None:
                raise ValueError("Missing required environment variable: GRAFANA_PORT")

            try:
                postgres_port = int(postgres_port)
                postgrest_port = int(postgrest_port)
                grafana_port = int(grafana_port)
            except Exception as e:
                raise ValueError(f"Cannot convert port values to int: {e}")

            if not all(1 <= p <= 65535 for p in [postgrest_port, grafana_port]):
                raise ValueError("Ports must be between 1 and 65535")

            postgres_user = config["POSTGRES_USER"]
            if postgres_user is None:
                raise ValueError("Missing required environment variable: POSTGRES_USER")

            postgres_password = config["POSTGRES_PASSWORD"]
            if postgres_password is None:
                raise ValueError(
                    "Missing required environment variable: POSTGRES_PASSWORD"
                )

            postgres_db = config["POSTGRES_DB"]
            if postgres_db is None:
                raise ValueError("Missing required environment variable: POSTGRES_DB")

            grafana_admin_user = config["GF_SECURITY_ADMIN_USER"]
            if grafana_admin_user is None:
                raise ValueError(
                    "Missing required environment variable: GF_SECURITY_ADMIN_USER"
                )

            grafana_admin_password = config["GF_SECURITY_ADMIN_PASSWORD"]
            if grafana_admin_password is None:
                raise ValueError(
                    "Missing required environment variable: GF_SECURITY_ADMIN_PASSWORD"
                )

            host = config.get("HOST", cls._env_var("HOST"))
            if host is None:
                raise ValueError("Missing required environment variable: HOST")

            return cls(
                host=host,
                postgres_user=postgres_user,
                postgres_password=postgres_password,
                postgres_database=postgres_db,
                grafana_admin_user=grafana_admin_user,
                grafana_admin_password=grafana_admin_password,
                postgrest_port=postgrest_port,
                grafana_port=grafana_port,
            )
        except ValueError as e:
            logger.debug("Invalid port values in environment variables: %s", e)
            return None

    @classmethod
    def from_cache(cls) -> "DBConfig | None":
        """
        Loads config from cache file if it exists and is valid.
        """

        if not _CACHE.exists() or _CACHE.stat().st_size == 0:
            logger.debug(f"No cache file found at {_CACHE}")
            return None
        try:
            return cls(**tomllib.loads(_CACHE.read_text()))
        except tomllib.TOMLDecodeError:
            logger.debug(f"Invalid TOML in cache file {_CACHE}, ignoring")
            return None

    @classmethod
    def prompt(cls) -> "DBConfig":
        """
        Prompts user for config and saves to cache.
        """

        print(f"\nFirst-time setup – credentials will be cached in {_CACHE}")
        while True:
            user = input("  Postgres user: ").strip()
            if user:
                break
            print("  Postgres user cannot be empty.")
        while True:
            password = getpass.getpass("  Postgres password: ").strip()
            if password:
                break
            print("  Postgres password cannot be empty.")
        while True:
            database = input("  Postgres database: ").strip()
            if database:
                break
            print("  Postgres database cannot be empty.")
        while True:
            graf_u = input("  Grafana admin user: ").strip()
            if graf_u:
                break
            print("  Grafana admin user cannot be empty.")
        while True:
            graf_pwd = getpass.getpass("  Grafana admin password: ").strip()
            if graf_pwd:
                break
            print("  Grafana admin password cannot be empty.")
        host = input("  Host [localhost]: ").strip() or _ENV_DEFAULTS["HOST"]

        # Validate port inputs
        while True:
            try:
                port = (
                    input("  Postgres port [5433]: ").strip()
                    or _ENV_DEFAULTS["POSTGRES_PORT"]
                )
                port = int(port)
                if not 1 <= port <= 65535:
                    raise ValueError("Port must be between 1 and 65535.")
                break
            except ValueError:
                print("  Please enter a valid port number.")
        while True:
            try:
                pgrst_p = (
                    input("  PostgREST port [3006]: ").strip()
                    or _ENV_DEFAULTS["POSTGREST_PORT"]
                )
                pgrst_p = int(pgrst_p)
                if not 1 <= pgrst_p <= 65535:
                    raise ValueError("Port must be between 1 and 65535.")
                break
            except ValueError:
                print("  Please enter a valid port number.")
        while True:
            try:
                graf_p = (
                    input("  Grafana port [3011]: ").strip()
                    or _ENV_DEFAULTS["GRAFANA_PORT"]
                )
                graf_p = int(graf_p)
                if not 1 <= graf_p <= 65535:
                    raise ValueError("Port must be between 1 and 65535.")
                break
            except ValueError:
                print("  Please enter a valid port number.")

        cfg = cls(
            user, password, database, graf_u, graf_pwd, host, port, pgrst_p, graf_p
        )

        with _CACHE.open("wb") as fp:
            tomli_w.dump(asdict(cfg), fp, multiline_strings=True)

        logger.debug(f"Config saved to {_CACHE}")
        return cfg


def get_db_config(**overrides) -> DBConfig:
    """
    Loads and returns a DBConfig object, logging its source.

    Resolves configuration from:
      1. Cache file (`~/.timescale_ingest/config.toml`)
      2. Environment variables (`.env`)
      3. Interactive prompts (saved to cache)

    Args:
        **overrides: Optional keyword arguments to override config fields
                     (e.g., host='dbhost', port=5432).

    Returns:
        DBConfig: Configuration object for database and services.
    """

    # Log the config sources once
    logged_config_source = False

    cfg = DBConfig.from_env()
    if cfg:
        src = "environment variables"
    else:
        cfg = DBConfig.from_cache()
        if cfg:
            src = f"cache file {_CACHE}"
        else:
            cfg = DBConfig.prompt()
            src = "interactive prompt"

    # the args passed, if any -- get_db_config(host="dbhoost", port=5555)
    if overrides:
        cfg = replace(cfg, **{k: v for k, v in overrides.items() if v is not None})
        src += " + overrides"

    # final notice
    if not logged_config_source:
        logger.info(f"Config loaded from {src}")
        logged_config_source = True
    logger.debug(f"Loaded config details: {asdict(cfg)}")

    return cfg

def get_config_file_path() -> Path:
    return _CACHE

if __name__ == "__main__":
    # print config path
    print(get_config_file_path())
