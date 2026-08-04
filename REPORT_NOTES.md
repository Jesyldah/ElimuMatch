# Report Notes — Elimu Match Capstone

Use this checklist when writing the Quantic MSBA (BSAN 590) report and presentation.  
These are clarifications and framing points from the project build — **add them so reviewers see judgment, not just code.**

---

## 1. Project framing (Quantic)

- Capstone deliverable = **consultancy plan + analytics solution / proof of concept** for a real or fictional organization.
- Quantic allows **fictional organizations** and focuses on problem definition, methodology, and business value — not one specific tool.
- Pass thresholds: written project ≥ 3/5; presentation ≥ 2/5.
- Frame Elimu Match as a **PoC**, not a live national system.

**One-liner:**  
*Elimu Match is a proof of concept that ranks students at risk of dropping out and routes sponsors to simple fee-support actions, while schools/ops use richer analytics behind the scenes.*

---

## 2. Synthetic data — what to say (and not say)

**Instructor guidance:** Synthetic data is OK when **factually grounded**. Capstone = defined **MVP**, not the whole product vision.

### Capstone MVP (in scope)
- Documented synthetic cohort, calibrated to known Kenya secondary patterns (fees/indirect costs, SES gradients, attendance–health links)
- Risk model + explanations + intervention routing
- Fee helper channel end to end (portal + term ledger)
- **Streamlit** demo (Helper + Ops + Analytics) for one-click review; HTML dashboards remain as offline backup (**instructor-confirmed OK**; Tableau optional)
- Illustrative cost–benefit + data-availability plan (have / messy / collect later)

### Explicitly out of Capstone scope
- Live partner records, M-Pesa, production auth
- Full tutoring / health / digital helper marketplaces
- National foundation portal / multi-org rollout
- Measured live retention lift (method shown; results wait for a real pilot)

**Paste-ready (scope):**  
> ElimuMatch’s product vision is ambitious by design. For the Capstone we deliberately scope an MVP: predictive retention analytics, multi-channel routing design, a working fee-support helper path with settlement integrity, and operations visibility. We are not claiming to deliver the full multi-channel marketplace in this submission.

### Include
- Data is a **documented synthetic cohort** (`synthetic_data_v2.py`, seed 2026) because partner student records were unavailable (privacy, MOUs, timelines).
- DGP encodes SES gradients, academic linkage, health–attendance links, missingness, and school effects — **backed by factual sector patterns**, not invented from thin air.
- Pipeline is designed to **swap in real records** when a data-sharing agreement exists.
- See also: `DATA_AND_LIMITATIONS.md`.

### Avoid
- “We analyzed Kenyan secondary school retention” without saying data is synthetic.
- Presenting AUC / retention rates as validated field results.
- Promising the full product roadmap as Capstone deliverables.

### Integrity statement (paste-ready)
> All performance metrics and dropout patterns in this capstone are proof-of-concept outputs from a documented synthetic cohort, unless and until replicated on partner data. The value of this submission is the consultancy framework, reproducible pipeline, and intervention design — not empirical claims about a live student population.

---

## 3. Product split (critical for the story)

| Audience | What they see | Artifact |
|---|---|---|
| **Sponsors** | County → Day/Boarding → School → Student → Pay | `sponsor_portal.html` |
| **Elimu Match ops / schools** | KPIs, investigation queue, fee-support progress, freshness | `ops_dashboard.html` |
| **Analysts / report appendix** | EDA, model, SHAP, personas, intervention matrix | `dashboard.html` |

Sponsors should **not** see models, SHAP, 37 features, or personas.  
Ops monitor day-to-day delivery; analytics explain *why* the routing works.

**Demo (preferred):** Streamlit — `python -m streamlit run streamlit_app.py` (or the deployed Cloud URL).  
**Demo (offline HTML):** double-click `OPEN_DEMO.bat` (or `python db/portal_server.py --open`) → http://127.0.0.1:8765/  
HTML files also open offline via relative links; live gifts/ops refresh need the server.  
**API:** `GET /api/ops`  

**Ops panels (beyond KPIs):** term aging · stuck partial pays · school concentration · rejected settlements (`settlement_attempts`) · scoring SLA (14d) · non–fee-support backlog · fee-queue gender/SES mix · **pilot success criteria** · **illustrative impact** (retained × gift; not causal).

### Pilot success criteria (paste-ready)
> A live Elimu Match pilot should be judged on: (1) fee-support queue coverage (share receiving ≥1 gift), (2) scoring + SES/gender fairness checks on a fixed cadence, (3) settlement integrity (no unallocated gifts; overpayments blocked), (4) reduction of aged Term-1 arrears pressure, and (5) **next-term retention** for helped vs matched peers. The PoC ops monitor tracks (1)–(4) live and shows (5) only as an illustrative method demo on synthetic labels.

