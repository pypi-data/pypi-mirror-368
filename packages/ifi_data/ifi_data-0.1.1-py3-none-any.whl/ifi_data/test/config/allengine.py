"""
tests/test_pgengine_all.py
============================================================
End-to-end smoke-test for credential resolution + connectivity.

Execution order
---------------
1. ENV  -> tests that pg_engine() works when all vars are exported
2. CACHE-> tests that it works when the TOML file exists (env cleared)
3. PROMPT -> tests that it falls back to the interactive wizard

The script never keeps your password on screen:
    – Mode-2 writes the cache (TOML) with 0600 permissions
    – Mode-3 writes a *fresh* cache at the end

Edit the three dummy credentials below so they point at your server
before running the test.
"""

from __future__ import annotations
import os, sys, shutil, getpass, textwrap
from pathlib import Path
from dataclasses import asdict
import tomli_w
from sqlalchemy import text
from ...config import DBConfig, _CACHE, get_db_config
from ...api import pg_engine


# ╭─────────────────────────────────────────────────────────────────╮
# │  CHANGE THESE ONCE THE SERVER (used in Mode-1 & Mode-2)         │
# ╰─────────────────────────────────────────────────────────────────╯
TEST_USER = "dbuser"
TEST_PASSWORD = "mypassword"
TEST_DB = "sensor_database"
TEST_HOST = "localhost"  # leave as-is unless remote
TEST_PORT = 5433  # leave default unless custom


# ──────────────────────────────────────────────────────────────────
def _banner(label: str) -> None:
    print("\n" + "-" * 60)
    print(f"{label:^60}")
    print("-" * 60 + "\n")


def _show_server_info() -> None:
    eng = pg_engine()
    try:
        with eng.connect() as conn:
            ver = conn.execute(text("select version()")).scalar()
            now = conn.execute(text("select now()")).scalar()
            rows = conn.execute(
                text("""
                   select table_name
                     from information_schema.tables
                    where table_schema='public'
                    order by table_name;
            """)
            ).fetchall()

        print("Connected OK")
        print("Server time  :", now)
        print("Postgres     :", ver.split(",")[0])
        print("Public tables:")
        for (tbl,) in rows:
            print("  •", tbl)
    finally:
        eng.dispose()


# ────────────────────────────────
#  MODE 1 – ENV-based credentials
# ────────────────────────────────
def mode_env() -> None:
    _banner("MODE 1  –  ENV variables only")

    # 1. wipe cache if present
    if _CACHE.exists():
        _CACHE.unlink()

    # 2. prepare environment variables
    os.environ["HOST"] = TEST_HOST
    os.environ["POSTGRES_USER"] = TEST_USER
    os.environ["POSTGRES_PASSWORD"] = TEST_PASSWORD
    os.environ["POSTGRES_DB"] = TEST_DB
    os.environ["POSTGRES_PORT"] = str(TEST_PORT)

    # 3. resolve + connect
    _show_server_info()


# ────────────────────────────────
#  MODE 2 – TOML cache only
# ────────────────────────────────
def mode_cache() -> None:
    _banner("MODE 2  –  TOML cache only")

    # 1. clear ENV entirely
    for v in (
        "HOST",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_PORT",
    ):
        os.environ.pop(v, None)

    # 2. write cache file (parent already ensured in config.py)
    cfg = DBConfig(TEST_USER, TEST_PASSWORD, TEST_DB, TEST_HOST, TEST_PORT)
    _CACHE.write_text(tomli_w.dumps(asdict(cfg)), encoding="utf-8")

    if os.name != "nt":
        _CACHE.chmod(0o600)

    # 3. resolve + connect
    _show_server_info()


# ────────────────────────────────
#  MODE 3 – Interactive prompt
# ────────────────────────────────
def mode_prompt() -> None:
    _banner("MODE 3  –  Interactive prompt")

    # 1. wipe env + cache
    for v in (
        "HOST",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_DB",
        "POSTGRES_PORT",
    ):
        os.environ.pop(v, None)
    if _CACHE.exists():
        _CACHE.unlink()

    print(
        textwrap.dedent(
            f"""
            Neither ENV vars nor cache are present – you should see the
            credential wizard now.  Enter the SAME credentials you used
            in Mode-1 so the DSN works.
            """
        )
    )

    # 2. resolve + connect  (this triggers the wizard)
    _show_server_info()


# ────────────────────────────────
#  CLI dispatcher
# ────────────────────────────────
def main() -> None:
    """
    Run:
        python tests/test_pgengine_all.py        # runs 1→2→3

    Or:
        python tests/test_pgengine_all.py env    # single mode
    """
    modes = {
        "env": mode_env,
        "cache": mode_cache,
        "prompt": mode_prompt,
    }

    if len(sys.argv) == 1:  # run all three
        for fn in modes.values():
            fn()
    elif sys.argv[1] in modes:
        modes[sys.argv[1]]()
    else:
        print("Usage: python test_pgengine_all.py [env|cache|prompt]")
        sys.exit(1)


if __name__ == "__main__":
    main()
