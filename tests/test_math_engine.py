"""Correctness tests for the math engine across every supported category."""

import pytest

from app.core import math_engine

# (input, substring that must appear in the answer; None = must not error)
CASES = [
    ("solve 2x + 3 = 11", "x = 4"),
    ("solve 5x - 7 = 2x + 8", "x = 5"),
    ("x^2 - 5x + 6 = 0", "2"),
    ("solve x^2 - 5x + 6 = 0", "3"),
    ("solve x^3 - x = 0", "0"),
    ("3/4 + 1/8", "7/8"),
    ("2 + 3 * 4", "14"),
    ("0.5 + 0.25", "3/4"),
    ("differentiate x^2 + 3x", "2*x + 3"),
    ("derivative of sin(x)", "cos"),
    ("integrate x^2", "x^3/3"),
    ("integrate 2x", "x^2"),
    ("factor x^2 - 9", "3"),
    ("expand (x+1)^2", "2*x"),
    ("simplify 2x + 3x", "5*x"),
    ("limit of (x^2 - 1)/(x - 1) as x -> 1", "2"),
    ("sqrt(16) + 2", "6"),
    ("what is 12 * 12", "144"),
    ("2^10", "1024"),
]


@pytest.mark.parametrize("text,expected", CASES)
def test_solve_answers(text, expected):
    r = math_engine.solve(text)
    assert r.ok, f"{text!r} errored: {r.error}"
    assert expected in r.answer, f"{text!r} -> {r.answer!r}"


def test_result_has_steps_and_concept():
    r = math_engine.solve("solve 2x + 3 = 11")
    assert len(r.steps) >= 2
    assert all(len(step) == 2 for step in r.steps)   # (expr, why)
    assert r.concept
    assert r.similar and all(isinstance(q, str) for q in r.similar)


def test_bad_input_does_not_crash():
    r = math_engine.solve("@@@ not math ###")
    assert r.ok is False
    assert r.error


def test_empty_input():
    r = math_engine.solve("   ")
    assert r.ok is False
