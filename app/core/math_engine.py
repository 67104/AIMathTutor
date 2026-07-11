"""The math engine: detect intent, solve with SymPy, build explained steps.

Entry point:  ``solve(raw_text) -> SolveResult``

Supported intents (detected from keywords + structure):
  * differentiate / derivative        -> sp.diff
  * integrate / integral              -> sp.integrate
  * limit ... as x -> a               -> sp.limit
  * factor / expand / simplify        -> algebraic rewriting
  * equations (contains '=' or solve) -> linear / quadratic / polynomial / general
  * otherwise                         -> arithmetic / expression evaluation

Every result carries: a final answer, ordered (expression, why) steps, a concept
blurb, and a set of generated *similar* practice questions.
"""

import re
from dataclasses import dataclass, field

import sympy as sp

from app.core import expr_parser as parser
from app.core import step_explainer as explain
from app.core import question_gen


@dataclass
class SolveResult:
    ok: bool
    raw: str = ""
    normalized: str = ""
    category: str = ""
    category_label: str = ""
    answer: str = ""
    steps: list = field(default_factory=list)   # list of (expr_text, why)
    concept: str = ""
    similar: list = field(default_factory=list)
    error: str = ""


def solve(raw):
    """Solve/evaluate ``raw`` text and return a fully explained SolveResult."""
    raw = (raw or "").strip()
    if not raw:
        return SolveResult(ok=False, raw=raw, error="Please enter a question.")

    lower = raw.lower()
    try:
        if any(k in lower for k in ("differentiate", "derivative")) or re.search(r"d\s*/\s*d[a-z]", lower):
            result = _differentiate(raw)
        elif any(k in lower for k in ("integrate", "integral")) or "∫" in raw:
            result = _integrate(raw)
        elif re.search(r"\blim(it)?\b", lower):
            result = _limit(raw)
        elif "factor" in lower:
            result = _rewrite(raw, "factor")
        elif "expand" in lower:
            result = _rewrite(raw, "expand")
        elif "simplify" in lower:
            result = _rewrite(raw, "simplify")
        elif "=" in raw or "solve" in lower:
            result = _solve_equation(raw)
        else:
            result = _evaluate(raw)
    except ValueError as exc:
        return SolveResult(ok=False, raw=raw,
                           error=f"Sorry, I couldn't parse that. {exc}")
    except Exception as exc:  # noqa: BLE001 - never crash the UI on a hard input
        return SolveResult(ok=False, raw=raw,
                           error=f"Sorry, I couldn't solve that ({type(exc).__name__}).")

    result.raw = raw
    result.concept = explain.concept_for(result.category)
    result.similar = question_gen.generate_similar(result.category)
    return result


# --------------------------------------------------------------------------
# Equation solving
# --------------------------------------------------------------------------

def _solve_equation(raw):
    obj, is_eq = parser.parse_equation(raw)
    if is_eq:
        lhs, rhs = obj.lhs, obj.rhs
        start = explain.eq_str(lhs, rhs)
        expr = sp.expand(lhs - rhs)
    else:
        expr = sp.expand(obj)
        start = f"{explain.pretty(expr)} = 0"

    var = parser.main_symbol(expr)
    sols = sp.solve(sp.Eq(expr, 0), var, dict=False)

    # Try to read the polynomial degree for tailored steps.
    degree = None
    try:
        poly = sp.Poly(expr, var)
        degree = poly.degree()
    except sp.PolynomialError:
        poly = None

    if degree == 1:
        return _steps_linear(start, expr, var, poly, sols)
    if degree == 2:
        return _steps_quadratic(start, expr, var, poly, sols)
    if degree and degree >= 3:
        return _steps_polynomial(start, expr, var, sols)
    return _steps_general(start, expr, var, sols)


def _fmt_sols(var, sols):
    if not sols:
        return "No real solution"
    return "   or   ".join(f"{var} = {explain.pretty(s)}" for s in sols)


def _steps_linear(start, expr, var, poly, sols):
    a, b = poly.all_coeffs()  # a*var + b
    sol = sols[0] if sols else -b / a
    steps = [
        (start, "Start with the given equation."),
        (f"{explain.pretty(expr)} = 0",
         "Bring every term to one side so the other side is 0."),
        (f"{explain.pretty(a * var)} = {explain.pretty(-b)}",
         f"Move the constant term to the right-hand side."),
        (f"{var} = {explain.pretty(sol)}",
         f"Divide both sides by the coefficient {explain.pretty(a)}."),
    ]
    return SolveResult(ok=True, category="linear_equation",
                       category_label="Linear equation",
                       answer=f"{var} = {explain.pretty(sol)}", steps=steps)


def _steps_quadratic(start, expr, var, poly, sols):
    a, b, c = poly.all_coeffs()
    disc = sp.simplify(b ** 2 - 4 * a * c)
    factored = sp.factor(expr)
    steps = [
        (start, "Start with the given equation."),
        (f"{explain.pretty(expr)} = 0",
         "Write it in standard form a*x^2 + b*x + c = 0."),
        (f"discriminant = b^2 - 4ac = {explain.pretty(disc)}",
         "The discriminant tells us how many real roots exist "
         "(positive → two, zero → one, negative → none)."),
    ]
    if factored != expr:
        steps.append((f"{explain.pretty(factored)} = 0",
                      "Factor the quadratic (or use the quadratic formula)."))
    steps.append((_fmt_sols(var, sols),
                  "Set each factor to zero to read off the solution(s)."))
    return SolveResult(ok=True, category="quadratic_equation",
                       category_label="Quadratic equation",
                       answer=_fmt_sols(var, sols), steps=steps)


