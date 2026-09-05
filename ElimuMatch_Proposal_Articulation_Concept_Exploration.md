# ElimuMatch: Proposal Articulation and Concept Exploration
### MSBA Capstone · Analytics Opportunity Brief

**Sector.** Education technology with a social-impact focus. ElimuMatch supports targeting, matching, and tracking of educational assistance for secondary school students in Kenya.

**Analytics role.** The platform ranks students by retention risk, explains the drivers of that ranking, recommends an appropriate type of support, and provides operations views that show whether assistance reached the intended fee accounts.

**Related deliverables.** `ElimuMatch_Investor_Brief.docx`; `ElimuMatch_Executive_Pitch.pptx`; `analysis_notebook/ElimuMatch_Analysis.ipynb`; https://jesyldah.github.io/ElimuMatch/

---

### Product summary

**ElimuMatch** connects people and organizations that wish to give with students and schools that require a defined form of support.

| Layer | Role |
|---|---|
| **Helpers (donors)** | Select the type of support (fees, tutoring, health, digital access, or enrichment), then select a location and a student. |
| **Analytics** | Determines who requires support, which type of support is appropriate, why a student was prioritized, and whether assistance was delivered. |
| **Foundations and larger programs** | Identify schools with concentrated fee, health, digital, or academic pressure so that larger resources can be directed accordingly. |

### MVP scope and ambitious vision

ElimuMatch is designed as a multi-channel matching platform for individuals, banks, CSR programs, and foundations. This proof of concept delivers a complete fee-support MVP first. Broader channels and national scale follow the ambitious vision once the fee path is proven on partner data.

| Delivered in this proof of concept | Reserved for later phases |
|---|---|
| Documented synthetic student data grounded in Kenyan secondary patterns | Live partner school student records |
| Retention-risk ranking, explanations, and need-type groupings | Continuous production model operations |
| Multi-channel routing design, visible on the Support Hub | Full donor marketplaces for tutoring, health, and digital support |
| End-to-end fee support path (select location, give, update school fee records) | Live M-Pesa or bank payouts and production authentication |
| ElimuMatch Support Hub and school-need views (HTML demos on GitHub Pages) | National foundation portal and multi-organization rollout |
| Analysis notebook for step-by-step reproduction of the analytics | Additional experimental interfaces |
| Investor brief, executive pitch, and Year-1 cost-benefit analysis | Formal national impact evaluation |

---

# Part 1: Pitch Canvas

## One-sentence value statement

ElimuMatch is a matching and targeting platform that ranks secondary students by retention risk, simplifies fee support for donors, and helps individuals and institutions direct the appropriate type of assistance to the students and schools that need it.

---

## 1. The problem and opportunity

**The challenge comprises two linked gaps.**

1. **Friction for donors.** Many people wish to support a student but lack time to search schools, compare cases, or complete administrative paperwork. Intention often fails to convert into a completed gift.
2. **Uneven allocation.** When support does move, it frequently follows personal networks or the most visible case rather than measured retention risk, and it may not match the true need (fees, tutoring, health, or digital access).

**The opportunity is a single platform that performs several roles.**

1. Match donors to need across fees, tutoring, health, digital access, and enrichment.
2. Reduce giving friction by allowing donors to choose the type of support and then a county, school, and student.
3. Use analytics so that shortlists reflect measured risk and can be explained to staff and partners.
4. Help foundations target schools by aggregating student signals by school and county (fee pressure, health, digital gaps, and academic struggle) so that larger grants are placed where gaps are greatest.

**If nothing changes**

- Intended gifts that are never completed
- Students and families facing fee shocks and dropout
- Schools carrying unpaid term fees
- Banks, CSR teams, and nonprofits relying on form-based screening with limited evidence that awards protected enrollment

**What becomes possible**

Donors filter by location and preference, review a shortlist, and complete a gift. Analytics ranks retention risk, indicates the appropriate type of support, and records fee gifts against verified term balances. The same system can serve individuals, banks and CSR programs, and foundations working at student or school level.

**How analytics changes decisions**

Manual case-finding is replaced by a repeatable sequence: rank students, explain priority, assign the type of support, present fee cases to donors, route non-fee needs to schools and partners, settle fees, and monitor fairness and outcomes.

**Who benefits**

Individual donors, students, schools, operations teams, banks and CSR programs, and foundations that require school-level targeting.

---

## 2. Data and insight

**What powers the idea**

- Documented synthetic student data for proof-of-concept design and demonstration. Partner administrative data is the planned input for a live pilot under agreement.
- A retention-risk model. Logistic Regression was selected because it identified more students who later dropped out than comparable alternatives on the holdout set.
- Explanations of why a student was prioritized.
- Need-type groupings and an intervention guide that separate fee support from tutoring, health, digital access, and enrichment.
- A term-level fee ledger that accepts partial gifts, clears the oldest unpaid term first, and rejects overpayment and outdated balances.
- Operations monitoring, pilot success measures, and a Year-1 cost-benefit case with stated assumptions and scenarios.

**How it works**

