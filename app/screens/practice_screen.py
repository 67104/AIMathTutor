"""Practice screen (Phase 5).

Runs an adaptive ``PracticeSession``: grade-aware generated questions, live
timer, MCQ grading with feedback, auto difficulty scaling, and every answer
recorded to SQLite.
"""

from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton

from app.services import practice_service

GREEN = (0.13, 0.66, 0.52, 1)
RED = (0.85, 0.27, 0.42, 1)


class PracticeScreen(MDScreen):

    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        self.session = practice_service.new_session(app.state.grade, app.state.user_id)
        self._answered = False
        self._elapsed = 0.0
        self._load_next()

    def on_leave(self, *args):
        Clock.unschedule(self._tick)

    def _load_next(self):
        self._answered = False
        q = self.session.next_question()
        self.ids.question_label.text = q.prompt
        self.ids.feedback_label.text = ""
        self.ids.difficulty_label.text = f"Difficulty: {self.session.difficulty}"
        self.ids.counter_label.text = f"Question {self.session.answered + 1}"
        self.ids.score_label.text = f"Score {self.session.correct}/{self.session.answered}"

        box = self.ids.options_box
        box.clear_widgets()
        for opt in q.options:
            box.add_widget(
                MDRaisedButton(
                    text=opt, size_hint_x=1,
                    on_release=lambda w, value=opt: self.check(value, w),
                )
            )

        self._elapsed = 0.0
        self.ids.timer_label.text = "0.0s"
        Clock.unschedule(self._tick)
        Clock.schedule_interval(self._tick, 0.1)

    def _tick(self, dt):
        self._elapsed += dt
        self.ids.timer_label.text = f"{self._elapsed:.1f}s"

    def check(self, value, widget):
        if self._answered:
            return
        self._answered = True
        Clock.unschedule(self._tick)

        res = self.session.submit(value)
        widget.md_bg_color = GREEN if res["correct"] else RED

        # Highlight the correct option when the user was wrong.
        if not res["correct"]:
            for btn in self.ids.options_box.children:
                if btn.text == str(res["answer"]):
                    btn.md_bg_color = GREEN

        fb = self.ids.feedback_label
        fb.theme_text_color = "Custom"
        fb.text_color = GREEN if res["correct"] else RED
        msg = f"Correct!  +{res['xp']} XP" if res["correct"] else f"Answer: {res['answer']}"
        if res["leveled"] == "up":
            msg += f"   ⬆ Leveled up to {res['difficulty']}"
        elif res["leveled"] == "down":
            msg += f"   ⬇ Easing to {res['difficulty']}"
        fb.text = msg

        self.ids.score_label.text = (
            f"Score {self.session.correct}/{self.session.answered}  •  {res['accuracy']}%"
        )

    def next_question(self):
        self._load_next()
