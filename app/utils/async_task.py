"""Run blocking work off the Kivy UI thread and deliver results back on it.

SymPy solves (and later OCR) can take noticeable time; doing them on the UI
thread freezes the app (and triggers ANR on Android). ``run_async`` runs the
function on a worker thread and marshals the result back to the main thread via
the Kivy Clock, so callbacks can safely touch widgets.
"""

import threading
import traceback

from kivy.clock import Clock


def run_async(func, on_done=None, on_error=None):
    """Execute ``func()`` on a background thread.

    Args:
        func: zero-arg callable performing the heavy work.
        on_done: called on the UI thread with ``func``'s return value.
        on_error: called on the UI thread with the Exception (optional).
    """

    def worker():
        try:
            result = func()
        except Exception as exc:  # noqa: BLE001 - surface any failure to UI
            traceback.print_exc()
            if on_error is not None:
                Clock.schedule_once(lambda _dt, e=exc: on_error(e), 0)
            return
        if on_done is not None:
            Clock.schedule_once(lambda _dt, r=result: on_done(r), 0)

    threading.Thread(target=worker, daemon=True).start()
