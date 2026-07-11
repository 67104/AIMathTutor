"""Home shell: top app bar + bottom navigation (Learn / Progress / Settings).

All three tabs' content lives inside the ``<HomeScreen>`` kv rule so their
``ids`` share one scope (HomeScreen). Progress content is now populated from the
real analytics in ``progress_service`` (Phase 7); the feature cards come from
``constants.FEATURE_CARDS``.
"""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen

from app.utils import constants, theme
from app.services import progress_service
from app.widgets.cards import FeatureCard


class HomeScreen(MDScreen):
    """Container for the bottom-navigation shell + all three tab contents."""

    def on_pre_enter(self, *args):
        self._populate_cards()
        self.refresh_progress()
        MDApp.get_running_app().refresh_greeting()

    def _populate_cards(self):
        grid = self.ids.get("card_grid")
        if grid is None or grid.children:
            return
        for icon, title, subtitle, target, color in constants.FEATURE_CARDS:
            grid.add_widget(
                FeatureCard(
                    icon=icon, title=title, subtitle=subtitle,
                    target=target, card_color=color,
                )
            )

    def refresh_progress(self):
        """Pull live stats/charts from the DB into the Learn + Progress tabs."""
        app = MDApp.get_running_app()
        uid = app.state.user_id
        s = progress_service.summary(uid)

        # Learn-tab header (level + XP bar)
        if "level_xp_label" in self.ids:
            self.ids.level_xp_label.text = (
                f"Level {s['level']}  •  {s['xp_into_level']} / {s['xp_per_level']} XP"
            )
        if "xp_bar_home" in self.ids:
            self.ids.xp_bar_home.max = s["xp_per_level"]
            self.ids.xp_bar_home.value = s["xp_into_level"]

        # Progress-tab stat tiles
        for key, val in (("accuracy_tile", f"{s['accuracy']}%"),
                         ("solved_tile", str(s["total"])),
                         ("streak_tile", str(s["streak"])),
                         ("level_tile", f"Lvl {s['level']}")):
            if key in self.ids:
                self.ids[key].value = val

        # Strong / weak topics
        tb = progress_service.topic_breakdown(uid)
        if "strong_topics" in self.ids:
            self.ids.strong_topics.text = ", ".join(tb["strong"]) or "Practice more to build strengths"
        if "weak_topics" in self.ids:
            self.ids.weak_topics.text = ", ".join(tb["weak"]) or "None spotted yet"

        # Monthly summary line
        if "monthly_label" in self.ids:
            m = progress_service.monthly(uid)
            self.ids.monthly_label.text = (
                f"Last 30 days: {m['attempts']} solved • {m['accuracy']}% accuracy"
            )

        # Weekly chart (pure-Kivy canvas widget)
        self._render_weekly_chart(app, uid)

    def _render_weekly_chart(self, app, uid):
        chart = self.ids.get("weekly_chart")
        if chart is None:
            return
        try:
            wk = progress_service.weekly(uid)
            dark = app.theme_cls.theme_style == "Dark"
            chart.accent = app.theme_cls.primary_color
            chart.faded = (0.29, 0.29, 0.35, 1) if dark else (0.85, 0.83, 0.95, 1)
            chart.text_color = (0.9, 0.9, 0.9, 1) if dark else (0.25, 0.25, 0.25, 1)
            chart.labels = wk["labels"]
            chart.data = list(zip(wk["attempts"], wk["correct"]))
        except Exception as exc:  # noqa: BLE001 - a chart failure must not break Home
            print(f"[chart] {exc}")

    def switch_tab(self, name):
        """Select a bottom-navigation tab by name."""
        self.ids.bottom_nav.switch_tab(name)

    # ---- Settings tab handlers ----

    def on_theme_switch(self, active):
        app = MDApp.get_running_app()
        app.state.theme_style = "Dark" if active else "Light"
        theme.apply_theme(app.theme_cls, app.state.theme_style)
        # Re-render the chart so it matches the new theme.
        self._render_weekly_chart(app, app.state.user_id)

    def on_font_scale(self, value):
        app = MDApp.get_running_app()
        app.state.font_scale = round(float(value), 2)
        if "font_scale_label" in self.ids:
            self.ids.font_scale_label.text = f"Font size  ×{app.state.font_scale:.2f}"

    def on_notifications(self, active):
        MDApp.get_running_app().state.notifications_on = bool(active)

    def on_sound(self, active):
        MDApp.get_running_app().state.sound_on = bool(active)
