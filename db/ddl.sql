-- Elimu Match — DDL (SQLite PoC)
-- Source of truth also embedded in db/schema.py as SCHEMA_SQL
-- Apply: python db/init_db.py   OR   sqlite3 db/elimu_match.db < db/ddl.sql

PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------
-- Reference / dimension tables
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS counties (
    county_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    county_name   TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS schools (
    school_id     INTEGER PRIMARY KEY,
    school_name   TEXT NOT NULL,
    county_id     INTEGER NOT NULL REFERENCES counties(county_id),
    school_type   TEXT NOT NULL CHECK (school_type IN ('Day', 'Boarding')),
    is_active     INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS academic_terms (
    term_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    academic_year INTEGER NOT NULL,
    term_number   INTEGER NOT NULL CHECK (term_number IN (1, 2, 3)),
    term_label    TEXT NOT NULL,
    start_date    TEXT,
    due_date      TEXT,
    UNIQUE (academic_year, term_number)
);

CREATE TABLE IF NOT EXISTS fee_categories (
    fee_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_code   TEXT NOT NULL UNIQUE,
    category_name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interventions (
    intervention_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    intervention_code TEXT NOT NULL UNIQUE,
    intervention_name TEXT NOT NULL,
    unit_cost_kes     INTEGER,
    owner             TEXT
);

-- ---------------------------------------------------------------------
-- Students & analytics snapshots
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS students (
    student_id          INTEGER PRIMARY KEY,
    school_id           INTEGER NOT NULL REFERENCES schools(school_id),
    display_name        TEXT NOT NULL,
    age_at_enrollment   INTEGER,
    gender              TEXT CHECK (gender IN ('Boy', 'Girl', 'Other', 'Unknown')),
    enrollment_status   TEXT NOT NULL DEFAULT 'enrolled'
        CHECK (enrollment_status IN ('enrolled', 'dropped', 'transferred', 'graduated')),
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS refresh_runs (
    run_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type    TEXT NOT NULL,
    source      TEXT,
    started_at  TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT,
    status      TEXT NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'success', 'failed')),
    notes       TEXT
);

CREATE TABLE IF NOT EXISTS student_risk_snapshots (
    snapshot_id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    refresh_run_id              INTEGER NOT NULL REFERENCES refresh_runs(run_id),
    student_id                  INTEGER NOT NULL REFERENCES students(student_id),
    ses_quintile                INTEGER,
    dropout_risk                REAL,
    persona                     TEXT,
    retained_flag               INTEGER,
    primary_intervention_code   TEXT,
    scored_at                   TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (refresh_run_id, student_id)
);

-- ---------------------------------------------------------------------
-- Fees by term
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS student_term_fees (
    student_term_fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id          INTEGER NOT NULL REFERENCES students(student_id),
    term_id             INTEGER NOT NULL REFERENCES academic_terms(term_id),
    fee_category_id     INTEGER NOT NULL REFERENCES fee_categories(fee_category_id),
    amount_due_kes      INTEGER NOT NULL CHECK (amount_due_kes >= 0),
    amount_paid_kes     INTEGER NOT NULL DEFAULT 0 CHECK (amount_paid_kes >= 0),
    status              TEXT NOT NULL DEFAULT 'unpaid'
        CHECK (status IN ('unpaid', 'partial', 'paid', 'waived')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (student_id, term_id, fee_category_id),
    CHECK (amount_paid_kes <= amount_due_kes)
);

-- ---------------------------------------------------------------------
-- Payments & allocations
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sponsors (
    sponsor_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    email        TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    sponsor_id     INTEGER REFERENCES sponsors(sponsor_id),
    student_id     INTEGER NOT NULL REFERENCES students(student_id),
    school_id      INTEGER NOT NULL REFERENCES schools(school_id),
    amount_kes     INTEGER NOT NULL CHECK (amount_kes > 0),
    currency       TEXT NOT NULL DEFAULT 'KES',
    payment_method TEXT NOT NULL DEFAULT 'simulated'
        CHECK (payment_method IN ('simulated', 'mpesa', 'card', 'bank', 'cash')),
    status         TEXT NOT NULL DEFAULT 'completed'
        CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    paid_at        TEXT NOT NULL DEFAULT (datetime('now')),
    external_ref   TEXT,
    notes          TEXT
);

CREATE TABLE IF NOT EXISTS payment_allocations (
    allocation_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id          INTEGER NOT NULL REFERENCES payments(payment_id),
    student_term_fee_id INTEGER NOT NULL REFERENCES student_term_fees(student_term_fee_id),
    amount_kes          INTEGER NOT NULL CHECK (amount_kes > 0),
    allocated_at        TEXT NOT NULL DEFAULT (datetime('now'))
);
