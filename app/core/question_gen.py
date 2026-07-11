"""Parametric question generators.

Two public APIs:
  * ``generate_similar(category)`` -> list[str]      (used by the AI Solver)
  * ``generate_practice(grade, difficulty)`` -> Question  (Practice/Olympiad)

Everything is generated fresh from random parameters — nothing is copied from
copyrighted material. Answers are computed exactly (Python/Fraction) so the
"correct" option is always genuinely correct; distractors are plausible common
mistakes.
"""

import random
from dataclasses import dataclass, field
from fractions import Fraction


# ==========================================================================
# AI Solver: "generate similar questions" (string prompts)
# ==========================================================================

def _sign(n):
    return f" + {n}" if n >= 0 else f" - {abs(n)}"


def _s_linear():
    a = random.randint(2, 9); x0 = random.randint(-6, 9); b = random.randint(-9, 9)
    return f"Solve  {a}x{_sign(b)} = {a * x0 + b}"


def _s_quadratic():
    r1, r2 = random.randint(-6, 6), random.randint(-6, 6)
    return f"Solve  x^2{_sign(-(r1 + r2))}x{_sign(r1 * r2)} = 0"


def _s_polynomial():
    return f"Solve  x^3 - {random.randint(1, 4)}x = 0"


def _s_diff():
    return f"Differentiate  {random.randint(2, 6)}x^{random.randint(2, 4)}{_sign(random.randint(1, 8))}x"


def _s_integrate():
    return f"Integrate  {random.randint(2, 6)}x^{random.randint(1, 4)}"


def _s_limit():
    a = random.randint(1, 5)
    return f"Find the limit of  (x^2 - {a * a}) / (x - {a})  as x -> {a}"


def _s_factor():
    n = random.randint(2, 9); return f"Factor  x^2 - {n * n}"


def _s_expand():
    return f"Expand  (x{_sign(random.randint(1, 8))})(x{_sign(random.randint(1, 8))})"


def _s_simplify():
    return f"Simplify  {random.randint(2, 9)}x + {random.randint(2, 9)}x"


def _s_arith():
    d = random.choice([2, 3, 4, 5, 8])
    return f"Evaluate  {random.randint(1, d - 1)}/{d} + {random.randint(1, d - 1)}/{d}"


_SIMILAR = {
    "linear_equation": _s_linear, "quadratic_equation": _s_quadratic,
    "polynomial_equation": _s_polynomial, "equation": _s_linear,
    "differentiation": _s_diff, "integration": _s_integrate, "limit": _s_limit,
    "factor": _s_factor, "expand": _s_expand, "simplify": _s_simplify,
    "arithmetic": _s_arith,
}


def generate_similar(category, n=3):
    gen = _SIMILAR.get(category, _s_linear)
    seen, out, tries = set(), [], 0
    while len(out) < n and tries < n * 6:
        q = gen()
        if q not in seen:
            seen.add(q); out.append(q)
        tries += 1
    return out


# ==========================================================================
# Practice / Olympiad: full MCQ questions
# ==========================================================================

@dataclass
class Question:
    prompt: str
    answer: str
    options: list = field(default_factory=list)
    topic_code: str = ""
    topic_name: str = ""
    difficulty: str = "Easy"
    explanation: str = ""


_TIER = {"Easy": 1, "Medium": 2, "Hard": 3}


def _pick(seq, tier):
    """Index a per-tier parameter list safely."""
    return seq[min(tier, len(seq)) - 1]


# Each generator returns (prompt, correct, distractors, topic_code, topic_name).

def _add_sub(tier):
    hi = _pick([20, 100, 1000], tier)
    a, b = random.randint(2, hi), random.randint(2, hi)
    if random.random() < 0.5:
        prompt, ans = f"{a} + {b}", a + b
    else:
        a, b = max(a, b), min(a, b)
        prompt, ans = f"{a} - {b}", a - b
    return (f"Calculate:  {prompt}", ans,
            [ans + 1, ans - 1, ans + tier + 2], "arithmetic.add_sub",
            "Addition & Subtraction")


def _mul_div(tier):
    hi = _pick([10, 15, 25], tier)
    a, b = random.randint(2, hi), random.randint(2, hi)
    if random.random() < 0.5:
        prompt, ans = f"{a} × {b}", a * b
    else:
        prompt, ans = f"{a * b} ÷ {a}", b
    return (f"Calculate:  {prompt}", ans,
            [ans + 1, ans - 1, ans + a], "arithmetic.mul_div",
            "Multiplication & Division")


