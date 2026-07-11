"""Turn messy human/OCR text into SymPy-safe objects.

This is the front door to the math engine. It handles the real-world mess:
unicode operators, ``^`` for powers, implicit multiplication (``3x``, ``2(x+1)``),
and the ``=`` sign that separates an equation's two sides.

Public API:
    normalize(text) -> str
    parse_expression(text) -> sympy expression
    parse_equation(text)   -> (sympy.Eq | expression, is_equation: bool)
"""

import re

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)

# parse_expr transformations: enable ``3x`` -> 3*x and ``^`` -> ** .
_TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

# Unicode / typographic normalisations (common in OCR output and copy-paste).
_REPLACEMENTS = {
    "×": "*", "·": "*", "⋅": "*", "∗": "*",
    "÷": "/", "∕": "/",
    "−": "-", "—": "-", "–": "-",   # various dashes -> minus
    "＝": "=",
    "√": "sqrt",
    "π": "pi", "𝜋": "pi",
    "∞": "oo",
    "≤": "<=", "≥": ">=",
    "’": "", "“": "", "”": "",
    ",": "",                         # thousands separators: 1,000 -> 1000
}

# Words we strip so "solve 2x+3=11" parses; the engine reads intent separately.
_COMMAND_WORDS = re.compile(
    r"\b(solve|evaluate|simplify|expand|factor(?:ise|ize)?|compute|calculate|"
    r"find|the|value|of|for|differentiate|derivative|integrate|integral|"
    r"limit|please|what|is|equals?)\b",
    re.IGNORECASE,
)


def normalize(text):
    """Return a cleaned string ready for SymPy parsing (no command words)."""
    s = text or ""
    for bad, good in _REPLACEMENTS.items():
        s = s.replace(bad, good)
    s = _COMMAND_WORDS.sub(" ", s)
    # Collapse whitespace.
    s = re.sub(r"\s+", " ", s).strip()
    # Trailing punctuation like a full stop or question mark.
    s = s.rstrip(".?!:; ")
    return s


def _to_sympy(fragment):
    """Parse a single expression fragment, raising ValueError on failure."""
    fragment = fragment.strip()
    if not fragment:
        raise ValueError("empty expression")
    try:
        return parse_expr(fragment, transformations=_TRANSFORMS, evaluate=True)
    except (SyntaxError, TypeError, sp.SympifyError) as exc:
        raise ValueError(f"could not understand: '{fragment}'") from exc


def parse_expression(text):
    """Parse text (no ``=``) into a single SymPy expression."""
    return _to_sympy(normalize(text))


def parse_equation(text):
    """Parse text into (obj, is_equation).

    * If the text contains ``=``: returns (sympy.Eq(lhs, rhs), True).
    * Otherwise: returns (expression, False).
    """
    s = normalize(text)
    if "=" in s:
        # Split on the first '=' only; guard against '==' from replacements.
        s = s.replace("==", "=")
        left, _, right = s.partition("=")
        lhs = _to_sympy(left)
        rhs = _to_sympy(right)
        return sp.Eq(lhs, rhs), True
    return _to_sympy(s), False


def main_symbol(expr, prefer="x"):
    """Pick the variable to solve for: prefer ``x``, else the first free symbol."""
    symbols = sorted(expr.free_symbols, key=lambda s: s.name)
    if not symbols:
        return sp.Symbol(prefer)
    for s in symbols:
        if s.name == prefer:
            return s
    return symbols[0]
