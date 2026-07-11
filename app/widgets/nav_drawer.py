"""Navigation drawer widget.

The drawer's items are built in Python from ``constants.DRAWER_ITEMS`` so the
menu stays in sync with the feature list in one place. Layout of each item is
the standard KivyMD ``MDNavigationDrawerItem``.
"""

from kivymd.app import MDApp
from kivymd.uix.navigationdrawer import (
    MDNavigationDrawer,
    MDNavigationDrawerMenu,
    MDNavigationDrawerHeader,
    MDNavigationDrawerItem,
)

from app.utils import constants


class NavDrawer(MDNavigationDrawer):
    """App-wide left navigation drawer."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.radius = (0, 16, 16, 0)
        menu = MDNavigationDrawerMenu()
        menu.add_widget(
            MDNavigationDrawerHeader(
                title=constants.APP_NAME,
                text=constants.APP_TAGLINE,
                spacing="4dp",
                padding=("12dp", "12dp", 0, "12dp"),
            )
        )
        for icon, label, target in constants.DRAWER_ITEMS:
            item = MDNavigationDrawerItem(icon=icon, text=label)
            # Bind release -> app router. Default-arg captures current target.
            item.bind(on_release=lambda _w, t=target: self._go(t))
            menu.add_widget(item)
        self.add_widget(menu)

    def _go(self, target):
        MDApp.get_running_app().route(target)
        self.set_state("close")
