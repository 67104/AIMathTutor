"""Static app-wide constants and placeholder content for the UI (Phase 2).

Nothing here talks to the database yet — Phase 2 is the interface layer.
Real data wiring happens in later phases; for now these values let every
screen render with representative content.
"""

APP_NAME = "AI Math Tutor"
APP_TAGLINE = "Learn math, step by step"
APP_VERSION = "0.1.0"

# Home screen feature cards: (icon, title, subtitle, target screen name, color)
# Colors are RGBA 0..1. `target` matches a screen registered in the ScreenManager
# (or a special "tab:<name>" to switch a bottom-navigation tab on Home).
FEATURE_CARDS = [
    ("robot-outline",   "Ask AI",        "Type a question",      "ask_ai",       (0.40, 0.31, 0.85, 1)),
    ("camera-outline",  "Camera Solver", "Scan a problem",       "camera",       (0.14, 0.59, 0.85, 1)),
    ("pencil-outline",  "Practice",      "Graded questions",     "practice",     (0.13, 0.66, 0.52, 1)),
    ("trophy-outline",  "Olympiad",      "SOF prep",             "olympiad",     (0.90, 0.49, 0.13, 1)),
    ("star-outline",    "Daily",         "Today's challenge",    "daily",        (0.85, 0.27, 0.42, 1)),
    ("medal-outline",   "Achievements",  "Badges & XP",          "achievements", (0.55, 0.35, 0.80, 1)),
]

# Navigation drawer destinations: (icon, label, target)
DRAWER_ITEMS = [
    ("home-outline",     "Home",         "tab:learn"),
    ("robot-outline",    "Ask AI",       "ask_ai"),
    ("camera-outline",   "Camera Solver","camera"),
    ("pencil-outline",   "Practice",     "practice"),
    ("trophy-outline",   "Olympiad",     "olympiad"),
    ("star-outline",     "Daily",        "daily"),
    ("medal-outline",    "Achievements", "achievements"),
    ("chart-line",       "Progress",     "tab:progress"),
    ("cog-outline",      "Settings",     "tab:settings"),
]

GRADES = [str(g) for g in range(1, 13)]
DIFFICULTIES = ["Easy", "Medium", "Hard"]
OLYMPIAD_EXAMS = ["IMO", "NSO", "IEO", "IGKO"]

# ---- Placeholder content (replaced by real engines in Phases 3-7) ----

SAMPLE_SOLUTION = {
    "answer": "x = 4",
    "steps": [
        ("2x + 3 = 11", "Start with the given equation."),
        ("2x = 11 - 3", "Subtract 3 from both sides to isolate the x-term."),
        ("2x = 8", "Simplify the right-hand side."),
        ("x = 8 / 2", "Divide both sides by the coefficient 2."),
        ("x = 4", "Simplify to get the value of x."),
    ],
    "concept": ("A linear equation in one variable is solved by keeping the "
                "equation balanced: whatever you do to one side, you do to the "
                "other, until x stands alone."),
}

SAMPLE_PRACTICE_Q = {
    "prompt": "What is 3/4 + 1/8 ?",
    "options": ["7/8", "1/2", "5/8", "1"],
    "answer": "7/8",
}

SAMPLE_OLYMPIAD_Q = {
    "prompt": "If the sum of three consecutive even numbers is 84, what is the largest of them?",
    "options": ["26", "28", "30", "32"],
    "answer": "30",
}

SAMPLE_STATS = {
    "accuracy": 82,
    "solved": 214,
    "streak": 5,
    "xp": 320,
    "xp_to_next": 500,
    "level": 3,
    "strong": ["Algebra", "Fractions", "Arithmetic"],
    "weak": ["Geometry", "Probability"],
    "weekly": [12, 18, 9, 22, 15, 25, 20],  # attempts Mon..Sun
}

SAMPLE_ACHIEVEMENTS = [
    ("fire",         "7-Day Streak",   "Practiced every day for a week",   True),
    ("numeric-1-box","First 100 XP",   "Earned your first 100 XP",         True),
    ("bullseye-arrow","Sharpshooter",  "10 correct answers in a row",      True),
    ("owl",          "Night Owl",      "Solved a problem after 10pm",      False),
    ("rocket-launch","Level 5",        "Reach level 5",                    False),
]
