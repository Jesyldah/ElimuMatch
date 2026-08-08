"""
Initialize and seed the Elimu Match SQLite database from existing project CSVs.

Creates:
  db/elimu_match.db

Includes term fee schedules, category arrears, and a sample partial payment.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
import sys

import numpy as np
import pandas as pd

DB_DIR = Path(__file__).resolve().parent
ROOT = DB_DIR.parent
if str(DB_DIR) not in sys.path:
    sys.path.insert(0, str(DB_DIR))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from schema import DB_PATH, SCHEMA_SQL  # noqa: E402
from kenya_schools import SCHOOLS
from student_display import first_name_label  # noqa: E402

RAW = ROOT / 'elimu_match_data_v4.csv'
ASSIGN = ROOT / 'intervention_outputs' / 'student_intervention_assignments.csv'
PERSONAS = ROOT / 'clustering_outputs' / 'student_personas.csv'

FEE_SCHEDULE = {
    # category_code: (day_amount, boarding_amount) illustrative KES
    'tuition': (12000, 12000),
    'boarding': (0, 18000),
    'lunch': (3000, 0),
    'activity': (1500, 1500),
}


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA_SQL)
    conn.commit()


def seed_reference(conn: sqlite3.Connection) -> dict[str, dict]:
    cur = conn.cursor()

    # Counties
    counties = sorted({m['county'] for m in SCHOOLS.values()})
    county_ids = {}
    for name in counties:
        cur.execute('INSERT OR IGNORE INTO counties (county_name) VALUES (?)', (name,))
        cur.execute('SELECT county_id FROM counties WHERE county_name = ?', (name,))
        county_ids[name] = cur.fetchone()[0]

    # Schools
    for sid, meta in SCHOOLS.items():
        cur.execute(
            """
            INSERT OR REPLACE INTO schools (school_id, school_name, county_id, school_type)
            VALUES (?, ?, ?, ?)
            """,
            (sid, meta['name'], county_ids[meta['county']], meta['type']),
        )

    # Terms 2025–2026
    terms = []
    for year in (2025, 2026):
        for num in (1, 2, 3):
            label = f'{year} Term {num}'
            cur.execute(
                """
                INSERT OR IGNORE INTO academic_terms (academic_year, term_number, term_label, due_date)
                VALUES (?, ?, ?, ?)
                """,
                (year, num, label, f'{year}-{num*4:02d}-15'),
            )
            cur.execute(
                'SELECT term_id FROM academic_terms WHERE academic_year=? AND term_number=?',
                (year, num),
            )
            terms.append({'term_id': cur.fetchone()[0], 'year': year, 'num': num, 'label': label})

    # Fee categories
    cat_ids = {}
    for code, name in [
        ('tuition', 'Tuition'),
        ('boarding', 'Boarding'),
        ('lunch', 'Lunch / Feeding'),
        ('activity', 'Activity / Development'),
    ]:
        cur.execute(
            'INSERT OR IGNORE INTO fee_categories (category_code, category_name) VALUES (?, ?)',
            (code, name),
        )
        cur.execute('SELECT fee_category_id FROM fee_categories WHERE category_code=?', (code,))
        cat_ids[code] = cur.fetchone()[0]

    # Interventions
    for code, name, cost, owner in [
        ('school_fee_support', 'School Fee Support', 15000, 'Sponsor'),
        ('academic_tutoring', 'Academic Tutoring', 8000, 'School'),
        ('transport_support', 'Transport / Boarding', 6000, 'Sponsor'),
        ('health_support', 'Health & Attendance', 5000, 'School'),
        ('digital_access', 'Digital Access Kit', 7000, 'Sponsor'),
        ('counseling', 'Psychosocial Counseling', 4000, 'School'),
        ('enrichment', 'STEM Enrichment', 3000, 'School'),
    ]:
        cur.execute(
            """
            INSERT OR IGNORE INTO interventions (intervention_code, intervention_name, unit_cost_kes, owner)
            VALUES (?, ?, ?, ?)
            """,
            (code, name, cost, owner),
        )

    conn.commit()
    return {'terms': terms, 'cat_ids': cat_ids}


def seed_students_and_fees(conn: sqlite3.Connection, refs: dict) -> None:
    raw = pd.read_csv(RAW)
    rng = np.random.default_rng(2026)

    # Optional analytics joins
    personas = pd.read_csv(PERSONAS) if PERSONAS.exists() else None
    assign = None
    if ASSIGN.exists():
        a = pd.read_csv(ASSIGN)
        assign = a[a['match_rank'] == 1][['student_id', 'intervention_id', 'dropout_risk', 'persona', 'ses_quintile']]

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO refresh_runs (run_type, source, status, notes)
        VALUES ('full_rescore', 'csv_seed', 'running', 'Initial DB seed from Capstone CSVs')
        """
    )
    run_id = cur.lastrowid

    # Focus fee generation on recent terms: 2025 T3, 2026 T1, 2026 T2
    active_terms = [t for t in refs['terms'] if (t['year'] == 2025 and t['num'] == 3) or (t['year'] == 2026 and t['num'] in (1, 2))]

    for _, row in raw.iterrows():
        sid = int(row['student_id'])
        school_id = int(row['school_id'])
        gender = 'Girl' if int(row['gender']) == 1 else 'Boy'
        status = 'enrolled' if int(row['retained']) == 1 else 'dropped'
        cur.execute(
            """
            INSERT OR REPLACE INTO students
                (student_id, school_id, display_name, age_at_enrollment, gender, enrollment_status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (sid, school_id, first_name_label(sid, gender), int(row['age_at_enrollment']), gender, status),
        )

        school_type = SCHOOLS[school_id]['type']

        # Students with low SES / high cash volatility more likely to have arrears
        ses = int(row['socioeconomic_status_index'])
        cash = row['cash_flow_volatility']
        cash = 0.22 if pd.isna(cash) else float(cash)
        arrears_pressure = (6 - ses) / 5 + max(0, cash - 0.20) * 5

        for term in active_terms:
            for code, (day_amt, board_amt) in FEE_SCHEDULE.items():
                due = board_amt if school_type == 'Boarding' else day_amt
                if due <= 0:
                    continue

                # Simulate how much already paid before sponsors
                # Higher pressure => lower paid share
                paid_share = float(np.clip(rng.normal(0.55 - 0.25 * arrears_pressure, 0.15), 0, 1))
                # Current term often less paid
                if term['year'] == 2026 and term['num'] == 2:
                    paid_share *= 0.6
                paid = int(round(due * paid_share / 100) * 100)  # round to 100s
                paid = min(paid, due)
                if paid == 0:
                    st = 'unpaid'
                elif paid < due:
                    st = 'partial'
                else:
                    st = 'paid'

                cur.execute(
                    """
                    INSERT OR REPLACE INTO student_term_fees
                        (student_id, term_id, fee_category_id, amount_due_kes, amount_paid_kes, status, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    """,
                    (sid, term['term_id'], refs['cat_ids'][code], due, paid, st),
                )

    # Risk snapshots
    if assign is not None:
        for _, r in assign.iterrows():
            cur.execute(
                """
                INSERT OR REPLACE INTO student_risk_snapshots
                    (refresh_run_id, student_id, ses_quintile, dropout_risk, persona,
                     retained_flag, primary_intervention_code)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    int(r['student_id']),
                    int(r['ses_quintile']) if pd.notna(r['ses_quintile']) else None,
                    float(r['dropout_risk']) if pd.notna(r['dropout_risk']) else None,
                    r['persona'] if pd.notna(r.get('persona')) else None,
                    int(raw.loc[raw['student_id'] == r['student_id'], 'retained'].iloc[0]),
                    r['intervention_id'] if pd.notna(r['intervention_id']) else None,
                ),
            )
    elif personas is not None:
        for _, r in personas.iterrows():
            cur.execute(
                """
                INSERT OR REPLACE INTO student_risk_snapshots
                    (refresh_run_id, student_id, ses_quintile, persona, retained_flag)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    int(r['student_id']),
                    int(r['socioeconomic_status_index']),
                    r['persona'],
                    int(r['retained']),
                ),
            )

    cur.execute(
        """
        UPDATE refresh_runs
        SET status='success', finished_at=datetime('now'),
            notes='Seeded students, term fees, risk snapshots'
        WHERE run_id=?
        """,
        (run_id,),
    )
    conn.commit()


def demo_partial_payment(conn: sqlite3.Connection) -> None:
    """Example: sponsor pays part of Term 2 tuition arrears only."""
    cur = conn.cursor()
    # Pick a student with outstanding tuition on 2026 Term 2
    row = cur.execute(
        """
        SELECT a.student_id, a.school_id, stf.student_term_fee_id, a.amount_outstanding_kes
        FROM v_term_arrears a
        JOIN student_term_fees stf
          ON stf.student_id = a.student_id
         AND stf.term_id = a.term_id
         AND stf.fee_category_id = (
                SELECT fee_category_id FROM fee_categories WHERE category_code='tuition'
             )
        WHERE a.category_code='tuition' AND a.term_label='2026 Term 2'
          AND a.amount_outstanding_kes >= 5000
        ORDER BY a.amount_outstanding_kes DESC
        LIMIT 1
        """
    ).fetchone()

    if not row:
        print('No demo arrears found for sample payment.')
        return

    student_id, school_id, fee_row_id, outstanding = row
    pay_amount = min(5000, outstanding)  # partial payment

    cur.execute(
        "INSERT INTO sponsors (display_name) VALUES ('Demo Sponsor')"
    )
    sponsor_id = cur.lastrowid

    cur.execute(
        """
        INSERT INTO payments (sponsor_id, student_id, school_id, amount_kes, payment_method, status, notes)
        VALUES (?, ?, ?, ?, 'simulated', 'completed', 'Partial Term 2 tuition support')
        """,
        (sponsor_id, student_id, school_id, pay_amount),
    )
    payment_id = cur.lastrowid

    cur.execute(
        """
        INSERT INTO payment_allocations (payment_id, student_term_fee_id, amount_kes)
        VALUES (?, ?, ?)
        """,
        (payment_id, fee_row_id, pay_amount),
    )

    # Update fee row balances
    cur.execute(
        """
        UPDATE student_term_fees
        SET amount_paid_kes = amount_paid_kes + ?,
            status = CASE
                WHEN amount_paid_kes + ? >= amount_due_kes THEN 'paid'
                WHEN amount_paid_kes + ? > 0 THEN 'partial'
                ELSE 'unpaid'
            END,
            updated_at = datetime('now')
        WHERE student_term_fee_id = ?
        """,
        (pay_amount, pay_amount, pay_amount, fee_row_id),
    )
    conn.commit()
    print(f'Demo partial payment: Student #{student_id} paid KES {pay_amount:,} toward 2026 Term 2 tuition (of {outstanding:,} outstanding).')


def print_summary(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    n_students = cur.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    n_arrears = cur.execute('SELECT COUNT(*) FROM v_term_arrears').fetchone()[0]
    total_out = cur.execute('SELECT COALESCE(SUM(amount_outstanding_kes),0) FROM v_term_arrears').fetchone()[0]
    by_term = cur.execute(
        """
        SELECT term_label, SUM(amount_outstanding_kes) AS arrears
        FROM v_term_arrears
        GROUP BY term_label
        ORDER BY term_label
        """
    ).fetchall()
    print('=' * 64)
    print('ELIMU MATCH DB READY')
    print('=' * 64)
    print(f'Database: {DB_PATH}')
    print(f'Students: {n_students:,}')
    print(f'Arrears line items: {n_arrears:,}')
    print(f'Total outstanding: KES {total_out:,}')
    print('Arrears by term:')
    for label, amt in by_term:
        print(f'  {label}: KES {amt:,}')


def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = connect()
    init_schema(conn)
    refs = seed_reference(conn)
    seed_students_and_fees(conn, refs)
    demo_partial_payment(conn)
    print_summary(conn)
    conn.close()


if __name__ == '__main__':
    main()
