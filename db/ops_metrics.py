"""
Organization / ops metrics for Elimu Match monitoring dashboard.

Pulls KPIs, investigation issues, progress, and recent activity from SQLite.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
DB_PATH = DB_DIR / 'elimu_match.db'

# PoC thresholds for "needs attention" flags
HIGH_RISK = 0.60
LARGE_ARREARS_KES = 40_000
STUCK_REMAINING_KES = 10_000  # gifted but still owes at least this
SCORE_SLA_DAYS = 14
SCHOOL_GIFT_SHARE_WARN = 0.35  # one school >35% of gift KES

# Illustrative pilot targets (report / ops framing — not live MoE SLAs)
PILOT_FEE_COVERAGE_TARGET_PCT = 25.0
PILOT_OLDEST_TERM_SHARE_MAX_PCT = 40.0
PILOT_REJECT_7D_MAX = 5


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _latest_score_run_id(conn: sqlite3.Connection) -> int | None:
    row = conn.execute(
        'SELECT MAX(refresh_run_id) AS rid FROM student_risk_snapshots'
    ).fetchone()
    return int(row['rid']) if row and row['rid'] is not None else None


def ensure_ops_tables(conn: sqlite3.Connection) -> None:
    """Ensure ops-only tables exist (safe on existing DBs)."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS settlement_attempts (
            attempt_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id      INTEGER REFERENCES students(student_id),
            amount_kes      INTEGER,
            code            TEXT NOT NULL,
            expected_outstanding INTEGER,
            available_outstanding INTEGER,
            detail          TEXT,
            source          TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now'))
        )
        """
    )
    conn.commit()


def log_settlement_attempt(
    conn: sqlite3.Connection,
    *,
    code: str,
    student_id: int | None = None,
    amount_kes: int | None = None,
    expected_outstanding: int | None = None,
    available_outstanding: int | None = None,
    detail: str | None = None,
    source: str = 'portal_server.py',
) -> None:
    ensure_ops_tables(conn)
    conn.execute(
        """
        INSERT INTO settlement_attempts (
            student_id, amount_kes, code, expected_outstanding,
            available_outstanding, detail, source
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student_id,
            amount_kes,
            code,
            expected_outstanding,
            available_outstanding,
            detail,
            source,
        ),
    )
    conn.commit()


def ensure_sponsor_candidate_view(conn: sqlite3.Connection) -> None:
    """Recreate portal feed view so risk joins latest scoring run, not payment imports."""
    conn.executescript(
        """
        DROP VIEW IF EXISTS v_sponsor_fee_candidates;
        CREATE VIEW v_sponsor_fee_candidates AS
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
           AND rs.refresh_run_id = (SELECT MAX(refresh_run_id) FROM student_risk_snapshots)
        WHERE s.enrollment_status = 'enrolled'
        GROUP BY s.student_id;
        """
    )
    conn.commit()


def ops_snapshot() -> dict:
    """Full ops command-center payload."""
    if not DB_PATH.exists():
        return {'ok': False, 'error': 'Database not found. Run python db/init_db.py'}

    conn = _connect()
    try:
        ensure_ops_tables(conn)
        ensure_sponsor_candidate_view(conn)
        rid = _latest_score_run_id(conn)

        kpis = _kpis(conn, rid)
        term_aging = _term_aging(conn)
        stuck = _stuck_partial_pays(conn)
        schools = _school_concentration(conn)
        rejections = _rejected_settlements(conn)
        non_fee = _non_fee_backlog(conn, rid)
        support_lanes = _support_lanes(conn, rid)
        school_targets = _school_resource_targets(conn, rid)
        fairness = _fee_queue_fairness(conn, rid)
        impact = _illustrative_impact(conn, rid)
        pilot = _pilot_kpi_strip(conn, rid, kpis, impact)
        fairness_cadence = _fairness_cadence(conn)
        issues = _issues(conn, rid, kpis, stuck, schools, rejections)
        progress = _progress(conn, rid)
        counties = _county_hotspots(conn, rid)
        recent = _recent_activity(conn)
        freshness = _freshness_brief(conn)

        return {
            'ok': True,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'kpis': kpis,
            'pilot_kpis': pilot,
            'illustrative_impact': impact,
            'fairness_cadence': fairness_cadence,
            'term_aging': term_aging,
            'stuck_partial_pays': stuck,
            'school_concentration': schools,
            'rejected_settlements': rejections,
            'non_fee_backlog': non_fee,
            'support_lanes': support_lanes,
            'school_resource_targets': school_targets,
            'fee_queue_fairness': fairness,
            'issues': issues,
            'progress': progress,
            'county_hotspots': counties,
            'recent_activity': recent,
            'freshness': freshness,
            'thresholds': {
                'high_risk': HIGH_RISK,
                'large_arrears_kes': LARGE_ARREARS_KES,
                'stuck_remaining_kes': STUCK_REMAINING_KES,
                'score_sla_days': SCORE_SLA_DAYS,
                'school_gift_share_warn': SCHOOL_GIFT_SHARE_WARN,
                'pilot_fee_coverage_target_pct': PILOT_FEE_COVERAGE_TARGET_PCT,
            },
            'links': {
                'sponsor_portal': '/sponsor_portal.html',
                'analytics_dashboard': '/dashboard.html',
                'schema_docs': '/db/schema_dashboard.html',
            },
        }
    finally:
        conn.close()


def _score_age_days(conn: sqlite3.Connection) -> tuple[int | None, str | None]:
    last_score = conn.execute(
        'SELECT MAX(scored_at) FROM student_risk_snapshots'
    ).fetchone()[0]
    if not last_score:
        return None, None
    try:
        scored_dt = datetime.strptime(str(last_score)[:19], '%Y-%m-%d %H:%M:%S')
        return (datetime.now() - scored_dt).days, str(last_score)[:19]
    except ValueError:
        return None, str(last_score)


