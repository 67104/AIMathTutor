"""Pure-Kivy weekly bar chart (no Matplotlib).

Draws directly on the widget canvas — a faded bar per day for total attempts
with the 'correct' portion stacked in the accent colour, plus day labels.

This replaces the Matplotlib PNG approach so the app has NO heavy plotting
dependency to package for Android (see docs/PROBLEMS.md #8). It's theme-aware
via the ``accent`` / ``faded`` / ``text_color`` properties.
"""

from kivy.uix.widget import Widget
from kivy.properties import ListProperty, ColorProperty
from kivy.core.text import Label as CoreLabel
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp


class WeeklyBarChart(Widget):
    data = ListProperty([])          # list of (attempts, correct) per day
    labels = ListProperty([])        # day labels, same length as data
    accent = ColorProperty((0.40, 0.31, 0.85, 1))
    faded = ColorProperty((0.85, 0.83, 0.95, 1))
    text_color = ColorProperty((0.2, 0.2, 0.2, 1))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._redraw, size=self._redraw, data=self._redraw,
                  labels=self._redraw, accent=self._redraw, faded=self._redraw,
                  text_color=self._redraw)

    def _redraw(self, *args):
        self.canvas.clear()
        if not self.data or self.width <= 1 or self.height <= 1:
            return

        n = len(self.data)
        pad_x = self.width * 0.03
        avail_w = self.width - 2 * pad_x
        col_w = avail_w / n
        bar_w = min(col_w * 0.55, dp(28))
        label_h = dp(18)
        base_y = self.y + label_h
        chart_h = max(1.0, self.height - label_h - dp(6))
        max_val = max([a for a, _ in self.data] + [1])

        with self.canvas:
            for i, (attempts, correct) in enumerate(self.data):
                cx = self.x + pad_x + i * col_w + col_w / 2
                bx = cx - bar_w / 2

                # Total attempts (faded backdrop bar)
                Color(*self.faded)
                Rectangle(pos=(bx, base_y),
                          size=(bar_w, chart_h * (attempts / max_val)))
                # Correct portion (accent), stacked from the baseline
                Color(*self.accent)
                Rectangle(pos=(bx, base_y),
                          size=(bar_w, chart_h * (correct / max_val)))

                # Day label centred under the column
                text = self.labels[i] if i < len(self.labels) else ""
                core = CoreLabel(text=text, font_size=dp(11))
                core.refresh()
                tex = core.texture
                Color(*self.text_color)
                Rectangle(texture=tex, size=tex.size,
                          pos=(cx - tex.width / 2, self.y))
