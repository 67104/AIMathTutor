"""Tests for Olympiad generators — well-formedness AND math exactness."""

import re

import pytest

from app.core import olympiad_gen


@pytest.mark.parametrize("exam", ["IMO", "NSO", "IEO", "IGKO"])
@pytest.mark.parametrize("level", [1, 2])
def test_olympiad_questions_well_formed(exam, level):
    for _ in range(40):
        q = olympiad_gen.generate(exam, level, grade=8)
        assert q.answer in q.options, f"{exam} L{level}: {q.answer!r} not in {q.options}"
        assert len(set(q.options)) == 4
        assert q.explanation
        assert q.topic_name


def test_percentage_word_is_exact():
    """A number increased by p% must equal the stated result exactly."""
    for _ in range(2000):
        prompt, ans, *_ = olympiad_gen._percentage_word(2, 8)
        m = re.search(r"increased by (\d+)% becomes (\d+)", prompt)
        pct, result = int(m.group(1)), int(m.group(2))
        assert ans + ans * pct / 100 == result, prompt


def test_average_is_exact():
    """The stated average must equal (sum of givens + answer) / count exactly."""
    for _ in range(2000):
        prompt, ans, *_ = olympiad_gen._average(2, 8)
        m = re.search(r"average of (\d+) numbers is (\d+)\. If .* are (.+), find", prompt)
        n, avg = int(m.group(1)), int(m.group(2))
        nums = [int(x) for x in m.group(3).split(", ")]
        assert (sum(nums) + ans) / n == avg, prompt


def test_lcm_hcf_correct():
    from math import gcd
    for _ in range(500):
        prompt, ans, *_ = olympiad_gen._lcm_hcf(2, 8)
        m = re.search(r"(LCM|HCF) of (\d+) and (\d+)", prompt)
        kind, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        expected = gcd(a, b) if kind == "HCF" else a * b // gcd(a, b)
        assert ans == expected, prompt
