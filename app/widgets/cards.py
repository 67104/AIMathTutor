"""Reusable Material widgets used across screens.

Layout for each is defined by a matching ``<ClassName>`` rule in
``app/kv/common.kv`` (auto-applied by Kivy on instantiation).
"""

from kivy.properties import StringProperty, ColorProperty
from kivymd.uix.card import MDCard


class FeatureCard(MDCard):
    """A tappable Material card for the Home dashboard grid.

    MDCard already mixes in ButtonBehavior, so ``on_release`` (bound in
    common.kv) fires when the card is tapped — no extra mixin needed.
    """

    icon = StringProperty("star")
    title = StringProperty("")
    subtitle = StringProperty("")
    target = StringProperty("")          # screen name or "tab:<name>"
    card_color = ColorProperty((0.4, 0.31, 0.85, 1))


class StatTile(MDCard):
    """A small statistic card (value + label) for the Progress view."""

    value = StringProperty("0")
    label = StringProperty("")
    icon = StringProperty("chart-box-outline")
    accent = ColorProperty((0.40, 0.31, 0.85, 1))


class SectionCard(MDCard):
    """A plain rounded container used to group content on a screen."""

    heading = StringProperty("")