def _kpis(conn: sqlite3.Connection, rid: int | None) -> dict:
    n_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    n_schools = conn.execute('SELECT COUNT(*) FROM schools').fetchone()[0]
    n_counties = conn.execute('SELECT COUNT(*) FROM counties').fetchone()[0]

    fee_support = 0
    high_risk = 0
    if rid is not None:
        fee_support = conn.execute(
            """
            SELECT COUNT(*) FROM student_risk_snapshots
            WHERE refresh_run_id = ? AND primary_intervention_code = 'school_fee_support'
            """,
            (rid,),
        ).fetchone()[0]
        high_risk = conn.execute(
            """
            SELECT COUNT(*) FROM student_risk_snapshots
            WHERE refresh_run_id = ? AND dropout_risk >= ?
            """,
            (rid, HIGH_RISK),
        ).fetchone()[0]

    arrears_students = conn.execute(
        """
        SELECT COUNT(DISTINCT student_id) FROM student_term_fees
        WHERE amount_due_kes > amount_paid_kes
        """
    ).fetchone()[0]
    total_arrears = conn.execute(
        """
        SELECT COALESCE(SUM(amount_due_kes - amount_paid_kes), 0)
        FROM student_term_fees
        """
    ).fetchone()[0]
    total_due = conn.execute(
        'SELECT COALESCE(SUM(amount_due_kes), 0) FROM student_term_fees'
    ).fetchone()[0]
    total_paid_fees = conn.execute(
        'SELECT COALESCE(SUM(amount_paid_kes), 0) FROM student_term_fees'
    ).fetchone()[0]

    gifts = conn.execute(
        "SELECT COUNT(*), COALESCE(SUM(amount_kes), 0) FROM payments WHERE status = 'completed'"
    ).fetchone()
    students_helped = conn.execute(
        """
        SELECT COUNT(DISTINCT student_id) FROM payments WHERE status = 'completed'
        """
    ).fetchone()[0]

    portal_queue = conn.execute(
        """
        SELECT COUNT(*) FROM v_sponsor_fee_candidates
        WHERE primary_intervention_code = 'school_fee_support'
        """
    ).fetchone()[0]

    high_risk_unpaid = 0
    if rid is not None:
        high_risk_unpaid = conn.execute(
            """
            SELECT COUNT(*) FROM student_risk_snapshots rs
            JOIN v_student_fee_summary f ON f.student_id = rs.student_id
            WHERE rs.refresh_run_id = ?
              AND rs.dropout_risk >= ?
              AND f.total_outstanding_kes > 0
            """,
            (rid, HIGH_RISK),
        ).fetchone()[0]

    clearance_pct = round(100.0 * total_paid_fees / total_due, 1) if total_due else 0.0
    score_age_days, last_scored_at = _score_age_days(conn)
    score_sla_ok = (
        score_age_days is not None and score_age_days <= SCORE_SLA_DAYS
    )

    rejection_total = conn.execute(
        'SELECT COUNT(*) FROM settlement_attempts'
    ).fetchone()[0]
    rejection_7d = conn.execute(
        """
        SELECT COUNT(*) FROM settlement_attempts
        WHERE created_at >= datetime('now', '-7 days')
        """
    ).fetchone()[0]

    stuck_n = conn.execute(
        """
        SELECT COUNT(*) FROM (
            SELECT f.student_id
            FROM v_student_fee_summary f
            WHERE f.total_outstanding_kes >= ?
              AND f.student_id IN (
                  SELECT DISTINCT student_id FROM payments WHERE status = 'completed'
              )
        )
        """,
        (STUCK_REMAINING_KES,),
    ).fetchone()[0]

    oldest_term_share = 0.0
    term1 = conn.execute(
        """
        SELECT COALESCE(SUM(amount_outstanding_kes), 0)
        FROM v_term_arrears WHERE term_number = 1
        """
    ).fetchone()[0]
    if total_arrears:
        oldest_term_share = round(100.0 * term1 / total_arrears, 1)

    return {
        'students': n_students,
        'schools': n_schools,
        'counties': n_counties,
        'fee_support_recommended': fee_support,
        'portal_fee_queue': portal_queue,
        'high_risk_students': high_risk,
        'high_risk_with_arrears': high_risk_unpaid,
        'students_with_arrears': arrears_students,
        'total_arrears_kes': int(total_arrears),
        'total_due_kes': int(total_due),
        'total_paid_on_fees_kes': int(total_paid_fees),
        'fee_clearance_pct': clearance_pct,
        'gifts_completed': int(gifts[0]),
        'gifts_kes': int(gifts[1]),
        'students_helped': students_helped,
        'score_run_id': rid,
        'score_age_days': score_age_days,
        'last_scored_at': last_scored_at,
        'score_sla_days': SCORE_SLA_DAYS,
        'score_sla_ok': score_sla_ok,
        'rejected_settlements_total': rejection_total,
        'rejected_settlements_7d': rejection_7d,
        'stuck_partial_pays': stuck_n,
        'oldest_term_arrears_pct': oldest_term_share,
    }


def _term_aging(conn: sqlite3.Connection) -> list[dict]:
    rows = [
        dict(r)
        for r in conn.execute(
            """
            SELECT
                t.term_number,
                t.term_label,
                COUNT(DISTINCT a.student_id) AS students,
                COALESCE(SUM(a.amount_outstanding_kes), 0) AS arrears_kes
            FROM v_term_arrears a
            JOIN academic_terms t ON t.term_id = a.term_id
            GROUP BY t.term_number, t.term_label
            ORDER BY t.term_number
            """
        )
    ]
    total = sum(r['arrears_kes'] for r in rows) or 1
    for r in rows:
        r['share_pct'] = round(100.0 * r['arrears_kes'] / total, 1)
    return rows


