# ElimuMatch — Concept Exploration
### MSBA Capstone · Analytics Opportunity Brief

**Sector:** EdTech with a social-impact focus — targeting, matching, and tracking educational support in Kenyan secondary schooling.

**Analytics type:** Primarily **predictive** (dropout risk), with **diagnostic** explainability, **light prescriptive** routing, and **descriptive** operations monitoring.

---

### Product in one breath

**ElimuMatch** connects people and organizations who want to help with students and schools that need a specific kind of support.

| Layer | What it does |
|---|---|
| **Helpers** | Choose *how* to help (fees, tutoring, health, digital, enrichment), then place and student. |
| **Analytics** | Decides *who needs what*, *which channel*, *why*, and *whether support worked*. |
| **Foundations** | See *which schools* carry the heaviest health, digital, academic, or fee burdens — and target resources there. |

### Capstone MVP vs product vision

The **product vision** can be wide (many help channels, foundations, banks/CSR). The **Capstone does not deliver the whole product.** It delivers a defined **MVP**:

| In Capstone scope (MVP) | Out of Capstone scope (later) |
|---|---|
| Documented synthetic cohort, factually grounded | Live partner student records |
| Predictive risk model + explanations + personas | Full production MLOps / continuous retraining |
| Intervention routing across channels (design + ops visibility) | Full helper marketplaces for tutoring / health / digital |
| **Fee helper channel end to end** (filters → pay → ledger) | M-Pesa / bank rails, auth, multi-tenant production |
| Ops monitor + early **school resource targets** view (**HTML**) | National foundation portal / multi-org rollout |
| Illustrative Year-1 cost–benefit | Live impact RCT / measured national retention lift |

**Delivery format:** instructor confirmed **HTML dashboards and helper interfaces are fine** for Capstone (Tableau optional, not required).  
**Instructor framing:** ambitious vision is fine; Capstone success = a clear MVP with honest limits — not the entire ElimuMatch roadmap.

---

# Part 1 — Pitch Canvas

## One-sentence value statement

ElimuMatch is an EdTech matching and targeting platform: dropout-risk analytics plus simple helper experiences so people and institutions can support the right students — and the right schools — with the right kind of help.

---

## 1. The problem and opportunity

**The challenge — two linked gaps**

1. **Friction for givers** — Many people want to help a student but lack time to search schools, compare cases, or chase paperwork. Intent often stops there.
2. **Quality of allocation** — When support does move, it may follow visibility or networks rather than who is most likely to leave school — or whether the real need is fees, tutoring, health, or digital access.

**The opportunity — one platform, three jobs**

1. **Match helpers to need** across fees, tutoring, health, digital access, and enrichment.  
2. **Make giving easy** — choose the kind of help, then county / school / student.
3. **Use analytics** so every shortlist is risk-informed and explainable.
4. **Help foundations target schools** — roll student signals up by school and county (health load, digital gaps, academic struggle, fee pressure) so larger grants land where the gap is greatest.

**If nothing changes**

- Goodwill that never becomes a gift  
- Students and families facing fee shocks and dropout  
- Schools carrying unpaid term fees  
- Banks, CSR teams, and nonprofits stuck in form-based screening with little proof that awards protected enrollment  

**What becomes possible**

Helpers filter by place and preference, see a shortlist, and act. Analytics ranks risk, routes the intervention, and settles fee gifts on a proper ledger. The same engine serves **individuals**, **banks / CSR desks**, and **foundations** working at student *or* school level.

**How analytics changes decisions**

Manual case-finding → a repeatable pipeline:  
**score → explain → assign intervention → publish fee cases to helpers / CSR → route non-fee cases to schools and partners → settle fees → monitor fairness and outcomes.**

**Who benefits**

Individual helpers · students · schools · operations teams · banks and CSR programs · foundations that need school-level resource targeting.

---

## 2. Data and insight

**What powers the idea**

- Documented **synthetic cohort** for the Capstone (live partner data under a later agreement)  
- Supervised **retention model** (logistic regression selected for stronger dropout recall; other models compared)  
- **Explainability** — which factors raised or lowered risk  
- **Personas + intervention matrix** — fee support vs tutoring, health, digital, enrichment  
- **Fee ledger** by term — partial payments, oldest-term first, overpayment and stale-balance controls  
- **Operations metrics**, pilot success criteria, and an illustrative Year-1 cost–benefit case  

**How it works**

1. Predict dropout risk from academic, economic, attendance, and related signals  
2. Diagnose why a student is flagged  
3. Prescribe the primary intervention from the matrix  
4. Split the work: fee-priority → helper marketplace; other needs → school / partner queues  
5. Present fee cases on a filterable experience  
6. Execute gifts against verified term arrears  
7. Monitor gifts, non-fee backlogs, freshness, fairness, and — in a live pilot — enrollment persistence  

