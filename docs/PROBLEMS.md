# Expected Development Problems & Mitigations (assessed before coding)

Each entry: **Problem · Why it occurs · Solution · Prevention · Best practice.**

---

### 1. OCR inaccuracies on printed math
- **Why:** Tesseract is tuned for prose, not math notation (`√`, `∫`, `π`,
  fraction bars, superscripts). It confuses `x`↔`×`, `l`↔`1`, `O`↔`0`, `-`↔`—`.
- **Solution:** Preprocess with OpenCV (grayscale → denoise → adaptive
  threshold → deskew → crop to ROI); run Tesseract with `--psm 6/7` and a
  restricted whitelist; post-correct with `expr_parser` symbol-normalisation.
- **Prevention:** Constrain capture with an on-screen guide box; require decent
  contrast; validate OCR output parses in SymPy before "solving".
- **Best practice:** Always show the recognised expression to the user for a
  one-tap edit before solving. Treat OCR as a *draft*, never as truth.

### 2. Handwriting recognition errors
- **Why:** Tesseract is essentially unusable on free handwriting; strokes vary.
- **Solution:** Scope v1 to **printed/typed** math. For handwriting, evaluate an
  on-device model later (Google ML Kit Digital Ink / a small tflite model via
  pyjnius) as a separate pipeline; keep manual-edit fallback.
- **Prevention:** Set user expectations in the camera UI ("works best on printed
  problems"). Don't promise handwriting until it's measured.
- **Best practice:** Confidence-gate: if OCR confidence is low, route to manual
  entry instead of returning a wrong solve.

### 3. Camera & storage permissions (Android)
- **Why:** Android 6+ needs runtime permission grants; Android 13+ splits media
  perms; users can deny.
- **Solution:** Request via `plyer`/`android.permissions` at point-of-use;
  handle denial gracefully (offer gallery or typed input).
- **Prevention:** Declare exactly the perms in `buildozer.spec`
  (CAMERA, media, POST_NOTIFICATIONS). Never crash on denial.
- **Best practice:** Feature-detect and degrade — the app stays fully usable via
  typed input if the camera is unavailable.

### 4. Slow image processing / UI freeze
- **Why:** OpenCV + Tesseract on a full-res photo can take seconds; on the UI
  thread that freezes Kivy and triggers Android ANR.
- **Solution:** Run the whole capture→OCR→solve pipeline in a worker thread via
  `utils/async_task.run_async`; marshal results back with `Clock`.
- **Prevention:** Downscale images to a max dimension (~1600px) before OCR.
- **Best practice:** Show a determinate/indeterminate spinner; never block input.

### 5. Incorrect equation parsing
- **Why:** `2^3`, `3(x+1)`, `sin30`, `1/2x`, unicode `−`/`×`/`÷` don't map
  straight to SymPy. Implicit multiplication and precedence bite.
- **Solution:** `expr_parser` normalises symbols + inserts implicit `*`, then
  uses `sympy.parsing.sympy_parser.parse_expr` with transformations
  (`implicit_multiplication_application`, `convert_xor`).
- **Prevention:** Unit-test the parser against a big fixture of real inputs.
- **Best practice:** Fail loud & friendly — if parse fails, tell the user which
  token was unexpected instead of guessing.

### 6. Kivy performance / jank
- **Why:** Rebuilding large widget trees, unbounded scroll children, per-frame
  Python work, big PNGs cause dropped frames.
- **Solution:** Use `RecycleView` for long lists; cache/atlas images; keep `.kv`
  bindings cheap; avoid work in `on_touch`/`update` loops.
- **Prevention:** Profile with Kivy inspector; lazy-load screens on first visit.
- **Best practice:** Static layout in `.kv`, dynamic data via properties/events.

### 7. Android compatibility (arch, API, libs)
- **Why:** python-for-android recipes differ from pip (e.g. `opencv` recipe vs
  `opencv-python`); NDK/API mismatches; native libs must build for arm64+armv7.
- **Solution:** Pin `android.api`, `minapi`, `ndk`, `archs` in `buildozer.spec`;
  use p4a recipe names in `requirements`.
- **Prevention:** Build on Linux/WSL2 in a clean container early; don't wait for
  Phase 9 to first attempt an APK.
- **Best practice:** Keep a "does it import on-device" smoke test.

### 8. APK size bloat
- **Why:** OpenCV, NumPy, Matplotlib, SymPy, Tesseract data are large; bundling
  every ABI doubles size.
- **Solution:** Ship arm64-v8a (+ armv7 only if needed); strip unused assets;
  consider dropping Matplotlib in favour of Kivy-drawn charts if size-critical.
- **Prevention:** Track APK size per build; lazy-import heavy modules.
- **Best practice:** Only bundle Tesseract language data actually used (`eng`).

### 9. Battery / CPU drain
- **Why:** Camera preview, repeated OCR, animations, background timers.
- **Solution:** Stop camera when leaving the screen; debounce OCR; cap animation
  rates; no polling loops.
- **Prevention:** Release resources in `on_leave`; single shared worker pool.
- **Best practice:** Do expensive work once, cache the result in SQLite.

### 10. Memory leaks
- **Why:** Retained references to old screens, unbound Clock events, undisposed
  camera/texture/OpenCV `Mat` objects.
- **Solution:** Explicitly `unbind`/`Clock.unschedule` on `on_leave`; release
  textures and camera; let large arrays go out of scope.
- **Prevention:** One ScreenManager, reuse screens; avoid global caches of
  widgets.
- **Best practice:** Manual GC checkpoints after heavy image ops; test long
  sessions.

### 11. SymPy solve hangs / wrong domain
- **Why:** Some inputs are slow or ambiguous (assumptions, complex roots).
- **Solution:** Run solves in a worker with a timeout; pick `solve`/`solveset`
  deliberately; declare symbol assumptions (real, positive) per topic.
- **Prevention:** Route by problem type (algebra vs calculus) to the right API.
- **Best practice:** Always present steps, not just the final answer.

### 12. Buildozer won't run on Windows
- **Why:** python-for-android toolchain is POSIX-only.
- **Solution:** Build the APK under WSL2/Linux or Docker; develop/test the app
  itself on Windows desktop normally.
- **Prevention:** Document the split (dev on Windows, package on Linux) now.
- **Best practice:** Provide a reproducible Docker/WSL build recipe in Phase 9.

### 13. Original Olympiad content vs copyright
- **Why:** SOF past papers are copyrighted; reproducing them verbatim is not ok.
- **Solution:** Parametric generators that match *syllabus, style, difficulty*
  and produce fresh numbers/wording each time; store as `source='generated'`.
- **Prevention:** No hardcoded past-paper text anywhere in the repo.
- **Best practice:** Tag every generated question with topic + difficulty for
  transparent, syllabus-aligned coverage.

### 14. Cross-platform file paths & DB location
- **Why:** Android app storage != desktop CWD; hardcoded paths break on-device.
- **Solution:** Resolve paths via `App.user_data_dir`; copy `schema.sql`/seed on
  first run into the writable app dir.
- **Prevention:** Never hardcode `C:\...` or `/data/...`.
- **Best practice:** All path logic centralised in `utils/paths.py`.
