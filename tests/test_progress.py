"""Tests for progress analytics + gamification evaluation + mock tests."""

from app.database.repositories import attempt_repo
from app.services import progress_service, gamification_service, olympiad_service


def _seed(user):
    # Strong topic (5/5), weak topic (1/4), plus more correct to pass 100 XP.
    for _ in range(5):
        attempt_repo.record(user, "algebra.linear_eq", "practice", "Medium", "x", True, 3000, 10)
    for i in range(4):
        attempt_repo.record(user, "number.fractions", "practice", "Easy", "y", i == 0, 4000, 10 if i == 0 else 0)
    for _ in range(6):
        attempt_repo.record(user, "number.exponents", "practice", "Hard", "z", True, 2500, 10)


def test_summary_totals(user):
    _seed(user)
    s = progress_service.summary(user)
    assert s["total"] == 15
    assert s["correct"] == 12
    assert s["accuracy"] == round(100 * 12 / 15)
    assert s["total_xp"] == 120


def test_weekly_series(user):
    _seed(user)
    wk = progress_service.weekly(user)
    assert len(wk["labels"]) == 7
    assert wk["attempts"][-1] == 15   # all recorded today
    assert wk["correct"][-1] == 12


def test_topic_breakdown_strong_weak(user):
    _seed(user)
    tb = progress_service.topic_breakdown(user)
    assert "Linear Equations" in tb["strong"]
    assert "Fractions" in tb["weak"]


def test_achievement_unlocks_first_100_xp(user):
    _seed(user)   # 120 XP
    newly = gamification_service.evaluate(user)
    assert "first_100_xp" in newly
    badges = gamification_service.list_badges(user)
    assert len(badges) == 5
    assert any(unlocked for *_, unlocked in badges)


def test_mock_test_scores_and_records(user):
    m = olympiad_service.new_mock("IMO", 1, 8, user, num_questions=5, duration_s=300)
    while m.current() is not None:
        q = m.questions[m.idx]
        m.answer(q.answer)          # answer everything correctly
    results = m.finish()
    assert results["score"] == 5
    assert results["accuracy"] == 100
    assert results["weak_topics"] == []
