"""Central theme configuration applied to KivyMD's ``theme_cls``.

Keeping palette/typography here (rather than scattered in screens) means a
single place controls the app's look and the Dark/Light switch.
"""

# KivyMD named palettes (see kivymd.color_definitions.palette)
PRIMARY_PALETTE = "DeepPurple"
ACCENT_PALETTE = "Amber"
PRIMARY_HUE = "500"

# Font-scale bounds for the Settings slider (multiplies base sizes).
FONT_SCALE_MIN = 0.85
FONT_SCALE_MAX = 1.40
FONT_SCALE_DEFAULT = 1.0


def apply_theme(theme_cls, style="Light"):
    """Apply the app palette to a KivyMD ``theme_cls``.

    Args:
        theme_cls: the running app's ``self.theme_cls``.
        style: "Light" or "Dark".
    """
    theme_cls.primary_palette = PRIMARY_PALETTE
    theme_cls.primary_hue = PRIMARY_HUE
    theme_cls.accent_palette = ACCENT_PALETTE
    theme_cls.theme_style = "Dark" if style == "Dark" else "Light"
    # Smooth transition when the user toggles dark mode at runtime.
    theme_cls.theme_style_switch_animation = True
    theme_cls.theme_style_switch_animation_duration = 0.25
