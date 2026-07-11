"""Olympiad screen (Phase 6).

Two modes, both rendered into the ``olympiad_content`` container:
  * Practice   – one question with instant, explained feedback.
  * Mock test  – 10 timed questions, then a performance analysis (score,
                 accuracy, time, weak topics) with a review list.
"""

import time

from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton

from app.core import olympiad_gen
from app.services import olympiad_service
from app.widgets.cards import SectionCard

GREEN = (0.13, 0.66, 0.52, 1)
RED = (0.85, 0.27, 0.42, 1)


class OlympiadScreen(MDScreen):

    exam = "IMO"
    level = 1

    # ---- lifecycle ----

    def on_pre_enter(self, *args):
        self._refresh_header()
        self.ids.olympiad_content.clear_widgets()
        self.ids.olympiad_content.add_widget(
            self._label("Choose Practice for explained questions, or Start Mock "
                        "Test for a timed 10-question challenge.",
                        style="Caption", secondary=True)
        )

    def on_leave(self, *args):
        self._stop_timer()

    # ---- selectors ----

    def set_exam(self, name):
        self.exam = name
        self._refresh_header()

    def set_level(self, level):
        self.level = int(level)
        self._refresh_header()

    def _refresh_header(self):
        self.ids.selection_label.text = f"{self.exam}  •  Level {self.level}"
        self.ids.exam_note.text = olympiad_gen.exam_note(self.exam)

    # ==================================================================
    # PRACTICE MODE
    # ==================================================================

    def start_practice(self):
        self._stop_timer()
        self._new_practice_question()

    def _new_practice_question(self):
        app = MDApp.get_running_app()
        self._q = olympiad_service.generate_practice(self.exam, self.level, app.state.grade)
        self._q_start = time.time()
        self._answered = False

        c = self.ids.olympiad_content
        c.clear_widgets()

        card = SectionCard()
        card.add_widget(self._label(f"{self._q.topic_name}", style="Overline",
                                    color=MDApp.get_running_app().theme_cls.primary_color))
        card.add_widget(self._label(self._q.prompt, style="H6", bold=True))
        c.add_widget(card)

        self._options_box = MDBoxLayout(orientation="vertical", adaptive_height=True,
                                        spacing="10dp", size_hint_y=None)
        self._options_box.bind(minimum_height=self._options_box.setter("height"))
        for opt in self._q.options:
            self._options_box.add_widget(
                MDRaisedButton(text=opt, size_hint_x=1,
                               on_release=lambda w, v=opt: self._practice_check(v, w))
            )
        c.add_widget(self._options_box)

        self._fb = self._label("", style="Subtitle1", bold=True)
        c.add_widget(self._fb)
        self._exp = self._label("", style="Body2", secondary=True)
        c.add_widget(self._exp)

        c.add_widget(MDRaisedButton(text="Next question", icon="arrow-right",
                                    size_hint_x=1, on_release=lambda w: self._new_practice_question()))

    def _practice_check(self, value, widget):
        if self._answered:
            return
        self._answered = True
        app = MDApp.get_running_app()
        elapsed = int((time.time() - self._q_start) * 1000)
        res = olympiad_service.record_practice(app.state.user_id, self._q,
                                               value, elapsed, self.level)
        color = GREEN if res["correct"] else RED
        widget.md_bg_color = color
        if not res["correct"]:
            for btn in self._options_box.children:
                if btn.text == str(res["answer"]):
                    btn.md_bg_color = GREEN
        self._fb.theme_text_color = "Custom"
        self._fb.text_color = color
        self._fb.text = (f"Correct!  +{res['xp']} XP" if res["correct"]
                         else f"Answer: {res['answer']}")
        self._exp.text = f"Why: {res['explanation']}"

    # ==================================================================
    # MOCK TEST MODE
    # ==================================================================

    def start_mock(self):
        self._stop_timer()
        app = MDApp.get_running_app()
        self.mock = olympiad_service.new_mock(
            self.exam, self.level, app.state.grade, app.state.user_id,
            num_questions=10, duration_s=300,
        )
        c = self.ids.olympiad_content
        c.clear_widgets()

        header = MDBoxLayout(adaptive_height=True, size_hint_y=None, height="28dp")
        self._counter = self._label("", style="Caption", secondary=True)
        self._timer = self._label("", style="Caption", secondary=True, halign="right")
        header.add_widget(self._counter)
        header.add_widget(self._timer)
        c.add_widget(header)

        self._mock_card = SectionCard()
        self._mock_prompt = self._label("", style="H6", bold=True)
        self._mock_card.add_widget(self._mock_prompt)
        c.add_widget(self._mock_card)

        self._mock_options = MDBoxLayout(orientation="vertical", adaptive_height=True,
                                         spacing="10dp", size_hint_y=None)
        self._mock_options.bind(minimum_height=self._mock_options.setter("height"))
        c.add_widget(self._mock_options)

        self._timer_event = Clock.schedule_interval(self._mock_tick, 1)
        self._load_mock_question()

    def _load_mock_question(self):
        q = self.mock.current()
        if q is None:
            self._end_mock()
            return
        self._mock_answered = False
        self._counter.text = f"Question {self.mock.idx + 1} / {self.mock.total}"
        self._mock_prompt.text = q.prompt
        self._mock_options.clear_widgets()
        for opt in q.options:
            self._mock_options.add_widget(
                MDRaisedButton(text=opt, size_hint_x=1,
                               on_release=lambda w, v=opt: self._mock_check(v, w))
            )

    def _mock_check(self, value, widget):
        if self._mock_answered:
            return
        self._mock_answered = True
        res = self.mock.answer(value)
        widget.md_bg_color = GREEN if res["correct"] else RED
        Clock.schedule_once(lambda _dt: self._advance_mock(res), 0.45)

    def _advance_mock(self, res):
        if res["done"]:
            self._end_mock()
        else:
            self._load_mock_question()

    def _mock_tick(self, _dt):
        rem = self.mock.remaining_s
        self._timer.text = f"Time {rem // 60}:{rem % 60:02d}"
        if rem <= 0:
            self._end_mock()

    def _end_mock(self):
        self._stop_timer()
        results = self.mock.finish()
        c = self.ids.olympiad_content
        c.clear_widgets()

        card = SectionCard()
        card.md_bg_color = MDApp.get_running_app().theme_cls.primary_color
        card.add_widget(self._label(f"{results['exam']} • Level {results['level']} — Results",
                                    style="Overline", white=True))
        card.add_widget(self._label(f"{results['score']} / {results['total']} correct",
                                    style="H4", bold=True, white=True))
        mins = results["time_s"] // 60
        card.add_widget(self._label(
            f"Accuracy {results['accuracy']}%   •   Time {mins}m {results['time_s'] % 60}s",
            style="Caption", white=True))
        c.add_widget(card)

        weak = results["weak_topics"]
        wc = SectionCard()
        wc.add_widget(self._label("Weak topics to review", style="Subtitle1", bold=True))
        wc.add_widget(self._label(", ".join(weak) if weak else "None — great job!",
                                  style="Body2", secondary=True))
        c.add_widget(wc)

        c.add_widget(self._label("Review", style="Subtitle1", bold=True))
        for i, r in enumerate(results["review"], 1):
            mark = "✓" if r["correct"] else "✗"
            rc = SectionCard()
            rc.add_widget(self._label(f"{mark}  Q{i}. {r['prompt']}", style="Body2", bold=True))
            if not r["correct"]:
                rc.add_widget(self._label(f"Correct answer: {r['answer']}",
                                          style="Caption", color=RED))
            rc.add_widget(self._label(f"Why: {r['explanation']}", style="Caption", secondary=True))
            c.add_widget(rc)

        c.add_widget(MDRaisedButton(text="Practice again", icon="refresh",
                                    size_hint_x=1, on_release=lambda w: self.start_practice()))

    # ---- helpers ----

    def _stop_timer(self):
        event = getattr(self, "_timer_event", None)
        if event is not None:
            event.cancel()
            self._timer_event = None

    def _label(self, text, style="Body1", bold=False, secondary=False,
               white=False, color=None, halign="left"):
        lbl = MDLabel(text=text, font_style=style, bold=bold, adaptive_height=True,
                      halign=halign)
        if white:
            lbl.theme_text_color = "Custom"
            lbl.text_color = (1, 1, 1, 1)
        elif color is not None:
            lbl.theme_text_color = "Custom"
            lbl.text_color = color
        elif secondary:
            lbl.theme_text_color = "Secondary"
        return lbl
