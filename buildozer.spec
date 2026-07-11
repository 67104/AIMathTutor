# ============================================================================
# AI Math Tutor — Buildozer configuration (Phase 9)
# Build (on Linux / WSL2 / Docker — NOT native Windows):
#     buildozer -v android debug
# The signed release path is documented in docs/BUILD_ANDROID.md.
# ============================================================================

[app]
title = AI Math Tutor
package.name = aimathtutor
package.domain = com.exxat.aimathtutor
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,ttf,otf,json,sql,txt,atlas
# Ship the bundled schema + assets. (weekly_chart.png is generated at runtime
# into the app's private dir, so no chart assets are bundled.)
source.include_patterns = data/schema.sql,assets/*
version = 0.1.0

# --- Python + library requirements ---
# NOTE: names here are python-for-android RECIPE names, which differ from pip:
#   * opencv   (NOT opencv-python)   – heavy; pulls numpy
#   * pillow, numpy, sympy, plyer all have p4a recipes
#   * pyjnius is needed for Android permission/camera bridging
#   * sqlite3 ships with the python3 recipe (no entry needed)
# Matplotlib is intentionally OMITTED — the progress chart is drawn in pure Kivy
# (app/widgets/bar_chart.py), removing the hardest-to-package dependency.
# Tesseract/pytesseract is also OMITTED on Android — the desktop OCR binary
# isn't practical to bundle. See docs/BUILD_ANDROID.md for on-device OCR
# options; the app degrades to typed input if OCR is unavailable.
requirements = python3,kivy==2.3.0,kivymd==1.2.0,sympy,numpy,pillow,opencv,plyer,pyjnius,android

orientation = portrait
fullscreen = 0

# --- Android permissions (runtime grants requested in app/utils/platform_utils) ---
android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, INTERNET, VIBRATE, POST_NOTIFICATIONS

# --- SDK / NDK / API levels ---
android.api = 34
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = 1

# Branding (add PNGs to assets/, then uncomment):
# presplash.filename = %(source.dir)s/assets/images/presplash.png
# icon.filename = %(source.dir)s/assets/icons/appicon.png

# Keep the build smaller: only the English tessdata isn't bundled (no Tesseract),
# and we target the two mainstream ABIs above.

[buildozer]
log_level = 2
warn_on_root = 1
