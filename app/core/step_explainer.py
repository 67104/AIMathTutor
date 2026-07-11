"""Concept explanations and pretty-printing helpers for solutions.

``math_engine`` builds the ordered steps; this module supplies the *why it
matters* concept text per category and utilities to render SymPy objects as
clean, student-friendly strings.
"""

import sympy as sp

# Human-readable concept blurbs keyed by solution category.
CONCEPTS = {
    "linear_equation": (
        "A linear equation has the variable to the first power. Solve it by "
        "keeping the equation balanced: do the same operation to both sides "
        "until the variable stands alone."
    ),
    "quadratic_equation": (
        "A quadratic equation has an x-squared term. It can have two, one, or "
        "no real solutions. You can solve it by factoring, completing the "
        "square, or the quadratic formula x = (-b ± √(b²-4ac)) / 2a."
    ),
    "polynomial_equation": (
        "A polynomial equation is solved by finding the values that make it "
        "equal to zero (its roots). Factoring reveals the roots directly."
    ),
    "equation_system": (
        "A system of equations is solved by finding values that satisfy all "
        "equations at once — using substitution or elimination."
    ),
    "differentiation": (
        "The derivative measures the instantaneous rate of change of a "
        "function. Apply the power, product, quotient, and chain rules term "
        "by term."
    ),
    "integration": (
        "Integration is the reverse of differentiation; the indefinite "
        "integral adds a constant of integration (+C) because many functions "
        "share the same derivative."
    ),
    "limit": (
        "A limit describes the value a function approaches as the input nears "
        "a point, even if the function is undefined exactly there."
    ),
    "factor": (
        "Factoring rewrites an expression as a product of simpler factors — "
        "useful for finding roots and simplifying."
    ),
    "expand": (
        "Expanding multiplies everything out and combines like terms to get a "
        "polynomial in standard form."
    ),
    "simplify": (
        "Simplifying rewrites an expression in its most compact equivalent "
        "form by combining like terms and reducing fractions."
    ),
    "arithmetic": (
        "Evaluate using the order of operations (PEMDAS/BODMAS): brackets, "
        "exponents, multiplication/division, then addition/subtraction."
    ),
}


def pretty(expr):
    """Render a SymPy object as a compact one-line string (^ for powers)."""
    try:
        s = sp.sstr(expr)
    except Exception:  # noqa: BLE001
        s = str(expr)
    return s.replace("**", "^")


def eq_str(lhs, rhs):
    """Format ``lhs = rhs`` for display."""
    return f"{pretty(lhs)} = {pretty(rhs)}"


def concept_for(category):
    return CONCEPTS.get(category, "")
