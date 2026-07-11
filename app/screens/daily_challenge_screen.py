"""Daily Challenge screen.

Phase 2: shows today's sample challenge and a claim-reward button. Phase 7 ties
this to the ``daily_challenges`` table (one per calendar day) and real rewards.
"""

from kivymd.uix.screen import MDScreen

from app.utils import constants


class DailyChallengeScreen(MDScreen):

    def on_pre_enter(self, *args):
        q = constants.SAMPLE_OLYMPIAD_Q
        self.ids.daily_question.text = q["prompt"]
        self.ids.daily_status.text = "Solve today's challenge to keep your streak alive."
        self._claimed = False

    def claim(self):
        if self._claimed:
            self.ids.daily_status.text = "You've already claimed today's reward."
            return
        self._claimed = True
        self.ids.daily_status.text = "Reward claimed!  +25 XP  •  Streak +1  🔥"
