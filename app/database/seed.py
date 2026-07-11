"""Seed reference tables (topics, achievements) — idempotent.

Topic ``code`` values match the codes the question generator tags questions
with, so attempts can be grouped by topic for weak-/strong-topic analytics
(Phase 7).
"""

from app.database import connection

# (code, name, category, min_grade, max_grade)
TOPICS = [
    ("arithmetic.add_sub", "Addition & Subtraction", "Arithmetic", 1, 6),
    ("arithmetic.mul_div", "Multiplication & Division", "Arithmetic", 2, 7),
    ("number.fractions", "Fractions", "Number", 3, 8),
    ("number.decimals", "Decimals", "Number", 4, 8),
    ("number.percentage", "Percentages", "Number", 5, 9),
    ("number.exponents", "Exponents & Powers", "Number", 6, 10),
    ("algebra.linear_eq", "Linear Equations", "Algebra", 6, 10),
    ("algebra.simplify", "Algebraic Simplification", "Algebra", 7, 10),
    ("algebra.quadratic", "Quadratic Equations", "Algebra", 8, 12),
    ("geometry.pythagoras", "Pythagoras Theorem", "Geometry", 7, 10),
]

# (code, title, description, icon, xp_reward)
ACHIEVEMENTS = [
    ("streak_7", "7-Day Streak", "Practice every day for a week", "fire", 50),
    ("first_100_xp", "First 100 XP", "Earn your first 100 XP", "numeric-1-box", 20),
    ("sharpshooter", "Sharpshooter", "10 correct answers in a row", "bullseye-arrow", 40),
    ("night_owl", "Night Owl", "Solve a problem after 10pm", "owl", 15),
    ("level_5", "Level 5", "Reach level 5", "rocket-launch", 60),
]


def run():
    for code, name, cat, lo, hi in TOPICS:
        connection.execute(
            "INSERT OR IGNORE INTO topics (code, name, category, min_grade, max_grade) "
            "VALUES (?, ?, ?, ?, ?)",
            (code, name, cat, lo, hi),
        )
    for code, title, desc, icon, xp in ACHIEVEMENTS:
        connection.execute(
            "INSERT OR IGNORE INTO achievements (code, title, description, icon, xp_reward) "
            "VALUES (?, ?, ?, ?, ?)",
            (code, title, desc, icon, xp),
        )
    connection.get_connection().commit()
