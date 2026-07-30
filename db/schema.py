"""
Elimu Match database schema (SQLite PoC).

Supports:
  - County / school (day vs boarding)
  - Students linked to schools
  - Fee schedules and balances by academic term
  - Partial payments allocated to specific term arrears
  - Refresh metadata for regular updates

Run:
  python db/init_db.py
"""

from pathlib import Path

SCHEMA_SQL = """
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
    term_label    TEXT NOT NULL,          -- e.g. '2026 Term 2'
    start_date    TEXT,
    due_date      TEXT,
    UNIQUE (academic_year, term_number)
);

CREATE TABLE IF NOT EXISTS fee_categories (
    fee_category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_code   TEXT NOT NULL UNIQUE,  -- tuition, boarding, lunch, activity, other
    category_name   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interventions (
    intervention_id INTEGER PRIMARY KEY AUTOINCREMENT,
    intervention_code TEXT NOT NULL UNIQUE,
    intervention_name TEXT NOT NULL,
    unit_cost_kes   INTEGER,
    owner           TEXT
);

-- ---------------------------------------------------------------------
-- Students & analytics snapshots (refreshed regularly)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS students (
    student_id      INTEGER PRIMARY KEY,
    school_id       INTEGER NOT NULL REFERENCES schools(school_id),
    display_name    TEXT NOT NULL,         -- anonymized for sponsors
    age_at_enrollment INTEGER,
    gender          TEXT CHECK (gender IN ('Boy', 'Girl', 'Other', 'Unknown')),
    enrollment_status TEXT NOT NULL DEFAULT 'enrolled'
        CHECK (enrollment_status IN ('enrolled', 'dropped', 'transferred', 'graduated')),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Latest scored analytics (overwrite or version via refresh_runs)
CREATE TABLE IF NOT EXISTS refresh_runs (
    run_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_type        TEXT NOT NULL,         -- full_rescore | fee_sync | payment_import
    source          TEXT,                  -- csv, api, manual
    started_at      TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at     TEXT,
    status          TEXT NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'success', 'failed')),
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS student_risk_snapshots (
    snapshot_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    refresh_run_id  INTEGER NOT NULL REFERENCES refresh_runs(run_id),
    student_id      INTEGER NOT NULL REFERENCES students(student_id),
    ses_quintile    INTEGER,
    dropout_risk    REAL,
    persona         TEXT,
    retained_flag   INTEGER,               -- historical outcome if known
    primary_intervention_code TEXT,
    scored_at       TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (refresh_run_id, student_id)
);

-- ---------------------------------------------------------------------
-- Fees by term (what is owed)
-- ---------------------------------------------------------------------

-- Expected fee for a student for a term + category
CREATE TABLE IF NOT EXISTS student_term_fees (
    student_term_fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      INTEGER NOT NULL REFERENCES students(student_id),
    term_id         INTEGER NOT NULL REFERENCES academic_terms(term_id),
    fee_category_id INTEGER NOT NULL REFERENCES fee_categories(fee_category_id),
    amount_due_kes  INTEGER NOT NULL CHECK (amount_due_kes >= 0),
    amount_paid_kes INTEGER NOT NULL DEFAULT 0 CHECK (amount_paid_kes >= 0),
    status          TEXT NOT NULL DEFAULT 'unpaid'
        CHECK (status IN ('unpaid', 'partial', 'paid', 'waived')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (student_id, term_id, fee_category_id),
    CHECK (amount_paid_kes <= amount_due_kes)
);

-- Convenience view: arrears by term (and overall)
CREATE VIEW IF NOT EXISTS v_term_arrears AS
SELECT
    stf.student_id,
    s.school_id,
    sch.school_name,
    c.county_name,
    sch.school_type,
    t.term_id,
    t.term_label,
    t.academic_year,
    t.term_number,
    fc.category_code,
    fc.category_name,
    stf.amount_due_kes,
    stf.amount_paid_kes,
    (stf.amount_due_kes - stf.amount_paid_kes) AS amount_outstanding_kes,
    stf.status
FROM student_term_fees stf
JOIN students s ON s.student_id = stf.student_id
JOIN schools sch ON sch.school_id = s.school_id
JOIN counties c ON c.county_id = sch.county_id
JOIN academic_terms t ON t.term_id = stf.term_id
JOIN fee_categories fc ON fc.fee_category_id = stf.fee_category_id
WHERE (stf.amount_due_kes - stf.amount_paid_kes) > 0
  AND stf.status IN ('unpaid', 'partial');

CREATE VIEW IF NOT EXISTS v_student_fee_summary AS
SELECT
    student_id,
    SUM(amount_due_kes) AS total_due_kes,
    SUM(amount_paid_kes) AS total_paid_kes,
    SUM(amount_due_kes - amount_paid_kes) AS total_outstanding_kes,
    SUM(CASE WHEN term_number = 1 THEN amount_due_kes - amount_paid_kes ELSE 0 END) AS term1_arrears_kes,
    SUM(CASE WHEN term_number = 2 THEN amount_due_kes - amount_paid_kes ELSE 0 END) AS term2_arrears_kes,
    SUM(CASE WHEN term_number = 3 THEN amount_due_kes - amount_paid_kes ELSE 0 END) AS term3_arrears_kes
FROM v_term_arrears
GROUP BY student_id;

-- ---------------------------------------------------------------------
-- Payments (sponsors can pay partially; allocate to term arrears)
-- ---------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS sponsors (
    sponsor_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name    TEXT NOT NULL,         -- 'Anonymous Sponsor' fine for PoC
    email           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    sponsor_id      INTEGER REFERENCES sponsors(sponsor_id),
    student_id      INTEGER NOT NULL REFERENCES students(student_id),
    school_id       INTEGER NOT NULL REFERENCES schools(school_id),
    amount_kes      INTEGER NOT NULL CHECK (amount_kes > 0),
    currency        TEXT NOT NULL DEFAULT 'KES',
    payment_method  TEXT NOT NULL DEFAULT 'simulated'
        CHECK (payment_method IN ('simulated', 'mpesa', 'card', 'bank', 'cash')),
    status          TEXT NOT NULL DEFAULT 'completed'
        CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    paid_at         TEXT NOT NULL DEFAULT (datetime('now')),
    external_ref    TEXT,                  -- M-Pesa receipt etc.
    notes           TEXT
);

-- Split one payment across one or more term/category arrears (partial OK)
CREATE TABLE IF NOT EXISTS payment_allocations (
    allocation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_id      INTEGER NOT NULL REFERENCES payments(payment_id),
    student_term_fee_id INTEGER NOT NULL REFERENCES student_term_fees(student_term_fee_id),
    amount_kes      INTEGER NOT NULL CHECK (amount_kes > 0),
    allocated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Rejected / blocked settlement attempts (overpayment, stale screen, etc.)
CREATE TABLE IF NOT EXISTS settlement_attempts (
    attempt_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      INTEGER REFERENCES students(student_id),
    amount_kes      INTEGER,
    code            TEXT NOT NULL,  -- overpayment | stale_balance | other
    expected_outstanding INTEGER,
    available_outstanding INTEGER,
    detail          TEXT,
    source          TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE VIEW IF NOT EXISTS v_payment_detail AS
SELECT
    p.payment_id,
    p.paid_at,
    p.amount_kes AS payment_amount_kes,
    p.status AS payment_status,
    p.payment_method,
    sp.display_name AS sponsor_name,
    p.student_id,
    st.display_name AS student_name,
    sch.school_name,
    c.county_name,
    t.term_label,
    fc.category_name,
    pa.amount_kes AS allocated_kes
FROM payments p
LEFT JOIN sponsors sp ON sp.sponsor_id = p.sponsor_id
JOIN students st ON st.student_id = p.student_id
JOIN schools sch ON sch.school_id = p.school_id
JOIN counties c ON c.county_id = sch.county_id
LEFT JOIN payment_allocations pa ON pa.payment_id = p.payment_id
LEFT JOIN student_term_fees stf ON stf.student_term_fee_id = pa.student_term_fee_id
LEFT JOIN academic_terms t ON t.term_id = stf.term_id
LEFT JOIN fee_categories fc ON fc.fee_category_id = stf.fee_category_id;

-- Sponsor portal feed: students with outstanding tuition/boarding arrears
CREATE VIEW IF NOT EXISTS v_sponsor_fee_candidates AS
SELECT
    s.student_id,
    s.display_name,
    s.gender,
    s.age_at_enrollment,
    sch.school_id,
    sch.school_name,
    sch.school_type,
    c.county_name,
    SUM(a.amount_outstanding_kes) AS total_outstanding_kes,
    SUM(CASE WHEN a.term_number = 1 THEN a.amount_outstanding_kes ELSE 0 END) AS term1_arrears_kes,
    SUM(CASE WHEN a.term_number = 2 THEN a.amount_outstanding_kes ELSE 0 END) AS term2_arrears_kes,
    SUM(CASE WHEN a.term_number = 3 THEN a.amount_outstanding_kes ELSE 0 END) AS term3_arrears_kes,
    rs.dropout_risk,
    rs.persona,
    rs.primary_intervention_code
FROM students s
JOIN schools sch ON sch.school_id = s.school_id
JOIN counties c ON c.county_id = sch.county_id
JOIN v_term_arrears a ON a.student_id = s.student_id
LEFT JOIN student_risk_snapshots rs
    ON rs.student_id = s.student_id
   AND rs.refresh_run_id = (
        -- Use latest *scoring* run, not latest payment_import (those have no snapshots)
        SELECT MAX(refresh_run_id) FROM student_risk_snapshots
   )
WHERE s.enrollment_status = 'enrolled'
GROUP BY s.student_id;
"""

# Path helpers used by init / payment scripts
DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / 'elimu_match.db'