def _stuck_partial_pays(conn: sqlite3.Connection) -> dict:
    sample = [
        dict(r)
        for r in conn.execute(
            """
            SELECT
                st.student_id,
                st.display_name,
                sch.school_name,
                c.county_name,
                f.total_outstanding_kes AS remaining_kes,
                COALESCE(g.gifted_kes, 0) AS gifted_kes,
                g.gift_count
            FROM v_student_fee_summary f
            JOIN students st ON st.student_id = f.student_id
            JOIN schools sch ON sch.school_id = st.school_id
            JOIN counties c ON c.county_id = sch.county_id
            JOIN (
                SELECT student_id,
                       COUNT(*) AS gift_count,
                       SUM(amount_kes) AS gifted_kes
                FROM payments
                WHERE status = 'completed'
                GROUP BY student_id
            ) g ON g.student_id = f.student_id
            WHERE f.total_outstanding_kes >= ?
            ORDER BY f.total_outstanding_kes DESC
            LIMIT 12
            """,
            (STUCK_REMAINING_KES,),
        )
    ]
    count = conn.execute(
        """
        SELECT COUNT(*) FROM v_student_fee_summary f
        WHERE f.total_outstanding_kes >= ?
          AND f.student_id IN (
              SELECT DISTINCT student_id FROM payments WHERE status = 'completed'
          )
        """,
        (STUCK_REMAINING_KES,),
    ).fetchone()[0]
    return {
        'threshold_kes': STUCK_REMAINING_KES,
        'count': count,
        'sample': sample,
    }


def _school_concentration(conn: sqlite3.Connection) -> dict:
    by_arrears = [
        dict(r)
        for r in conn.execute(
            """
            SELECT sch.school_name, c.county_name, sch.school_type,
                   COUNT(DISTINCT a.student_id) AS students_in_arrears,
                   COALESCE(SUM(a.amount_outstanding_kes), 0) AS arrears_kes
            FROM v_term_arrears a
            JOIN schools sch ON sch.school_id = a.school_id
            JOIN counties c ON c.county_id = sch.county_id
            GROUP BY sch.school_id
            ORDER BY arrears_kes DESC
            LIMIT 10
            """
        )
    ]
    by_gifts = [
        dict(r)
        for r in conn.execute(
            """
            SELECT sch.school_name, c.county_name,
                   COUNT(*) AS gifts,
                   SUM(p.amount_kes) AS gift_kes,
                   COUNT(DISTINCT p.student_id) AS students_helped
            FROM payments p
            JOIN schools sch ON sch.school_id = p.school_id
            JOIN counties c ON c.county_id = sch.county_id
            WHERE p.status = 'completed'
            GROUP BY sch.school_id
            ORDER BY gift_kes DESC
            LIMIT 10
            """
        )
    ]
    total_gift_kes = conn.execute(
        "SELECT COALESCE(SUM(amount_kes), 0) FROM payments WHERE status = 'completed'"
    ).fetchone()[0]
    top_share = 0.0
    top_school = None
    if by_gifts and total_gift_kes:
        top_school = by_gifts[0]['school_name']
        top_share = round(by_gifts[0]['gift_kes'] / total_gift_kes, 3)
    return {
        'by_arrears': by_arrears,
        'by_gifts': by_gifts,
        'top_gift_school': top_school,
        'top_gift_share': top_share,
        'top_gift_share_pct': round(100.0 * top_share, 1),
        'warn': top_share >= SCHOOL_GIFT_SHARE_WARN,
    }


def _rejected_settlements(conn: sqlite3.Connection) -> dict:
    by_code = [
        dict(r)
        for r in conn.execute(
            """
            SELECT code, COUNT(*) AS attempts
            FROM settlement_attempts
            GROUP BY code
            ORDER BY attempts DESC
            """
        )
    ]
    recent = [
        dict(r)
        for r in conn.execute(
            """
            SELECT sa.created_at, sa.code, sa.amount_kes,
                   sa.expected_outstanding, sa.available_outstanding,
                   sa.detail, st.display_name AS student_name
            FROM settlement_attempts sa
            LEFT JOIN students st ON st.student_id = sa.student_id
            ORDER BY sa.created_at DESC, sa.attempt_id DESC
            LIMIT 12
            """
        )
    ]
    total = sum(r['attempts'] for r in by_code)
    last_7d = conn.execute(
        """
        SELECT COUNT(*) FROM settlement_attempts
        WHERE created_at >= datetime('now', '-7 days')
        """
    ).fetchone()[0]
    return {
        'total': total,
        'last_7d': last_7d,
        'by_code': by_code,
        'recent': recent,
    }


# Non-fee lanes: ownership + next step (handoff, not fulfillment).
# Fee support stays on the Helper portal; these stay school/partner channels.
_SUPPORT_LANE_META = {
    'academic_tutoring': {
        'label': 'Academic tutoring',
        'owner': 'School academic lead',
        'channel': 'School',
        'action': (
            'Share this lane\'s school list with the academic lead. '
            'Start catch-up for the highest-risk students first.'
        ),
    },
    'health_support': {
        'label': 'Health and attendance',
        'owner': 'School clinic / county health partner',
        'channel': 'School / partner',
        'action': (
            'Hand the school list to the clinic or attendance lead. '
            'Prioritize students flagged high risk.'
        ),
    },
    'digital_access': {
        'label': 'Digital access',
        'owner': 'CSR / device partner',
        'channel': 'Partner',
        'action': (
            'Share the school list with the device or data partner. '
            'Bundle kits where several students share one school.'
        ),
    },
    'enrichment': {
        'label': 'STEM enrichment',
        'owner': 'School clubs / mentoring lead',
        'channel': 'School',
        'action': (
            'Route the school list to clubs or mentoring. '
            'Use for placement, not as a fee-gift queue.'
        ),
    },
    'counseling': {
        'label': 'Psychosocial counseling',
        'owner': 'School counselor / peer support',
        'channel': 'School',
        'action': (
            'Share the school list with counseling staff. '
            'Schedule follow-up for high-risk students.'
        ),
    },
    'transport_support': {
        'label': 'Transport / boarding',
        'owner': 'School admin / bursary partner',
        'channel': 'School / partner',
        'action': (
            'Review the school list with admin or a bursary partner. '
            'Confirm commute or boarding need before funding.'
        ),
    },
}


