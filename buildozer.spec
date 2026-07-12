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
# NOTE: names here are python-for-android RECIPE names, which differ from pip.
# OMITTED on Android on purpose (hardest-to-package libs that provide no working
# mobile feature here, so leaving them out makes the build reliable with zero
# feature loss on the phone):
#   * matplotlib     -> progress chart is drawn in pure Kivy (widgets/bar_chart.py)
#   * opencv + numpy -> only used for OCR image pre-processing, which needs
#       Tesseract; Tesseract isn't bundled on Android, so camera OCR degrades to
#       typed input anyway (guarded by image_pipeline.is_available()).
#   * pyjnius bridges Android permissions/camera; sqlite3 ships with python3.
requirements = python3,kivy==2.3.0,kivymd==1.2.0,sympy,pillow,plyer,pyjnius,android

# CRITICAL: Buildozer clones its OWN python-for-android (default branch = master),
# ignoring any pip-installed p4a. Master now builds Python 3.14, which no recipe
# supports. Pin p4a to the stable 2024.01.21 release (builds Python 3.11).
p4a.branch = 2024.01.21

orientation = portrait
fullscreen = 0

# --- Android permissions (runtime grants requested in app/utils/platform_utils) ---
android.permissions = CAMERA, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_IMAGES, INTERNET, VIBRATE, POST_NOTIFICATIONS

# --- SDK / NDK / API levels ---
android.api = 34
android.minapi = 24
android.ndk = 25b
# Single ABI for the first build: arm64-v8a covers virtually all modern phones,
# halves build time, and avoids 32-bit compile issues. Add armeabi-v7a later if
# you need to support very old devices.
android.archs = arm64-v8a
android.allow_backup = 1

# Branding (add PNGs to assets/, then uncomment):
# presplash.filename = %(source.dir)s/assets/images/presplash.png
# icon.filename = %(source.dir)s/assets/icons/appicon.png

# Keep the build smaller: only the English tessdata isn't bundled (no Tesseract),
# and we target the two mainstream ABIs above.

[buildozer]
log_level = 2
warn_on_root = 1