---

## 4. Sponsor portal — PoC scope

### Enough for PoC
- County → school type (Day/Boarding) → school → anonymized student → **choose term arrears** → **enter any KES amount** (partial OK) → simulated pay → **receipt + gift history**.
- List driven by Intervention Matrix (primary = School Fee Support); balances from fee DB when present.
- Allocation: oldest selected term first; balances + receipts persist in localStorage for the demo.

### Out of scope (say so explicitly)
- Login / accounts / KYC  
- Real M-Pesa or card payments  
- Live school data feeds  
- Receipts to school bank accounts  
- Mobile app  

**Paste-ready:**  
> Authentication and payment processing are out of scope for the PoC and listed as next-phase implementation.

**Paste-ready:**  
> The sponsor PoC demonstrates that donors can support a student in a chosen county and school type in under a minute, while targeting is powered by the retention model and intervention matrix offline. The school catalog includes a sample secondary school in **each of Kenya’s 47 counties** so geographic coverage is national (not limited to a subset of regions).

---

## 5b. Data freshness — how “live” is the PoC?

| Layer | Mode | Cadence |
|---|---|---|
| Fee balances | **Live** (event-driven) | Each gift + termly school sync |
| Risk scores | **Periodic** | Termly / after scoring run (`refresh_runs`) |
| Model retrain | **Periodic** | Each term on new outcomes |
| Cohort | **Illustrative** | Synthetic PoC — not a live MoE feed |

**Demo:** Portal home → **Data freshness** (or `GET /api/freshness`). Ops dashboard Key Insights has the same table.  
**Coverage:** 1,000 students · 47 counties (sample school each) — national *design*, not national *volume*.

**Paste-ready:**  
> Live means the fee ledger and payments. Periodic means risk rescoring logged in `refresh_runs`. Illustrative means a synthetic cohort with 47-county sample schools — ready to swap onto partner data under an MOU.

### Payment integrity (arrears still owed? overpayment?)

**Policy:** the **ledger is authoritative**, not the sponsor screen.

| Risk | PoC control |
|---|---|
| Screen shows arrears that were just paid by someone else | Re-fetch balances before pay; send `expected_outstanding`; DB rejects if changed (`stale_balance`) |
| Sponsor types more than owed | **Overpayment rejected** — never creates a credit balance |
| Two gifts at once | SQLite `BEGIN IMMEDIATE` + row update guards |

Receipt confirms the amount actually applied after verification.

---

## 5. Data scarcity — real-world honesty

Collecting all PoC features in Kenyan schools would be hard. Say that.

### Easy (often already in school systems)
- Age, gender, school  
- Marks / failed subjects  
- Attendance / absences  
- Fee arrears / unpaid balances  

### Hard (surveys / special collection)
- Cash-flow volatility  
- Exact commute km  
- Home digital access  
- Precise SES quintiles  
- Psychosocial support flags  

### Recommendation to include
- **Phase 1 MVP:** fee status, grades, absences, demographics → enough to flag fee support vs tutoring vs attendance follow-up.  
- **Phase 2:** commute (or “walks > 1 hour?”), device access.  
- **Phase 3:** richer household surveys.  

**Paste-ready:**  
> Data scarcity is the constraint, not the algorithm. Elimu Match is designed so school-fee sponsorship can launch on administrative data schools already have (fees, grades, attendance). Richer features improve targeting later; they are not a blocker to the first pilot.

**Proxies:** fee arrears ≈ economic need; absences ≈ health/attendance risk; low marks ≈ tutoring need.

---

## 6. Real deployment scenario (vs PoC)

| PoC | Real |
|---|---|
| Synthetic CSV | School MIS / EMIS / partner Excel |
| Simulated pay | M-Pesa / bank → school fee account |
| Instant labels | Outcomes lag by term/year |
| Static model | Retrain each term; monitor drift |
| No legal layer | MOU, data protection, child safeguarding |

### Real flow (short)
1. MOU + limited fields + anonymization for sponsors  
2. Score risk → persona → Intervention Matrix  
3. Human-in-the-loop ops review/override  
4. Sponsors pay via simple portal  
5. Next term: measure who stayed → retrain → fairness check  

### Risks to mention
- Survey fields missing/noisy  
- Label lag  
- Schools gaming “high risk” lists if funding is tied to them  
- Geographic bias if model trained on one region  
- Payment ops harder than ML  

---

## 7. Features — how we got to 37

**37 = 16 raw + 16 engineered + 5 missing indicators.**

