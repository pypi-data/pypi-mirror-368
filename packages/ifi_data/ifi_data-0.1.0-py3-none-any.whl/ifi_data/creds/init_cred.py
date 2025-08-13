"""
init_cred.py
------------------
Run this once to enter (or change) the Postgres
credentials that all API / CLI calls will use.

The script invokes DBConfig.prompt(), which:
  1. Loads credentials from .env or cache, if available, and asks to confirm
  2. Prompts for user / password / database / host / port if needed
  3. Saves to user cache (e.g., %LOCALAPPDATA%\ifi_data\.timescale_ingest.toml on Windows)
  4. Quits.
"""

from ..config import DBConfig, _CACHE
def main() -> None:
    # Force the wizard and let it write the cache
    DBConfig.prompt()
    print(f"\nCredentials stored in {_CACHE.resolve()}")

if __name__ == "__main__":
    main()