"""Camera Solver screen (Phase 4).

Flow:  capture (webcam) / pick image  ->  OpenCV preprocess + Tesseract OCR
       ->  editable recognised text  ->  Phase 3 solver.

OCR runs on a background thread (it can take a second or two). The recognised
text is always shown in an editable field — OCR is a draft, never the truth
(see docs/PROBLEMS.md). Android's native camera/gallery is wired in the APK
phase; on desktop we use OpenCV's webcam grab and a Kivy file chooser.
"""

import os
import tempfile

from kivymd.uix.screen import MDScreen

from app.core import image_pipeline
from app.services import ocr_service, solver_service
from app.utils import paths, platform_utils
from app.utils.async_task import run_async


class CameraScreen(MDScreen):

    def on_pre_enter(self, *args):
        # Ask for camera/storage at point-of-use (no-op on desktop).
        platform_utils.request_camera_permissions()

    # ---- image acquisition ----

    def capture(self):
        if platform_utils.is_android():
            self._android_capture()
            return
        # Desktop: grab a frame from the webcam via OpenCV (off-thread).
        self._set_status("Opening camera...")
        save = os.path.join(tempfile.gettempdir(), "aimt_capture.png")
        run_async(lambda: save if image_pipeline.capture_webcam(save) else None,
                  on_done=self._on_capture, on_error=self._on_error)

    def _android_capture(self):
        save = os.path.join(paths.writable_dir(), "aimt_capture.png")
        try:
            from plyer import camera
            self._set_status("Opening camera...")
            camera.take_picture(filename=save, on_complete=self._on_capture)
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Camera unavailable — use Gallery instead ({exc}).")

    def _on_capture(self, path):
        if not path:
            self._set_status("No camera available — use Gallery or type it below.")
            return
        self._run_ocr(path)

    def pick_gallery(self):
        if platform_utils.is_android():
            self._android_gallery()
            return
        self._desktop_gallery()

    def _android_gallery(self):
        try:
            from plyer import filechooser
            filechooser.open_file(
                on_selection=self._on_gallery_selection,
                filters=[["Images", "*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp"]],
            )
        except Exception as exc:  # noqa: BLE001
            self._set_status(f"Gallery unavailable ({exc}).")

    def _on_gallery_selection(self, selection):
        if selection:
            self._run_ocr(selection[0])

    def _desktop_gallery(self):
        """Open a Kivy file chooser (desktop)."""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.filechooser import FileChooserIconView
        from kivy.uix.popup import Popup
        from kivymd.uix.button import MDRaisedButton, MDFlatButton

        box = BoxLayout(orientation="vertical", spacing=8, padding=8)
        chooser = FileChooserIconView(
            filters=["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.webp"]
        )
        bar = BoxLayout(size_hint_y=None, height="48dp", spacing=8)
        popup = Popup(title="Select an image", content=box, size_hint=(0.95, 0.95))

        def do_select(*_):
            selection = chooser.selection
            popup.dismiss()
            if selection:
                self._run_ocr(selection[0])

        bar.add_widget(MDFlatButton(text="Cancel", on_release=lambda *_: popup.dismiss()))
        bar.add_widget(MDRaisedButton(text="Select", on_release=do_select))
        box.add_widget(chooser)
        box.add_widget(bar)
        popup.open()

    # ---- OCR (background) ----

    def _run_ocr(self, path):
        self._set_status("Reading image...")
        run_async(lambda: ocr_service.read_math(path),
                  on_done=self._on_ocr, on_error=self._on_error)

    def _on_ocr(self, res):
        if not res["ok"]:
            self._set_status(res["error"])
            return
        self.ids.recognized_field.text = res["text"]
        self._set_status(
            f"Recognised (confidence ~{res['confidence']}%). "
            "Check/fix it, then tap Solve."
        )

    # ---- solve the (editable) recognised text ----

    def solve(self):
        expr = self.ids.recognized_field.text.strip()
        if not expr:
            self._set_status("Nothing to solve — capture or type an expression.")
            return
        self._set_status("Solving...")
        solver_service.solve_async(expr, on_done=self._on_solved,
                                   on_error=self._on_error)

    def _on_solved(self, result):
        if not result.ok:
            self._set_status(result.error)
            return
        self.ids.answer_label.text = result.answer
        self.ids.result_box.opacity = 1
        self._set_status(f"Solved as: {result.category_label}")

    # ---- helpers ----

    def _on_error(self, exc):
        self._set_status(f"Something went wrong: {exc}")

    def _set_status(self, msg):
        self.ids.status_label.text = msg
