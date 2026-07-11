"""OCR pipeline test — skipped automatically if Tesseract isn't installed.

Renders a clean printed equation to a PNG (simulating a photo) and checks the
OCR service reads it and the solver can then solve it.
"""

import os

import pytest

from app.services import ocr_service, solver_service

pytestmark = pytest.mark.skipif(
    not ocr_service.is_available(),
    reason="Tesseract OCR binary not installed on this machine",
)


def _make_image(text, path):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (760, 200), "white")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except OSError:
        try:
            font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 72)
        except OSError:
            font = ImageFont.load_default()
    draw.text((40, 60), text, fill="black", font=font)
    img.save(path)


def test_ocr_reads_printed_equation(tmp_path):
    path = str(tmp_path / "eq.png")
    _make_image("2x + 3 = 11", path)
    res = ocr_service.read_math(path)
    assert res["ok"], res["error"]
    assert "2x+3=11" in res["text"].replace(" ", "")


def test_ocr_result_solves(tmp_path):
    path = str(tmp_path / "eq2.png")
    _make_image("2x + 3 = 11", path)
    res = ocr_service.read_math(path)
    assert res["ok"]
    sol = solver_service.solve_sync(res["text"])
    assert sol.ok and "x = 4" in sol.answer


def test_missing_image_reported_gracefully():
    res = ocr_service.read_math("does_not_exist_12345.png")
    assert res["ok"] is False
    assert res["error"]
