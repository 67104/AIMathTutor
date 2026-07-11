"""First-run onboarding: collect Name, Age, Grade."""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class OnboardingScreen(MDScreen):
    """Captures the learner profile before entering the app."""

    def submit(self):
        """Validate inputs, store to app state, and route to Home."""
        name = self.ids.name_field.text.strip()
        age_raw = self.ids.age_field.text.strip()
        grade_raw = self.ids.grade_field.text.strip()

        # Minimal validation with inline error text (no crashes on bad input).
        ok = True
        if not name:
            self.ids.name_field.error = True
            ok = False
        age = self._to_int(age_raw, 3, 120)
        if age is None:
            self.ids.age_field.error = True
            ok = False
        grade = self._to_int(grade_raw, 1, 12)
        if grade is None:
            self.ids.grade_field.error = True
            ok = False
        if not ok:
            return

        app = MDApp.get_running_app()
        app.state.set_profile(name, age, grade)
        # Persist the profile so it's remembered next launch.
        try:
            from app.database.repositories import profile_repo
            app.state.user_id = profile_repo.create(app.state.name, age, grade)
        except Exception as exc:  # noqa: BLE001 - onboarding still works offline
            print(f"[DB] could not save profile: {exc}")
        app.refresh_greeting()
        app.route("tab:learn")

    @staticmethod
    def _to_int(raw, lo, hi):
        try:
            v = int(raw)
        except (TypeError, ValueError):
            return None
        return v if lo <= v <= hi else None
