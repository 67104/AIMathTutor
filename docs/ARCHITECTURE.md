# AI Math Tutor — Architecture (Phase 1)

100% Python. UI in Kivy + KivyMD, math in SymPy/NumPy, OCR via OpenCV +
Tesseract, storage in local SQLite. No paid cloud services. Optional FastAPI
backend is **off by default** — everything runs on-device.

## 1. Layered architecture

```
┌───────────────────────────────────────────────────────────────┐
│  PRESENTATION  (Kivy / KivyMD)                                 │
│  app/screens/*.py  +  app/kv/*.kv  +  app/widgets/*            │
│  Navigation drawer, bottom nav, Material cards, animations     │
└───────────────▲───────────────────────────────────────────────┘
                │ calls (never touches SQL/OCR directly)
┌───────────────┴───────────────────────────────────────────────┐
│  SERVICES  (business logic, framework-agnostic, unit-testable) │
│  solver_service · ocr_service · practice_service ·             │
│  olympiad_service · progress_service · gamification_service    │
└───────────────▲───────────────────────────────────────────────┘
                │ uses
┌───────────────┴───────────────────────────────────────────────┐
│  CORE ENGINES                                                  │
│  math_engine (SymPy)  ·  step_explainer  ·  question_gen       │
│  image_pipeline (OpenCV/Pillow)  ·  expr_parser                │
└───────────────▲───────────────────────────────────────────────┘
                │ persists via
┌───────────────┴───────────────────────────────────────────────┐
│  DATA  (SQLite)  app/database/  +  data/schema.sql             │
│  repositories (users, attempts, questions, progress, ...)      │
└────────────────────────────────────────────────────────────────┘
```

**Rule:** Screens never import `sqlite3`, `cv2`, or `sympy` directly. They call
`services`. Services call `core` + `database`. This keeps the UI thin and lets
every engine be tested without Kivy running.

## 2. Threading model (critical for a responsive UI)

Kivy runs a single UI thread. Heavy work (SymPy solve, OpenCV OCR) must **not**
block it or the app freezes / Android shows ANR.

- Long tasks run on a background `threading.Thread` (or a small worker pool).
- Results are marshalled back to the UI with `kivy.clock.Clock.schedule_once`.
- Pattern is centralised in `app/utils/async_task.py` (`run_async(fn, on_done)`).

## 3. App startup flow

```
main.py
  └─ MathTutorApp (MDApp)
       ├─ Database.bootstrap()        # create db, run schema.sql, migrate, seed
       ├─ load .kv files              # app/kv/*.kv
       ├─ build ScreenManager         # register all screens
       └─ route: profile exists? → Home  else → Onboarding
```

## 4. Screen map (ScreenManager routes)

| Route name        | Screen file                | Purpose                                  |
|-------------------|----------------------------|------------------------------------------|
| `onboarding`      | onboarding_screen.py       | First run: name / age / grade            |
| `home`            | home_screen.py             | Card grid of features + drawer + bottom nav |
| `ask_ai`          | ask_ai_screen.py           | Type question → steps + concept + similar |
| `camera`          | camera_screen.py           | Capture / gallery → OCR → solve          |
| `practice`        | practice_screen.py         | Adaptive graded practice                 |
| `olympiad`        | olympiad_screen.py         | SOF prep: IMO/NSO/IEO/IGKO, mocks        |
| `progress`        | progress_screen.py         | Charts, streak, strong/weak topics       |
| `daily`           | daily_challenge_screen.py  | One challenge/day + reward               |
| `achievements`    | achievements_screen.py     | XP, level, badges                        |
| `settings`        | settings_screen.py         | Theme, font, notifications, grade, age   |

## 5. Module responsibilities

- `app/core/math_engine.py` — parse + solve via SymPy; returns structured result.
- `app/core/step_explainer.py` — turns a solve into ordered, human steps + the
  "why" + the underlying concept blurb.
- `app/core/expr_parser.py` — normalises typed/OCR text into SymPy-safe input
  (handles `×`, `÷`, `^`, implicit multiplication, unicode).
- `app/core/question_gen.py` — parametric generators per topic/grade/difficulty;
  produces original questions (Olympiad style without copying past papers).
- `app/core/image_pipeline.py` — OpenCV/Pillow preprocessing (grayscale,
  denoise, threshold, deskew, crop) before OCR.
- `app/services/*` — orchestrate core + db for each feature; the UI's API.
- `app/database/` — `connection.py`, `migrations.py`, `seed.py`, `repositories/`.
- `app/utils/` — `async_task.py`, `theme.py`, `constants.py`, `validators.py`.

## 6. Configuration & theming

- Central palette + typography scale in `app/utils/theme.py`, applied to
  KivyMD `theme_cls`. Dark/Light/System driven by `settings.theme`.
- Font scale (`settings.font_scale`) multiplies base font sizes app-wide.

## 7. Offline-first guarantee

Every feature works with no network: SymPy solves locally, questions are
generated locally, OCR runs on-device, SQLite is local. FastAPI is only a
future optional sync/backup surface and ships disabled.
