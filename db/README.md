# Elimu Match DB (SQLite PoC)

Tracks school fees by **academic term** and **category**, with **partial payments** allocated to arrears.

**Full schema pack (for the report appendix):** [`SCHEMA_DOCUMENTATION.md`](SCHEMA_DOCUMENTATION.md) — ERD, data dictionary, relationships, DDL.  
**Interactive HTML (open in browser):** [`schema_dashboard.html`](schema_dashboard.html) — ERD **with columns**, dictionary, views, DDL.  
**DDL file:** [`ddl.sql`](ddl.sql)

## Portal live write-back

```bash
python db/portal_server.py
# open http://127.0.0.1:8765/sponsor_portal.html
```

Gifts `POST /api/payments` → SQLite `payments` + `payment_allocations` + updated `student_term_fees`.
Receipts load from `GET /api/receipts`. Freshness: `GET /api/freshness` (also on portal **Data freshness** screen).
Without the server, the portal falls back to localStorage + embedded freshness snapshot.

## Setup

```bash
python db/init_db.py
```

Creates `db/elimu_match.db` from the synthetic cohort + fee simulation.

## Record a payment (partial OK)

```bash
python db/record_payment.py --student-id 22 --amount 3000
python db/record_payment.py --student-id 22 --amount 5000 --term-label "2026 Term 2" --category tuition
python db/record_payment.py --student-id 22 --show-only
```

**Allocation default:** oldest term first; within a term: tuition → boarding → lunch → activity.

## Useful views

| View | Purpose |
|---|---|
| `v_term_arrears` | Outstanding lines by student / term / category |
| `v_student_fee_summary` | Totals + term1/2/3 arrears columns |
| `v_payment_detail` | Payment → allocation audit trail |
| `v_sponsor_fee_candidates` | Students with outstanding fees (portal feed) |

## Refresh cadence

| Cadence | `refresh_runs.run_type` | What updates |
|---|---|---|
| Termly | `fee_sync` | Fee schedules / balances from schools |
| Weekly / after model run | `risk_rescore` | `student_risk_snapshots` |
| On payment | `payment_import` | Balances via allocations |

PoC is SQLite; same schema maps cleanly to Postgres + SIS/M-Pesa later.
