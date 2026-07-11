"""Tests for the expression parser (normalisation + parsing)."""

import sympy as sp

from app.core import expr_parser as p


def test_normalize_unicode_operators():
    assert p.normalize("2 × 3 ÷ 4") == "2 * 3 / 4"
    assert p.normalize("5 − 2") == "5 - 2"


def test_normalize_strips_command_words():
    assert "solve" not in p.normalize("solve 2x + 3 = 11").lower()
    assert "=" in p.normalize("solve 2x + 3 = 11")


def test_parse_equation_returns_eq():
    obj, is_eq = p.parse_equation("2x + 3 = 11")
    assert is_eq is True
    assert isinstance(obj, sp.Equality)


def test_parse_expression_no_equals():
    obj, is_eq = p.parse_equation("3/4 + 1/8")
    assert is_eq is False
    assert obj == sp.Rational(7, 8)


def test_implicit_multiplication_and_power():
    # "3x^2" -> 3*x**2
    expr = p.parse_expression("3x^2")
    x = sp.Symbol("x")
    assert expr == 3 * x ** 2


def test_main_symbol_prefers_x():
    expr = p.parse_expression("a + x + b")
    assert p.main_symbol(expr).name == "x"
