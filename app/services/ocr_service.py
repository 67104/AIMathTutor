"""OCR service: read a math expression from an image using Tesseract.

Design decisions driven by docs/PROBLEMS.md:
  * OCR is treated as a *draft* — the UI always lets the user edit the result.
  * The Tesseract binary is auto-located; if it's missing we fail with a clear,
    actionable message instead of crashing.
  * Light post-correction fixes the most common math misreads; the heavier
    normalisation lives in expr_parser (single source of truth).
"""

import os
import shutil

import pytesseract

# Common install locations to probe if Tesseract isn't already on PATH.
_CANDIDATE_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
    "/usr/bin/tesseract",
    "/usr/local/bin/tesseract",
    "/opt/homebrew/bin/tesseract",
]

# Characters we expect in printed math (helps Tesseract avoid prose guesses).
# Lowercase-only: math variables/functions (x, y, sin, cos, sqrt...) are lower
# case, and excluding uppercase removes a common misread (e.g. "2x" -> "2Xx").
_WHITELIST = (
    "0123456789"
    "abcdefghijklmnopqrstuvwxyz"
    "+-*/=().,^<>[]{}|"
)

# psm 6 = assume a uniform block of text (robust for one or few lines of math).
_CONFIG = f'--oem 3 --psm 6 -c tessedit_char_whitelist={_WHITELIST}'

# Frequent OCR confusions in a math context (applied conservatively).
_FIXES = {
    "×": "*", "÷": "/", "−": "-", "—": "-", "–": "-",
    "“": "", "”": "", "’": "", "·": "*",
}


def _locate_binary():
    """Find and register the Tesseract executable. Returns path or None."""
    onpath = shutil.which("tesseract")
    if onpath:
        pytesseract.pytesseract.tesseract_cmd = onpath
        return onpath
    for p in _CANDIDATE_PATHS:
        if p and os.path.exists(p):
            pytesseract.pytesseract.tesseract_cmd = p
            return p
    return None


def is_available():
    return _locate_binary() is not None


def _post_process(text):
    for bad, good in _FIXES.items():
        text = text.replace(bad, good)
    # Collapse to a single line; math expressions are usually one line.
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return " ".join(lines).strip()


def read_math(image_path):
    """OCR the math in ``image_path``.

    Returns a dict:
        {"ok": bool, "text": str, "confidence": float, "error": str}
    Never raises — failures are reported in the dict for the UI to show.
    """
    from app.core import image_pipeline  # local import keeps cv2 off cold paths

    if not _locate_binary():
        return {"ok": False, "text": "", "confidence": 0.0,
                "error": ("Tesseract OCR engine not found. Install it "
                          "(Windows: UB-Mannheim build) and retry.")}
    if not os.path.exists(image_path):
        return {"ok": False, "text": "", "confidence": 0.0,
                "error": f"Image not found: {image_path}"}

    try:
        processed = image_pipeline.preprocess(image_path)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "text": "", "confidence": 0.0,
                "error": f"Could not process image: {exc}"}

    try:
        raw = pytesseract.image_to_string(processed, config=_CONFIG)
        data = pytesseract.image_to_data(
            processed, config=_CONFIG, output_type=pytesseract.Output.DICT
        )
    except pytesseract.TesseractError as exc:
        return {"ok": False, "text": "", "confidence": 0.0,
                "error": f"OCR failed: {exc}"}

    confs = [float(c) for c in data.get("conf", []) if str(c) not in ("-1", "")]
    confidence = round(sum(confs) / len(confs), 1) if confs else 0.0

    text = _post_process(raw)
    if not text:
        return {"ok": False, "text": "", "confidence": confidence,
                "error": "No text detected. Try better lighting or framing."}
    return {"ok": True, "text": text, "confidence": confidence, "error": ""}