def _non_fee_backlog(conn: sqlite3.Connection, rid: int | None) -> list[dict]:
    if rid is None:
        return []
    return [
        dict(r)
        for r in conn.execute(
            """
            SELECT
                primary_intervention_code AS code,
                COUNT(*) AS students,
                ROUND(AVG(dropout_risk), 3) AS avg_risk,
                SUM(CASE WHEN dropout_risk >= ? THEN 1 ELSE 0 END) AS high_risk
            FROM student_risk_snapshots
            WHERE refresh_run_id = ?
              AND primary_intervention_code IS NOT NULL
              AND primary_intervention_code != 'school_fee_support'
            GROUP BY primary_intervention_code
            ORDER BY students DESC
            """,
            (HIGH_RISK, rid),
        )
    ]


def _lane_top_schools(
    conn: sqlite3.Connection, rid: int, code: str, limit: int = 3
) -> list[dict]:
    return [
        dict(r)
        for r in conn.execute(
            """
            SELECT
                sch.school_name,
                c.county_name,
                COUNT(*) AS students,
                SUM(CASE WHEN rs.dropout_risk >= ? THEN 1 ELSE 0 END) AS high_risk
            FROM student_risk_snapshots rs
            JOIN students st ON st.student_id = rs.student_id
            JOIN schools sch ON sch.school_id = st.school_id
            JOIN counties c ON c.county_id = sch.county_id
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code = ?
            GROUP BY sch.school_id
            ORDER BY students DESC, high_risk DESC
            LIMIT ?
            """,
            (HIGH_RISK, rid, code, limit),
        )
    ]


def _support_lanes(conn: sqlite3.Connection, rid: int | None) -> dict:
    """
    Fee channel + other support lanes with owner, next step, and handoff status.
    Handoff = listed for review (no fake fulfillment tracking in the PoC).
    """
    fee_students = 0
    fee_high = 0
    if rid is not None:
        row = conn.execute(
            """
            SELECT
                COUNT(*) AS students,
                SUM(CASE WHEN dropout_risk >= ? THEN 1 ELSE 0 END) AS high_risk
            FROM student_risk_snapshots
            WHERE refresh_run_id = ?
              AND primary_intervention_code = 'school_fee_support'
            """,
            (HIGH_RISK, rid),
        ).fetchone()
        fee_students = int(row['students'] or 0)
        fee_high = int(row['high_risk'] or 0)

    fee_channel = {
        'code': 'school_fee_support',
        'label': 'School fee support',
        'owner': 'Helpers via Helper portal',
        'channel': 'Helper portal',
        'students': fee_students,
        'high_risk': fee_high,
        'action': 'Open the Helper portal and place gifts against school fee balances.',
        'handoff_status': 'live_channel',
        'handoff_label': 'Live on Helper portal',
        'top_schools': [],
    }

    by_code = {r['code']: r for r in _non_fee_backlog(conn, rid)}
    other_lanes: list[dict] = []
    known_order = list(_SUPPORT_LANE_META.keys())
    codes = [c for c in known_order if c in by_code] + [
        c for c in by_code if c not in _SUPPORT_LANE_META
    ]
    for code in known_order:
        if code not in codes:
            codes.append(code)

    for code in codes:
        meta = _SUPPORT_LANE_META.get(
            code,
            {
                'label': str(code).replace('_', ' ').title(),
                'owner': 'School / partner',
                'channel': 'School / partner',
                'action': 'Share the school worklist with the named owner for this need.',
            },
        )
        stats = by_code.get(code) or {'students': 0, 'high_risk': 0, 'avg_risk': None}
        n = int(stats.get('students') or 0)
        other_lanes.append(
            {
                'code': code,
                'label': meta['label'],
                'owner': meta['owner'],
                'channel': meta['channel'],
                'students': n,
                'high_risk': int(stats.get('high_risk') or 0),
                'avg_risk': stats.get('avg_risk'),
                'action': meta['action'],
                'handoff_status': 'listed_for_review' if n else 'none_routed',
                'handoff_label': (
                    'Listed for school / partner review' if n else 'No students routed'
                ),
                'top_schools': (
                    _lane_top_schools(conn, rid, code) if rid is not None and n else []
                ),
            }
        )

    other_lanes.sort(key=lambda x: (-(x['students'] or 0), x['label']))

    return {
        'note': (
            'Fee help settles on the Helper portal. '
            'Other needs are handed to school or partner owners using the school worklist below. '
            'Progress here means handoff, not completed tutoring or clinic visits.'
        ),
        'fee_channel': fee_channel,
        'other_lanes': other_lanes,
    }


