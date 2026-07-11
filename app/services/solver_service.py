"""Solver service: the UI's single entry point to the math engine.

Runs ``math_engine.solve`` on a worker thread (SymPy can be slow) and delivers
the ``SolveResult`` back on the Kivy UI thread via ``run_async``.
"""

from app.core import math_engine
from app.utils.async_task import run_async


def solve_async(raw, on_done, on_error=None):
    """Solve ``raw`` in the background; call ``on_done(SolveResult)`` on the UI thread."""
    run_async(lambda: math_engine.solve(raw), on_done=on_done, on_error=on_error)


def solve_sync(raw):
    """Blocking solve (used by tests / non-UI callers)."""
    return math_engine.solve(raw)
