"""AI Math Tutor — application entry point (Phase 2).

Builds the KivyMD shell: a navigation drawer + a screen manager holding every
screen, with a bottom-navigation Home shell (Learn / Progress / Settings).

Run (desktop):  python main.py

Design:
  * Screen classes are instantiated in Python and their layouts come from
    ``<ClassName>`` rules in app/kv/*.kv (auto-applied by Kivy).
  * Custom widgets instantiated *inside* kv are registered with the Factory.
  * ``route()`` is the single navigation entry point used by cards + drawer.
"""

import os

from kivy.core.window import Window
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder

from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import MDNavigationLayout
from kivymd.uix.screenmanager import MDScreenManager

from app.utils import constants, theme
from app.utils.state import AppState

# Screen + widget classes
from app.widgets.cards import FeatureCard, StatTile, SectionCard
from app.widgets.bar_chart import WeeklyBarChart
from app.widgets.nav_drawer import NavDrawer
from app.screens.onboarding_screen import OnboardingScreen
from app.screens.home_screen import HomeScreen
from app.screens.ask_ai_screen import AskAIScreen
from app.screens.camera_screen import CameraScreen
from app.screens.practice_screen import PracticeScreen
from app.screens.olympiad_screen import OlympiadScreen
from app.screens.daily_challenge_screen import DailyChallengeScreen
from app.screens.achievements_screen import AchievementsScreen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KV_DIR = os.path.join(BASE_DIR, "app", "kv")

# kv files loaded in order (rule files first; root built in Python).
KV_FILES = [
    "common.kv",
    "onboarding.kv",
    "home.kv",
    "ask_ai.kv",
    "camera.kv",
    "practice.kv",
    "olympiad.kv",
    "daily.kv",
    "achievements.kv",
]

# Custom classes instantiated *by name inside kv* must be known to the Factory.
for _name, _cls in (
    ("FeatureCard", FeatureCard),
    ("StatTile", StatTile),
    ("SectionCard", SectionCard),
    ("WeeklyBarChart", WeeklyBarChart),
):
    Factory.register(_name, cls=_cls)


class MathTutorApp(MDApp):
    """Root application class."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = AppState()
        self.screen_manager = None
        self.nav_drawer = None

    def build(self):
        self.title = constants.APP_NAME
        theme.apply_theme(self.theme_cls, self.state.theme_style)

        # Activate the database (create schema + seed) and load any saved profile.
        self._bootstrap_database()

        # Desktop dev: phone-like portrait window. (Ignored on Android.)
        Window.size = (400, 760)

        for kv in KV_FILES:
            Builder.load_file(os.path.join(KV_DIR, kv))

        # Build the root: MDNavigationLayout( ScreenManager, NavDrawer )
        root = MDNavigationLayout()
        sm = MDScreenManager()
        sm.add_widget(OnboardingScreen(name="onboarding"))
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(AskAIScreen(name="ask_ai"))
        sm.add_widget(CameraScreen(name="camera"))
        sm.add_widget(PracticeScreen(name="practice"))
        sm.add_widget(OlympiadScreen(name="olympiad"))
        sm.add_widget(DailyChallengeScreen(name="daily"))
        sm.add_widget(AchievementsScreen(name="achievements"))

        drawer = NavDrawer()
        root.add_widget(sm)          # content first
        root.add_widget(drawer)      # then the drawer overlay

        self.screen_manager = sm
        self.nav_drawer = drawer

        # Start on onboarding if no profile, else Home.
        sm.current = "home" if self.state.has_profile else "onboarding"
        return root

    def on_start(self):
        # Warm up SymPy off the UI thread so the user's *first* solve is fast
        # (the first SymPy call in a process pays a one-time import/caching cost).
        from app.services import solver_service
        solver_service.solve_async("1 + 1", on_done=lambda _r: None,
                                   on_error=lambda _e: None)

    def _bootstrap_database(self):
        """Create/seed the DB and hydrate AppState from any saved profile."""
        try:
            from app.database import connection
            from app.database.repositories import profile_repo
            connection.bootstrap()
            row = profile_repo.get_active()
            if row is not None:
                self.state.set_profile(row["name"], row["age"], row["grade"])
                self.state.user_id = row["id"]
        except Exception as exc:  # noqa: BLE001 - app still works without DB
            print(f"[DB] bootstrap skipped: {exc}")

    # ---- Navigation API (used by cards, drawer, back buttons) ----

    def route(self, target):
        """Navigate. ``target`` is a screen name or ``tab:<name>`` for a Home tab."""
        if target.startswith("tab:"):
            tab = target.split(":", 1)[1]
            self.screen_manager.current = "home"
            Clock.schedule_once(
                lambda _dt: self.screen_manager.get_screen("home").switch_tab(tab), 0
            )
        else:
            self.screen_manager.current = target

    def go_home(self):
        self.route("tab:learn")

    def open_drawer(self):
        if self.nav_drawer:
            self.nav_drawer.set_state("open")

    def refresh_greeting(self):
        home = self.screen_manager.get_screen("home")
        label = home.ids.get("greeting_label")
        if label is not None:
            label.text = self.state.as_greeting()


if __name__ == "__main__":
    MathTutorApp().run()
