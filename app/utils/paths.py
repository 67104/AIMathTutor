"""Cross-platform path resolution.

On Android the app can only write to its private ``user_data_dir``; on desktop
we keep the database next to the bundled schema in ``data/``. All path logic
lives here so nothing hardcodes ``C:\\...`` or ``/data/...`` (see
docs/PROBLEMS.md #14).
"""

import os

# Project root = two levels up from this file (app/utils/paths.py -> project).
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUNDLED_DATA = os.path.join(PROJECT_ROOT, "data")


def writable_dir():
    """Return a directory the app may write to (DB, captures)."""
    try:
        from kivymd.app import MDApp
        app = MDApp.get_running_app()
        if app is not None and app.user_data_dir:
            return app.user_data_dir
    except Exception:  # noqa: BLE001 - Kivy may not be running (tests)
        pass
    os.makedirs(BUNDLED_DATA, exist_ok=True)
    return BUNDLED_DATA


def db_path():
    return os.path.join(writable_dir(), "mathtutor.db")


def schema_path():
    return os.path.join(BUNDLED_DATA, "schema.sql")