def _school_resource_targets(conn: sqlite3.Connection, rid: int | None) -> list[dict]:
    """Roll primary interventions up by school for foundation / CSR targeting."""
    if rid is None:
        return []
    return [
        dict(r)
        for r in conn.execute(
            """
            SELECT
                sch.school_name,
                c.county_name,
                sch.school_type,
                COUNT(*) AS at_risk_routed,
                SUM(CASE WHEN rs.primary_intervention_code = 'school_fee_support'
                         THEN 1 ELSE 0 END) AS fee_support,
                SUM(CASE WHEN rs.primary_intervention_code = 'academic_tutoring'
                         THEN 1 ELSE 0 END) AS tutoring,
                SUM(CASE WHEN rs.primary_intervention_code = 'health_support'
                         THEN 1 ELSE 0 END) AS health,
                SUM(CASE WHEN rs.primary_intervention_code = 'digital_access'
                         THEN 1 ELSE 0 END) AS digital,
                SUM(CASE WHEN rs.primary_intervention_code IN ('enrichment', 'counseling')
                         THEN 1 ELSE 0 END) AS enrichment,
                ROUND(AVG(rs.dropout_risk), 3) AS avg_risk
            FROM student_risk_snapshots rs
            JOIN students st ON st.student_id = rs.student_id
            JOIN schools sch ON sch.school_id = st.school_id
            JOIN counties c ON c.county_id = sch.county_id
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code IS NOT NULL
            GROUP BY sch.school_id
            ORDER BY
                (SUM(CASE WHEN rs.primary_intervention_code = 'health_support' THEN 1 ELSE 0 END)
               + SUM(CASE WHEN rs.primary_intervention_code = 'digital_access' THEN 1 ELSE 0 END)
               + SUM(CASE WHEN rs.primary_intervention_code = 'academic_tutoring' THEN 1 ELSE 0 END)
               + SUM(CASE WHEN rs.primary_intervention_code = 'school_fee_support' THEN 1 ELSE 0 END)) DESC,
                avg_risk DESC
            LIMIT 15
            """,
            (rid,),
        )
    ]


def _fee_queue_fairness(conn: sqlite3.Connection, rid: int | None) -> dict:
    if rid is None:
        return {'by_gender': [], 'by_ses': []}
    by_gender = [
        dict(r)
        for r in conn.execute(
            """
            SELECT st.gender,
                   COUNT(*) AS students,
                   ROUND(AVG(rs.dropout_risk), 3) AS avg_risk,
                   COALESCE(SUM(f.total_outstanding_kes), 0) AS arrears_kes
            FROM student_risk_snapshots rs
            JOIN students st ON st.student_id = rs.student_id
            LEFT JOIN v_student_fee_summary f ON f.student_id = rs.student_id
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code = 'school_fee_support'
            GROUP BY st.gender
            ORDER BY students DESC
            """,
            (rid,),
        )
    ]
    by_ses = [
        dict(r)
        for r in conn.execute(
            """
            SELECT rs.ses_quintile,
                   COUNT(*) AS students,
                   ROUND(AVG(rs.dropout_risk), 3) AS avg_risk,
                   COALESCE(SUM(f.total_outstanding_kes), 0) AS arrears_kes
            FROM student_risk_snapshots rs
            LEFT JOIN v_student_fee_summary f ON f.student_id = rs.student_id
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code = 'school_fee_support'
            GROUP BY rs.ses_quintile
            ORDER BY rs.ses_quintile
            """,
            (rid,),
        )
    ]
    return {'by_gender': by_gender, 'by_ses': by_ses}


def _group_retention(conn: sqlite3.Connection, rid: int, where_extra: str) -> dict:
    """Retention split for helped vs not-helped under an extra WHERE clause."""
    rows = [
        dict(r)
        for r in conn.execute(
            f"""
            SELECT
                CASE WHEN p.student_id IS NOT NULL THEN 1 ELSE 0 END AS helped,
                COUNT(*) AS students,
                SUM(CASE WHEN rs.retained_flag = 1 THEN 1 ELSE 0 END) AS retained,
                SUM(CASE WHEN rs.retained_flag = 0 THEN 1 ELSE 0 END) AS dropped
            FROM student_risk_snapshots rs
            LEFT JOIN (
                SELECT DISTINCT student_id FROM payments WHERE status = 'completed'
            ) p ON p.student_id = rs.student_id
            WHERE rs.refresh_run_id = ?
              AND {where_extra}
            GROUP BY 1
            """,
            (rid,),
        )
    ]
    out = {
        'helped': {'students': 0, 'retained': 0, 'dropped': 0, 'retention_pct': None},
        'not_helped': {'students': 0, 'retained': 0, 'dropped': 0, 'retention_pct': None},
    }
    for r in rows:
        key = 'helped' if r['helped'] else 'not_helped'
        n = int(r['students'] or 0)
        retained = int(r['retained'] or 0)
        out[key] = {
            'students': n,
            'retained': retained,
            'dropped': int(r['dropped'] or 0),
            'retention_pct': round(100.0 * retained / n, 1) if n else None,
        }
    return out


def _illustrative_impact(conn: sqlite3.Connection, rid: int | None) -> dict:
    """
    Retention comparison for helped vs not-helped students.
    Use as an outcome check; confirm with next-term enrollment follow-up.
    """
    if rid is None:
        return {
            'disclaimer': 'No risk snapshots available.',
            'illustrative': True,
            'fee_support': {},
            'high_risk': {},
            'cohort': {},
        }

    fee = _group_retention(
        conn, rid, "rs.primary_intervention_code = 'school_fee_support'"
    )
    high = _group_retention(conn, rid, f'rs.dropout_risk >= {HIGH_RISK}')

    cohort = conn.execute(
        """
        SELECT COUNT(*) AS students,
               SUM(CASE WHEN retained_flag = 1 THEN 1 ELSE 0 END) AS retained,
               SUM(CASE WHEN retained_flag = 0 THEN 1 ELSE 0 END) AS dropped
        FROM student_risk_snapshots
        WHERE refresh_run_id = ?
        """,
        (rid,),
    ).fetchone()
    cn = int(cohort['students'] or 0)
    cr = int(cohort['retained'] or 0)

    fee_gap = None
    if (
        fee['helped']['retention_pct'] is not None
        and fee['not_helped']['retention_pct'] is not None
        and fee['helped']['students'] >= 1
    ):
        fee_gap = round(
            fee['helped']['retention_pct'] - fee['not_helped']['retention_pct'], 1
        )

    return {
        'illustrative': True,
        'disclaimer': (
            'Outcome comparison only. Treat differences carefully when samples are small. '
            'A next-term follow-up should confirm whether helped students stay enrolled.'
        ),
        'fee_support': fee,
        'high_risk': high,
        'cohort': {
            'students': cn,
            'retained': cr,
            'dropped': int(cohort['dropped'] or 0),
            'retention_pct': round(100.0 * cr / cn, 1) if cn else None,
        },
        'fee_support_retention_gap_pp': fee_gap,
        'small_n_warning': fee['helped']['students'] < 20,
    }


