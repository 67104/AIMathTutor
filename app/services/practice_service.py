"""Practice session logic: generate questions, grade answers, adapt difficulty,
and record every attempt to SQLite.

Adaptive rule (auto-increase as the learner improves):
  * 3 correct in a row  -> step difficulty up (Easy -> Medium -> Hard)
  * 2 wrong in a row     -> step difficulty down
Difficulty starts at Easy each session; persistence across sessions is a
Phase 7 enhancement.
"""

import time

from app.core import question_gen

DIFFICULTIES = ["Easy", "Medium", "Hard"]
STEP_UP_STREAK = 3
STEP_DOWN_STREAK = 2


class PracticeSession:
    def __init__(self, grade, user_id=None, mode="practice"):
        self.grade = int(grade) if grade else 5
        self.user_id = user_id
        self.mode = mode
        self.diff_idx = 0
        self.answered = 0
        self.correct = 0
        self._consec_correct = 0
        self._consec_wrong = 0
        self.current = None
        self._start_time = None

    @property
    def difficulty(self):
        return DIFFICULTIES[self.diff_idx]

    def next_question(self):
        self.current = question_gen.generate_practice(self.grade, self.difficulty)
        self._start_time = time.time()
        return self.current

    def submit(self, given):
        q = self.current
        is_correct = str(given).strip() == str(q.answer).strip()
        elapsed_ms = int((time.time() - self._start_time) * 1000) if self._start_time else 0

        self.answered += 1
        xp = 0
        if is_correct:
            self.correct += 1
            self._consec_correct += 1
            self._consec_wrong = 0
            xp = 10 * (self.diff_idx + 1)
        else:
            self._consec_wrong += 1
            self._consec_correct = 0

        # Persist the attempt (+ daily_stats + gamification). Never block the UI
        # flow on a DB hiccup.
        wallet = {"total_xp": 0, "level": 1, "current_streak": 0}
        try:
            from app.database.repositories import attempt_repo
            wallet = attempt_repo.record(
                self.user_id, q.topic_code, self.mode, self.difficulty,
                given, is_correct, elapsed_ms, xp,
            )
        except Exception:  # noqa: BLE001
            pass

        leveled = self._adapt()
        return {
            "correct": is_correct,
            "answer": q.answer,
            "xp": xp,
            "time_ms": elapsed_ms,
            "leveled": leveled,          # "up" | "down" | None
            "difficulty": self.difficulty,
            "accuracy": round(100 * self.correct / self.answered),
            "wallet": wallet,
        }

    def _adapt(self):
        if self._consec_correct >= STEP_UP_STREAK and self.diff_idx < 2:
            self.diff_idx += 1
            self._consec_correct = 0
            return "up"
        if self._consec_wrong >= STEP_DOWN_STREAK and self.diff_idx > 0:
            self.diff_idx -= 1
            self._consec_wrong = 0
            return "down"
        return None


def new_session(grade, user_id=None, mode="practice"):
    return PracticeSession(grade, user_id=user_id, mode=mode)