### Multi-channel design

| If analytics points mainly to… | Channel | Who can help |
|---|---|---|
| Fee pressure / arrears | School fee support | Individuals; bank / CSR fee programs |
| Weak academics | Academic tutoring | Tutors, NGOs, school programs, CSR |
| Health / absences | Health support | Clinics, nurses, health CSR, partners |
| Device / connectivity | Digital access | Device donors, connectivity partners |
| Broader support | Enrichment / mentoring | Mentors, alumni, clubs, partners |

**Product plan**

- Same engine for every channel: predict → explain → route → match → track  
- Helpers choose their lane  
- Schools stay in the loop for delivery and safeguarding  
- Foundations work at **school level** — labs, clinic partnerships, tutoring contracts, fee funds where need clusters  

**What “aha!” moment does this enable?**  
Helping can feel as easy as online checkout — while still being guided by risk and need, not by who you happen to know. And need is not one-size-fits-all: analytics matches **type of need** to **type of helper**, then ranks within each channel — and can roll up to **schools** so foundations aim larger resources where gaps cluster.

**Why better than gut instinct or manual processes?**  
Consistent shortlists; explainable priorities; payment tied to real term balances; less chance of paying the wrong amount or a balance that already changed; school-level views for institutions that fund programs, not only individual gifts.

**Vs classic bank / CSR form programs**  
Those programs screen applicants and pick winners in batch cycles. ElimuMatch is complementary: always-on preference-based giving for individuals, and — for institutions — ranked, explainable candidates plus school heatmaps for foundations.

---

## 3. Strategic fit, innovation, and timing

**Strategic fit — three buyers, one backbone**

1. **Individuals** — help a student quickly, in the lane they choose  
2. **Banks / CSR** — ranked, explainable beneficiaries instead of paper piles  
3. **Foundations** — which schools lack health, digital, tutoring, or fee capacity, so larger investments are aimed well  

**What is distinctive**  
One risk-and-routing engine for a **portfolio of help channels** — student matching *and* school-level targeting.

**Why now**  
Digital giving expectations, mobile money, and pressure for transparency. Schools already hold fees, grades, and attendance — enough to start a pilot.

**Scale**  
National design in the proof of concept; live rollout starts with a small partner-school set under agreement, then expands.

---

## 4. What success looks like

**What would “wow” look like?**  
A busy professional opens the site after work, picks a county and school they care about, supports a student in under a minute, and gets a clear receipt — without calling anyone. Behind that moment, the organization can show the student was priority and high-risk, the payment hit the correct term balance, and (after a real pilot) the student was still enrolled. For a foundation, “wow” is seeing which schools need health, digital, or tutoring capacity — and placing a program where the gap is greatest.

**Near-term Capstone success**  
A working MVP with clear scope: analytics engine + fee helper channel + ops views + cost–benefit — not the full multi-channel marketplace.

**Longer-term product impact** (beyond Capstone)  
Higher share of support reaching priority students · less admin friction · measured persistence · foundations using school-level need views  

**What metrics tell you it is working?**

| Area | Signal |
|---|---|
| Helper | Time to completed gift; completion rate |
| Analytics | Ranking quality (incl. dropout recall); clear explanations; fairness |
| Targeting | Priority students supported; non-fee queues still owned |
| Settlement | Clean allocations; blocked overpayments; stale balances caught |
| Impact (live) | Next-term / 12-month enrollment for helped vs comparable students |
| Business case | Pilot platform cost vs targeting and avoided-dropout benefits |

---

## 5. Feasibility and responsibility

**Capstone feasibility**  
Python · lightweight database · **HTML** helper portal, ops monitor, and analytics dashboard (instructor-confirmed acceptable for Capstone). Live school feeds, authentication, and mobile-money payouts are explicitly **out of Capstone scope**.

**Ethics and explainability**  
Anonymized helper-facing identities · honest limits on synthetic data · explanations for priority · fairness review · human approval before any live student list is published.

**Responsible operations**  
Ledger-authoritative settlement · no invented credit balances · child-data agreements before real records · never present synthetic results as national field evidence.

---

## 6. Ask for this consult

Aligned with instructor guidance:

1. **Synthetic data** is acceptable when factually grounded and limits are stated clearly  
2. **MVP scope** is the Capstone deliverable — the wider ElimuMatch vision is roadmap, not required submission  
3. An illustrative pilot cost–benefit analysis is the right shape for this project  
4. **HTML dashboards / helper interfaces are acceptable** for the Capstone MVP (Tableau optional for exploration, not required)