### Dropped (not predictors)
- `student_id` — ID  
- `retained` — **target**  
- `retention_risk_score` — **oracle / leakage** (drop at train time)  
- `dropout_reason` — post-outcome  
- `academic_catchup_status` — near-deterministic from failed subjects  

### Missing indicators (5)
For survey fields with intentional missingness + `any_survey_missing`.

Remind readers: the **original CSV is not 37 columns**; the modeling matrix grew after feature engineering.

---

## 8. Modeling notes

### Objective
Predict `retained` (1/0) so at-risk students can be prioritized for support (especially fees).

### Class imbalance
~86% retained / ~14% dropped → **accuracy alone is misleading**. Prefer AUC + **dropout recall**.

### Selection rule used
Highest test AUC; if models within ~0.015 AUC, prefer higher **dropout recall** (business priority = find students who need help).

### Result to report
- Gradient Boosting ≈ highest AUC (~0.754) but weaker dropout recall (~33%).  
- **Logistic Regression selected** (AUC ~0.753, dropout recall ~67%).  
- Near-tied ranking quality; LR better for intervention flagging.

### Baseline
Majority-class baseline AUC = 0.50 — shows models beat chance.

### Fairness
Report AUC by SES quintile; note weaker separation in high-SES bands (most students retained → little label variance).

---

## 9. SHAP / explainability

- SHAP on selected Logistic Regression.  
- Values oriented so **positive = higher dropout risk** (stakeholder-friendly).  
- Use: global importance, beeswarm, waterfalls (high vs low risk), dependence plots.  

**Talking point:**  
> The model doesn’t just flag students — SHAP shows *why*. Drivers like cash-flow volatility and health burden justify routing to school fee support vs tutoring.

---

## 10. Clustering / risk personas

- K-Means on behavioral features (**not** the retention label).  
- k chosen with elbow + silhouette; prefer interpretable 3–5 personas.  
- Personas found: Health-Constrained, Academic Strugglers, Stable Achievers.  
- Silhouette modest (~0.17) — expected with overlapping risks; frame as **actionable segments**, not perfect separation.  

Personas answer *why / what to do*; the classifier answers *who*.

---

## 11. Intervention Matrix

### Priority scale
| Score | Meaning |
|---|---|
| 0 | Not indicated |
| 1 | Optional |
| 2 | Recommended |
| 3 | Priority |

### Logic
1. Start from **persona × intervention** policy row  
2. Add **signal boosts** (SES, cash-flow, failures, commute, health, digital)  
3. Weight by dropout risk  
4. Rank → primary + secondary recommendation  

### Sponsor link
Only students whose **primary** intervention is **School Fee Support** appear on the sponsor portal.  
Other actions (tutoring, health, transport) go to school/partner channels.

See: `intervention_outputs/INTERVENTION_PLAYBOOK.md`.

---

## 12. Leakage & evaluation hygiene (must mention)

Do **not** train on:
- `retention_risk_score`  
- `dropout_reason`  
- `academic_catchup_status` (optional drop; redundant)  

Preprocessing: median imputation + scaling **fit on train only**.  
Stratified 75/25 split.

---

## 13. Tableau / exploration

**Instructor confirmation:** HTML dashboards are acceptable for the Capstone PoC. Streamlit/Tableau are **not required** — Streamlit is used here to reduce reviewer friction (one URL).

- Primary deliverables: `dashboard.html`, `ops_dashboard.html`, `sponsor_portal.html`  
- Optional: use `tableau_exports/students_exploration.csv` for extra exploration if useful  
- `AVG([Retained Flag])` for retention rates  
- Hide **Model Risk Score (oracle)** from stakeholder views  
- Schools have county + Day/Boarding in `schools_dimension.csv`

---

## 14. Suggested report section map

1. **Problem & client** — retention + fee barriers; Elimu Match PoC  
2. **Data & limitations** — synthetic; why; integrity statement  
3. **EDA** — HTML analytics dashboard charts (Tableau optional)  
4. **Feature engineering** — 16 + 16 + 5 = 37; leakage drops  
5. **Modeling** — baselines, tuning, LR selection rationale  
6. **Explainability** — SHAP  
7. **Personas & Intervention Matrix** — ops logic  
8. **Sponsor experience** — portal PoC; no login/payments  
9. **Real-world feasibility** — data scarcity; MVP fields; next steps  
10. **Recommendations & roadmap** — MOU → pilot → retrain → M-Pesa  

**Cost–benefit (handbook-required):** see [`COST_BENEFIT_ANALYSIS.md`](COST_BENEFIT_ANALYSIS.md) — illustrative Year-1 pilot (~KES 2.0M platform cost; base BCR ≈ 2.6×). Paste §8 recommendation into *Evaluate Business Value: Cost Analysis*.

---

