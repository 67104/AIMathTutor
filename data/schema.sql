-- ============================================================================
-- AI Math Tutor — SQLite Database Schema
-- Phase 1 deliverable: Database Design
-- ----------------------------------------------------------------------------
-- Design notes:
--   * Single local SQLite file (data/mathtutor.db). No cloud dependency.
--   * All timestamps stored as ISO-8601 TEXT in UTC ("YYYY-MM-DD HH:MM:SS").
--   * Booleans stored as INTEGER 0/1 (SQLite has no native BOOLEAN).
--   * Foreign keys ON. Schema is versioned via `schema_meta` for migrations.
--   * Denormalised aggregates (e.g. daily_stats) are cached for fast charts;
--     they are always derivable from `attempts`, which is the source of truth.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- Schema versioning (used by app.database.migrations)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_meta (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    version         INTEGER NOT NULL,
    applied_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
INSERT OR IGNORE INTO schema_meta (id, version) VALUES (1, 1);

-- ---------------------------------------------------------------------------
-- USER / PROFILE
-- Local single-user (or multi-profile) app. `is_active` marks current profile.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    age             INTEGER CHECK (age BETWEEN 3 AND 120),
    grade           INTEGER CHECK (grade BETWEEN 1 AND 12),
    avatar          TEXT,                              -- asset path / emoji
    is_active       INTEGER NOT NULL DEFAULT 1,        -- 0/1
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- SETTINGS (one row per user; key app preferences)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS settings (
    user_id             INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme               TEXT    NOT NULL DEFAULT 'Light',   -- 'Light' | 'Dark' | 'System'
    font_scale          REAL    NOT NULL DEFAULT 1.0,       -- 0.85 .. 1.5
    notifications_on     INTEGER NOT NULL DEFAULT 1,
    daily_reminder_time  TEXT    DEFAULT '18:00',           -- HH:MM local
    sound_on             INTEGER NOT NULL DEFAULT 1,
    haptics_on           INTEGER NOT NULL DEFAULT 1,
    updated_at           TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- TOPIC TAXONOMY (drives practice generation, weak-topic analytics)
-- Seeded by app.database.seed. `code` is a stable machine key.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS topics (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT    NOT NULL UNIQUE,          -- e.g. 'algebra.linear_eq'
    name            TEXT    NOT NULL,                 -- 'Linear Equations'
    category        TEXT    NOT NULL,                 -- 'Algebra','Geometry',...
    min_grade       INTEGER NOT NULL DEFAULT 1,
    max_grade       INTEGER NOT NULL DEFAULT 12
);

-- ---------------------------------------------------------------------------
-- QUESTIONS
-- Generated (source='generated') or captured/typed (source='camera'/'typed').
-- `payload_json` holds the structured problem (operands, expr, MCQ options...).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id        INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    grade           INTEGER,
    difficulty      TEXT    NOT NULL DEFAULT 'easy',  -- 'easy'|'medium'|'hard'|'olympiad'
    mode            TEXT    NOT NULL DEFAULT 'practice', -- 'practice'|'olympiad'|'daily'|'solver'
    prompt_text     TEXT    NOT NULL,                 -- human-readable question
    answer_text     TEXT,                             -- canonical answer
    options_json    TEXT,                             -- MCQ options (Olympiad), JSON array
    payload_json    TEXT,                             -- generator metadata, JSON
    source          TEXT    NOT NULL DEFAULT 'generated',
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- ATTEMPTS  (SOURCE OF TRUTH for all analytics/gamification)
-- One row per answered question across every mode.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS attempts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_id     INTEGER REFERENCES questions(id) ON DELETE SET NULL,
    topic_id        INTEGER REFERENCES topics(id) ON DELETE SET NULL,
    mode            TEXT    NOT NULL,                 -- practice|olympiad|daily|solver
    difficulty      TEXT,
    given_answer    TEXT,
    is_correct      INTEGER NOT NULL DEFAULT 0,       -- 0/1
    time_taken_ms   INTEGER NOT NULL DEFAULT 0,
    xp_awarded      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_attempts_user_date  ON attempts(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_attempts_user_topic ON attempts(user_id, topic_id);

-- ---------------------------------------------------------------------------
-- DAILY STATS (denormalised cache for streaks + charts; upserted on attempt)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_stats (
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day             TEXT    NOT NULL,                 -- 'YYYY-MM-DD' (local)
    attempts        INTEGER NOT NULL DEFAULT 0,
    correct         INTEGER NOT NULL DEFAULT 0,
    total_time_ms   INTEGER NOT NULL DEFAULT 0,
    xp              INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day)
);

-- ---------------------------------------------------------------------------
-- GAMIFICATION: progress + streak wallet per user
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gamification (
    user_id             INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    total_xp            INTEGER NOT NULL DEFAULT 0,
    level               INTEGER NOT NULL DEFAULT 1,
    current_streak      INTEGER NOT NULL DEFAULT 0,
    longest_streak      INTEGER NOT NULL DEFAULT 0,
    last_active_day     TEXT,                         -- 'YYYY-MM-DD'
    coins               INTEGER NOT NULL DEFAULT 0
);

-- ---------------------------------------------------------------------------
-- ACHIEVEMENTS catalogue + per-user unlock ledger
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS achievements (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    code            TEXT    NOT NULL UNIQUE,          -- 'streak_7', 'first_100_xp'
    title           TEXT    NOT NULL,
    description     TEXT    NOT NULL,
    icon            TEXT,
    xp_reward       INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS user_achievements (
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id  INTEGER NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    unlocked_at     TEXT    NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (user_id, achievement_id)
);

-- ---------------------------------------------------------------------------
-- OLYMPIAD ATTEMPTS / MOCK TESTS (aggregated per session for analysis)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mock_tests (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    exam            TEXT    NOT NULL,                 -- 'IMO'|'NSO'|'IEO'|'IGKO'
    level           INTEGER NOT NULL DEFAULT 1,       -- 1 or 2
    grade           INTEGER,
    total_questions INTEGER NOT NULL,
    correct         INTEGER NOT NULL DEFAULT 0,
    duration_ms     INTEGER NOT NULL DEFAULT 0,
    started_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    finished_at     TEXT
);

-- ---------------------------------------------------------------------------
-- SOLVER HISTORY (Ask AI + Camera Solver saved solutions)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS solver_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    input_type      TEXT    NOT NULL DEFAULT 'typed', -- 'typed'|'camera'|'gallery'
    raw_input       TEXT    NOT NULL,                 -- typed text or OCR text
    image_path      TEXT,                             -- local capture, if any
    parsed_expr     TEXT,                             -- normalised expression
    answer_text     TEXT,
    steps_json      TEXT,                             -- ordered explanation steps
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_solver_user_date ON solver_history(user_id, created_at);

-- ---------------------------------------------------------------------------
-- DAILY CHALLENGE ledger (one challenge per calendar day per user)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_challenges (
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    day             TEXT    NOT NULL,                 -- 'YYYY-MM-DD'
    question_id     INTEGER REFERENCES questions(id) ON DELETE SET NULL,
    completed       INTEGER NOT NULL DEFAULT 0,
    is_correct      INTEGER NOT NULL DEFAULT 0,
    reward_claimed  INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, day)
);

-- ============================================================================
-- End of schema v1
-- ============================================================================
