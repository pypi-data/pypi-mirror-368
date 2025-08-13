"""
pgengine.py  –  Quick connectivity smoke-test
================================================

Run it:

    python pgengine.py

What it does
------------
• Uses api.pg_engine()  → credentials are resolved in this order:
    1. Explicit overrides (none here)
    2. Environment variables  (POSTGRES_USER, POSTGRES_PASSWORD, …)
    3. $HOME/.timescale_ingest.toml  (created automatically after first prompt)
    4. Interactive prompt (only first time)

• On success prints:
    - server version
    - current server timestamp (SELECT now())
    - list of tables in the *public* schema

• On failure shows the error and exits with code 1.
"""

from ...api import pg_engine
from sqlalchemy import text
import sys


def main() -> None:
    try:
        engine = pg_engine()       # may trigger the credential wizard
    except Exception as exc:
        print("Could not build engine –", exc)
        sys.exit(1)

    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version()")).scalar()
            now     = conn.execute(text("SELECT now()")).scalar()

            print("Connected OK")
            print("Server time  :", now)
            print("Postgres     :", version.split(',')[0])

            rows = conn.execute(text("""
                SELECT table_name
                  FROM information_schema.tables
                 WHERE table_schema = 'public'
                 ORDER BY table_name;
            """)).fetchall()

            if rows:
                print("Public tables:")
                for (tbl,) in rows:
                    print("  •", tbl)
            else:
                print("(no tables in public schema)")

    except Exception as exc:
        print("Query failed –", exc)
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