def _steps_polynomial(start, expr, var, sols):
    factored = sp.factor(expr)
    steps = [
        (start, "Start with the given equation."),
        (f"{explain.pretty(factored)} = 0",
         "Factor the polynomial into simpler factors."),
        (_fmt_sols(var, sols),
         "Each factor set to zero gives a root."),
    ]
    return SolveResult(ok=True, category="polynomial_equation",
                       category_label="Polynomial equation",
                       answer=_fmt_sols(var, sols), steps=steps)


def _steps_general(start, expr, var, sols):
    steps = [
        (start, "Start with the given equation."),
        (f"Solve for {var}",
         "Isolate the variable using inverse operations."),
        (_fmt_sols(var, sols), "This gives the solution(s)."),
    ]
    return SolveResult(ok=True, category="equation",
                       category_label="Equation",
                       answer=_fmt_sols(var, sols), steps=steps)


# --------------------------------------------------------------------------
# Calculus
# --------------------------------------------------------------------------

def _pick_var(expr, prefer="x"):
    return parser.main_symbol(expr, prefer=prefer)


def _differentiate(raw):
    expr = parser.parse_expression(_strip_calculus_words(raw))
    var = _pick_var(expr)
    deriv = sp.diff(expr, var)
    steps = [
        (f"f({var}) = {explain.pretty(expr)}",
         f"Identify the function to differentiate with respect to {var}."),
    ]
    if isinstance(expr, sp.Add):
        for term in expr.args:
            steps.append(
                (f"d/d{var} [ {explain.pretty(term)} ] = {explain.pretty(sp.diff(term, var))}",
                 "Differentiate each term (power/constant/chain rule)."))
    result = sp.simplify(deriv)
    steps.append((f"f'({var}) = {explain.pretty(result)}",
                  "Combine the differentiated terms for the final derivative."))
    return SolveResult(ok=True, category="differentiation",
                       category_label="Differentiation",
                       answer=f"f'({var}) = {explain.pretty(result)}", steps=steps)


def _integrate(raw):
    expr = parser.parse_expression(_strip_calculus_words(raw))
    var = _pick_var(expr)
    integral = sp.integrate(expr, var)
    steps = [
        (f"∫ {explain.pretty(expr)} d{var}",
         f"Set up the indefinite integral with respect to {var}."),
    ]
    if isinstance(expr, sp.Add):
        for term in expr.args:
            steps.append(
                (f"∫ {explain.pretty(term)} d{var} = {explain.pretty(sp.integrate(term, var))}",
                 "Integrate each term (reverse power rule)."))
    steps.append((f"{explain.pretty(integral)} + C",
                  "Add the constant of integration C."))
    return SolveResult(ok=True, category="integration",
                       category_label="Integration",
                       answer=f"{explain.pretty(integral)} + C", steps=steps)


def _limit(raw):
    lower = raw.lower()
    m = re.search(r"as\s+([a-z])\s*(?:->|→|to|approaches)\s*([^\s]+)", lower)
    if m:
        var = sp.Symbol(m.group(1))
        point = parser.parse_expression(m.group(2))
        body = re.sub(r"as\s+[a-z]\s*(?:->|→|to|approaches)\s*[^\s]+", "", raw, flags=re.IGNORECASE)
    else:
        body, var, point = raw, sp.Symbol("x"), sp.Integer(0)
    expr = parser.parse_expression(_strip_calculus_words(body))
    value = sp.limit(expr, var, point)
    steps = [
        (f"lim({var} -> {explain.pretty(point)}) {explain.pretty(expr)}",
         "Set up the limit as the variable approaches the point."),
        (f"= {explain.pretty(value)}",
         "Substitute / simplify to evaluate the limit."),
    ]
    return SolveResult(ok=True, category="limit", category_label="Limit",
                       answer=explain.pretty(value), steps=steps)


def _strip_calculus_words(raw):
    """Remove leading verbs like 'derivative of' before parsing the expression."""
    s = re.sub(r"d\s*/\s*d[a-z]", " ", raw, flags=re.IGNORECASE)
    s = re.sub(r"\b(with|respect|to)\b", " ", s, flags=re.IGNORECASE)
    return s


# --------------------------------------------------------------------------
# Rewriting (factor / expand / simplify) and plain evaluation
# --------------------------------------------------------------------------

def _rewrite(raw, kind):
    expr = parser.parse_expression(raw)
    fn = {"factor": sp.factor, "expand": sp.expand, "simplify": sp.simplify}[kind]
    result = fn(expr)
    label = {"factor": "Factoring", "expand": "Expanding", "simplify": "Simplifying"}[kind]
    steps = [
        (explain.pretty(expr), f"Start with the expression to {kind}."),
        (explain.pretty(result), f"{label} gives the equivalent form."),
    ]
    return SolveResult(ok=True, category=kind, category_label=label,
                       answer=explain.pretty(result), steps=steps)


def _evaluate(raw):
    expr = parser.parse_expression(raw)
    simplified = sp.simplify(expr)
    steps = [(explain.pretty(expr), "Evaluate using the order of operations (BODMAS).")]

    if simplified.free_symbols:
        steps.append((explain.pretty(simplified), "Combine like terms to simplify."))
        answer = explain.pretty(simplified)
        category = "simplify"
        label = "Simplify expression"
    else:
        exact = sp.nsimplify(simplified)
        approx = sp.N(simplified, 6)
        answer = explain.pretty(exact)
        if sp.simplify(exact - approx) != 0 and not exact.is_Integer:
            answer = f"{explain.pretty(exact)}  (≈ {explain.pretty(approx)})"
        steps.append((answer, "Compute the exact value (and a decimal if useful)."))
        category = "arithmetic"
        label = "Arithmetic"
    return SolveResult(ok=True, category=category, category_label=label,
                       answer=answer, steps=steps)