def _fairness_cadence(conn: sqlite3.Connection) -> dict:
    age_days, last_at = _score_age_days(conn)
    due = age_days is None or age_days > SCORE_SLA_DAYS
    next_due = None
    if last_at:
        try:
            scored_dt = datetime.strptime(last_at[:19], '%Y-%m-%d %H:%M:%S')
            next_due = (scored_dt + timedelta(days=SCORE_SLA_DAYS)).strftime(
                '%Y-%m-%d'
            )
        except ValueError:
            next_due = None
    return {
        'interval_days': SCORE_SLA_DAYS,
        'last_check_at': last_at,
        'next_due_date': next_due,
        'days_since_check': age_days,
        'status': 'due' if due else 'ok',
        'note': (
            'We recheck that support recommendations stay balanced by gender and income group '
            'whenever risk scores are updated. See the analytics dashboard for detail.'
        ),
    }


def _pilot_kpi_strip(
    conn: sqlite3.Connection,
    rid: int | None,
    kpis: dict,
    impact: dict,
) -> list[dict]:
    """Progress goals for the fee-support channel, with current measurable status."""
    coverage = 0.0
    if rid is not None:
        fee_total = conn.execute(
            """
            SELECT COUNT(*) FROM student_risk_snapshots
            WHERE refresh_run_id = ? AND primary_intervention_code = 'school_fee_support'
            """,
            (rid,),
        ).fetchone()[0]
        fee_touched = conn.execute(
            """
            SELECT COUNT(DISTINCT rs.student_id)
            FROM student_risk_snapshots rs
            JOIN payments p ON p.student_id = rs.student_id AND p.status = 'completed'
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code = 'school_fee_support'
            """,
            (rid,),
        ).fetchone()[0]
        coverage = round(100.0 * fee_touched / fee_total, 1) if fee_total else 0.0

    unallocated = conn.execute(
        """
        SELECT COUNT(*) FROM payments p
        WHERE p.status = 'completed'
          AND NOT EXISTS (
              SELECT 1 FROM payment_allocations pa WHERE pa.payment_id = p.payment_id
          )
        """
    ).fetchone()[0]

    items = [
        {
            'id': 'fee_coverage',
            'label': 'Students who received a gift',
            'target': (
                f'At least {PILOT_FEE_COVERAGE_TARGET_PCT:.0f}% of students recommended '
                'for fee support should receive one or more gifts'
            ),
            'current': f'{coverage}% have received a gift',
            'current_value': coverage,
            'status': (
                'on_track' if coverage >= PILOT_FEE_COVERAGE_TARGET_PCT else 'watch'
            ),
            'note': 'Shows whether recommended students are actually getting help.',
        },
        {
            'id': 'score_sla',
            'label': 'Risk score freshness',
            'target': f'Update risk scores at least every {SCORE_SLA_DAYS} days',
            'current': (
                f"{kpis.get('score_age_days')} days since last update"
                if kpis.get('score_age_days') is not None
                else '-'
            ),
            'current_value': kpis.get('score_age_days'),
            'status': 'on_track' if kpis.get('score_sla_ok') else 'watch',
            'note': 'Stale scores mean recommendations may be out of date.',
        },
        {
            'id': 'ledger_integrity',
            'label': 'Gifts applied to school fees',
            'target': 'Every completed gift should land on a fee term; overpayments blocked',
            'current': (
                f'{unallocated} gifts not yet applied to a fee term · '
                f'{kpis.get("rejected_settlements_7d", 0)} blocked attempts in 7 days'
            ),
            'current_value': unallocated,
            'status': 'on_track' if unallocated == 0 else 'watch',
            'note': 'Helpers and schools need gifts to clear against real fee balances.',
        },
        {
            'id': 'oldest_term',
            'label': 'Old unpaid terms',
            'target': (
                f'Oldest-term share of unpaid fees should stay at or below '
                f'{PILOT_OLDEST_TERM_SHARE_MAX_PCT:.0f}%'
            ),
            'current': f"{kpis.get('oldest_term_arrears_pct')}% of unpaid fees are in the oldest term",
            'current_value': kpis.get('oldest_term_arrears_pct'),
            'status': (
                'on_track'
                if (kpis.get('oldest_term_arrears_pct') or 0)
                <= PILOT_OLDEST_TERM_SHARE_MAX_PCT
                else 'watch'
            ),
            'note': 'A high share of old unpaid terms means debt is stacking up.',
        },
        {
            'id': 'settlement_friction',
            'label': 'Blocked gift attempts',
            'target': f'At most {PILOT_REJECT_7D_MAX} blocked attempts in 7 days',
            'current': str(kpis.get('rejected_settlements_7d', 0)),
            'current_value': kpis.get('rejected_settlements_7d', 0),
            'status': (
                'on_track'
                if (kpis.get('rejected_settlements_7d') or 0) <= PILOT_REJECT_7D_MAX
                else 'watch'
            ),
            'note': 'Blocked gifts usually mean balances changed or the amount was too high.',
        },
        {
            'id': 'outcome_loop',
            'label': 'Did helped students stay in school?',
            'target': 'Compare stay-in-school rates for helped students vs similar peers',
            'current': (
                f"Difference {impact.get('fee_support_retention_gap_pp')} points"
                if impact.get('fee_support_retention_gap_pp') is not None
                else 'Awaiting next-term outcomes'
            ),
            'current_value': impact.get('fee_support_retention_gap_pp'),
            'status': 'n_a',
            'note': 'Track after the next school term whether helped students stay enrolled.',
        },
    ]
    return items


