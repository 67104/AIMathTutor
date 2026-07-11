"""SQLite connection + one-time bootstrap.

A single shared connection is used app-wide. ``check_same_thread=False`` lets
worker threads record attempts; a lock serialises writes so we stay safe.
"""

import sqlite3
import threading

from app.utils import paths

_conn = None
_lock = threading.RLock()


def get_connection():
    """Return the shared SQLite connection (opening it on first use)."""
    global _conn
    with _lock:
        if _conn is None:
            _conn = sqlite3.connect(paths.db_path(), check_same_thread=False)
            _conn.row_factory = sqlite3.Row
            _conn.execute("PRAGMA foreign_keys = ON;")
        return _conn


def execute(query, params=(), commit=False):
    """Run a write/read query under the shared lock; return the cursor."""
    with _lock:
        conn = get_connection()
        cur = conn.execute(query, params)
        if commit:
            conn.commit()
        return cur


def bootstrap():
    """Create the schema (idempotent) and seed reference data."""
    with _lock:
        conn = get_connection()
        with open(paths.schema_path(), "r", encoding="utf-8") as fh:
            conn.executescript(fh.read())
        conn.commit()
    # Seed after the schema exists.
    from app.database import seed
    seed.run()


def close():
    global _conn
    with _lock:
        if _conn is not None:
            _conn.close()
            _conn = None
