"""In-memory application state for Phase 2.

This is a lightweight stand-in for the persistence layer. In later phases the
profile/settings/progress read and write through ``app/database`` repositories;
for the UI phase we keep them in a simple object so screens have something to
bind to and mutate.
"""

from app.utils import theme


class AppState:
    """Holds the current session's profile + settings in memory."""

    def __init__(self):
        # Profile (collected in Onboarding). None until set.
        self.user_id = None
        self.name = None
        self.age = None
        self.grade = None

        # Settings
        self.theme_style = "Light"          # "Light" | "Dark"
        self.font_scale = theme.FONT_SCALE_DEFAULT
        self.notifications_on = True
        self.sound_on = True

    @property
    def has_profile(self):
        return bool(self.name and self.grade)

    def set_profile(self, name, age, grade):
        self.name = (name or "").strip() or "Learner"
        self.age = age
        self.grade = grade

    def as_greeting(self):
        grade = f"Grade {self.grade}" if self.grade else "Learner"
        return f"Hi {self.name or 'there'} • {grade}"
