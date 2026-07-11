"""Attempt persistence + the aggregates that hang off each attempt.

``attempts`` is the source of truth. On every insert we also update the
denormalised ``daily_stats`` cache and the ``gamification`` wallet (XP, level,
streak) so Progress/Achievements (Phase 7) read instantly. A day-boundary
streak update keeps the streak correct across sessions.
"""

from datetime import date, timedelta

from app.database import connection

XP_PER_LEVEL = 500  # simple linear leveling


def _topic_id(topic_code):
    if not topic_code:
        return None
    cur = connection.execute("SELECT id FROM topics WHERE code = ?", (topic_code,))
    row = cur.fetchone()
    return row["id"] if row else None


def record(user_id, topic_code, mode, difficulty, given_answer,
           is_correct, time_taken_ms, xp_awarded):
    """Insert an attempt and update daily_stats + gamification. Returns dict."""
    if not user_id:
        return {"total_xp": 0, "level": 1, "current_streak": 0}

    topic_id = _topic_id(topic_code)
    today = date.today().isoformat()

    connection.execute(
        "INSERT INTO attempts (user_id, topic_id, mode, difficulty, given_answer, "
        "is_correct, time_taken_ms, xp_awarded) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (user_id, topic_id, mode, difficulty, str(given_answer),
         1 if is_correct else 0, int(time_taken_ms), int(xp_awarded)),
    )

    # daily_stats upsert
    connection.execute(
        "INSERT INTO daily_stats (user_id, day, attempts, correct, total_time_ms, xp) "
        "VALUES (?, ?, 1, ?, ?, ?) "
        "ON CONFLICT(user_id, day) DO UPDATE SET "
        "attempts = attempts + 1, correct = correct + ?, "
        "total_time_ms = total_time_ms + ?, xp = xp + ?",
        (user_id, today, 1 if is_correct else 0, int(time_taken_ms), int(xp_awarded),
         1 if is_correct else 0, int(time_taken_ms), int(xp_awarded)),
    )

    _update_gamification(user_id, xp_awarded, today)
    connection.get_connection().commit()
    return get_wallet(user_id)


def _update_gamification(user_id, xp_awarded, today):
    cur = connection.execute(
        "SELECT total_xp, current_streak, longest_streak, last_active_day "
        "FROM gamification WHERE user_id = ?", (user_id,)
    )
    row = cur.fetchone()
    if row is None:
        connection.execute(
            "INSERT INTO gamification (user_id) VALUES (?)", (user_id,)
        )
        total_xp, streak, longest, last_day = 0, 0, 0, None
    else:
        total_xp = row["total_xp"]
        streak = row["current_streak"]
        longest = row["longest_streak"]
        last_day = row["last_active_day"]

    # Streak logic: same day -> unchanged; yesterday -> +1; older/none -> reset to 1.
    if last_day == today:
        new_streak = max(streak, 1)
    elif last_day == (date.today() - timedelta(days=1)).isoformat():
        new_streak = streak + 1
    else:
        new_streak = 1

    new_total = total_xp + int(xp_awarded)
    new_level = max(1, new_total // XP_PER_LEVEL + 1)
    connection.execute(
        "UPDATE gamification SET total_xp = ?, level = ?, current_streak = ?, "
        "longest_streak = ?, last_active_day = ? WHERE user_id = ?",
        (new_total, new_level, new_streak, max(longest, new_streak), today, user_id),
    )


def get_wallet(user_id):
    cur = connection.execute(
        "SELECT total_xp, level, current_streak, longest_streak "
        "FROM gamification WHERE user_id = ?", (user_id,)
    )
    row = cur.fetchone()
    if row is None:
        return {"total_xp": 0, "level": 1, "current_streak": 0, "longest_streak": 0}
    return dict(row)