1. Rank dropout risk using academic, economic, attendance, and related signals.
2. Show why a student was flagged.
3. Recommend the primary type of support.
4. Route fee-priority students to the donor path and other needs to school and partner queues.
5. Present fee cases on a filterable donor interface.
6. Apply gifts to verified term balances.
7. Monitor gifts, non-fee queues, data freshness, fairness, and, in a live pilot, continued enrollment.

### Multi-channel design

| Primary pressure | Type of support | Typical providers |
|---|---|---|
| Unpaid fees | School fee support | Individuals; bank and CSR fee programs |
| Weak academics | Tutoring | Tutors, NGOs, school programs, CSR |
| Health and absences | Health support | Clinics, nurses, health CSR, partners |
| Device and connectivity | Digital access | Device donors, connectivity partners |
| Broader support needs | Mentoring and enrichment | Mentors, alumni, clubs, partners |

**Product plan**

- Apply the same sequence for every channel: rank, explain, route, match, and track.
- Allow donors to select their preferred type of support.
- Keep schools involved in delivery and safeguarding.
- Enable foundations to act at school level, for example through fee funds, tutoring contracts, or health partnerships where need is concentrated.

**Decision insight for stakeholders**  
Donors can complete support through a simple digital path while allocation remains guided by retention risk and need type rather than personal networks alone. The system matches type of need to type of helper, ranks within each channel, and can aggregate to school level so that foundations direct larger resources to the greatest gaps.

**Advantage over informal or purely manual processes**  
Shortlists are consistent, priorities can be explained, payments are tied to verified term balances, incorrect or obsolete balances are less likely to be funded, and institutions receive school-level views in addition to individual gift paths.

**Relationship to classic bank and CSR form programs**  
Seasonal application programs screen applicants and select recipients in batches. ElimuMatch is complementary. It supports continuous preference-based giving for individuals and provides ranked shortlists and school-level need views for institutions.

---

## 3. Strategic fit, innovation, and timing

**Strategic fit across three audiences**

1. **Individuals.** Complete support for a student quickly within a chosen type of help.
2. **Banks and CSR programs.** Obtain ranked, explainable beneficiary shortlists instead of relying mainly on paper applications.
3. **Foundations.** Identify schools that lack health, digital, tutoring, or fee capacity so that larger investments are better aimed.

**Distinctive contribution**  
A single ranking and routing system supports multiple help channels and serves both student-level matching and school-level targeting.

**Why now**  
Digital giving is established, mobile money is widely used, and transparency expectations are rising. Schools already hold fees, grades, and attendance data, which is sufficient to begin a measured pilot.

**Scale**  
The proof of concept is designed for national coverage. Live rollout begins with a small set of partner schools under agreement and expands after pilot gates clear.

---

## 4. What success looks like

**Success for a donor**  
A time-constrained professional opens the site, selects a county and school of interest, supports a student within a short session, and receives a clear receipt. The organization can show that the student was a priority case, that the payment was applied to the correct term balance, and, after a live pilot, that the student remained enrolled.

**Success for a foundation**  
Program staff see which schools face concentrated health, digital, or tutoring pressure and place resources where the gap is greatest.

**What this proof of concept delivers**  
Retention ranking and routing, an end-to-end fee helper path, Support Hub, Year-1 cost-benefit analysis, investor brief, executive pitch, and a reproducible analysis notebook. The multi-channel marketplace and live payment rails are sequenced after the fee MVP.

**Ambitious vision (beyond the MVP)**  
A higher share of support reaches priority students, administrative friction declines, stay-in-school outcomes are measured, and foundations use school-level need views on ElimuMatch.

**Indicators of success**

| Area | Indicator |
|---|---|
| Helper | Time to complete a gift; share of started gifts that are completed |
| Analytics | Ability of the ranking to identify students who leave; clarity of explanations; fairness review |
| Targeting | Priority students receiving support; non-fee needs remaining with schools and partners |
| Settlement | Clean allocations; overpayments blocked; outdated balances rejected |
| Impact (live) | Next-term or twelve-month enrollment for helped students versus comparable peers |
| Business case | Pilot platform cost relative to targeting gains and avoided-dropout benefits |

---

## 5. Feasibility and responsibility

**Technical feasibility**  
The proof of concept is implemented in Python with a lightweight database and HTML interfaces for the helper portal, Support Hub, and analytics views. Live school data feeds, production authentication, and mobile-money payouts are planned for the partner pilot phase.

**Ethics and transparency**  
Donors see anonymized profiles. Limits of synthetic data are stated explicitly. Staff can review why a student was prioritized. Fairness is assessed. Human approval is required before any live student list is published.

**Responsible operations**  
The fee ledger is authoritative. Unauthorized credit balances are not created. Child-data agreements precede use of real records. Results from synthetic data are presented as proof-of-concept evidence, not as national field results.

---

## 6. The ask

Fund an eight-school Year-1 fee-support pilot (approximately KES 2.0 million in platform cost, excluding pass-through gifts to schools). The ask includes part-time analytics and school-liaison capacity, partner data access under signed agreements, live fee giving with human review before any public student list, and expansion only after pilot results clear stated gates.