## 15. Database PoC — fees, partial pay, term arrears

SQLite PoC at `db/elimu_match.db` (rebuild: `python db/init_db.py`).

**Schema pack (appendix):** [`db/SCHEMA_DOCUMENTATION.md`](db/SCHEMA_DOCUMENTATION.md) — **ERD** (entity-relationship diagram), data dictionary, FK relationship map, and DDL ([`db/ddl.sql`](db/ddl.sql)).  
**Browse in browser:** open [`db/schema_dashboard.html`](db/schema_dashboard.html) — ERD with **table columns**, dictionary tabs, views, normalization, DDL.

### Why a DB (say in the report)
- CSV snapshots are fine for modeling; **operations need balances that change** when sponsors pay.
- Real schools bill **by term** and accept **partial** payments — the schema mirrors that.

### What it supports
| Need | How |
|---|---|
| Partial payments | Any KES amount; status `unpaid` → `partial` → `paid` |
| Term arrears | `student_term_fees` per student × term × category; views `v_term_arrears`, `v_student_fee_summary` |
| Allocation | Oldest term first; within term: tuition → boarding → lunch → activity |
| Sponsor list | `v_sponsor_fee_candidates` (outstanding + term1/2/3 arrears columns) |
| Regular updates | `refresh_runs` log; see cadence below |

### CLI
```text
python db/init_db.py
python db/record_payment.py --student-id 22 --amount 3000 --sponsor "Demo Sponsor"
python db/record_payment.py --student-id 22 --amount 5000 --term-label "2026 Term 2" --category tuition
python db/record_payment.py --student-id 22 --show-only
```
### Refresh / update cadence (paste-ready)
> **Termly (primary):** import fee schedules and balances from school admin systems into `student_term_fees`; log in `refresh_runs` (`fee_sync`).  
> **Weekly / after scoring runs:** refresh `student_risk_snapshots` from the retention model so the sponsor queue stays current (`risk_rescore`).  
> **Event-driven:** each sponsor payment updates balances immediately via `payment_allocations` (`payment_import`).  
> PoC uses SQLite; production would use Postgres (or school SIS APIs) with the same logical model.

### Out of scope for DB PoC
- Live M-Pesa webhooks  
- Multi-user auth  
- Wiring `sponsor_portal.html` write-back to SQLite — **done via** `python db/portal_server.py` (localhost API); offline file:// falls back to localStorage

**Paste-ready:**  
> The database layer demonstrates that Elimu Match can track fee arrears by academic term, accept partial sponsor gifts, and allocate payments to the oldest outstanding balances — prerequisites for real school reconciliation.

---

## 16. Paste-ready “Next steps” bullets

1. Partner MOU + ethics / child-data safeguards  
2. Pilot on **minimum viable admin data** (fees, grades, attendance)  
3. Human review before publishing students to sponsors  
4. Integrate real payments (e.g. M-Pesa) + school reconciliation via the fee DB  
5. Retrain each term; monitor SES/gender fairness  
6. Expand features only when collection cost is justified  
7. Connect sponsor portal to `v_sponsor_fee_candidates` (live balances)

---

## 17. Key file map (for appendix)

| File | Role |
|---|---|
| `synthetic_data_v2.py` / `elimu_match_data_v4.csv` | Synthetic cohort |
| `feature_engineering.py` / `preprocess_data.py` | Features + train/test |
| `modeling_phase.py` / `modeling_outputs/` | Model selection |
| `shap_analysis.py` / `shap_outputs/` | Explainability |
| `cluster_personas.py` | Risk personas |
| `intervention_matrix.py` | Persona × action policy |
| `kenya_schools.py` | 47-county school catalog (shared) |
| `sponsor_portal.html` | Sponsor PoC |
| `dashboard.html` | Analytics gallery (EDA / model / SHAP) |
| `ops_dashboard.html` | Org ops monitor (KPIs, issues, progress) |
| `db/` (`schema.py`, `ddl.sql`, `init_db.py`, `record_payment.py`) | Fees / partial pay / term arrears |
| `db/SCHEMA_DOCUMENTATION.md` | ERD + data dictionary + relationships |
| `DATA_AND_LIMITATIONS.md` | Full data write-up |
| `COST_BENEFIT_ANALYSIS.md` | Year-1 pilot cost–benefit (report section) |
| `CONCEPT_EXPLORATION_ANSWERS.md` | Filled Concept Exploration / Pitch Canvas + Articulation |
| `Concept_Exploration_Answers_ElimuMatch.docx` | Same answers in Word (for Google Doc copy-paste) |
| `tableau_exports/` | Tableau-ready tables |

---

*Last consolidated for report drafting — keep this file as a checklist; copy sections into the formal Quantic report as needed.*
