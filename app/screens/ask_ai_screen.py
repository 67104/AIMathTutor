"""Ask AI screen: type a question -> answer, steps, why, concept, similar Qs.

Phase 3: wired to the real SymPy engine via ``solver_service`` on a background
thread, so the UI never freezes on a slow solve.
"""

from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.button import MDFlatButton

from app.services import solver_service


class AskAIScreen(MDScreen):

    def solve(self):
        question = self.ids.question_field.text.strip()
        if not question:
            self.ids.question_field.error = True
            return
        self.ids.question_field.error = False

        # Show spinner, hide previous result while we compute off-thread.
        self.ids.spinner.active = True
        self.ids.result_box.opacity = 0
        self.ids.error_label.text = ""
        solver_service.solve_async(
            question, on_done=self._on_solved, on_error=self._on_error
        )

    def solve_text(self, text):
        """Fill the field with a question and solve it (used by 'similar')."""
        self.ids.question_field.text = text
        self.solve()

    # ---- callbacks (run on the UI thread) ----

    def _on_solved(self, result):
        self.ids.spinner.active = False
        if not result.ok:
            self.ids.error_label.text = result.error
            return
        self._render(result)

    def _on_error(self, exc):
        self.ids.spinner.active = False
        self.ids.error_label.text = f"Something went wrong: {exc}"

    def _render(self, result):
        self.ids.result_box.opacity = 1
        self.ids.category_label.text = result.category_label
        self.ids.answer_label.text = result.answer
        self.ids.concept_label.text = result.concept

        steps = self.ids.steps_list
        steps.clear_widgets()
        for i, (expr, why) in enumerate(result.steps, start=1):
            steps.add_widget(
                TwoLineListItem(text=f"Step {i}:  {expr}", secondary_text=why)
            )

        similar = self.ids.similar_box
        similar.clear_widgets()
        for q in result.similar:
            similar.add_widget(
                MDFlatButton(
                    text=q,
                    size_hint_x=1,
                    on_release=lambda _w, text=q: self.solve_text(text),
                )
            )