def _issues(
    conn: sqlite3.Connection,
    rid: int | None,
    kpis: dict,
    stuck: dict,
    schools: dict,
    rejections: dict,
) -> list[dict]:
    issues: list[dict] = []

    missing_risk = conn.execute(
        """
        SELECT COUNT(*) FROM v_sponsor_fee_candidates
        WHERE dropout_risk IS NULL
        """
    ).fetchone()[0]
    if missing_risk:
        issues.append({
            'severity': 'high',
            'code': 'portal_missing_risk',
            'title': 'Some students are missing risk information',
            'detail': (
                f'{missing_risk} students with unpaid fees appear in the helper list '
                'without a risk score. Recommendations may be incomplete.'
            ),
            'count': missing_risk,
            'action': 'Refresh student risk scores, then reload this monitor.',
        })

    fee_no_gift = 0
    if rid is not None:
        fee_no_gift = conn.execute(
            """
            SELECT COUNT(*) FROM student_risk_snapshots rs
            JOIN v_student_fee_summary f ON f.student_id = rs.student_id
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code = 'school_fee_support'
              AND f.total_outstanding_kes > 0
              AND rs.student_id NOT IN (
                  SELECT DISTINCT student_id FROM payments WHERE status = 'completed'
              )
            """,
            (rid,),
        ).fetchone()[0]
    if fee_no_gift:
        issues.append({
            'severity': 'medium',
            'code': 'fee_queue_untouched',
            'title': 'Students recommended for fee help have not received a gift yet',
            'detail': (
                f'{fee_no_gift} students are recommended for school fee support, '
                'still owe fees, and have not received a gift.'
            ),
            'count': fee_no_gift,
            'action': 'Open the helper portal and give toward one of these students.',
        })

    urgent = []
    if rid is not None:
        urgent = [
            dict(r)
            for r in conn.execute(
                """
                SELECT rs.student_id, st.display_name, sch.school_name, c.county_name,
                       rs.dropout_risk, f.total_outstanding_kes, rs.persona
                FROM student_risk_snapshots rs
                JOIN students st ON st.student_id = rs.student_id
                JOIN schools sch ON sch.school_id = st.school_id
                JOIN counties c ON c.county_id = sch.county_id
                JOIN v_student_fee_summary f ON f.student_id = rs.student_id
                WHERE rs.refresh_run_id = ?
                  AND rs.dropout_risk >= ?
                  AND f.total_outstanding_kes >= ?
                ORDER BY rs.dropout_risk DESC, f.total_outstanding_kes DESC
                LIMIT 15
                """,
                (rid, HIGH_RISK, LARGE_ARREARS_KES),
            )
        ]
    if urgent:
        issues.append({
            'severity': 'high',
            'code': 'high_risk_large_arrears',
            'title': 'Students with high dropout risk and large unpaid fees',
            'detail': (
                f'{len(urgent)} students (top list shown) have risk at or above {HIGH_RISK:.0%} '
                f'and unpaid fees of at least {LARGE_ARREARS_KES:,} KES.'
            ),
            'count': len(urgent),
            'action': 'Review these cases first and open the helper portal for fee support.',
            'sample': urgent,
        })

    if stuck.get('count'):
        issues.append({
            'severity': 'medium',
            'code': 'stuck_partial_pay',
            'title': 'Students who still need substantial support after a gift',
            'detail': (
                f"{stuck['count']} students already received one or more gifts "
                f"but still owe at least {STUCK_REMAINING_KES:,} KES."
            ),
            'count': stuck['count'],
            'action': 'Consider another gift or ask the school about a payment plan.',
            'sample': [
                {
                    'display_name': s['display_name'],
                    'county_name': s['county_name'],
                    'dropout_risk': None,
                    'total_outstanding_kes': s['remaining_kes'],
                }
                for s in stuck.get('sample', [])[:8]
            ],
        })

    if schools.get('warn'):
        issues.append({
            'severity': 'medium',
            'code': 'school_gift_concentration',
            'title': 'Most gifts are going to one school',
            'detail': (
                f"{schools.get('top_gift_school')} received "
                f"{schools.get('top_gift_share_pct')}% of gift money "
                f"(warning starts at {int(SCHOOL_GIFT_SHARE_WARN * 100)}%)."
            ),
            'count': schools.get('top_gift_share_pct') or 0,
            'action': 'Encourage helpers to support students across more schools and counties.',
        })

    if rejections.get('last_7d', 0) >= 3:
        issues.append({
            'severity': 'medium',
            'code': 'settlement_friction',
            'title': 'Several gift attempts were blocked recently',
            'detail': (
                f"{rejections['last_7d']} gift attempts were blocked in the last 7 days "
                f"(usually because balances changed or the amount was too high). "
                f"Total blocked attempts logged: {rejections.get('total', 0)}."
            ),
            'count': rejections['last_7d'],
            'action': 'Check that fee balances are current before the next gift drive.',
        })

    score_age = kpis.get('score_age_days')
    if score_age is not None and score_age > SCORE_SLA_DAYS:
        issues.append({
            'severity': 'medium',
            'code': 'stale_scores',
            'title': 'Risk scores need updating',
            'detail': (
                f"Risk scores were last updated on {kpis.get('last_scored_at')} "
                f"({score_age} days ago). The target is every {SCORE_SLA_DAYS} days."
            ),
            'count': score_age,
            'action': 'Run an updated risk score pass for the next school term.',
        })

    unallocated = conn.execute(
        """
        SELECT COUNT(*) FROM payments p
        WHERE p.status = 'completed'
          AND NOT EXISTS (
              SELECT 1 FROM payment_allocations pa WHERE pa.payment_id = p.payment_id
          )
        """
    ).fetchone()[0]
    if unallocated:
        issues.append({
            'severity': 'high',
            'code': 'payment_no_allocation',
            'title': 'Some gifts were not applied to fee terms',
            'detail': (
                f'{unallocated} completed gift(s) are not linked to any school fee term yet.'
            ),
            'count': unallocated,
            'action': 'Fix gift-to-fee matching before more helpers give.',
        })

    if not issues:
        issues.append({
            'severity': 'info',
            'code': 'all_clear',
            'title': 'Nothing urgent right now',
            'detail': 'Current checks look healthy against the active thresholds.',
            'count': 0,
            'action': 'Keep watching gifts and update risk scores each term.',
        })

    severity_rank = {'high': 0, 'medium': 1, 'low': 2, 'info': 3}
    issues.sort(key=lambda x: severity_rank.get(x['severity'], 9))
    return issues


