# AI Math Tutor 🎓

A modern, offline-first **AI Math Tutor mobile app built 100% in Python**
(Kivy + KivyMD UI, SymPy math engine, OpenCV + Tesseract OCR, local SQLite).
No paid cloud services required.

> **Status:** Phase 1 complete (architecture, folder structure, wireframes,
> database design). Build proceeds one phase at a time.

## Folder structure
```
AIMathTutor/
├── main.py                     # app entry point (Phase 2)
├── requirements.txt            # Python deps (desktop dev)
├── buildozer.spec              # Android packaging (Phase 9)
├── README.md
│
├── app/
│   ├── core/                   # framework-agnostic engines
│   │   ├── math_engine.py      #   SymPy solve
│   │   ├── expr_parser.py      #   text/OCR -> SymPy-safe expr
│   │   ├── step_explainer.py   #   steps + "why" + concept
│   │   ├── question_gen.py     #   parametric question generators
│   │   └── image_pipeline.py   #   OpenCV/Pillow preprocessing
│   ├── services/               # feature orchestration (UI's API)
│   │   ├── solver_service.py
│   │   ├── ocr_service.py
│   │   ├── practice_service.py
│   │   ├── olympiad_service.py
│   │   ├── progress_service.py
│   │   └── gamification_service.py
│   ├── screens/                # one .py per screen (Phase 2)
│   ├── kv/                     # matching KivyMD .kv layouts (Phase 2)
│   ├── widgets/                # reusable Material components
│   ├── database/               # connection, migrations, seed, repositories
│   └── utils/                  # theme, async_task, paths, constants, validators
│
├── assets/                     # images, icons, fonts, animations, sounds
├── data/
│   └── schema.sql              # SQLite schema (this phase)
├── docs/
│   ├── ARCHITECTURE.md
│   ├── WIREFRAMES.md
│   └── PROBLEMS.md             # expected problems + mitigations
└── tests/                      # pytest suites (Phase 8)
```

## Running the tests
```bash
pip install pytest
python -m pytest            # 72 tests: parser, engine, generators, DB, analytics, OCR
```
OCR tests self-skip if the Tesseract binary isn't installed.

## Build phases
1. ✅ Architecture, folder structure, wireframes, DB design
2. ✅ Complete KivyMD interface (9 screens, drawer + bottom nav)
3. ✅ AI Solver (SymPy engine, steps, concept, similar questions)
4. ✅ OCR Camera Solver (OpenCV + Tesseract, editable draft)
5. ✅ Practice question generator (grade-aware, adaptive difficulty)
6. ✅ Olympiad module (IMO/NSO/IEO/IGKO, timed mocks, analysis)
7. ✅ Progress tracking (analytics, Matplotlib charts, badges)
8. ✅ Testing (72-test pytest suite)
9. ✅ Android APK via Buildozer — see [docs/BUILD_ANDROID.md](docs/BUILD_ANDROID.md)
   (build under Linux/WSL2/Docker; Android Studio for SDK/NDK/emulator/debug)

## Dev setup (desktop)
```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
pip install -r requirements.txt
# Install Tesseract OCR engine separately (see requirements.txt)
python main.py                    # available from Phase 2
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the design and
[docs/PROBLEMS.md](docs/PROBLEMS.md) for the risk register.
