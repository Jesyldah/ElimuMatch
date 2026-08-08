"""
Build a sponsor-facing portal:
  County → Day/Boarding → School → Student → choose terms → custom amount → Pay

Balances come from the fee DB when available (term arrears).
Partial payments allocate oldest-selected-term first and reduce displayed arrears
(persisted in localStorage for the PoC demo).
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd

from kenya_schools import SCHOOLS
from student_display import first_name_label

ROOT = Path(__file__).parent
MATCH_PATH = ROOT / 'intervention_outputs' / 'student_intervention_assignments.csv'
FALLBACK_MATCH = ROOT / 'matching_outputs' / 'sponsor_match_list.csv'
RAW_PATH = ROOT / 'elimu_match_data_v4.csv'
DB_PATH = ROOT / 'db' / 'elimu_match.db'
OUTPUT = ROOT / 'sponsor_portal.html'
SCHOOLS_CSV = ROOT / 'tableau_exports' / 'schools_dimension.csv'


def human_reason(match_reason: str) -> str:
    parts = []
    r = (match_reason or '').lower()
    if 'low ses' in r or 'mid-low ses' in r or 'fee' in r:
        parts.append('Family needs financial help')
    if 'cash-flow' in r or 'economic' in r:
        parts.append('Income is unstable this term')
    if 'dropout' in r or 'risk' in r:
        parts.append('At risk of leaving school')
    if 'academic' in r:
        parts.append('Needs support to stay enrolled')
    if 'health' in r:
        parts.append('Health-related barriers to attendance')
    if not parts:
        parts.append('Recommended for fee support')
    return ' · '.join(dict.fromkeys(parts))


def fee_support_student_ids() -> set[int]:
    path = MATCH_PATH if MATCH_PATH.exists() else FALLBACK_MATCH
    matches = pd.read_csv(path)
    if 'intervention_id' in matches.columns:
        fee = matches[
            (matches['match_rank'] == 1) & (matches['intervention_id'] == 'school_fee_support')
        ]
    else:
        fee = matches[
            (matches['match_rank'] == 1)
            & (matches['intervention'].astype(str).str.contains('Fee', na=False))
        ]
    return set(fee['student_id'].astype(int))


def load_term_arrears_from_db(student_ids: set[int]) -> dict[int, list[dict]]:
    """student_id → list of term arrears (oldest first), rolled up by term."""
    if not DB_PATH.exists() or not student_ids:
        return {}
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    placeholders = ','.join('?' * len(student_ids))
    rows = conn.execute(
        f"""
        SELECT student_id, term_label, academic_year, term_number,
               SUM(amount_outstanding_kes) AS outstanding_kes
        FROM v_term_arrears
        WHERE student_id IN ({placeholders})
        GROUP BY student_id, term_label, academic_year, term_number
        ORDER BY student_id, academic_year, term_number
        """,
        tuple(student_ids),
    ).fetchall()
    conn.close()

    out: dict[int, list[dict]] = {}
    for r in rows:
        sid = int(r['student_id'])
        out.setdefault(sid, []).append({
            'term_label': r['term_label'],
            'academic_year': int(r['academic_year']),
            'term_number': int(r['term_number']),
            'outstanding': int(r['outstanding_kes']),
        })
    return out


def load_student_meta(student_ids: set[int]) -> dict[int, dict]:
    path = MATCH_PATH if MATCH_PATH.exists() else FALLBACK_MATCH
    matches = pd.read_csv(path)
    raw = pd.read_csv(RAW_PATH)[['student_id', 'age_at_enrollment', 'gender']]
    if 'intervention_id' in matches.columns:
        fee = matches[
            (matches['match_rank'] == 1) & (matches['intervention_id'] == 'school_fee_support')
        ].copy()
    else:
        fee = matches[
            (matches['match_rank'] == 1)
            & (matches['intervention'].astype(str).str.contains('Fee', na=False))
        ].copy()
    fee = fee.merge(raw, on='student_id', how='left')
    reason_col = 'sponsor_action' if 'sponsor_action' in fee.columns else 'match_reason'
    meta = {}
    for _, row in fee.iterrows():
        sid = int(row['student_id'])
        if sid not in student_ids:
            continue
        why = human_reason(str(row.get(reason_col, '')))
        if 'persona' in row and pd.notna(row.get('persona')):
            why = f"{row['persona']} · {why}"
        meta[sid] = {
            'school_id': int(row['school_id']),
            'age': int(row['age_at_enrollment']),
            'gender': 'Girl' if int(row['gender']) == 1 else 'Boy',
            'why': why,
            'priority': float(row['priority_score']) if 'priority_score' in row and pd.notna(row.get('priority_score')) else 0,
        }
    return meta


def build_payload() -> dict:
    ids = fee_support_student_ids()
    arrears_map = load_term_arrears_from_db(ids)
    meta = load_student_meta(ids)

    students = []
    for sid, m in meta.items():
        terms = arrears_map.get(sid, [])
        # Fallback if DB missing: single synthetic current-term balance
        if not terms:
            terms = [{
                'term_label': '2026 Term 2',
                'academic_year': 2026,
                'term_number': 2,
                'outstanding': 15000,
            }]
        total = sum(t['outstanding'] for t in terms)
        if total <= 0:
            continue
        school = SCHOOLS.get(m['school_id'], {
            'name': f"School {m['school_id']}", 'county': 'Unknown', 'type': 'Day',
        })
        students.append({
            'id': sid,
            'school_id': m['school_id'],
            'school': school['name'],
            'county': school['county'],
            'school_type': school['type'],
            'display_name': first_name_label(sid, m['gender']),
            'age': m['age'],
            'gender': m['gender'],
            'why': m['why'],
            'priority': m['priority'],
            'amount': total,  # total outstanding across terms
            'terms': terms,
        })

    # Portal demo: balance fee-support students across Day + Boarding in each
    # county so both school-type buttons always lead to real queue entries.
    # Payments still key off student_id (ledger school is unchanged in SQLite).
    students = _balance_students_by_county_type(students)
    students.sort(key=lambda s: (-s['priority'], -s['amount'], s['id']))

    # All 47 counties × Day + Boarding (national coverage, no regional bias)
    school_list = []
    for sid, meta_s in SCHOOLS.items():
        count = sum(1 for s in students if s['school_id'] == sid)
        school_list.append({
            'id': sid,
            'name': meta_s['name'],
            'county': meta_s['county'],
            'type': meta_s['type'],
            'count': count,
        })
    school_list.sort(key=lambda s: (s['county'], s['type'], s['name']))
    counties = sorted({s['county'] for s in school_list})

    SCHOOLS_CSV.parent.mkdir(exist_ok=True)
    pd.DataFrame([
        {'school_id': sid, 'school_name': m['name'], 'county': m['county'], 'school_type': m['type']}
        for sid, m in SCHOOLS.items()
    ]).to_csv(SCHOOLS_CSV, index=False)

    return {
        'counties': counties,
        'schools': school_list,
        'students': students,
        'source': 'sqlite' if arrears_map else 'fallback',
        'freshness': _embed_freshness(),
    }


def _balance_students_by_county_type(students: list[dict]) -> list[dict]:
    """Alternate fee-queue students onto Day and Boarding schools in each county."""
    by_ct: dict[tuple[str, str], int] = {
        (m['county'], m['type']): sid for sid, m in SCHOOLS.items()
    }
    by_county: dict[str, list[dict]] = {}
    for s in students:
        by_county.setdefault(s['county'], []).append(s)

    balanced: list[dict] = []
    for county, group in by_county.items():
        day_id = by_ct.get((county, 'Day'))
        board_id = by_ct.get((county, 'Boarding'))
        group.sort(key=lambda s: (-s['priority'], -s['amount'], s['id']))
        if not day_id or not board_id:
            balanced.extend(group)
            continue
        for i, s in enumerate(group):
            school_type = 'Day' if i % 2 == 0 else 'Boarding'
            sid = day_id if school_type == 'Day' else board_id
            m = SCHOOLS[sid]
            s = dict(s)
            s['school_id'] = sid
            s['school'] = m['name']
            s['school_type'] = m['type']
            balanced.append(s)
    return balanced


def _embed_freshness() -> dict:
    try:
        import sys
        db_dir = str(ROOT / 'db')
        if db_dir not in sys.path:
            sys.path.insert(0, db_dir)
        from freshness import freshness_report
        return freshness_report()
    except Exception:
        return {'ok': False, 'layers': [], 'coverage': {}, 'recent_runs': []}


def build_html(payload: dict) -> str:
    data_json = json.dumps(payload)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ElimuMatch | Keep a student in school</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="apple-touch-icon" href="favicon.svg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {{
      --ink: #14213d;
      --leaf: #1b7a5a;
      --leaf-deep: #0f5c42;
      --sun: #f4b942;
      --sand: #f7f1e8;
      --mist: #e8efe9;
      --white: #ffffff;
      --muted: #5c6b73;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Outfit', sans-serif;
      color: var(--ink);
      background: var(--sand);
      min-height: 100vh;
    }}
    .hero {{
      min-height: 100vh;
      display: none;
      align-items: end;
      padding: 2rem clamp(1.25rem, 4vw, 4rem) 3.5rem;
      background:
        linear-gradient(120deg, rgba(20,33,61,0.72) 0%, rgba(15,92,66,0.55) 55%, rgba(20,33,61,0.35) 100%),
        radial-gradient(ellipse at 20% 20%, rgba(244,185,66,0.25), transparent 50%),
        linear-gradient(160deg, #1b7a5a 0%, #14213d 100%);
      color: var(--white);
      position: relative;
      overflow: hidden;
    }}
    .hero.screen-active {{ display: grid; }}
    .flow {{
      max-width: 880px;
      margin: 0 auto;
      padding: 2rem clamp(1.25rem, 4vw, 2rem) 4rem;
      display: none;
      min-height: 100vh;
    }}
    .flow.screen-active {{ display: block; }}
    .history {{
      max-width: 880px;
      margin: 0 auto;
      padding: 2rem clamp(1.25rem, 4vw, 2rem) 4rem;
      display: none;
      min-height: 100vh;
    }}
    .history.screen-active {{ display: block; }}
    .confirm {{
      display: none;
      min-height: 100vh;
      align-items: center;
      justify-content: center;
      padding: 2rem;
      text-align: center;
      background: radial-gradient(circle at 30% 20%, rgba(244,185,66,0.2), transparent 40%), var(--sand);
    }}
    .confirm.screen-active {{ display: flex; }}
    .topbar {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      margin-bottom: 1.75rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid #e0d8cc;
    }}
    .topbar .brand-mini {{
      font-family: 'Fraunces', serif;
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--ink);
    }}
    .back-btn {{
      background: none;
      border: none;
      color: var(--leaf);
      font-family: inherit;
      font-weight: 600;
      font-size: 0.95rem;
      cursor: pointer;
      padding: 0.35rem 0;
    }}
    .back-btn:hover {{ color: var(--leaf-deep); }}
    footer.note {{
      text-align: center;
      padding: 1.5rem;
      font-size: 0.8rem;
      color: var(--muted);
      display: none;
    }}
    footer.note.screen-active {{ display: block; }}
    footer.note .footer-mode {{
      margin: 0;
      line-height: 1.45;
    }}
    .hero-inner {{ position: relative; z-index: 1; max-width: 720px; }}
    .project-home-link {{
      display: inline-flex;
      align-items: center;
      color: var(--sun);
      font-weight: 700;
      font-size: 0.95rem;
      text-decoration: none;
      margin-bottom: 1rem;
      animation: rise 0.7s ease-out both;
    }}
    .project-home-link:hover {{ text-decoration: underline; }}
    .brand {{
      font-family: 'Fraunces', serif;
      font-size: clamp(2.8rem, 8vw, 5rem);
      font-weight: 700;
      line-height: 0.95;
      letter-spacing: -0.02em;
      margin-bottom: 1.25rem;
      animation: rise 0.8s ease-out both;
    }}
    .hero h1 {{
      font-weight: 500;
      font-size: clamp(1.15rem, 2.5vw, 1.45rem);
      max-width: 28ch;
      line-height: 1.35;
      margin-bottom: 0.75rem;
      animation: rise 0.8s ease-out 0.12s both;
    }}
    .hero p {{
      color: rgba(255,255,255,0.82);
      font-size: 1.05rem;
      max-width: 40ch;
      margin-bottom: 2rem;
      animation: rise 0.8s ease-out 0.22s both;
    }}
    .cta {{
      display: inline-flex;
      background: var(--sun);
      color: var(--ink);
      font-weight: 700;
      font-size: 1.05rem;
      padding: 0.95rem 1.6rem;
      border: none;
      border-radius: 999px;
      cursor: pointer;
      text-decoration: none;
      animation: rise 0.8s ease-out 0.32s both;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .cta:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.25); }}
    @keyframes rise {{
      from {{ opacity: 0; transform: translateY(18px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    .step-label {{
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--leaf);
      margin-bottom: 0.5rem;
    }}
    .section-title {{
      font-family: 'Fraunces', serif;
      font-size: 1.85rem;
      margin-bottom: 1.25rem;
    }}
    .filters {{
      display: grid;
      gap: 1rem;
      margin-bottom: 2rem;
    }}
    @media (min-width: 700px) {{
      .filters {{ grid-template-columns: 1fr 1fr; }}
      .filters .full {{ grid-column: 1 / -1; }}
    }}
    label.field {{
      display: block;
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--muted);
      margin-bottom: 0.4rem;
    }}
    select.school-select, input.amount-input {{
      width: 100%;
      appearance: none;
      background: var(--white);
      border: 2px solid #d5ddd8;
      border-radius: 14px;
      padding: 1rem 1.15rem;
      font-family: inherit;
      font-size: 1.05rem;
      font-weight: 500;
      color: var(--ink);
      transition: border-color 0.2s;
    }}
    select.school-select {{
      background: var(--white) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' fill='%2314213d'%3E%3Cpath d='M4 6l4 4 4-4'/%3E%3C/svg%3E") right 1rem center no-repeat;
      padding-right: 2.5rem;
    }}
    select.school-select:focus, input.amount-input:focus {{ outline: none; border-color: var(--leaf); }}
    select.school-select:disabled {{
      opacity: 0.55;
      cursor: not-allowed;
      background-color: #eee;
    }}

    .type-toggle {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }}
    .type-btn {{
      border: 2px solid #d5ddd8;
      background: var(--white);
      border-radius: 14px;
      padding: 1rem;
      font-family: inherit;
      font-size: 1.05rem;
      font-weight: 600;
      cursor: pointer;
      transition: border-color 0.2s, background 0.2s;
    }}
    .type-btn:hover {{ border-color: var(--leaf); }}
    .type-btn.active {{
      border-color: var(--leaf);
      background: var(--mist);
      color: var(--leaf-deep);
    }}
    .type-btn:disabled {{ opacity: 0.45; cursor: not-allowed; }}

    .student-list {{
      display: flex;
      flex-direction: column;
      gap: 0.85rem;
      margin-bottom: 1.5rem;
    }}
    .student {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 1rem;
      align-items: center;
      background: var(--white);
      border: 2px solid transparent;
      border-radius: 16px;
      padding: 1.15rem 1.25rem;
      cursor: pointer;
      text-align: left;
      font-family: inherit;
      transition: border-color 0.2s, transform 0.15s, box-shadow 0.2s;
      width: 100%;
    }}
    .student:hover {{ transform: translateY(-1px); box-shadow: 0 6px 20px rgba(20,33,61,0.08); }}
    .student.selected {{ border-color: var(--leaf); background: var(--mist); }}
    .student .name {{ font-weight: 700; font-size: 1.1rem; margin-bottom: 0.2rem; }}
    .student .meta {{ color: var(--muted); font-size: 0.9rem; }}
    .trust-inline {{
      font-size: 0.85rem;
      color: var(--muted);
      margin: 0.35rem 0 0.85rem;
      line-height: 1.45;
    }}
    .mode-banner {{
      display: none;
      margin: 0 0 1rem;
      padding: 0.55rem 0.75rem;
      border-radius: 10px;
      font-size: 0.82rem;
      line-height: 1.4;
      color: var(--muted);
      background: rgba(20, 33, 61, 0.05);
      border: 1px solid #e0d8cc;
    }}
    .mode-banner.show {{ display: block; }}
    .mode-banner.live {{
      color: var(--leaf-deep);
      background: rgba(31, 122, 108, 0.08);
      border-color: rgba(31, 122, 108, 0.22);
    }}
    .student .amount {{
      font-family: 'Fraunces', serif;
      font-size: 1.35rem;
      font-weight: 700;
      white-space: nowrap;
    }}
    .student .amount span {{
      display: block;
      font-family: 'Outfit', sans-serif;
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--muted);
      text-align: right;
      margin-top: 0.15rem;
    }}
    .empty {{ color: var(--muted); padding: 2rem 0; text-align: center; }}
    .hidden {{ display: none !important; }}

    .pay-panel {{
      background: var(--white);
      border: 2px solid #d5ddd8;
      border-radius: 18px;
      padding: 1.35rem 1.4rem 1.5rem;
      margin-bottom: 6rem;
      display: none;
    }}
    .pay-panel.visible {{ display: block; }}
    .pay-panel h3 {{
      font-family: 'Fraunces', serif;
      font-size: 1.35rem;
      margin-bottom: 0.35rem;
    }}
    .pay-panel .sub {{ color: var(--muted); font-size: 0.92rem; margin-bottom: 1.1rem; }}

    .term-list {{ display: flex; flex-direction: column; gap: 0.55rem; margin-bottom: 1rem; }}
    .term-row {{
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 0.75rem;
      align-items: center;
      padding: 0.75rem 0.9rem;
      border-radius: 12px;
      border: 1.5px solid #e0d8cc;
      background: var(--sand);
      cursor: pointer;
    }}
    .term-row.checked {{
      border-color: var(--leaf);
      background: var(--mist);
    }}
    .term-row input {{ width: 1.1rem; height: 1.1rem; accent-color: var(--leaf); }}
    .term-row .t-label {{ font-weight: 600; }}
    .term-row .t-hint {{ font-size: 0.78rem; color: var(--muted); font-weight: 400; }}
    .term-row .t-amt {{ font-family: 'Fraunces', serif; font-weight: 700; }}

    .quick-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.5rem;
      margin-bottom: 1rem;
    }}
    .chip {{
      border: 1.5px solid #d5ddd8;
      background: var(--sand);
      border-radius: 999px;
      padding: 0.45rem 0.9rem;
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 600;
      cursor: pointer;
      color: var(--ink);
    }}
    .chip:hover {{ border-color: var(--leaf); color: var(--leaf-deep); }}

    .amount-row {{
      display: grid;
      gap: 0.75rem;
      margin-bottom: 0.75rem;
    }}
    @media (min-width: 560px) {{
      .amount-row {{ grid-template-columns: 1fr auto; align-items: end; }}
    }}
    .hint {{ font-size: 0.82rem; color: var(--muted); margin-bottom: 1rem; }}
    .hint strong {{ color: var(--leaf-deep); }}
    .err {{ color: #b42318; font-size: 0.85rem; margin-bottom: 0.75rem; display: none; }}
    .err.show {{ display: block; }}

    .pay-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      justify-content: space-between;
    }}
    .pay-btn {{
      background: var(--leaf);
      color: white;
      border: none;
      border-radius: 999px;
      padding: 0.95rem 1.8rem;
      font-family: inherit;
      font-weight: 700;
      font-size: 1.05rem;
      cursor: pointer;
    }}
    .pay-btn:hover {{ background: var(--leaf-deep); }}
    .pay-btn:disabled {{ opacity: 0.5; cursor: not-allowed; }}

    .confirm-box {{ max-width: 480px; animation: rise 0.6s ease-out; }}
    .confirm-box .check {{
      width: 72px; height: 72px; border-radius: 50%;
      background: var(--leaf); color: white;
      display: grid; place-items: center;
      font-size: 2rem; margin: 0 auto 1.25rem;
    }}
    .confirm-box h2 {{
      font-family: 'Fraunces', serif;
      font-size: 2rem;
      margin-bottom: 0.75rem;
    }}
    .confirm-box p {{ color: var(--muted); margin-bottom: 1rem; line-height: 1.5; }}
    .confirm-box ul {{
      text-align: left;
      margin: 0 auto 1.75rem;
      max-width: 320px;
      color: var(--ink);
      font-size: 0.92rem;
    }}

    .history-head {{
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      justify-content: space-between;
      gap: 0.75rem;
      margin-bottom: 1rem;
    }}
    .history-head h2 {{
      font-family: 'Fraunces', serif;
      font-size: 1.5rem;
    }}
    .history-total {{
      font-size: 0.92rem;
      color: var(--leaf-deep);
      font-weight: 600;
    }}
    .receipt {{
      background: var(--white);
      border: 1.5px solid #e0d8cc;
      border-radius: 14px;
      padding: 1rem 1.15rem;
      margin-bottom: 0.75rem;
    }}
    .receipt-top {{
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.45rem;
    }}
    .receipt-id {{
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: var(--leaf);
    }}
    .receipt-date {{ font-size: 0.85rem; color: var(--muted); }}
    .receipt-amt {{
      font-family: 'Fraunces', serif;
      font-size: 1.25rem;
      font-weight: 700;
    }}
    .receipt-who {{ font-weight: 600; margin-bottom: 0.25rem; }}
    .receipt-meta {{ font-size: 0.88rem; color: var(--muted); margin-bottom: 0.55rem; }}
    .receipt-alloc {{
      list-style: none;
      font-size: 0.88rem;
      border-top: 1px dashed #e0d8cc;
      padding-top: 0.55rem;
      margin-top: 0.35rem;
    }}
    .receipt-alloc li {{
      display: flex;
      justify-content: space-between;
      gap: 1rem;
      padding: 0.15rem 0;
    }}
    .receipt-remain {{
      font-size: 0.82rem;
      color: var(--muted);
      margin-top: 0.4rem;
    }}
    .receipt-remain.cleared {{ color: var(--leaf-deep); font-weight: 600; }}
    .history-empty {{
      color: var(--muted);
      font-size: 0.95rem;
      padding: 0.5rem 0 1rem;
    }}
    .linkish {{
      background: none;
      border: none;
      color: var(--leaf);
      font-family: inherit;
      font-weight: 600;
      font-size: 0.9rem;
      cursor: pointer;
      text-decoration: underline;
      text-underline-offset: 3px;
    }}
    .hero-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
      align-items: center;
      animation: rise 0.8s ease-out 0.32s both;
    }}
    .cta-ghost {{
      display: inline-flex;
      background: transparent;
      color: var(--white);
      font-weight: 600;
      font-size: 0.95rem;
      padding: 0.85rem 1.2rem;
      border: 1.5px solid rgba(255,255,255,0.45);
      border-radius: 999px;
      cursor: pointer;
      text-decoration: none;
    }}
    .cta-ghost:hover {{ border-color: var(--sun); color: var(--sun); }}
    .confirm-receipt {{
      text-align: left;
      background: var(--white);
      border: 1.5px solid #e0d8cc;
      border-radius: 14px;
      padding: 1rem 1.15rem;
      margin: 0 auto 1.5rem;
      max-width: 360px;
    }}
    .fresh-screen .layer {{
      background: var(--white);
      border: 1.5px solid #e0d8cc;
      border-radius: 14px;
      padding: 1rem 1.15rem;
      margin-bottom: 0.75rem;
    }}
    .fresh-screen .layer h4 {{
      font-size: 1.05rem;
      margin-bottom: 0.25rem;
    }}
    .fresh-screen .tag {{
      display: inline-block;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 0.15rem 0.5rem;
      border-radius: 999px;
      margin-bottom: 0.45rem;
    }}
    .tag.live {{ background: #d8f3ea; color: var(--leaf-deep); }}
    .tag.mixed {{ background: #e4f0ea; color: var(--leaf-deep); }}
    .tag.periodic {{ background: #fff3d6; color: #8a6a12; }}
    .tag.illustrative {{ background: #e8eef5; color: #3a4a5c; }}
    .fresh-screen .muted {{ color: var(--muted); font-size: 0.9rem; }}
    .runs-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.85rem;
      margin-top: 0.75rem;
    }}
    .runs-table th, .runs-table td {{
      text-align: left;
      padding: 0.45rem 0.5rem;
      border-bottom: 1px solid #e0d8cc;
    }}
    .runs-table th {{ color: var(--muted); font-size: 0.72rem; text-transform: uppercase; }}
  </style>
</head>
<body>
  <section class="hero screen-active" id="hero" data-screen="home">
    <div class="hero-inner">
      <a class="project-home-link" href="index.html">← Project home</a>
      <div class="brand">ElimuMatch</div>
      <h1>Keep a student in school in the county you care about.</h1>
      <p>Choose a school, see verified term arrears, and give any amount (partial gifts welcome). Students are shown by first name only.</p>
      <div class="hero-actions">
        <button class="cta" type="button" id="startSponsorBtn">Help Keep a Student in School →</button>
        <button class="cta-ghost" type="button" id="heroGiftsLink">Your gifts</button>
        <button class="cta-ghost" type="button" id="heroFreshLink">Data freshness</button>
      </div>
    </div>
  </section>

  <main class="flow" id="sponsor" data-screen="sponsor">
    <div class="topbar">
      <button type="button" class="back-btn" id="backFromSponsor">← Home</button>
      <div class="brand-mini">ElimuMatch</div>
    </div>
    <div class="mode-banner" id="modeBanner" role="status"></div>
    <div class="step-label">Find a student</div>
    <h2 class="section-title">Where do you want to keep a student in school?</h2>

    <div class="filters">
      <div>
        <label class="field" for="countySelect">1. County</label>
        <select class="school-select" id="countySelect">
          <option value="">Select a county…</option>
        </select>
      </div>
      <div>
        <label class="field">2. School type</label>
        <div class="type-toggle">
          <button type="button" class="type-btn" id="typeDay" data-type="Day" disabled>Day school</button>
          <button type="button" class="type-btn" id="typeBoarding" data-type="Boarding" disabled>Boarding</button>
        </div>
      </div>
      <div class="full">
        <label class="field" for="schoolSelect">3. School</label>
        <select class="school-select" id="schoolSelect" disabled>
          <option value="">Select a school…</option>
        </select>
      </div>
    </div>

    <div id="stepStudents" class="hidden">
      <div class="step-label">4. Student</div>
      <h2 class="section-title">Pick a student to keep in school</h2>
      <p class="trust-inline">Real student at a named partner school. Need verified from school fee records. Reviewed before publish. Gifts pass through to school fee accounts.</p>
      <div class="student-list" id="studentList"></div>
    </div>

    <div class="pay-panel" id="payPanel">
      <div class="step-label">5. Gift</div>
      <h3 id="payTitle">Choose terms &amp; amount</h3>
      <p class="sub" id="paySub"></p>

      <label class="field">Arrears by term: tick what you want to cover</label>
      <div class="quick-row">
        <button type="button" class="chip" id="chipOldest">Oldest unpaid only</button>
        <button type="button" class="chip" id="chipAll">All terms</button>
        <button type="button" class="chip" id="chipCurrent">Current term only</button>
      </div>
      <div class="term-list" id="termList"></div>

      <div class="amount-row">
        <div>
          <label class="field" for="amountInput">Your gift (KES)</label>
          <input class="amount-input" id="amountInput" type="number" min="1" step="100" placeholder="e.g. 5000" />
        </div>
        <button type="button" class="chip" id="chipFillSelected" style="margin-bottom:0.15rem">Fill selected total</button>
      </div>
      <p class="hint" id="payHint">Payments apply to the <strong>oldest selected term first</strong>, then newer terms. Gifts cannot exceed arrears currently recorded on the fee ledger.</p>
      <p class="hint" id="verifiedAt" style="display:none;color:var(--leaf-deep)"></p>
      <p class="err" id="payErr"></p>
      <div class="pay-actions">
        <div id="payPreview" style="color:var(--muted);font-size:0.9rem;"></div>
        <button class="pay-btn" id="payBtn" type="button">Pay this amount</button>
      </div>
    </div>
  </main>

  <section class="history fresh-screen" id="freshness" data-screen="freshness">
    <div class="topbar">
      <button type="button" class="back-btn" id="backFromFresh">← Home</button>
      <div class="brand-mini">ElimuMatch</div>
    </div>
    <div class="step-label">Transparency</div>
    <h2 class="section-title">How live is this data?</h2>
    <p class="muted" id="freshHonesty" style="margin-bottom:1.25rem"></p>
    <div id="freshLayers"></div>
    <h3 style="font-family:'Fraunces',serif;font-size:1.25rem;margin:1.5rem 0 0.5rem">What this PoC represents</h3>
    <div class="layer" id="freshCoverage"></div>
    <h3 style="font-family:'Fraunces',serif;font-size:1.25rem;margin:1.5rem 0 0.5rem">Recent refresh runs</h3>
    <p class="muted">Logged in <code>refresh_runs</code> (the audit trail for fee sync, scoring, and payments).</p>
    <table class="runs-table" id="freshRuns">
      <thead>
        <tr><th>When</th><th>Type</th><th>Source</th><th>Status</th></tr>
      </thead>
      <tbody></tbody>
    </table>
  </section>

  <section class="history" id="gifts" data-screen="gifts">
    <div class="topbar">
      <button type="button" class="back-btn" id="backFromGifts">← Home</button>
      <div class="brand-mini">ElimuMatch</div>
    </div>
    <div class="history-head">
      <div>
        <div class="step-label">Receipts</div>
        <h2>Your gifts</h2>
      </div>
      <div class="history-total" id="historyTotal"></div>
    </div>
    <p class="history-empty" id="historyEmpty">No gifts yet. When you help a student, a receipt appears here.</p>
    <div id="historyList"></div>
    <button type="button" class="linkish" id="clearHistoryBtn" style="display:none;margin-top:0.5rem">Clear gift history (demo)</button>
  </section>

  <section class="confirm" id="confirm" data-screen="confirm">
    <div class="confirm-box">
      <div class="check">✓</div>
      <h2>You're keeping them in class.</h2>
      <p id="confirmText"></p>
      <div class="confirm-receipt" id="confirmReceipt"></div>
      <button class="cta" type="button" id="againBtn" style="background:var(--leaf);color:white;">Help another student</button>
      <div style="margin-top:1rem">
        <button type="button" class="linkish" id="viewGiftsBtn">View all gifts</button>
      </div>
    </div>
  </section>

  <footer class="note" id="siteFooter">
    <p class="footer-mode" id="footerMode">
      Demo portal for Quantic MSBA Capstone · Run <code>python db/portal_server.py</code> so gifts write to SQLite · First-name display only (no surnames)
    </p>
  </footer>

  <script>
    const DATA = {data_json};
    const STORAGE_KEY = 'elimu_match_portal_balances_v1';
    const HISTORY_KEY = 'elimu_match_portal_gifts_v1';
    const API_BASE = (location.protocol === 'http:' || location.protocol === 'https:')
      ? ''
      : 'http://127.0.0.1:8765';
    let apiOnline = false;
    let selectedType = null;
    let selectedStudent = null;
    let giftHistory = [];

    const countySelect = document.getElementById('countySelect');
    const schoolSelect = document.getElementById('schoolSelect');
    const typeDay = document.getElementById('typeDay');
    const typeBoarding = document.getElementById('typeBoarding');
    const stepStudents = document.getElementById('stepStudents');
    const studentList = document.getElementById('studentList');
    const payPanel = document.getElementById('payPanel');
    const termList = document.getElementById('termList');
    const amountInput = document.getElementById('amountInput');
    const payBtn = document.getElementById('payBtn');
    const payErr = document.getElementById('payErr');
    const payHint = document.getElementById('payHint');
    const payPreview = document.getElementById('payPreview');
    const confirm = document.getElementById('confirm');
    const confirmText = document.getElementById('confirmText');
    const confirmReceipt = document.getElementById('confirmReceipt');
    const againBtn = document.getElementById('againBtn');
    const hero = document.getElementById('hero');
    const flow = document.getElementById('sponsor');
    const giftsSection = document.getElementById('gifts');
    const freshSection = document.getElementById('freshness');
    const siteFooter = document.getElementById('siteFooter');
    const historyList = document.getElementById('historyList');
    const historyEmpty = document.getElementById('historyEmpty');
    const historyTotal = document.getElementById('historyTotal');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');

    const SCREENS = {{
      home: [hero],
      sponsor: [flow, siteFooter],
      gifts: [giftsSection, siteFooter],
      freshness: [freshSection, siteFooter],
      confirm: [confirm],
    }};

    function showScreen(name) {{
      Object.values(SCREENS).flat().forEach(el => el.classList.remove('screen-active'));
      (SCREENS[name] || []).forEach(el => el.classList.add('screen-active'));
      window.scrollTo({{ top: 0, behavior: 'instant' in window ? 'instant' : 'auto' }});
    }}

    function loadGiftHistory() {{
      try {{
        giftHistory = JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]');
        if (!Array.isArray(giftHistory)) giftHistory = [];
      }} catch (e) {{
        giftHistory = [];
      }}
    }}

    function saveGiftHistory() {{
      if (apiOnline) return; // DB is source of truth when API is up
      localStorage.setItem(HISTORY_KEY, JSON.stringify(giftHistory));
    }}

    async function probeApi() {{
      try {{
        const res = await fetch(API_BASE + '/api/health', {{ cache: 'no-store' }});
        apiOnline = res.ok;
      }} catch (e) {{
        apiOnline = false;
      }}
      const footMode = document.getElementById('footerMode');
      if (footMode) {{
        footMode.innerHTML = apiOnline
          ? 'Connected to the fee ledger · Gifts update ledger balances · First-name display only'
          : 'Offline demo mode (browser only). For ledger writes run <code>python db/portal_server.py</code> then open the localhost URL.';
      }}
      updateModeBanner();
      return apiOnline;
    }}

    function updateModeBanner() {{
      const banner = document.getElementById('modeBanner');
      if (!banner) return;
      banner.classList.add('show');
      if (apiOnline) {{
        banner.classList.add('live');
        banner.innerHTML = 'Connected to the fee ledger. Gifts write to balances.';
      }} else {{
        banner.classList.remove('live');
        banner.innerHTML = 'Demo mode. Gifts save in this browser only. Run <code>python db/portal_server.py</code> for ledger writes.';
      }}
    }}

    function fmtWhen(iso) {{
      if (!iso) return '-';
      try {{
        return new Date(iso.includes('T') ? iso : iso.replace(' ', 'T') + 'Z').toLocaleString('en-KE', {{
          dateStyle: 'medium',
          timeStyle: 'short',
        }});
      }} catch (e) {{
        return iso;
      }}
    }}

    function renderFreshness(report) {{
      if (!report || !report.ok) {{
        const honesty = document.getElementById('freshHonesty');
        if (honesty) honesty.textContent = 'Freshness unavailable. Run python db/init_db.py';
        return;
      }}
      const layers = report.layers || [];

      document.getElementById('freshHonesty').textContent =
        (report.coverage && report.coverage.honesty) ||
        'Gifts update the fee ledger live. School sync is periodic. The cohort is a synthetic PoC.';

      document.getElementById('freshLayers').innerHTML = layers.map(l => `
        <div class="layer">
          <span class="tag ${{l.live_level}}">${{l.live_level}}</span>
          <h4>${{l.label}}</h4>
          <p><strong>${{l.mode}}</strong> · ${{l.cadence}}</p>
          <p class="muted">Last updated: ${{fmtWhen(l.last_updated)}}</p>
          <p class="muted">${{l.detail}}</p>
        </div>
      `).join('');

      const cov = report.coverage || {{}};
      document.getElementById('freshCoverage').innerHTML = `
        <p><strong>Students:</strong> ${{(cov.students || 0).toLocaleString('en-KE')}} ·
           <strong>Schools:</strong> ${{cov.schools || 0}} ·
           <strong>Counties:</strong> ${{cov.counties || 0}}</p>
        <p class="muted" style="margin-top:0.5rem">${{cov.geography || ''}}</p>
        <p class="muted">${{cov.population || ''}}</p>
        <p class="muted">${{cov.time_window || ''}}</p>
      `;

      const tbody = document.querySelector('#freshRuns tbody');
      const runs = report.recent_runs || [];
      tbody.innerHTML = runs.length
        ? runs.map(r => `
            <tr>
              <td>${{fmtWhen(r.finished_at || r.started_at)}}</td>
              <td>${{r.run_type}}</td>
              <td>${{r.source || '-'}}</td>
              <td>${{r.status}}</td>
            </tr>`).join('')
        : '<tr><td colspan="4">No refresh runs logged yet.</td></tr>';
    }}

    async function loadFreshness() {{
      let report = DATA.freshness;
      if (apiOnline) {{
        try {{
          const res = await fetch(API_BASE + '/api/freshness', {{ cache: 'no-store' }});
          if (res.ok) report = await res.json();
        }} catch (e) {{ /* keep embedded */ }}
      }}
      renderFreshness(report);
    }}

    async function fetchDbReceipts() {{
      if (!apiOnline) return false;
      try {{
        const res = await fetch(API_BASE + '/api/receipts', {{ cache: 'no-store' }});
        if (!res.ok) return false;
        const data = await res.json();
        giftHistory = (data.receipts || []).map(r => ({{
          id: String(r.payment_id),
          receipt_id: r.receipt_id,
          paid_at: r.paid_at,
          student_id: r.student_id,
          display_name: r.display_name,
          school: r.school,
          county: r.county,
          school_type: r.school_type,
          amount: r.amount,
          allocations: r.allocations || [],
          remaining_after: r.remaining_after,
        }}));
        renderGiftHistory();
        return true;
      }} catch (e) {{
        return false;
      }}
    }}

    async function refreshStudentFromDb(studentId) {{
      if (!apiOnline) return null;
      try {{
        const res = await fetch(API_BASE + `/api/student/${{studentId}}/arrears`, {{ cache: 'no-store' }});
        if (!res.ok) return null;
        const data = await res.json();
        const s = liveStudent(studentId);
        if (!s) return data;
        s.terms = (data.terms || []).map(t => ({{ ...t }}));
        s.amount = data.amount || 0;
        s.verifiedAt = new Date().toISOString();
        const badge = document.getElementById('verifiedAt');
        if (badge) {{
          badge.style.display = 'block';
          badge.textContent = `Current fee-ledger balance loaded (${{new Date().toLocaleTimeString('en-KE')}}). Gift capped at recorded arrears.`;
        }}
        return data;
      }} catch (e) {{
        return null;
      }}
    }}

    async function postPaymentToDb(studentId, amount, termLabels, expectedOutstanding) {{
      const res = await fetch(API_BASE + '/api/payments', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          student_id: studentId,
          amount,
          term_labels: termLabels,
          expected_outstanding: expectedOutstanding,
          sponsor: 'Portal Sponsor',
        }}),
      }});
      const data = await res.json();
      if (!res.ok) {{
        const err = new Error(data.error || 'Payment failed');
        err.code = data.code;
        err.payload = data;
        throw err;
      }}
      return data.receipt;
    }}

    function receiptNumber(id, paidAt) {{
      const d = new Date(paidAt);
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `EM-${{y}}${{m}}${{day}}-${{String(id).slice(-4).toUpperCase()}}`;
    }}

    function formatWhen(iso) {{
      try {{
        return new Date(iso).toLocaleString('en-KE', {{
          dateStyle: 'medium',
          timeStyle: 'short',
        }});
      }} catch (e) {{
        return iso;
      }}
    }}

    function renderGiftHistory() {{
      historyList.innerHTML = '';
      if (!giftHistory.length) {{
        historyEmpty.classList.remove('hidden');
        historyTotal.textContent = '';
        clearHistoryBtn.style.display = 'none';
        return;
      }}
      historyEmpty.classList.add('hidden');
      clearHistoryBtn.style.display = 'inline';
      const total = giftHistory.reduce((a, g) => a + g.amount, 0);
      historyTotal.textContent = `${{giftHistory.length}} gift${{giftHistory.length === 1 ? '' : 's'}} · Total ${{formatKes(total)}}`;

      giftHistory.forEach(g => {{
        const card = document.createElement('article');
        card.className = 'receipt';
        const allocHtml = (g.allocations || []).map(a =>
          `<li><span>${{a.term_label}}</span><span>${{formatKes(a.amount)}}</span></li>`
        ).join('');
        const remainHtml = g.remaining_after > 0
          ? `<div class="receipt-remain">Still owed after gift: ${{formatKes(g.remaining_after)}}</div>`
          : `<div class="receipt-remain cleared">Fees fully cleared for this student</div>`;
        card.innerHTML = `
          <div class="receipt-top">
            <span class="receipt-id">${{g.receipt_id}}</span>
            <span class="receipt-date">${{formatWhen(g.paid_at)}}</span>
          </div>
          <div class="receipt-top">
            <div class="receipt-who">${{g.display_name}}</div>
            <div class="receipt-amt">${{formatKes(g.amount)}}</div>
          </div>
          <div class="receipt-meta">${{g.school}} · ${{g.county}} · ${{g.school_type}}</div>
          <ul class="receipt-alloc">${{allocHtml}}</ul>
          ${{remainHtml}}
        `;
        historyList.appendChild(card);
      }});
    }}

    function addGiftReceipt(payload) {{
      const id = Math.random().toString(36).slice(2, 10);
      const paidAt = new Date().toISOString();
      const gift = {{
        id,
        receipt_id: receiptNumber(id, paidAt),
        paid_at: paidAt,
        ...payload,
      }};
      giftHistory.unshift(gift);
      saveGiftHistory();
      renderGiftHistory();
      return gift;
    }}

    function loadSavedBalances() {{
      if (apiOnline) return; // live balances come from SQLite
      try {{
        const raw = localStorage.getItem(STORAGE_KEY);
        if (!raw) return;
        const saved = JSON.parse(raw);
        DATA.students.forEach(s => {{
          if (!saved[s.id]) return;
          s.terms = saved[s.id].terms.map(t => ({{ ...t }}));
          s.amount = s.terms.reduce((a, t) => a + t.outstanding, 0);
        }});
        DATA.students = DATA.students.filter(s => s.amount > 0);
        refreshSchoolCounts();
      }} catch (e) {{ /* ignore */ }}
    }}

    function persistBalances() {{
      if (apiOnline) return;
      const out = {{}};
      DATA.students.forEach(s => {{
        out[s.id] = {{ terms: s.terms.map(t => ({{ ...t }})) }};
      }});
      localStorage.setItem(STORAGE_KEY, JSON.stringify(out));
    }}

    function refreshSchoolCounts() {{
      DATA.schools.forEach(sch => {{
        sch.count = DATA.students.filter(s => s.school_id === sch.id).length;
      }});
      DATA.schools = DATA.schools.filter(s => s.count > 0);
      DATA.counties = [...new Set(DATA.schools.map(s => s.county))].sort();
    }}

    loadGiftHistory();
    function formatKes(n) {{
      return 'KES ' + Math.round(n).toLocaleString('en-KE');
    }}
    renderGiftHistory();

    (async () => {{
      await probeApi();
      await loadFreshness();
      if (apiOnline) {{
        await fetchDbReceipts();
      }} else {{
        loadSavedBalances();
        refillCounties();
        renderGiftHistory();
      }}
    }})();

    function refillCounties() {{
      const cur = countySelect.value;
      countySelect.innerHTML = '<option value="">Select a county…</option>';
      DATA.counties.forEach(c => {{
        const opt = document.createElement('option');
        opt.value = c;
        opt.textContent = c;
        countySelect.appendChild(opt);
      }});
      if (DATA.counties.includes(cur)) countySelect.value = cur;
    }}
    refillCounties();

    function schoolsFor(county, type) {{
      return DATA.schools.filter(s =>
        (!county || s.county === county) &&
        (!type || s.type === type)
      );
    }}

    function availableTypes(county) {{
      return new Set(DATA.schools.filter(s => s.county === county).map(s => s.type));
    }}

    function resetFromCounty() {{
      selectedType = null;
      selectedStudent = null;
      typeDay.classList.remove('active');
      typeBoarding.classList.remove('active');
      schoolSelect.innerHTML = '<option value="">Select a school…</option>';
      schoolSelect.disabled = true;
      stepStudents.classList.add('hidden');
      payPanel.classList.remove('visible');
    }}

    function updateTypeButtons(county) {{
      // Always offer Day + Boarding once a county is chosen (catalog has both).
      typeDay.disabled = !county;
      typeBoarding.disabled = !county;
    }}

    function fillSchools() {{
      const county = countySelect.value;
      schoolSelect.innerHTML = '<option value="">Select a school…</option>';
      selectedStudent = null;
      payPanel.classList.remove('visible');
      stepStudents.classList.add('hidden');

      if (!county || !selectedType) {{
        schoolSelect.disabled = true;
        return;
      }}

      const list = schoolsFor(county, selectedType);
      if (!list.length) {{
        schoolSelect.disabled = true;
        schoolSelect.innerHTML = '<option value="">No schools with fee needs in this filter</option>';
        return;
      }}

      list.forEach(s => {{
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.textContent = `${{s.name}} (${{s.count}} students)`;
        schoolSelect.appendChild(opt);
      }});
      schoolSelect.disabled = false;
    }}

    function liveStudent(id) {{
      return DATA.students.find(s => s.id === id);
    }}

    function renderStudents(schoolId) {{
      const list = DATA.students.filter(s => s.school_id === Number(schoolId) && s.amount > 0);
      studentList.innerHTML = '';
      selectedStudent = null;
      payPanel.classList.remove('visible');

      if (!list.length) {{
        studentList.innerHTML = '<p class="empty">No students currently need fee support at this school.</p>';
        return;
      }}

      list.forEach(s => {{
        const termsWithBal = s.terms.filter(t => t.outstanding > 0);
        const termSummary = termsWithBal.map(t => t.term_label.replace(' Term ', ' T')).join(' · ');
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'student';
        btn.innerHTML = `
          <div>
            <div class="name">${{s.display_name}}</div>
            <div class="meta">${{s.school_type}} · Arrears: ${{termSummary || '-'}}</div>
          </div>
          <div class="amount">${{formatKes(s.amount)}}<span>Total owed</span></div>
        `;
        btn.addEventListener('click', () => {{
          document.querySelectorAll('.student').forEach(el => el.classList.remove('selected'));
          btn.classList.add('selected');
          openPayPanel(s.id);
        }});
        studentList.appendChild(btn);
      }});
    }}

    async function openPayPanel(studentId) {{
      await refreshStudentFromDb(studentId);
      const s = liveStudent(studentId);
      if (!s || s.amount <= 0) {{
        payPanel.classList.remove('visible');
        if (schoolSelect.value) renderStudents(schoolSelect.value);
        return;
      }}
      selectedStudent = s;
      document.getElementById('payTitle').textContent = `Keep ${{s.display_name}} in school`;
      document.getElementById('paySub').textContent =
        `${{s.school}} · ${{s.county}} · ${{s.school_type}} · Total owed ${{formatKes(s.amount)}}`
        + (apiOnline ? ' · From fee ledger' : '');
      renderTermRows(s);
      selectTermsPolicy('all');
      amountInput.value = '';
      payErr.classList.remove('show');
      updatePreview();
      payPanel.classList.add('visible');
      payPanel.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }}

    function renderTermRows(s) {{
      termList.innerHTML = '';
      const unpaid = s.terms.filter(t => t.outstanding > 0);
      unpaid.forEach((t, idx) => {{
        const row = document.createElement('label');
        row.className = 'term-row checked';
        const ageHint = idx === 0 ? 'oldest unpaid' : (idx === unpaid.length - 1 ? 'newest' : '');
        row.innerHTML = `
          <input type="checkbox" data-term="${{t.term_label}}" checked />
          <div>
            <div class="t-label">${{t.term_label}}</div>
            ${{ageHint ? `<div class="t-hint">${{ageHint}}</div>` : ''}}
          </div>
          <div class="t-amt">${{formatKes(t.outstanding)}}</div>
        `;
        const cb = row.querySelector('input');
        cb.addEventListener('change', () => {{
          row.classList.toggle('checked', cb.checked);
          updatePreview();
        }});
        termList.appendChild(row);
      }});
    }}

    function selectedTermLabels() {{
      return [...termList.querySelectorAll('input[type=checkbox]:checked')].map(cb => cb.dataset.term);
    }}

    function selectedOutstandingTotal() {{
      if (!selectedStudent) return 0;
      const labels = new Set(selectedTermLabels());
      return selectedStudent.terms
        .filter(t => labels.has(t.term_label) && t.outstanding > 0)
        .reduce((a, t) => a + t.outstanding, 0);
    }}

    function selectTermsPolicy(policy) {{
      if (!selectedStudent) return;
      const unpaid = selectedStudent.terms.filter(t => t.outstanding > 0);
      let want = new Set();
      if (policy === 'all') {{
        unpaid.forEach(t => want.add(t.term_label));
      }} else if (policy === 'oldest') {{
        if (unpaid[0]) want.add(unpaid[0].term_label);
      }} else if (policy === 'current') {{
        const last = unpaid[unpaid.length - 1];
        if (last) want.add(last.term_label);
      }}
      termList.querySelectorAll('input[type=checkbox]').forEach(cb => {{
        cb.checked = want.has(cb.dataset.term);
        cb.closest('.term-row').classList.toggle('checked', cb.checked);
      }});
      updatePreview();
    }}

    function updatePreview() {{
      const sel = selectedOutstandingTotal();
      const amt = Number(amountInput.value);
      if (!sel) {{
        payPreview.textContent = 'Select at least one term.';
        return;
      }}
      if (!amt || amt <= 0) {{
        payPreview.textContent = `Selected arrears: ${{formatKes(sel)}} · Enter any amount up to that (or less).`;
        return;
      }}
      if (amt > sel) {{
        payPreview.textContent = `Gift exceeds selected terms (${{formatKes(sel)}}). Reduce amount or select more terms.`;
        return;
      }}
      payPreview.textContent = `Will apply ${{formatKes(amt)}} to selected terms (oldest first). Remaining on selection: ${{formatKes(sel - amt)}}.`;
    }}

    /** Allocate amount across selected terms, oldest first. Mutates student.terms. */
    function allocatePayment(student, amount, termLabels) {{
      const labelSet = new Set(termLabels);
      const lines = student.terms
        .filter(t => labelSet.has(t.term_label) && t.outstanding > 0)
        .sort((a, b) => (a.academic_year - b.academic_year) || (a.term_number - b.term_number));

      let remaining = amount;
      const allocations = [];
      for (const line of lines) {{
        if (remaining <= 0) break;
        const take = Math.min(remaining, line.outstanding);
        line.outstanding -= take;
        remaining -= take;
        allocations.push({{ term_label: line.term_label, amount: take }});
      }}
      student.amount = student.terms.reduce((a, t) => a + t.outstanding, 0);
      student.terms = student.terms.filter(t => t.outstanding > 0);
      return {{ allocations, leftover: remaining }};
    }}

    countySelect.addEventListener('change', () => {{
      resetFromCounty();
      updateTypeButtons(countySelect.value);
    }});

    [typeDay, typeBoarding].forEach(btn => {{
      btn.addEventListener('click', () => {{
        if (btn.disabled || !countySelect.value) return;
        selectedType = btn.dataset.type;
        typeDay.classList.toggle('active', selectedType === 'Day');
        typeBoarding.classList.toggle('active', selectedType === 'Boarding');
        fillSchools();
      }});
    }});

    schoolSelect.addEventListener('change', (e) => {{
      if (!e.target.value) {{
        stepStudents.classList.add('hidden');
        payPanel.classList.remove('visible');
        return;
      }}
      stepStudents.classList.remove('hidden');
      renderStudents(e.target.value);
      stepStudents.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
    }});

    document.getElementById('chipOldest').addEventListener('click', () => selectTermsPolicy('oldest'));
    document.getElementById('chipAll').addEventListener('click', () => selectTermsPolicy('all'));
    document.getElementById('chipCurrent').addEventListener('click', () => selectTermsPolicy('current'));
    document.getElementById('chipFillSelected').addEventListener('click', () => {{
      const sel = selectedOutstandingTotal();
      if (sel > 0) amountInput.value = sel;
      updatePreview();
    }});
    amountInput.addEventListener('input', updatePreview);

    payBtn.addEventListener('click', async () => {{
      if (!selectedStudent) return;
      payErr.classList.remove('show');
      const labels = selectedTermLabels();
      const amt = Number(amountInput.value);
      const sel = selectedOutstandingTotal();

      if (!labels.length) {{
        payErr.textContent = 'Select at least one term to pay toward.';
        payErr.classList.add('show');
        return;
      }}
      if (!amt || amt <= 0) {{
        payErr.textContent = 'Enter a gift amount in KES.';
        payErr.classList.add('show');
        return;
      }}
      if (amt > sel) {{
        payErr.textContent = `Amount cannot exceed selected arrears (${{formatKes(sel)}}).`;
        payErr.classList.add('show');
        return;
      }}

      payBtn.disabled = true;
      payBtn.textContent = 'Processing…';

      const studentSnapshot = {{
        display_name: selectedStudent.display_name,
        school: selectedStudent.school,
        county: selectedStudent.county,
        school_type: selectedStudent.school_type,
        school_id: selectedStudent.school_id,
        id: selectedStudent.id,
      }};

      try {{
        let gift;
        let allocations;
        let remaining;

        if (apiOnline) {{
          await refreshStudentFromDb(studentSnapshot.id);
          const liveCheck = liveStudent(studentSnapshot.id);
          if (!liveCheck || liveCheck.amount <= 0) {{
            throw new Error('No outstanding arrears remain for this student. Balances were refreshed.');
          }}
          renderTermRows(liveCheck);
          const stillWanted = new Set(labels);
          termList.querySelectorAll('input[type=checkbox]').forEach(cb => {{
            const keep = stillWanted.has(cb.dataset.term);
            cb.checked = keep;
            cb.closest('.term-row').classList.toggle('checked', keep);
          }});
          const freshLabels = selectedTermLabels();
          const freshSel = selectedOutstandingTotal();
          if (!freshLabels.length || freshSel <= 0) {{
            throw new Error('Selected terms are no longer outstanding. Choose again.');
          }}
          if (amt > freshSel) {{
            amountInput.value = freshSel;
            updatePreview();
            throw new Error(
              `Overpayment blocked. Only ${{formatKes(freshSel)}} remains on the selected terms. Amount was updated; click Pay again to confirm.`
            );
          }}
          const receipt = await postPaymentToDb(studentSnapshot.id, amt, freshLabels, freshSel);
          allocations = receipt.allocations || [];
          remaining = receipt.remaining_after;
          const live = liveStudent(studentSnapshot.id);
          if (live) {{
            live.terms = (receipt.terms || []).map(t => ({{ ...t }}));
            live.amount = remaining;
            if (live.amount <= 0) {{
              DATA.students = DATA.students.filter(s => s.id !== live.id);
            }}
          }}
          refreshSchoolCounts();
          gift = {{
            receipt_id: receipt.receipt_id,
            paid_at: receipt.paid_at,
            display_name: receipt.display_name,
            school: receipt.school,
            county: receipt.county,
            school_type: receipt.school_type,
            amount: receipt.amount,
            allocations,
            remaining_after: remaining,
          }};
          await fetchDbReceipts();
          await loadFreshness();
        }} else {{
          await new Promise(r => setTimeout(r, 500));
          const live = liveStudent(studentSnapshot.id);
          const result = allocatePayment(live, amt, labels);
          allocations = result.allocations;
          remaining = live ? live.amount : 0;
          persistBalances();
          refreshSchoolCounts();
          gift = addGiftReceipt({{
            student_id: studentSnapshot.id,
            display_name: studentSnapshot.display_name,
            school: studentSnapshot.school,
            county: studentSnapshot.county,
            school_type: studentSnapshot.school_type,
            amount: amt,
            allocations,
            remaining_after: remaining,
          }});
        }}

        payPanel.classList.remove('visible');
        showScreen('confirm');
        confirmText.textContent =
          `You gave ${{formatKes(amt)}} toward school fees for ${{studentSnapshot.display_name}} at ${{studentSnapshot.school}}.`
          + (apiOnline ? ' Gift applied to the fee ledger and capped at recorded arrears.' : '');
        confirmReceipt.innerHTML = `
          <div class="receipt-top">
            <span class="receipt-id">${{gift.receipt_id}}</span>
            <span class="receipt-date">${{formatWhen(gift.paid_at)}}</span>
          </div>
          <div class="receipt-top">
            <div class="receipt-who">${{gift.display_name}}</div>
            <div class="receipt-amt">${{formatKes(gift.amount)}}</div>
          </div>
          <div class="receipt-meta">${{gift.school}} · ${{gift.county}} · ${{gift.school_type}}</div>
          <ul class="receipt-alloc">
            ${{allocations.map(a => `<li><span>${{a.term_label}}</span><span>${{formatKes(a.amount)}}</span></li>`).join('')}}
          </ul>
          ${{remaining > 0
            ? `<div class="receipt-remain">Still owed: ${{formatKes(remaining)}}</div>`
            : `<div class="receipt-remain cleared">Fully cleared</div>`}}
        `;
        selectedStudent = null;
      }} catch (err) {{
        if (err.code === 'stale_balance' || err.code === 'overpayment') {{
          const p = err.payload || {{}};
          const live = liveStudent(studentSnapshot.id);
          if (live && p.terms) {{
            live.terms = p.terms.map(t => ({{ ...t }}));
            live.amount = p.amount || 0;
            renderTermRows(live);
            selectTermsPolicy('all');
            if (err.code === 'overpayment' && p.available) {{
              amountInput.value = p.available;
            }}
            updatePreview();
          }}
        }}
        payErr.textContent = err.message || 'Payment failed.';
        payErr.classList.add('show');
      }} finally {{
        payBtn.disabled = false;
        payBtn.textContent = 'Pay this amount';
      }}
    }});

    function goHome() {{
      refillCounties();
      countySelect.value = '';
      resetFromCounty();
      updateTypeButtons('');
      showScreen('home');
    }}

    document.getElementById('startSponsorBtn').addEventListener('click', () => {{
      refillCounties();
      countySelect.value = '';
      resetFromCounty();
      updateTypeButtons('');
      showScreen('sponsor');
    }});
    document.getElementById('heroGiftsLink').addEventListener('click', () => {{
      renderGiftHistory();
      showScreen('gifts');
    }});
    document.getElementById('heroFreshLink').addEventListener('click', async () => {{
      await loadFreshness();
      showScreen('freshness');
    }});
    document.getElementById('backFromSponsor').addEventListener('click', goHome);
    document.getElementById('backFromGifts').addEventListener('click', goHome);
    document.getElementById('backFromFresh').addEventListener('click', goHome);

    againBtn.addEventListener('click', () => {{
      refillCounties();
      countySelect.value = '';
      resetFromCounty();
      updateTypeButtons('');
      showScreen('sponsor');
    }});

    document.getElementById('viewGiftsBtn').addEventListener('click', () => {{
      renderGiftHistory();
      showScreen('gifts');
    }});

    clearHistoryBtn.addEventListener('click', () => {{
      if (apiOnline) {{
        window.alert('Gift history is stored in SQLite while the portal server is running. Re-seed with python db/init_db.py to reset demo payments.');
        return;
      }}
      if (!window.confirm('Clear all gift receipts on this device? (Demo only)')) return;
      giftHistory = [];
      saveGiftHistory();
      renderGiftHistory();
    }});

    showScreen('home');
  </script>
</body>
</html>"""


def main() -> None:
    payload = build_payload()
    OUTPUT.write_text(build_html(payload), encoding='utf-8')
    print(f'Sponsor portal saved: {OUTPUT}')
    print(f"Source: {payload['source']}")
    print(f"Counties: {len(payload['counties'])} | Schools: {len(payload['schools'])} | Students: {len(payload['students'])}")
    if payload['students']:
        sample = payload['students'][0]
        print(f"Sample {sample['display_name']}: total {sample['amount']:,} KES across {len(sample['terms'])} term(s)")
    print('Flow: County -> Day/Boarding -> School -> Student -> Terms + amount -> Pay')


if __name__ == '__main__':
    main()
