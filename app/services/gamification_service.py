"""Gamification: evaluate achievement conditions against the DB and expose the
badge list (locked/unlocked) for the Achievements screen.

Achievements unlock as a *badge* (the XP that earns them already lives in the
gamification wallet from attempts, so we don't double-count XP here).
"""

from app.database import connection


def _wallet(user_id):
    row = connection.execute(
        "SELECT total_xp, level, current_streak, longest_streak "
        "FROM gamification WHERE user_id=?", (user_id,)
    ).fetchone()
    if row is None:
        return {"total_xp": 0, "level": 1, "current_streak": 0, "longest_streak": 0}
    return dict(row)


def _max_correct_run(user_id):
    rows = connection.execute(
        "SELECT is_correct FROM attempts WHERE user_id=? ORDER BY id", (user_id,)
    ).fetchall()
    best = run = 0
    for r in rows:
        run = run + 1 if r["is_correct"] else 0
        best = max(best, run)
    return best


def _has_night_attempt(user_id):
    return connection.execute(
        "SELECT 1 FROM attempts WHERE user_id=? AND CAST(strftime('%H', created_at) AS INT) >= 22 LIMIT 1",
        (user_id,),
    ).fetchone() is not None


def evaluate(user_id):
    """Unlock any newly-satisfied achievements. Returns list of unlocked codes."""
    if not user_id:
        return []
    w = _wallet(user_id)
    satisfied = {
        "first_100_xp": w["total_xp"] >= 100,
        "level_5": w["level"] >= 5,
        "streak_7": max(w["current_streak"], w["longest_streak"]) >= 7,
        "sharpshooter": _max_correct_run(user_id) >= 10,
        "night_owl": _has_night_attempt(user_id),
    }
    already = {
        r["code"] for r in connection.execute(
            "SELECT a.code FROM user_achievements ua "
            "JOIN achievements a ON a.id = ua.achievement_id WHERE ua.user_id=?",
            (user_id,),
        ).fetchall()
    }
    newly = []
    for code, ok in satisfied.items():
        if ok and code not in already:
            aid = connection.execute("SELECT id FROM achievements WHERE code=?", (code,)).fetchone()
            if aid:
                connection.execute(
                    "INSERT OR IGNORE INTO user_achievements (user_id, achievement_id) VALUES (?, ?)",
                    (user_id, aid["id"]),
                )
                newly.append(code)
    if newly:
        connection.get_connection().commit()
    return newly


def list_badges(user_id):
    """Return [(title, description, icon, unlocked_bool), ...] for display."""
    evaluate(user_id)  # keep unlocks fresh on view
    rows = connection.execute(
        "SELECT a.title, a.description, a.icon, "
        "  (SELECT 1 FROM user_achievements ua WHERE ua.achievement_id=a.id AND ua.user_id=?) AS unlocked "
        "FROM achievements a ORDER BY a.id",
        (user_id,) if user_id else (None,),
    ).fetchall()
    return [(r["title"], r["description"], r["icon"], bool(r["unlocked"])) for r in rows]
