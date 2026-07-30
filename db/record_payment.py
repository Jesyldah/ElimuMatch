"""
Record a (possibly partial) sponsor payment and allocate it to term arrears.

Allocation policy (default):
  1. Oldest term first
  2. Within a term: tuition → boarding → lunch → activity
  3. Stop when payment is fully allocated

Examples:
  python db/record_payment.py --student-id 231 --amount 5000
  python db/record_payment.py --student-id 231 --amount 8000 --term-label "2026 Term 2"
  python db/record_payment.py --student-id 231 --amount 3000 --category tuition
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent
if str(DB_DIR) not in sys.path:
    sys.path.insert(0, str(DB_DIR))

from schema import DB_PATH  # noqa: E402

CATEGORY_ORDER = ['tuition', 'boarding', 'lunch', 'activity']


def connect() -> sqlite3.Connection:
    if not DB_PATH.exists():
        raise FileNotFoundError(f'Missing {DB_PATH}. Run: python db/init_db.py')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def outstanding_lines(
    conn: sqlite3.Connection,
    student_id: int,
    term_label: str | None = None,
    category: str | None = None,
    term_labels: list[str] | None = None,
):
    sql = """
        SELECT
            stf.student_term_fee_id,
            stf.student_id,
            s.school_id,
            t.term_label,
            t.academic_year,
            t.term_number,
            fc.category_code,
            fc.category_name,
            (stf.amount_due_kes - stf.amount_paid_kes) AS outstanding_kes
        FROM student_term_fees stf
        JOIN students s ON s.student_id = stf.student_id
        JOIN academic_terms t ON t.term_id = stf.term_id
        JOIN fee_categories fc ON fc.fee_category_id = stf.fee_category_id
        WHERE stf.student_id = ?
          AND (stf.amount_due_kes - stf.amount_paid_kes) > 0
          AND stf.status IN ('unpaid', 'partial')
    """
    params: list = [student_id]
    if term_labels:
        placeholders = ','.join('?' * len(term_labels))
        sql += f' AND t.term_label IN ({placeholders})'
        params.extend(term_labels)
    elif term_label:
        sql += ' AND t.term_label = ?'
        params.append(term_label)
    if category:
        sql += ' AND fc.category_code = ?'
        params.append(category)
    sql += ' ORDER BY t.academic_year ASC, t.term_number ASC'

    rows = conn.execute(sql, params).fetchall()

    def sort_key(r):
        try:
            cat_rank = CATEGORY_ORDER.index(r['category_code'])
        except ValueError:
            cat_rank = 99
        return (r['academic_year'], r['term_number'], cat_rank)

    return sorted(rows, key=sort_key)


def allocate(amount: int, lines: list[sqlite3.Row]) -> list[tuple[int, int]]:
    """Return list of (student_term_fee_id, amount). Rejects overpayment."""
    selectable = sum(int(line['outstanding_kes']) for line in lines)
    if amount > selectable:
        raise OverpaymentError(amount, selectable)
    remaining = amount
    out = []
    for line in lines:
        if remaining <= 0:
            break
        take = min(remaining, int(line['outstanding_kes']))
        if take > 0:
            out.append((int(line['student_term_fee_id']), take))
            remaining -= take
    if remaining > 0:
        # Should not happen after the guard above
        raise OverpaymentError(amount, selectable)
    return out


class OverpaymentError(ValueError):
    def __init__(self, requested: int, available: int):
        self.requested = requested
        self.available = available
        super().__init__(
            f'Overpayment blocked: requested KES {requested:,} but only '
            f'KES {available:,} is outstanding on the selected terms.'
        )


class StaleBalanceError(ValueError):
    """Sponsor screen no longer matches the ledger at commit time."""

    def __init__(self, expected: int, actual: int):
        self.expected = expected
        self.actual = actual
        super().__init__(
            f'Balances changed since you loaded this page '
            f'(shown KES {expected:,}, now KES {actual:,}). Refresh and confirm again.'
        )


def term_arrears_summary(conn: sqlite3.Connection, student_id: int) -> list[dict]:
    rows = conn.execute(
        """
        SELECT term_label, academic_year, term_number,
               SUM(amount_outstanding_kes) AS outstanding
        FROM v_term_arrears
        WHERE student_id = ?
        GROUP BY term_label, academic_year, term_number
        ORDER BY academic_year, term_number
        """,
        (student_id,),
    ).fetchall()
    return [
        {
            'term_label': r['term_label'],
            'academic_year': int(r['academic_year']),
            'term_number': int(r['term_number']),
            'outstanding': int(r['outstanding']),
        }
        for r in rows
    ]


def payment_receipt(conn: sqlite3.Connection, payment_id: int) -> dict:
    header = conn.execute(
        """
        SELECT
            p.payment_id, p.paid_at, p.amount_kes, p.student_id,
            st.display_name, sch.school_name, c.county_name, sch.school_type
        FROM payments p
        JOIN students st ON st.student_id = p.student_id
        JOIN schools sch ON sch.school_id = p.school_id
        JOIN counties c ON c.county_id = sch.county_id
        WHERE p.payment_id = ?
        """,
        (payment_id,),
    ).fetchone()
    if not header:
        raise ValueError(f'Payment {payment_id} not found')

    alloc_rows = conn.execute(
        """
        SELECT t.term_label, SUM(pa.amount_kes) AS amount
        FROM payment_allocations pa
        JOIN student_term_fees stf ON stf.student_term_fee_id = pa.student_term_fee_id
        JOIN academic_terms t ON t.term_id = stf.term_id
        WHERE pa.payment_id = ?
        GROUP BY t.term_label, t.academic_year, t.term_number
        ORDER BY t.academic_year, t.term_number
        """,
        (payment_id,),
    ).fetchall()

    terms = term_arrears_summary(conn, int(header['student_id']))
    remaining = sum(t['outstanding'] for t in terms)
    return {
        'payment_id': int(header['payment_id']),
        'receipt_id': f"EM-DB-{int(header['payment_id']):05d}",
        'paid_at': header['paid_at'],
        'amount': int(header['amount_kes']),
        'student_id': int(header['student_id']),
        'display_name': header['display_name'],
        'school': header['school_name'],
        'county': header['county_name'],
        'school_type': header['school_type'],
        'allocations': [
            {'term_label': r['term_label'], 'amount': int(r['amount'])} for r in alloc_rows
        ],
        'remaining_after': remaining,
        'terms': terms,
    }


def list_receipts(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    ids = conn.execute(
        """
        SELECT payment_id FROM payments
        WHERE status = 'completed'
        ORDER BY paid_at DESC, payment_id DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    return [payment_receipt(conn, int(r['payment_id'])) for r in ids]


