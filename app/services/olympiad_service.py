"""Olympiad service: single-question practice + timed mock tests.

* Practice: one question at a time with an instant explanation.
* Mock test: a fixed set of questions under a countdown; on completion it
  scores, records a ``mock_tests`` row + per-question ``attempts``, and produces
  a performance analysis (accuracy, time, weak topics).
"""

import time

from app.core import olympiad_gen


def generate_practice(exam, level, grade):
    return olympiad_gen.generate(exam, level, grade)


def _record(user_id, q, given, is_correct, elapsed_ms, xp):
    try:
        from app.database.repositories import attempt_repo
        return attempt_repo.record(user_id, q.topic_code, "olympiad",
                                   q.difficulty, given, is_correct, elapsed_ms, xp)
    except Exception:  # noqa: BLE001
        return {"total_xp": 0, "level": 1, "current_streak": 0}


def record_practice(user_id, q, given, elapsed_ms, level):
    is_correct = str(given).strip() == str(q.answer).strip()
    xp = (10 + 5 * int(level)) if is_correct else 0
    wallet = _record(user_id, q, given, is_correct, elapsed_ms, xp)
    return {"correct": is_correct, "answer": q.answer,
            "explanation": q.explanation, "xp": xp, "wallet": wallet}


class MockTest:
    def __init__(self, exam, level, grade, user_id=None,
                 num_questions=10, duration_s=300):
        self.exam = exam
        self.level = int(level)
        self.grade = grade
        self.user_id = user_id
        self.duration_s = duration_s
        self.questions = [
            olympiad_gen.generate(exam, level, grade) for _ in range(num_questions)
        ]
        self.idx = 0
        self.correct = 0
        self._tally = {}                # topic_name -> [correct, total]
        self._review = []
        self._start = time.time()
        self._q_start = time.time()
        self.finished = False

    @property
    def total(self):
        return len(self.questions)

    @property
    def remaining_s(self):
        return max(0, int(self.duration_s - (time.time() - self._start)))

    def current(self):
        if self.idx < self.total:
            self._q_start = time.time()
            return self.questions[self.idx]
        return None

    def answer(self, given):
        q = self.questions[self.idx]
        is_correct = str(given).strip() == str(q.answer).strip()
        elapsed_ms = int((time.time() - self._q_start) * 1000)
        xp = (10 + 5 * self.level) if is_correct else 0

        tally = self._tally.setdefault(q.topic_name, [0, 0])
        tally[1] += 1
        if is_correct:
            self.correct += 1
            tally[0] += 1
        _record(self.user_id, q, given, is_correct, elapsed_ms, xp)
        self._review.append({
            "prompt": q.prompt, "given": given, "answer": q.answer,
            "correct": is_correct, "explanation": q.explanation,
        })

        self.idx += 1
        done = self.idx >= self.total
        return {"correct": is_correct, "answer": q.answer,
                "explanation": q.explanation, "done": done,
                "index": self.idx, "total": self.total}

    def finish(self):
        """Persist the mock and return the performance analysis."""
        if not self.finished:
            self.finished = True
            duration_ms = int((time.time() - self._start) * 1000)
            try:
                from app.database import connection
                connection.execute(
                    "INSERT INTO mock_tests (user_id, exam, level, grade, "
                    "total_questions, correct, duration_ms, finished_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
                    (self.user_id, self.exam, self.level, self.grade,
                     self.total, self.correct, duration_ms), commit=True,
                )
            except Exception:  # noqa: BLE001
                pass
        return self.results()

    def results(self):
        answered = max(1, len(self._review))
        weak = sorted(
            (name for name, (c, t) in self._tally.items() if c < t),
            key=lambda n: self._tally[n][0] / self._tally[n][1],
        )
        return {
            "exam": self.exam,
            "level": self.level,
            "score": self.correct,
            "total": self.total,
            "answered": len(self._review),
            "accuracy": round(100 * self.correct / answered),
            "time_s": int(time.time() - self._start),
            "weak_topics": weak,
            "review": self._review,
        }


def new_mock(exam, level, grade, user_id=None, num_questions=10, duration_s=300):
    return MockTest(exam, level, grade, user_id=user_id,
                    num_questions=num_questions, duration_s=duration_s)
