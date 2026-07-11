# UI Wireframes (Phase 1) — low-fidelity, KivyMD

Portrait, mobile-first. Modern learning-app feel: navigation drawer + bottom
navigation + Material cards + rounded buttons. NOT a calculator.

## Onboarding (first run)
```
┌──────────────────────────────┐
│        🎓  Welcome!           │
│   Let's set up your profile   │
│                              │
│  Name   [__________________] │
│  Age    [____]  Grade [▼ 6 ] │
│                              │
│        ( Get Started )        │   <- rounded raised button
└──────────────────────────────┘
```

## Home
```
┌──────────────────────────────┐
│ ☰  AI Math Tutor        🔥 5  │  <- drawer icon, streak chip
│ Hi Ankur • Grade 6 • Lvl 3    │
│ ▓▓▓▓▓▓░░░  XP 320/500         │  <- level progress bar
│                              │
│ ┌────────┐ ┌────────┐         │
│ │ 🤖     │ │ 📷     │         │
│ │ Ask AI │ │ Camera │         │  <- Material cards, 2-col grid
│ └────────┘ └────────┘         │
│ ┌────────┐ ┌────────┐         │
│ │ ✏️     │ │ 🏆     │         │
│ │Practice│ │Olympiad│         │
│ └────────┘ └────────┘         │
│ ┌────────┐ ┌────────┐         │
│ │ 📊     │ │ ⭐     │         │
│ │Progress│ │ Daily  │         │
│ └────────┘ └────────┘         │
│                              │
│ [ 🏠 Home | 📊 Progress | ⚙ ] │  <- bottom navigation
└──────────────────────────────┘
```

## Ask AI (solver)
```
┌──────────────────────────────┐
│ ←  Ask AI                     │
│ ┌──────────────────────────┐ │
│ │ Type a math question…    │ │  <- text field
│ └──────────────────────────┘ │
│            ( Solve )          │
│ ── Answer ──────────────────  │
│  x = 4                        │  <- highlighted answer card
│ ── Steps ───────────────────  │
│  1. Move terms  … (why: …)    │  <- expandable step list
│  2. Divide both sides (why:…) │
│ ── Concept ─────────────────  │
│  Linear equations: …          │
│  [ Generate similar ]         │  <- chip/button
└──────────────────────────────┘
```

## Camera Solver
```
┌──────────────────────────────┐
│ ←  Camera Solver              │
│ ┌──────────────────────────┐ │
│ │      live preview        │ │
│ │   ┌──────────────────┐   │ │  <- guide box for the expression
│ │   │  frame the math  │   │ │
│ │   └──────────────────┘   │ │
│ └──────────────────────────┘ │
│   ( 📸 Capture )  ( 🖼 Gallery)│
│ Recognised: 2x + 3 = 11  ✎    │  <- editable OCR result
│            ( Solve )          │
└──────────────────────────────┘
```

## Practice
```
┌──────────────────────────────┐
│ ←  Practice   Difficulty:Med  │
│ Q 3 / 10        ⏱ 00:42       │
│ ┌──────────────────────────┐ │
│ │  What is 3/4 + 1/8 ?     │ │
│ └──────────────────────────┘ │
│  ( 7/8 ) ( 1/2 ) ( 5/8 ) (1) │  <- answer chips / input
│  ▓▓▓░░░░░░░  progress          │
│         ( Submit )            │
└──────────────────────────────┘
```

## Olympiad
```
┌──────────────────────────────┐
│ ←  Olympiad Prep              │
│ Exam: [IMO][NSO][IEO][IGKO]   │  <- segmented chips
│ Level: (1) (2)                │
│ ┌────────┐ ┌────────┐         │
│ │Practice│ │  Mock   │        │
│ │  Set   │ │  Test ⏱ │        │
│ └────────┘ └────────┘         │
│ Weak topics: Number Sense,…   │
└──────────────────────────────┘
```

## Progress
```
┌──────────────────────────────┐
│ ←  Progress          🔥 5-day │
│  Accuracy  82%   Solved 214   │  <- stat tiles
│  ┌───────── line/bar ───────┐ │
│  │  weekly attempts chart   │ │  <- Matplotlib texture / Kivy graph
│  └──────────────────────────┘ │
│  Strong: Algebra, Fractions   │
│  Weak:   Geometry, Probability│
└──────────────────────────────┘
```

## Settings
```
┌──────────────────────────────┐
│ ←  Settings                   │
│  Theme      ( Light | Dark )  │
│  Font size  [──●────]         │
│  Notifications        [ ON ]  │
│  Grade      [▼ 6 ]            │
│  Age        [ 11 ]           │
└──────────────────────────────┘
```