def _fractions(tier):
    d1, d2 = random.choice([2, 3, 4, 6, 8]), random.choice([2, 3, 4, 6, 8])
    n1, n2 = random.randint(1, d1 - 1), random.randint(1, d2 - 1)
    f = Fraction(n1, d1) + Fraction(n2, d2)
    correct = f"{f.numerator}/{f.denominator}" if f.denominator != 1 else f"{f.numerator}"
    wrong = Fraction(n1 + n2, d1 + d2)  # classic "add across" mistake
    distractors = [
        f"{n1 + n2}/{d1 + d2}",
        f"{wrong.numerator}/{wrong.denominator}",
        f"{f.numerator + 1}/{f.denominator}",
    ]
    return (f"Add the fractions:  {n1}/{d1} + {n2}/{d2}", correct, distractors,
            "number.fractions", "Fractions")


def _decimals(tier):
    a, b = random.randint(1, 99) / 10, random.randint(1, 99) / 10
    ans = round(a + b, 1)
    return (f"Calculate:  {a} + {b}", ans,
            [round(ans + 0.1, 1), round(ans - 0.1, 1), round(ans + 1, 1)],
            "number.decimals", "Decimals")


def _percentage(tier):
    p = random.choice([5, 10, 15, 20, 25, 50])
    n = random.randint(1, 10) * 20
    ans = p * n // 100
    return (f"What is {p}% of {n}?", ans,
            [ans + n // 10, ans - n // 10 if ans - n // 10 > 0 else ans + 2, ans + 1],
            "number.percentage", "Percentages")


def _exponents(tier):
    base = random.randint(2, _pick([5, 9, 12], tier))
    exp = random.randint(2, _pick([2, 3, 3], tier))
    ans = base ** exp
    return (f"Evaluate:  {base}^{exp}", ans,
            [ans + base, ans - base, base * exp], "number.exponents",
            "Exponents & Powers")


def _linear(tier):
    span = _pick([5, 9, 12], tier)
    a = random.randint(2, _pick([5, 9, 12], tier))
    x0 = random.randint(-span, span)
    b = random.randint(-9, 9)
    c = a * x0 + b
    return (f"Solve for x:  {a}x{_sign(b)} = {c}", x0,
            [x0 + 1, x0 - 1, -x0 if x0 != 0 else x0 + 2], "algebra.linear_eq",
            "Linear Equations")


def _simplify(tier):
    a, b = random.randint(2, 9), random.randint(2, 9)
    return (f"Simplify:  {a}x + {b}x", f"{a + b}x",
            [f"{a * b}x", f"{a + b}x^2", f"{a + b + 1}x"], "algebra.simplify",
            "Algebraic Simplification")


def _quadratic(tier):
    r1, r2 = random.randint(-6, 6), random.randint(-6, 6)
    b, c = -(r1 + r2), r1 * r2
    s = r1 + r2
    return (f"What is the sum of the roots of  x^2{_sign(b)}x{_sign(c)} = 0 ?",
            s, [s + 1, s - 1, -s if s != 0 else s + 2], "algebra.quadratic",
            "Quadratic Equations")


def _pythagoras(tier):
    a, b, c = random.choice([(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15)])
    return (f"A right triangle has legs {a} and {b}. Find the hypotenuse.",
            c, [c + 1, c - 1, a + b], "geometry.pythagoras", "Pythagoras Theorem")


def _pool_for_grade(grade):
    if grade <= 2:
        return [_add_sub, _mul_div]
    if grade <= 4:
        return [_add_sub, _mul_div, _fractions]
    if grade <= 6:
        return [_fractions, _decimals, _percentage, _mul_div]
    if grade <= 8:
        return [_percentage, _exponents, _linear, _simplify, _pythagoras]
    if grade <= 10:
        return [_linear, _quadratic, _simplify, _exponents, _pythagoras]
    return [_quadratic, _exponents, _linear, _simplify]


def _build_options(correct, distractors):
    opts = [str(correct)]
    for d in distractors:
        s = str(d)
        if s not in opts:
            opts.append(s)
        if len(opts) == 4:
            break
    k = 2
    while len(opts) < 4:
        try:
            base = float(correct)
            cand = str(int(base) + k) if base.is_integer() else str(round(base + k * 0.1, 2))
        except ValueError:
            cand = f"{correct} ({k})"
        if cand not in opts:
            opts.append(cand)
        k += 1
    random.shuffle(opts)
    return opts


def generate_practice(grade, difficulty="Easy"):
    """Return a fresh MCQ ``Question`` for the given grade + difficulty."""
    grade = int(grade) if grade else 5
    tier = _TIER.get(difficulty, 1)
    gen = random.choice(_pool_for_grade(grade))
    prompt, correct, distractors, code, name = gen(tier)
    return Question(
        prompt=prompt,
        answer=str(correct),
        options=_build_options(correct, distractors),
        topic_code=code,
        topic_name=name,
        difficulty=difficulty,
    )
