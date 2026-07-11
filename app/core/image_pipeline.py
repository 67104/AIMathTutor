"""OpenCV/Pillow image preprocessing for OCR.

A good OCR result depends far more on preprocessing than on Tesseract options.
``preprocess`` runs the standard cleanup chain that makes printed math legible:

    load -> grayscale -> resize to a sane range -> denoise -> adaptive threshold
    -> deskew

It returns a binarised NumPy image ready to hand to Tesseract. A best-effort
``capture_webcam`` grabs a single frame on desktop (Android camera is wired in
the APK phase via a platform camera).
"""

import cv2
import numpy as np

# Keep the long edge within this range: too small hurts accuracy, too large is slow.
_MIN_LONG_EDGE = 900
_MAX_LONG_EDGE = 1600


def _resize_into_range(gray):
    h, w = gray.shape[:2]
    long_edge = max(h, w)
    if long_edge == 0:
        return gray
    if long_edge < _MIN_LONG_EDGE:
        scale = _MIN_LONG_EDGE / long_edge
    elif long_edge > _MAX_LONG_EDGE:
        scale = _MAX_LONG_EDGE / long_edge
    else:
        return gray
    interp = cv2.INTER_CUBIC if scale > 1 else cv2.INTER_AREA
    return cv2.resize(gray, (int(w * scale), int(h * scale)), interpolation=interp)


def _deskew(binary):
    """Rotate so text lines are horizontal (small angles only)."""
    coords = np.column_stack(np.where(binary > 0))
    if coords.shape[0] < 50:
        return binary
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    if abs(angle) < 0.5 or abs(angle) > 20:  # ignore noise / large tilts
        return binary
    h, w = binary.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(binary, m, (w, h),
                          flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def load_image(path):
    """Read an image from disk as a BGR NumPy array (raises on failure)."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        # Fallback for paths/codecs OpenCV's imread trips on (e.g. unicode).
        data = np.fromfile(path, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"Could not read image: {path}")
    return img


def preprocess(path):
    """Return a cleaned, binarised image (NumPy uint8) ready for OCR."""
    img = load_image(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = _resize_into_range(gray)
    # Reduce sensor/scan noise while keeping edges.
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    # CLAHE normalises uneven lighting (shadows/glare) before thresholding, so
    # a clean global Otsu threshold works on real photos too. Empirically this
    # beat plain adaptive thresholding on printed math (see docs/PROBLEMS.md).
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Tesseract wants dark text on light background; ensure that orientation.
    if np.mean(binary) < 127:
        binary = cv2.bitwise_not(binary)
    # Deskew works on white-text-on-black, so invert for the calc then restore.
    inv = cv2.bitwise_not(binary)
    inv = _deskew(inv)
    binary = cv2.bitwise_not(inv)
    return binary


def capture_webcam(save_path, cam_index=0):
    """Grab one frame from a desktop webcam and save it. Returns True on success."""
    cap = cv2.VideoCapture(cam_index)
    try:
        if not cap.isOpened():
            return False
        ok, frame = cap.read()
        if not ok or frame is None:
            return False
        cv2.imwrite(save_path, frame)
        return True
    finally:
        cap.release()
