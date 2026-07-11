"""Achievements screen: live XP/level header + badge list (locked/unlocked)."""

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import IconLeftWidget, TwoLineIconListItem

from app.services import progress_service, gamification_service


class AchievementsScreen(MDScreen):

    def on_pre_enter(self, *args):
        uid = MDApp.get_running_app().state.user_id
        s = progress_service.summary(uid)

        self.ids.level_label.text = f"Level {s['level']}"
        self.ids.xp_label.text = f"{s['xp_into_level']} / {s['xp_per_level']} XP"
        self.ids.xp_bar.max = s["xp_per_level"]
        self.ids.xp_bar.value = s["xp_into_level"]

        lst = self.ids.badge_list
        lst.clear_widgets()
        for title, desc, icon, unlocked in gamification_service.list_badges(uid):
            status = "Unlocked" if unlocked else "Locked"
            item = TwoLineIconListItem(text=title, secondary_text=f"{desc}  •  {status}")
            leading = IconLeftWidget(icon=icon)
            if not unlocked:
                leading.theme_text_color = "Hint"
            item.add_widget(leading)
            lst.add_widget(item)