def _progress(conn: sqlite3.Connection, rid: int | None) -> dict:
    by_intervention = [
        dict(r)
        for r in conn.execute(
            """
            SELECT primary_intervention_code AS code, COUNT(*) AS students
            FROM student_risk_snapshots
            WHERE refresh_run_id = ?
            GROUP BY 1
            ORDER BY students DESC
            """,
            (rid,),
        )
    ] if rid is not None else []

    by_persona = [
        dict(r)
        for r in conn.execute(
            """
            SELECT persona, COUNT(*) AS students,
                   ROUND(AVG(dropout_risk), 3) AS avg_risk
            FROM student_risk_snapshots
            WHERE refresh_run_id = ?
            GROUP BY 1
            ORDER BY students DESC
            """,
            (rid,),
        )
    ] if rid is not None else []

    fee_touched = 0
    fee_total = 0
    if rid is not None:
        fee_total = conn.execute(
            """
            SELECT COUNT(*) FROM student_risk_snapshots
            WHERE refresh_run_id = ? AND primary_intervention_code = 'school_fee_support'
            """,
            (rid,),
        ).fetchone()[0]
        fee_touched = conn.execute(
            """
            SELECT COUNT(DISTINCT rs.student_id)
            FROM student_risk_snapshots rs
            JOIN payments p ON p.student_id = rs.student_id AND p.status = 'completed'
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code = 'school_fee_support'
            """,
            (rid,),
        ).fetchone()[0]

    gifts_by_day = [
        dict(r)
        for r in conn.execute(
            """
            SELECT substr(paid_at, 1, 10) AS day,
                   COUNT(*) AS gifts,
                   SUM(amount_kes) AS kes
            FROM payments
            WHERE status = 'completed'
            GROUP BY 1
            ORDER BY 1
            """
        )
    ]

    return {
        'intervention_mix': by_intervention,
        'persona_mix': by_persona,
        'fee_support_total': fee_total,
        'fee_support_with_gift': fee_touched,
        'fee_support_coverage_pct': (
            round(100.0 * fee_touched / fee_total, 1) if fee_total else 0.0
        ),
        'gifts_by_day': gifts_by_day,
    }


def _county_hotspots(conn: sqlite3.Connection, rid: int | None) -> list[dict]:
    if rid is None:
        return []
    return [
        dict(r)
        for r in conn.execute(
            """
            SELECT c.county_name,
                   COUNT(*) AS fee_support_students,
                   COALESCE(SUM(f.total_outstanding_kes), 0) AS arrears_kes,
                   ROUND(AVG(rs.dropout_risk), 3) AS avg_risk,
                   SUM(CASE WHEN p.student_id IS NOT NULL THEN 1 ELSE 0 END) AS with_gift
            FROM student_risk_snapshots rs
            JOIN students st ON st.student_id = rs.student_id
            JOIN schools sch ON sch.school_id = st.school_id
            JOIN counties c ON c.county_id = sch.county_id
            LEFT JOIN v_student_fee_summary f ON f.student_id = rs.student_id
            LEFT JOIN (
                SELECT DISTINCT student_id FROM payments WHERE status = 'completed'
            ) p ON p.student_id = rs.student_id
            WHERE rs.refresh_run_id = ?
              AND rs.primary_intervention_code = 'school_fee_support'
            GROUP BY c.county_name
            ORDER BY arrears_kes DESC
            LIMIT 12
            """,
            (rid,),
        )
    ]


def _recent_activity(conn: sqlite3.Connection) -> list[dict]:
    return [
        dict(r)
        for r in conn.execute(
            """
            SELECT p.payment_id, p.paid_at, p.amount_kes, p.status,
                   COALESCE(sp.display_name, 'Sponsor') AS sponsor_name,
                   st.display_name AS student_name,
                   sch.school_name, c.county_name
            FROM payments p
            LEFT JOIN sponsors sp ON sp.sponsor_id = p.sponsor_id
            JOIN students st ON st.student_id = p.student_id
            JOIN schools sch ON sch.school_id = p.school_id
            JOIN counties c ON c.county_id = sch.county_id
            ORDER BY p.paid_at DESC, p.payment_id DESC
            LIMIT 20
            """
        )
    ]


def _freshness_brief(conn: sqlite3.Connection) -> list[dict]:
    return [
        dict(r)
        for r in conn.execute(
            """
            SELECT run_id, run_type, source, started_at, finished_at, status, notes
            FROM refresh_runs
            ORDER BY run_id DESC
            LIMIT 8
            """
        )
    ]


if __name__ == '__main__':
    import json

    print(json.dumps(ops_snapshot(), indent=2, default=str)[:5000])
