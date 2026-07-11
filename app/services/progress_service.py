"""Progress analytics: read attempts / daily_stats / gamification and turn them
into the numbers and series the Progress screen shows.

Everything degrades gracefully to zeros when there's no data yet.
"""

from datetime import date, timedelta

from app.database import connection

XP_PER_LEVEL = 500


def _scalar(query, params=(), default=0):
    row = connection.execute(query, params).fetchone()
    if row is None:
        return default
    val = row[0]
    return default if val is None else val


def summary(user_id):
    """Headline stats: totals, accuracy, avg time, streak, XP/level."""
    if not user_id:
        return _empty_summary()

    total = _scalar("SELECT COUNT(*) FROM attempts WHERE user_id=?", (user_id,))
    correct = _scalar("SELECT COUNT(*) FROM attempts WHERE user_id=? AND is_correct=1", (user_id,))
    avg_ms = _scalar("SELECT AVG(time_taken_ms) FROM attempts WHERE user_id=?", (user_id,))

    row = connection.execute(
        "SELECT total_xp, level, current_streak, longest_streak "
        "FROM gamification WHERE user_id=?", (user_id,)
    ).fetchone()
    total_xp = row["total_xp"] if row else 0
    level = row["level"] if row else 1
    streak = row["current_streak"] if row else 0
    longest = row["longest_streak"] if row else 0

    return {
        "total": total,
        "correct": correct,
        "wrong": total - correct,
        "accuracy": round(100 * correct / total) if total else 0,
        "avg_time_s": round(avg_ms / 1000, 1) if avg_ms else 0.0,
        "streak": streak,
        "longest_streak": longest,
        "total_xp": total_xp,
        "level": level,
        "xp_into_level": total_xp % XP_PER_LEVEL,
        "xp_per_level": XP_PER_LEVEL,
    }


def _empty_summary():
    return {"total": 0, "correct": 0, "wrong": 0, "accuracy": 0, "avg_time_s": 0.0,
            "streak": 0, "longest_streak": 0, "total_xp": 0, "level": 1,
            "xp_into_level": 0, "xp_per_level": XP_PER_LEVEL}


def weekly(user_id):
    """Attempts + correct for each of the last 7 days (oldest -> newest)."""
    labels, attempts, correct = [], [], []
    today = date.today()
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        iso = day.isoformat()
        labels.append(day.strftime("%a"))
        row = connection.execute(
            "SELECT attempts, correct FROM daily_stats WHERE user_id=? AND day=?",
            (user_id, iso),
        ).fetchone() if user_id else None
        attempts.append(row["attempts"] if row else 0)
        correct.append(row["correct"] if row else 0)
    return {"labels": labels, "attempts": attempts, "correct": correct}


def monthly(user_id):
    """Totals over the last 30 days."""
    if not user_id:
        return {"attempts": 0, "correct": 0, "accuracy": 0}
    since = (date.today() - timedelta(days=29)).isoformat()
    a = _scalar("SELECT SUM(attempts) FROM daily_stats WHERE user_id=? AND day>=?", (user_id, since))
    c = _scalar("SELECT SUM(correct) FROM daily_stats WHERE user_id=? AND day>=?", (user_id, since))
    return {"attempts": a, "correct": c, "accuracy": round(100 * c / a) if a else 0}


def topic_breakdown(user_id, min_attempts=2):
    """Return strong/weak topic names based on per-topic accuracy."""
    if not user_id:
        return {"strong": [], "weak": []}
    rows = connection.execute(
        "SELECT t.name AS name, SUM(a.is_correct) AS c, COUNT(*) AS n "
        "FROM attempts a JOIN topics t ON a.topic_id = t.id "
        "WHERE a.user_id=? GROUP BY t.id", (user_id,),
    ).fetchall()
    scored = [(r["name"], r["c"] / r["n"], r["n"]) for r in rows if r["n"] >= min_attempts]
    strong = [n for n, acc, _ in sorted(scored, key=lambda x: -x[1]) if acc >= 0.8]
    weak = [n for n, acc, _ in sorted(scored, key=lambda x: x[1]) if acc < 0.6]
    return {"strong": strong[:4], "weak": weak[:4]}
