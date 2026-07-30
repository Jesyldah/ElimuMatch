"""
Data freshness report for Elimu Match (PoC honesty + demo).

Pulls timestamps from refresh_runs, risk snapshots, fees, and payments
so the portal/dashboard can show what is live vs periodic vs illustrative.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / 'elimu_match.db'


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _latest_run(conn: sqlite3.Connection, run_type: str | None = None) -> dict | None:
    if run_type:
        row = conn.execute(
            """
            SELECT run_id, run_type, source, started_at, finished_at, status, notes
            FROM refresh_runs
            WHERE status = 'success' AND run_type = ?
            ORDER BY COALESCE(finished_at, started_at) DESC, run_id DESC
            LIMIT 1
            """,
            (run_type,),
        ).fetchone()
    else:
        row = conn.execute(
            """
            SELECT run_id, run_type, source, started_at, finished_at, status, notes
            FROM refresh_runs
            WHERE status = 'success'
            ORDER BY COALESCE(finished_at, started_at) DESC, run_id DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def freshness_report() -> dict:
    """Structured freshness / coverage summary for UI and report."""
    if not DB_PATH.exists():
        return {
            'ok': False,
            'error': 'Database not found. Run python db/init_db.py',
            'layers': [],
            'coverage': {},
            'recent_runs': [],
        }

    conn = _connect()
    try:
        n_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
        n_schools = conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
        n_counties = conn.execute('SELECT COUNT(*) FROM counties').fetchone()[0]
        n_payments = conn.execute(
            "SELECT COUNT(*) FROM payments WHERE status = 'completed'"
        ).fetchone()[0]
        last_payment = conn.execute(
            "SELECT MAX(paid_at) FROM payments WHERE status = 'completed'"
        ).fetchone()[0]
        last_fee_update = conn.execute(
            'SELECT MAX(updated_at) FROM student_term_fees'
        ).fetchone()[0]
        last_scored = conn.execute(
            'SELECT MAX(scored_at) FROM student_risk_snapshots'
        ).fetchone()[0]
        n_snapshots = conn.execute(
            'SELECT COUNT(*) FROM student_risk_snapshots'
        ).fetchone()[0]

        fee_sync = _latest_run(conn, 'fee_sync') or _latest_run(conn, 'full_rescore')
        risk_run = _latest_run(conn, 'risk_rescore') or _latest_run(conn, 'full_rescore')
        pay_run = _latest_run(conn, 'payment_import')

        recent = conn.execute(
            """
            SELECT run_id, run_type, source, started_at, finished_at, status, notes
            FROM refresh_runs
            ORDER BY run_id DESC
            LIMIT 8
            """
        ).fetchall()

        layers = [
            {
                'id': 'fees',
                'label': 'Fee balances',
                'mode': 'Live (event-driven)',
                'cadence': 'On each sponsor payment + termly school sync',
                'last_updated': last_fee_update or last_payment,
                'detail': f'{n_payments} completed payment(s) in DB',
                'live_level': 'live',
            },
            {
                'id': 'risk',
                'label': 'Risk scores / personas',
                'mode': 'Periodic',
                'cadence': 'Termly (or after each scoring run)',
                'last_updated': last_scored or (risk_run or {}).get('finished_at'),
                'detail': f'{n_snapshots} snapshot row(s); last run type: {(risk_run or {}).get("run_type", "—")}',
                'live_level': 'periodic',
            },
            {
                'id': 'retrain',
                'label': 'Model retrain',
                'mode': 'Periodic',
                'cadence': 'Each term / semester on new outcomes',
                'last_updated': (risk_run or fee_sync or {}).get('finished_at'),
                'detail': 'PoC uses documented synthetic retrain workflow',
                'live_level': 'periodic',
            },
            {
                'id': 'cohort',
                'label': 'Student cohort',
                'mode': 'Illustrative (synthetic)',
                'cadence': 'Regenerated for PoC builds — not a live MoE feed',
                'last_updated': (fee_sync or {}).get('finished_at'),
                'detail': f'{n_students:,} students · {n_schools} schools · {n_counties} counties',
                'live_level': 'illustrative',
            },
        ]

        return {
            'ok': True,
            'as_of': last_fee_update or last_scored,
            'layers': layers,
            'coverage': {
                'students': n_students,
                'schools': n_schools,
                'counties': n_counties,
                'payments': n_payments,
                'geography': 'Sample school in each of Kenya’s 47 counties',
                'population': 'Scaled PoC cohort — not full national enrollment',
                'time_window': 'Simulated academic terms (fee ledger)',
                'honesty': (
                    'Current situation in the demo means current fee balances and the '
                    'last scoring run within the synthetic pilot cohort.'
                ),
            },
            'recent_runs': [dict(r) for r in recent],
            'last_payment_at': last_payment,
            'last_risk_scored_at': last_scored,
            'last_fee_update_at': last_fee_update,
        }
    finally:
        conn.close()
