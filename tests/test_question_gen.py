"""Tests for the practice question generator + 'similar' generator."""

import pytest

from app.core import question_gen


@pytest.mark.parametrize("grade", [1, 3, 5, 7, 9, 11])
@pytest.mark.parametrize("difficulty", ["Easy", "Medium", "Hard"])
def test_practice_questions_are_well_formed(grade, difficulty):
    for _ in range(30):
        q = question_gen.generate_practice(grade, difficulty)
        assert q.answer in q.options, f"answer {q.answer!r} not in {q.options}"
        assert len(set(q.options)) == 4, f"options not 4-unique: {q.options}"
        assert q.topic_code and q.topic_name
        assert q.prompt


def test_generate_similar_returns_strings():
    for category in ["linear_equation", "differentiation", "arithmetic", "factor"]:
        out = question_gen.generate_similar(category)
        assert out and all(isinstance(s, str) for s in out)


def test_similar_unknown_category_falls_back():
    out = question_gen.generate_similar("nonexistent_category")
    assert len(out) >= 1
