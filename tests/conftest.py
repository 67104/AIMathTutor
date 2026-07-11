"""Shared pytest fixtures.

The ``db`` fixture points the database at a throwaway temp file, resets the
shared connection, and bootstraps a fresh schema — so DB tests never touch the
real app database and never leak state between tests.
"""

import pytest

from app.utils import paths
from app.database import connection


@pytest.fixture
def db(tmp_path, monkeypatch):
    dbfile = tmp_path / "test.db"
    monkeypatch.setattr(paths, "db_path", lambda: str(dbfile))
    connection.close()          # drop any existing shared connection
    connection.bootstrap()      # create schema + seed into the temp DB
    yield connection
    connection.close()


@pytest.fixture
def user(db):
    from app.database.repositories import profile_repo
    return profile_repo.create("Test", 12, 8)