def apply_payment(
    conn: sqlite3.Connection,
    student_id: int,
    amount: int,
    term_label: str | None = None,
    category: str | None = None,
    sponsor_name: str = 'Anonymous Sponsor',
    term_labels: list[str] | None = None,
    source: str = 'record_payment.py',
    expected_outstanding: int | None = None,
) -> int:
    """
    Record a payment against *current* ledger balances.

    Settlement is ledger-authoritative:
      - Re-reads outstanding lines inside BEGIN IMMEDIATE
      - Rejects if expected_outstanding (from the sponsor screen) no longer matches
      - Rejects overpayment (never creates a credit / negative arrears)
    """
    # Manual transaction control so we can lock with BEGIN IMMEDIATE
    prev_isolation = conn.isolation_level
    conn.isolation_level = None
    conn.execute('BEGIN IMMEDIATE')
    try:
        lines = outstanding_lines(
            conn,
            student_id,
            term_label=None if term_labels else term_label,
            category=category,
            term_labels=term_labels,
        )
        if not lines:
            raise ValueError('No outstanding arrears for this student/filter.')

        actual = sum(int(r['outstanding_kes']) for r in lines)
        if expected_outstanding is not None and int(expected_outstanding) != actual:
            raise StaleBalanceError(int(expected_outstanding), actual)

        school_id = int(lines[0]['school_id'])
        splits = allocate(amount, lines)

        cur = conn.cursor()
        cur.execute('INSERT INTO sponsors (display_name) VALUES (?)', (sponsor_name,))
        sponsor_id = cur.lastrowid

        cur.execute(
            """
            INSERT INTO payments (sponsor_id, student_id, school_id, amount_kes, payment_method, status, notes)
            VALUES (?, ?, ?, ?, 'simulated', 'completed', ?)
            """,
            (
                sponsor_id,
                student_id,
                school_id,
                amount,
                f'Allocated to {len(splits)} fee line(s); verified outstanding was KES {actual:,}',
            ),
        )
        payment_id = cur.lastrowid

        for fee_id, alloc_amt in splits:
            cur.execute(
                """
                INSERT INTO payment_allocations (payment_id, student_term_fee_id, amount_kes)
                VALUES (?, ?, ?)
                """,
                (payment_id, fee_id, alloc_amt),
            )
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
                  AND (amount_due_kes - amount_paid_kes) >= ?
                """,
                (alloc_amt, alloc_amt, alloc_amt, fee_id, alloc_amt),
            )
            if cur.rowcount != 1:
                raise StaleBalanceError(actual, max(0, actual - alloc_amt))

        cur.execute(
            """
            INSERT INTO refresh_runs (run_type, source, status, finished_at, notes)
            VALUES ('payment_import', ?, 'success', datetime('now'), ?)
            """,
            (source, f'payment_id={payment_id}'),
        )
        conn.execute('COMMIT')
        return payment_id
    except Exception:
        conn.execute('ROLLBACK')
        raise
    finally:
        conn.isolation_level = prev_isolation


def show_student_arrears(conn: sqlite3.Connection, student_id: int) -> None:
    rows = conn.execute(
        """
        SELECT term_label, category_name, amount_due_kes, amount_paid_kes, amount_outstanding_kes, status
        FROM v_term_arrears
        WHERE student_id = ?
        ORDER BY academic_year, term_number, category_name
        """,
        (student_id,),
    ).fetchall()
    if not rows:
        print(f'Student #{student_id}: no outstanding arrears.')
        return
    print(f'Student #{student_id} outstanding:')
    for r in rows:
        print(
            f"  {r['term_label']:12s} | {r['category_name']:22s} | "
            f"due {r['amount_due_kes']:,} | paid {r['amount_paid_kes']:,} | "
            f"owed {r['amount_outstanding_kes']:,} | {r['status']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description='Record partial/full fee payment')
    parser.add_argument('--student-id', type=int, required=True)
    parser.add_argument('--amount', type=int, default=None, help='KES amount (can be partial)')
    parser.add_argument('--term-label', type=str, default=None, help='e.g. "2026 Term 2"')
    parser.add_argument('--category', type=str, default=None, choices=CATEGORY_ORDER)
    parser.add_argument('--sponsor', type=str, default='Anonymous Sponsor')
    parser.add_argument('--show-only', action='store_true', help='Only print arrears')
    args = parser.parse_args()

    conn = connect()
    show_student_arrears(conn, args.student_id)
    if args.show_only:
        conn.close()
        return

    if args.amount is None or args.amount <= 0:
        raise SystemExit('--amount is required (positive KES) unless --show-only')

    payment_id = apply_payment(
        conn,
        student_id=args.student_id,
        amount=args.amount,
        term_label=args.term_label,
        category=args.category,
        sponsor_name=args.sponsor,
    )
    print(f'\nPayment #{payment_id} recorded: KES {args.amount:,}')
    print('Updated arrears:')
    show_student_arrears(conn, args.student_id)
    conn.close()


if __name__ == '__main__':
    main()
