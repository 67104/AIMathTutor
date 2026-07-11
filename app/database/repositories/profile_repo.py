"""Profile persistence: create/read the active learner and ensure a
gamification wallet exists for them.
"""

from app.database import connection


def get_active():
    """Return the active user Row, or None if no profile exists yet."""
    cur = connection.execute(
        "SELECT * FROM users WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
    )
    return cur.fetchone()


def create(name, age, grade):
    """Create a profile, make it the active one, and return its id."""
    # Only one active profile at a time.
    connection.execute("UPDATE users SET is_active = 0")
    cur = connection.execute(
        "INSERT INTO users (name, age, grade, is_active) VALUES (?, ?, ?, 1)",
        (name, age, grade), commit=True,
    )
    user_id = cur.lastrowid
    # Companion rows.
    connection.execute(
        "INSERT OR IGNORE INTO settings (user_id) VALUES (?)", (user_id,)
    )
    connection.execute(
        "INSERT OR IGNORE INTO gamification (user_id) VALUES (?)", (user_id,),
        commit=True,
    )
    return user_id


def update_grade_age(user_id, grade=None, age=None):
    if grade is not None:
        connection.execute("UPDATE users SET grade = ? WHERE id = ?", (grade, user_id))
    if age is not None:
        connection.execute("UPDATE users SET age = ? WHERE id = ?", (age, user_id))
    connection.get_connection().commit()