**How to review the proof of concept.** Open the live demo at https://jesyldah.github.io/ElimuMatch/, read the investor brief and executive pitch, and use `analysis_notebook/ElimuMatch_Analysis.ipynb` to reproduce the analytics step by step.

---

## Wild card

**Positioning line.** Support that is simple to complete and carefully directed to the students and places that need it.

**Long-term vision.** ElimuMatch becomes a standard channel through which individuals and institutions support secondary school students in Kenya, with low friction for donors and disciplined selection and follow-up for students and schools.

---

# Part 2: Proposal articulation

## Company overview

| | |
|---|---|
| Focus | Education technology and social-impact venture concept |
| What it does | Matching and targeting platform that ranks retention risk; routes fee, tutoring, health, digital, and enrichment support; maintains a fee ledger; provides donor interfaces; and offers school-level views for foundations |
| Problem | Donors lack a low-friction path to give; student needs vary by type; scarce support is often allocated by visibility rather than measured risk; institutional form processes are slow and difficult to audit for enrollment outcomes |
| Scope | This submission delivers the fee-support MVP (analytics, helper path, operations view, and cost-benefit). Multi-channel marketplaces and institutional portals are part of the ambitious vision. The venture concept is set in Kenyan secondary education. Synthetic data is documented and factually grounded for the proof of concept. |

## Team

| | |
|---|---|
| Members | Jesyldah Mwanyamba (founder, analytics, product, and author); Dorine Okello (concept partner and report reviewer) |
| Skills | Analytics and modeling; product interfaces; data and operations metrics; investor brief, pitch, and cost-benefit analysis; early concept validation and submission review |

## Analytics project

| | |
|---|---|
| Summary | Retention ranking that routes need by support type, with an end-to-end fee helper path and fee ledger, plus Support Hub visibility including school resource targets. Wider marketplaces and live partner data follow the pilot roadmap. |
| Solution type | Hybrid proof of concept comprising a risk model, explanations, multi-channel routing design, a built fee giving path and ledger, and the Support Hub |

## Strategic analysis

| | |
|---|---|
| Alignment | Increase completed, well-targeted gifts and improve the likelihood that students remain enrolled |
| Drivers | Mobile money adoption; digital giving habits; fee-related dropout risk; demand for transparent giving; institutional interest in fairer and faster selection |

## Analytics opportunity

| | |
|---|---|
| Opportunity | Provide responsible shortlists for donors and CSR programs; enable school-level targeting for foundations; preserve donor choice of location and support type |
| Data | Proof of concept uses a documented synthetic cohort. The live pilot uses school fees, grades, and attendance under agreement. |
| Improvement | Faster than manual case-finding; better aimed than visibility-based giving; complementary to annual bursary contests |

## Rationale

| | |
|---|---|
| Timing | Friction reduces completed individual gifts. Institutions seek fairer, faster screening and clearer school targeting. |
| Viability | Sector need is documented; published methods provide benchmarks; an end-to-end proof of concept is complete; cost-benefit analysis includes scenarios. |

## Stakeholders and requirements

| | |
|---|---|
| Stakeholders | Individual donors; banks, CSR programs, and foundations (student shortlists and school-level targeting); students; schools; operations |
| Expectations | Speed and a clear support path; ranked lists with explanations; school views by need type; privacy; accurate fee settlement |
| Constraints | Ethics for minors; synthetic data for proof of concept; live payment rails in the partner pilot phase |

## Success criteria

| | |
|---|---|
| Business | High gift completion with low donor effort; institutional use of shortlists; gifts concentrated on priority students |
| Technical | Useful ranking, including identification of students who leave; stable product surfaces; clean fee settlement |
| Impact | Continued enrollment of helped students in a live pilot |

## Scope and schedule

| Scope | Contents |
|---|---|
| **Proof of concept (this submission)** | Risk ranking; explanations; need groups and routing; fee helper path; fee ledger; ElimuMatch Support Hub; analysis notebook; investor brief; executive pitch; cost-benefit analysis; data plan |
| **Year-1 pilot** | Partner school data under agreement; human review; validation on real extracts; live fee giving |
| **Ambitious vision** | Institutional giving on ElimuMatch; nationwide reach; enrolment support; support beyond fees; in-product chatbot; ElimuMatch mobile application |

**Phases.** Research; data and modeling; MVP proof of concept; evaluation and business case; partner pilot; scale decision against stated gates.

## Feasibility

| | |
|---|---|
| Proof of concept | Delivered with current tools and skills |
| Risks | Bias, privacy exposure, and overclaiming synthetic results. Mitigations include explanations, fairness checks, explicit limits, and fee-ledger controls. |

## Wild card

Establish low-friction giving as normal for individuals, ranked shortlists as normal for banks and CSR programs, and school-level targeting as normal for foundations, using one shared ranking and routing system.

---

## Summary

ElimuMatch’s destination is a multi-channel matching platform for secondary school support in Kenya. This submission proves the fee path: ranking and routing, a working helper experience with disciplined settlement, and a Support Hub that already surfaces other channels and school-level targets. Synthetic data grounds the proof of concept. The Year-1 ask is an eight-school fee pilot with explicit go and no-go gates. That is the destination ElimuMatch is built to grow into.
