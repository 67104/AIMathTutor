"""Tests for the database layer: bootstrap, profile, attempt recording."""

from app.database import connection
from app.database.repositories import profile_repo, attempt_repo


def test_bootstrap_creates_tables(db):
    tables = {r["name"] for r in connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    for expected in ("users", "attempts", "daily_stats", "gamification",
                     "topics", "achievements", "mock_tests"):
        assert expected in tables


def test_seed_populates_topics(db):
    n = connection.execute("SELECT COUNT(*) c FROM topics").fetchone()["c"]
    assert n >= 8


def test_profile_create_and_active(db):
    uid = profile_repo.create("Ana", 11, 6)
    active = profile_repo.get_active()
    assert active["id"] == uid
    assert active["name"] == "Ana"
    # Companion rows exist.
    assert connection.execute(
        "SELECT 1 FROM gamification WHERE user_id=?", (uid,)).fetchone()


def test_only_one_active_profile(db):
    profile_repo.create("First", 10, 5)
    second = profile_repo.create("Second", 12, 7)
    rows = connection.execute("SELECT COUNT(*) c FROM users WHERE is_active=1").fetchone()["c"]
    assert rows == 1
    assert profile_repo.get_active()["id"] == second


def test_record_attempt_updates_aggregates(user):
    attempt_repo.record(user, "algebra.linear_eq", "practice", "Easy", "4", True, 3000, 10)
    attempt_repo.record(user, "number.fractions", "practice", "Easy", "x", False, 5000, 0)

    n = connection.execute("SELECT COUNT(*) c FROM attempts").fetchone()["c"]
    assert n == 2

    ds = connection.execute("SELECT attempts, correct, xp FROM daily_stats").fetchone()
    assert ds["attempts"] == 2 and ds["correct"] == 1 and ds["xp"] == 10

    wallet = attempt_repo.get_wallet(user)
    assert wallet["total_xp"] == 10
    assert wallet["current_streak"] >= 1