**Proposed next step:** lock the MVP boundary in the formal Capstone report (what is in / out), then write up analytics + fee channel + ops + cost–benefit.

---

## Wild card

**Line:** Easy to give. Smart about whom — and where — you help.

**Vision:** The default way individuals and institutions support secondary places in Kenya: fast for the giver, rigorous in how students and schools are chosen and followed.

---

# Part 2 — Proposal articulation

## Company overview

| | |
|---|---|
| Focus | EdTech startup / social-impact concept |
| What it does | Matching and targeting platform: dropout-risk analytics; channels for fees, tutoring, health, digital access, enrichment; fee ledger; simple helper experiences; school-level views for foundations |
| Problem | Busy helpers lack an easy path; need comes in many forms; scarce help must be aimed better than visibility alone; CSR forms are slow and hard to audit for persistence |
| Scope | **Capstone = MVP only** (analytics + fee helper channel + ops + CBA). Full multi-channel / foundation product is vision, not Capstone delivery. Fictional org; Kenya secondary grounding; synthetic data factually grounded. |

## Team

| | |
|---|---|
| Members | *[Insert name(s)]* |
| Skills | Analytics and modeling · product interfaces · data and operations metrics · report and cost–benefit |

## Analytics project

| | |
|---|---|
| Summary | Capstone MVP: predictive retention analytics that routes need by channel, with the **fee helper path and ledger proven end to end**, plus ops visibility (including school resource targets). Wider marketplaces and live partner data are roadmap. |
| Solution type | Hybrid analytics PoC: predictive model, explanations, multi-channel routing design, fee marketplace + ledger (built), ops views |

## Strategic analysis

| | |
|---|---|
| Alignment | Maximize completed, well-targeted support and student persistence |
| Drivers | Mobile money · digital habits · fee-related dropout risk · demand for transparent giving · institutional desire to modernize form-based selection |

## Analytics opportunity

| | |
|---|---|
| Opportunity | Automate responsible shortlisting for helpers and CSR; enable school-level targeting for foundations; keep individual preference choice |
| Data | Capstone: synthetic cohort. Live: school fees, grades, and attendance under agreement |
| Improvement | Faster than manual case-finding · smarter than visibility-based giving · complementary to annual application contests |

## Rationale

| | |
|---|---|
| Timing | Friction kills individual giving; institutions want fairer, faster screening and clearer school targeting |
| Viability | Clear sector need · public method benchmarks · working end-to-end PoC · cost–benefit with sensitivity |

## Stakeholders and requirements

| | |
|---|---|
| Stakeholders | Individual helpers · banks / CSR / foundations (student shortlists **and** school-level targeting) · students · schools · operations |
| Expectations | Speed and a clear help lane · ranked explainable lists · **school heatmaps by need type** · privacy · accurate fee settlement |
| Constraints | Ethics for minors · synthetic limits in Capstone · real payment rails later |

## Success criteria

| | |
|---|---|
| Business | High gift completion with low effort · institutional adoption of shortlists · gifts concentrated on analytics-priority students |
| Technical | Useful ranking (incl. dropout recall) · stable product · clean ledger settlement |
| Impact | Persistence of helped students in a live pilot |

## Scope and schedule

| Scope | Contents |
|---|---|
| **Capstone MVP (this submission)** | Risk analytics · explanations · personas and multi-intervention routing · **fee** helper channel · fee ledger · ops dashboards (incl. other channels + school resource targets) · cost–benefit draft · data availability plan |
| Lean next (post-Capstone) | Partner school ingest under MOU · human review · pilot one additional helper channel |
| Ambitious later (product vision) | Mobile money · multi-school pilot · full helper marketplaces · expanded foundation school-targeting · outcome evaluation |

**Phases:** research → data and modeling → **MVP proof of concept** → evaluation and Capstone report. Vision items stay on the roadmap.

## Feasibility

| | |
|---|---|
| Capstone | Feasible with current tools and skills |
| Risks | Bias, privacy, overclaiming synthetic results — managed with explanations, fairness checks, honest limits, and ledger rules |

## Wild card

Make effortless help normal for individuals; ranked shortlists normal for banks and CSR; and school-level targeting normal for foundations — on one shared analytics backbone.

---

## Closing line for discussion

ElimuMatch’s vision is broad; the Capstone delivers a clear MVP: analytics that ranks and routes need, a working fee helper channel with ledger integrity, and ops views that already show other channels and school-level targets — with synthetic data factually grounded and live expansion left for after the Capstone.
