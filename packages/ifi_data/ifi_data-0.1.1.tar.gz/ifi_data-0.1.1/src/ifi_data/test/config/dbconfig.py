from pathlib import Path
import os, getpass
from ...config import get_db_config

# 1. clean slate
for v in ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"):
    os.environ.pop(v, None)

# Remove the cache file from api/env instead of home directory
cache_path = Path(__file__).parent.parent.parent.parent / "env" / ".timescale_ingest.toml"
cache_path.unlink(missing_ok=True)

print("\n--- first call (expects prompt) ---")
cfg = get_db_config()
print("DSN:", cfg.pg_dsn())

print("\n--- second call (should be silent) ---")
print("DSN:", get_db_config().pg_dsn())