# ElimuMatch
## Retention Analytics and Fee-Support Matching for Kenyan Secondary Students

**Status:** Narrative draft for review 
**Live demo:** https://jesyldah.github.io/ElimuMatch/ 
**Code:** https://github.com/Jesyldah/ElimuMatch 

---

<div align="center">

<br/><br/>

# ElimuMatch: Matching Support to Retention Risk

## A Strategic Analysis of Fee-Support Matching for Kenyan Secondary Education

<br/><br/><br/>

**Prepared For:**

Impact Investors, CSR Partners, and Education Foundations

<br/><br/>

**Prepared By:**

*[Insert full name(s)]* 
Business Analytics

<br/>

**Date:** August 2026

<br/><br/><br/>

*Live demo: https://jesyldah.github.io/ElimuMatch/* 
*Repository: https://github.com/Jesyldah/ElimuMatch*

</div>

---

<!--
Word/PDF typesetting notes (delete before submission if desired):
- Center all cover text; title ~28-32 pt bold; subtitle ~14-16 pt regular.
- Generous white space above title and between “Prepared For” / “Prepared By”.
- Do not put course code, tables, or figures on the cover - one clean page, then TOC.
- Footer page number optional (example used “1”).
-->

---

# Table of Contents

1. [Executive Summary](#sec-1) 
2. [Introduction and Background](#sec-2) 
3. [Company Overview](#sec-3) 
4. [Team and Analytics Project](#sec-4) 
5. [Strategic Analysis](#sec-5) 
6. [Analytics Opportunity](#sec-6) 
7. [Rationale](#sec-7) 
8. [Stakeholder and Requirement Analysis](#sec-8) 
9. [Success Criteria](#sec-9) 
10. [Scope and Schedule of Deliverables](#sec-10) 
11. [Data Understanding](#sec-11) 
12. [Data Preparation](#sec-12) 
13. [Exploratory Data Analysis](#sec-13) 
14. [Methods and Frameworks](#sec-14) 
15. [Architect the Solution: Proof of Concept](#sec-15) 
16. [Evaluate Business Value: Cost Analysis](#sec-16) 
17. [Scale Up the POC: Recommendations](#sec-17) 
18. [Reflective Statement(s)](#sec-18) 
19. [References](#sec-19) 
20. [Appendix](#sec-20) 


---

<a id="sec-1"></a>

# 1. Executive Summary

Kenya has expanded secondary access, yet equity, quality, and mid-course retention remain fragile (Glennerster et al., 2011; Childress, 2015). Household cash-flow shocks still turn into fee arrears (Gongera & Okoth, 2013), and schools can wait on delayed external funds merely to keep operating (Adhola et al., 2025). At the same time, helpers who would contribute often never finish a gift, and scarce support too often follows personal networks or the most visible story - not measured dropout risk, and not a clear diagnosis of need type (fees, tutoring, health, digital access, enrichment). Access gains stall into unfinished years; goodwill is misallocated. That is the problem this project set out to address.

The objective was deliberately narrow: design and prove a minimum viable system that ranks secondary students for retention risk, explains drivers for school and partner staff, routes fee-priority cases into a simple helper experience, settles gifts against verified term arrears without inventing balances, and surfaces fairness and integrity metrics for operators - so capital can fund a cautious pilot rather than a national claim built on synthetic metrics alone.

ElimuMatch is the solution: a matching and targeting proof of concept. Behind the wall, a retention model (Logistic Regression, selected for business recall), SHAP explainability, risk personas, and an intervention matrix decide priority and need type. Helpers choose county and school type (Day and Boarding), see an anonymized student with term arrears, give a partial or full amount, and receive a receipt. Operations watch queues, concentration, rejections, data freshness, and pilot KPIs. Sponsor gifts pass through to school fee accounts; they are not platform revenue. Multi-channel design (tutoring, health, digital) remains available for school and partner action, but the MVP helper marketplace is the fee lane only. The synthetic cohort (n = 1,000, seed 2026) and browser demos are open at https://jesyldah.github.io/ElimuMatch/.

Evidence from the held-out synthetic test set supports that design choice without overselling it. Logistic Regression posts AUC near 0.75 and dropout recall near 0.67, preferred over higher-looking boosters under a rule that favors finding leavers when ranking quality is essentially tied; a majority baseline is useless for rescue on a roughly 14% dropout base. Fairness diagnostics show weaker ranking where almost everyone stays (high SES). Settlement rules in the fee ledger block overpayment and stale balances and apply oldest-term-first allocation. The product surface is intentional: helpers never face SHAP beeswarms or a thirty-seven-feature matrix. All numerical performance in this brief is proof-of-concept on synthetic data until partner schools validate it.

On value, an illustrative eight-school Year-1 pilot sized to the PoC has platform cost of about KES 2.0 million for setup and operations (excluding pass-through bursaries). Base quantified benefits - better targeting of the same gift volume, restrained avoided-dropout proxies, and modest ops productivity - total about KES 5.2 million, for a benefit-cost ratio near 2.6. Conservative scenarios sit near break-even; optimistic ones are higher. Operational success is not AUC alone: Section 9 defines fee-queue gift coverage, settlement integrity, scoring freshness, fairness cadence, and next-term retention for helped students versus matched peers.

On that basis, we recommend Year-1 platform funding and partnership for a measured eight-school fee-support pilot. The work is most likely to succeed with signed MOUs and child-safeguarding in place, Tier-1 administrative fields schools already hold (fees, grades, attendance), human review before any live student list is published, real payment rails to school fee accounts, and clear go/no-go criteria at each stage. National scale and multi-channel helper markets should wait until partner-data results - not synthetic benchmarks alone - justify a larger commitment.

The principal risks are synthetic overconfidence, ranking bias by subgroup, settlement or helper UX failure under live load, school data that never arrives, and stigma if risk labels leak into public views. Mitigations already designed include human review, feature ethics (no orphan flags), the product surface split, settlement hard rules, termly fairness packs, and a published “what would change our mind” gate (Section 17). Moving forward requires a legal and partnership gate with school MOUs; a soft pilot that scores and reviews only; live fee gifts with weekly integrity monitoring; a termly scorecard against Section 9; and a board go/no-go before any expansion.

---

<a id="sec-2"></a>

# 2. Introduction and Background

Imagine a busy professional who wants to help a secondary student in Kenya, but not to navigate paper, gossip, or a maze of school offices. Imagine, at the same moment, a school that already knows who is behind on term fees, who is missing class for illness, and who is quietly sinking academically, yet has no simple way to turn that knowledge into targeted help. ElimuMatch is built for that gap: analytics that ranks risk and need, a helper experience that makes a fee gift feel almost as simple as online checkout, and an operations view so partners can see whether the system is honest, fair, and useful.

Kenya’s progress on secondary access is real, but the harder story is what happens after a child has a desk. Research on Kenya’s education system has long argued that expansion of enrolment has not been matched by equal gains in quality and equity (Glennerster et al., 2011; Childress, 2015). Families still face financial volatility, often tied to agriculture and irregular income streams (Gongera & Okoth, 2013). Schools, for their part, sometimes wait on delayed donor or community funds simply to keep daily operations running (Adhola et al., 2025). Against that backdrop, goodwill alone is not enough: many people who would happily support a student never finish a gift, and money that does move often follows personal networks rather than measured risk of dropping out or the real *type* of need (fees, tutoring, health, digital access, or enrichment).

Public statistics that matter for ElimuMatch are less “enrolment ever rose” and more **whether students reach and finish secondary under pressure**. The charts below use recent official and UN-linked sources. They are **sector context**, not model scores.

**Figure 1.** Estimated completion still falls from near-universal primary levels to roughly **half by upper secondary** (approx. 2024 estimates) - the mid-course attrition zone ElimuMatch is built to address.

![Figure 1. Kenya completion funnel](report_figures/ext_02_kenya_completion_funnel.png)

*Source:* Author chart from UNESCO IICBA (2025) Kenya education data brief estimates (midpoints of reported girl/boy rates). *Note:* Sector context only.

**Figure 2.** Official secondary enrolment rose to about **4.32 million by 2024** (latest year in KNBS *Economic Survey 2025*; full-year **2025** national enrolment is not in that release) - a larger in-school population means more students for whom fee shocks, health absence, and academic stall can still force exit.

![Figure 2. Kenya secondary enrolment 2020-2024](report_figures/ext_03_kenya_access_progress.png)

*Source:* Author chart from Kenya National Bureau of Statistics (2025), *Economic Survey 2025* (Popular Version), education - secondary enrolment (‘000), series **2020-2024**. *Note:* 2024 is provisional in KNBS tables; **2025 national total not released** in that survey. Enrolment growth ≠ completed retention. Sector context only.



ElimuMatch sits between those two frustrations. For helpers, it offers a short path from place (county and school) to a specific fee gift. For the venture and partner schools, it offers a risk model, explainable drivers, multi-channel intervention logic, and a ledger that treats term arrears as a serious operational reality rather than a spreadsheet afterthought. This report does not claim to ship the entire product vision. It presents a finished minimum viable product - predictive retention analytics, a working fee-support channel with settlement integrity, browser-based operations and analytics demos, and a transparent Year-1 pilot business case - and asks for capital only where that MVP can be stress-tested in the field.

On the analytics side, the venture uses a fully synthetic but factually grounded cohort of one thousand students, generated with a fixed seed so the work is reproducible - then runs validation and EDA, feature engineering, preprocessing, a retention model, and intervention routing (score risk, explain drivers, assign support, publish fee priority, settle gifts, and monitor fairness). The selected model is Logistic Regression (test AUC near 0.75, dropout recall near 0.67), chosen after comparing stronger-looking boosters that ranked well on AUC but missed too many students who later dropped out. Around the model sit SHAP explanations, risk personas, and an intervention matrix that distinguishes school-fee support from tutoring, health, digital, and enrichment pathways. On the product side, a helper portal and fee ledger support partial payments, oldest-term-first allocation, and hard stops on overpayment or stale balances. The live demos at https://jesyldah.github.io/ElimuMatch/ let a partner open the story without an install ritual. The claim of this work is not “we measured Kenya.” The claim is that the pipeline, product split, and settlement design are ready for a cautious pilot on partner data under proper governance.

---

<a id="sec-3"></a>

# 3. Company Overview

ElimuMatch is a fictional EdTech and social-impact organization built to force real design choices without impersonating a live ministry system. Its mission is simple to state and demanding to execute. It exists so that individuals and institutions can support secondary students and schools with the *right kind of help*, guided by retention risk rather than by chance encounters.

**Figure 3.** Three product layers: helpers stay simple; operations and analytics absorb complexity.

![Figure 3. Product layers](report_figures/01_product_layers.png)

The organization thinks in three layers of experience. Helpers, in the MVP, choose a place and complete a fee gift that lands against verified term arrears. Analytics decide who needs what and why, using models and routing logic that never appear on the helper screen. Operations and foundation-facing views roll signals up to schools and counties, so larger programs can see where fee pressure, health burden, tutoring need, or digital gaps cluster. Geography in the proof of concept is national by design: the school catalog covers all forty-seven counties, with Day and Boarding options for each, while the student volume of the synthetic cohort remains a manageable one thousand records. That combination is intentional. National *design* is not the same as national *census volume*.

Money follows the same clarity. Sponsor fee gifts are treated as pass-through capital to school fee accounts, not as ElimuMatch revenue. The organization earns its keep by targeting, trust, and the ability to show that support reached priority cases cleanly. The wider product vision includes helper markets for tutoring and health, multi-tenant foundation portals, and mobile-money rails; those remain on the roadmap. What ships today is the backbone that makes that roadmap fundable rather than a wishlist.

---

<a id="sec-4"></a>

# 4. Team and Analytics Project

## 3.1 Team

ElimuMatch was built by *[insert name(s)]*, combining analytics, product design, and written evaluation. In practice that meant the synthetic data generation and model pipeline; helper, ops, and analytics interfaces; a fee ledger that respects real school billing patterns; Kenya-relevant research and open statistical context; and a business case written so numbers stay transparent rather than theatrical. Where a single founder wears many hats, the venture deliberately reuses shared artifacts: one school catalog for both data and portal, one intervention matrix for both ops and matching, one integrity language for both demos and this brief.

## 3.2 The analytics project in narrative form

The problem is dual. First, helpers who care often never convert intention into a completed gift. Second, scarce support is easily misallocated when visibility and paperwork dominate over risk and need type. Theory gives language for the student-side risk: Tinto’s (1993) emphasis on academic and social integration, and Adelman’s (1999/2006) academic-momentum tradition that makes prior trajectory, including GPA trend and failure, a serious signal rather than decoration. Applied to secondary Kenya, those traditions sit beside cash-flow shocks, commute friction, health-related absence, and weak protective support.

The solution is therefore hybrid. It is predictive where it ranks who is at risk of leaving, diagnostic where SHAP shows why, lightly prescriptive where an intervention matrix routes fee support versus school or partner actions, and descriptive where ops monitors gifts, concentration, fairness cadence, and data freshness. The outcome for an investor or partner is a working story they can click: open the Pages demo for the helper path, ops health, and analytics evidence; optionally run a local live ledger if settlement writing must be seen on SQLite rather than offline demo mode.

---

<a id="sec-5"></a>

# 5. Strategic Analysis

If ElimuMatch is only “another model,” it fails. Its strategy starts from how the environment already works. Kenya’s system has improved access, yet equity and quality still lag, which means a platform that only celebrates enrolment numbers misses the real mission (Glennerster et al., 2011; Childress, 2015). Households often rely on volatile income, so a static snapshot of “poor versus rich” understates the shock that can push a student out mid-year (Gongera & Okoth, 2013). Schools navigating delayed external funding learn to improvise; latency in money is itself operational risk (Adhola et al., 2025). Policy pressure for high transition between levels raises the cost of late discovery of attrition risk (Orodho, 2020). Meanwhile helpers live in a world of digital payments and short attention, and Kenya’s open-data and transparency agenda (including KODI / KNBS framing) makes black-box ranking politically and ethically weak.

ElimuMatch’s strategic fit is one analytics backbone serving three kinds of buyers, without forcing all three into the MVP UI. Individuals want a fast, preference-based gift. Banks and CSR desks want ranked, explainable shortlists instead of opaque batches. Foundations want school-level pictures of need, not only one student at a time. The MVP proves the shared engine on the fee channel, while ops surfaces already hint at the multi-channel future by showing non-fee backlogs and school resource targets.

Relative to substitutes, the platform is not romantic about charity as currently practiced. Manual case-finding is slow and uneven. Visibility-based giving rewards the story that travels farthest, not necessarily the risk that is highest. Annual application contests matter, but they are complementary to always-on preference giving and a ledger trail that can explain what happened after the gift, not only who won a form process. The map below places that choice for funders.

**Figure 4.** Perceptual map of substitutes versus ElimuMatch (illustrative positioning for CSR and impact funders).

![Figure 4. Perceptual map](report_figures/09_perceptual_map.png)

*Reading the map.* The upper-right is where impact capital should prefer platforms to sit: gifts that are simple for helpers *and* prioritized by explained retention risk and need type. Personal and campaign giving sit low on systematic targeting - generous, but uneven. Annual bursary contests can screen carefully, yet high form friction and seasonal cadence limit continuous preference gifts. ElimuMatch’s MVP claims only the fee lane of that upper-right zone; multi-channel school and partner routing remain on the ops side. Seasonal bursaries and ElimuMatch are **complements**, not rivals: one is often a formal award process; the other is always-on matching with a settlement trail.

---

<a id="sec-6"></a>

# 6. Analytics Opportunity

The analytics opportunity is less “predict something novel” and more “replace a decision culture.” Today many allocation decisions still reduce to who knows whom, who is in the office, or who files on time. ElimuMatch rewrites that into a loop an organization can defend.

**Figure 5.** Defensible decision loop from risk score to monitored outcomes (also the product architecture spine: score → route → gift → monitor).

![Figure 5. Matching loop](report_figures/02_matching_loop.png)

That loop opens several concrete opportunities. Helpers can complete gifts with geographic preference without being shown internal model complexity. Ops can watch whether gifts concentrate on a few schools, whether term arrears are ageing, and whether scoring is getting stale. Institutions can later use the same engine for shortlists and for school-targeting. The feature design does not claim to invent education data science from thin air. It borrows proven families of predictors from student-performance and dropout machine-learning literature (Cortez & Silva, 2008; Realinho et al., 2021), then adapts them to Kenyan secondary constraints and to a three-layer data dictionary that keeps money fields in the ledger rather than smuggling them into the only story the model can tell.

---

<a id="sec-7"></a>

# 7. Rationale

There is a practical reason to build this now, and a theoretical reason to build it this way. Practically, retention fragility and financial pressure are documented sector problems; modern analytics tooling is mature enough to demonstrate matching without pretending production payment rails already exist; browser-based product demos are sufficient for a fundable proof of concept; and an end-to-end fee path with transparent assumptions yields a base-case benefit-cost story worth defending. Theoretically, integration and momentum ideas justify including belonging, academic trajectory, and barriers rather than treating dropout as random noise. Ethically, the venture refuses to treat sensitive demographic labels such as orphan status as convenient predictors, refuses overclaim on synthetic results, and insists on human review before any live student list is published. Scope discipline is itself part of the rationale: an ambitious product vision remains the horizon, while success for this raise is a finished MVP with known limits and a clear pilot plan.

---

<a id="sec-8"></a>

# 8. Stakeholder and Requirement Analysis

Every design choice in ElimuMatch is really a choice about *who is allowed to see what* - the same product split shown in Figure 3, restated as stakeholder requirements rather than another diagram.

The helper is a time-poor adult who may care about a particular county or school type. Their requirement is speed, clarity, and dignity: select place, see an anonymized student with arrears by term, give a partial or full amount, receive a receipt. They are not a data scientist. Showing them SHAP beeswarms or a thirty-seven-feature matrix would be both confusing and operationally dangerous. Schools and ElimuMatch operations want the opposite density: investigation queues, pilot criteria, concentration risk, rejected settlements, and data freshness. Analysts and leadership want to know whether the ranking engine earns trust. Students and families want support without stigma; anonymized display and careful feature ethics matter more to them than dashboard aesthetics. Future banks, CSR desks, and foundations care about fair shortlists and school-level targeting, which the design anticipates even when the MVP UI does not yet fully build their portal.

Requirements fall into several voices. Functionally, the system must predict retention risk, explain priority, assign interventions, settle fee gifts against term arrears, and expose operational health. Governance demands human-in-the-loop review before any real list is made public. Ethical requirements bar orphan flags as model inputs, insist on MOU protections for minors in any live pilot, and forbid presenting synthetic AUC as national truth. Technically, the ledger is authoritative over whatever a helper’s screen once displayed. Constraints for the current proof of concept are explicit: no production authentication, no live M-Pesa rails, and no full tutoring or health marketplaces masquerading as finished deliverables.

### Ethics, privacy, bias, and stakeholder impact

ElimuMatch is meant to allocate *support*, never to exclude, shame, or deny enrolment based on a risk score. That purpose constraint is non-negotiable. Practical safeguards include:

| Risk | Stakeholder impact | Safeguard in design |
|---|---|---|
| **Protected-attribute proxies** (e.g. orphan status as a convenient “need” flag) | Stigma, bias, unfair channeling | Orphan status **excluded** from model features; need expressed via SES and behavioral proxies |
| **Stigma if helpers see “high risk” labels** | Harm to student dignity | Helper UI is **anonymized** and action-framed; SHAP/model detail stays in analytics/ops |
| **Minors’ data and misuse** | Legal and moral harm | Live pilot requires **MOU**, data-protection clauses, child safeguarding, and **human review** before publish |
| **Synthetic metrics sold as national truth** | Misled capital and policy | Report and demos state **PoC / synthetic** limits; scale gated on pilot KPIs |
| **Unequal ranking quality by SES** | High-SES groups hard to separate | Fairness by SES quintile reported; termly fairness reviews required |
| **School gaming high-risk lists for funds** | Distorted incentives | Ops concentration monitoring; review queues; settlement only against verified arrears |
| **Settlement error as trust collapse** | Donor and school harm | No overpay, no stale pay, oldest-term-first, ledger authority over screen cache |

These controls do not remove residual model risk. They define a duty of care appropriate to education and CSR capital: explainable, reviewable, and limited in claim.

---

<a id="sec-9"></a>

# 9. Success Criteria

Success has two horizons, and they must not be confused.

For *this proof of concept and investor brief*, success means a leakage-safe model with a documented business selection rule; a fee path and ledger that work; demos that open without an ordeal; and integrity language that makes synthetic data and cost assumptions unmistakable. One public Pages link and a reproducible repository are part of that definition, because a venture that cannot be inspected is only rhetoric.

For a *live pilot after this brief*, success is operational and measured. The organization should raise fee-queue gift coverage so that more priority students actually receive at least one gift. Scoring and fairness checks by SES and gender should run on a fixed cadence rather than occasional inspiration. Settlement must stay clean: no unallocated money, no overpayments inventing credit balances. Aged Term-1 arrears pressure should decline as gifts are allocated with oldest-term logic. Finally, next-term retention for helped students versus matched peers must be measured on real outcomes. The ops monitor can already display method for those ideas; only a live pilot can convert the retention comparison from illustrative method into measured result. We are careful not to pretend synthetic labels have already proven causal impact.

### Pilot success metrics (targets, not synthetic claims)

| Metric | Why it matters | PoC baseline (synthetic / design) | Pilot Year-1 target | Owner |
|---|---|---|---|---|
| **Fee-queue gift coverage** | Priority students should actually receive support, not only a rank | Queue design live; gift volume illustrative | ≥ **40%** of fee-primary queue receives ≥1 meaningful gift | Ops / school liaison |
| **Settlement integrity** | Trust dies if money mis-allocates | Ledger enforces reject on overpay / stale | **0** successful overpays; under **2%** rejected gifts after helper fix | Platform + finance ops |
| **Oldest-term clearance** | Fee pressure ages; Term-1 should not rot | Oldest-term-first rule engineered | Share of gifts applying to Term-1 first ≥ **70%** when Term-1 arrears exist | Platform |
| **Scoring freshness** | Stale risk scores mis-route help | Periodic scoring concept | Rescore within **14 days** of each term start (or after major MIS extract) | Analytics lead |
| **Fairness cadence** | Ranking must not quietly fail subgroups | SES AUC gap diagnosed on synthetic holdout | Document gender + SES fairness review **each term**; escalate if AUC gap widens without cause | Analytics + governance |
| **Next-term retention (helped vs peers)** | Proves impact beyond AUC theater | Not measurable on synthetic “gifts” | Define matched peers; report retention **delta** (no causal claim without design) | Ops + research partner |
| **Human review gate** | Minors and false priority | Required in design; not live production auth | **100%** public queue cases reviewed before first live publish | Ops case review |
| **Platform budget adherence** | Capital discipline | Illustrative stack ≈ KES 2.0M | Year-1 platform spend within **±10%** of approved budget (ex-bursary) | Founder / finance |

Targets are directional pilot commitments. They are intentionally more ambitious on process integrity than on claim of causal dropout prevention, because process is what the organization can control in Year 1.

---

<a id="sec-10"></a>

# 10. Scope and Schedule of Deliverables

The MVP scope is intentionally a finished slice of a larger story. In scope are the documented synthetic data generating process and its calibration narrative; the feature dictionary and thirty-seven-column modeling matrix; modeling, SHAP, personas, and the intervention matrix; the SQLite fee ledger; the helper, ops, analytics, and schema HTML experiences; GitHub Pages as the share surface; Year-1 cost-benefit and social-value framing; and this report. Out of scope, with equal intention, are live ministry feeds, production authentication, real mobile-money settlement, full non-fee helper marketplaces, multi-tenant national portals, and claims of causal retention lift from randomized live trials.

**Figure 6.** Scale only after earned gates - PoC → MOU → pilot → expansion (this gate sequence is the scale narrative for the rest of the report).

![Figure 6. Pilot roadmap](report_figures/07_pilot_roadmap.png)

Work moved through a professional engagement arc: research grounding (Kenyan literature, open data context, education ML benchmarks), data and modeling, MVP proof of concept build, then evaluation, cost analysis, and this investor-facing brief. Later phases lean first into partner school MOUs and administrative data, then into one additional channel, then (much later) payment rails and broader foundation tooling. This report refuses to narrate those later phases as if they were already delivered.

---

<a id="sec-11"></a>

# 11. Data Understanding

## Why the cohort is synthetic, and why that is not an excuse

Partner student records were unavailable in development for the reasons any serious education venture should respect: minors’ privacy, data-sharing agreements, and timelines that do not wait on academic calendars. The project therefore built a fully synthetic cohort of one thousand students through `synthetic_data_v2.py` (seed 2026) into `elimu_match_data_v4.csv`. “Synthetic” here does not mean “invented for convenience without shape.” The data generating process encodes SES gradients, conditional barriers, academic linkage, health-driven absences, intentional missingness on survey-like fields, and a retention outcome near eighty-six percent retained, consistent with a world where most students stay but attrition is still serious for targeting. Distributions were oriented using Kenyan structural context of the sort discussed in open statistical sources and sector reporting: household-size order of magnitude near national averages, retention and transition pressure as orientation for prevalence, commute distances that reflect rural and peri-urban friction, poverty and nutrition as reasons certain features matter, not as copied microdata from a single school.

The deeper limitations of this choice must be spoken aloud, because they are part of data understanding rather than footnotes. Relationships in synthetic data are cleaner than in messy school ledgers and can flatter model separability. Unobserved shocks such as family relocation, school closure, or sudden fee crises are absent. Support-program variables in the generator can co-move with SES, which creates endogeneity risk if one pretends coefficients are pure causal effects. Median later imputation is a PoC convenience, not a production missing-data theory. The model has not been externally validated on partner administrative records. Results belong to the parameterization of this cohort and should not be treated as portable truth across every region and school type. Ethics still hold: risk scores are for *support allocation*, never for exclusion, shaming, or denying enrolment. Fuller discussion lives in `DATA_AND_LIMITATIONS.md`; this chapter carries the same spine into the main narrative.

| **Assumption / limitation** | **Mitigation for the organization** |
|---|---|
| Synthetic relationships flatter separability | Treat metrics as design proof; retrain and re-threshold on school extracts before public publish |
| Unobserved shocks (closure, relocation, sudden fee crisis) absent | Human review + school liaison override; never fully automate enrolment decisions |
| Support variables co-move with SES (endogeneity) | Do not sell coefficients as pure causal effects; use ranking for prioritization, not blame |
| Survey fields often missing | Missingness indicators in model; Tier-3 surveys only for high-risk slice |
| No external validation yet | Soft pilot (internal scoring first); gate public lists on partner holdout performance |
| National catalog ≠ national volume | Start with eight schools; expand only after KPI gates |
| Median imputation is a PoC shortcut | Production: school-informed missing-data policy and termly audit |

## A three-layer dictionary, because money and risk must not pretend to be the same thing

The product layers in Figure 3 already draw a visibility wall for helpers versus staff. Underneath that wall, the *data* design deliberately separates three books of record, so money and risk never pretend to be the same thing. **Layer 1** trains retention risk from demographics, household strain and income shocks, access barriers, academic momentum, health and absences, belonging, and protective support - not from fee arrears alone. **Layer 2** is what helpers filter on: county, school, and preference-oriented signals that help a giver choose place and type. **Layer 3** is the ledger: term fee arrears, sponsorship status, last payment, human review flags - the authoritative books operations and settlement use. Fee arrears deliberately stay operational rather than becoming the model’s only definition of poverty. Orphan status is not allowed as a model feature, out of concern for bias and dignity; need is expressed through socioeconomic and behavioral proxies instead. The data generating process’s latent risk oracle and post-outcome dropout reasons are never trained as predictors. Catch-up status, which sits near-deterministic with failures, is dropped for leakage and redundancy hygiene in preprocessing even when design notes discuss it as a conceptual sensitivity feature.

This separation is how ElimuMatch avoids the dumb story “owe money therefore drop out” and the cruel story “use protected status as a convenient flag.” At gift time, a helper still sees arrears, because arrears are real school books. The ranking of who reaches the fee queue comes from risk and intervention matrix logic built on Layer 1, not from a model that merely predicts unpaid balances.

### Data dictionary snapshot (not the full field list)

| Field / family | Layer | Role in the product | In retention model? | Pilot collection tier |
|---|---|---|---|---|
| Age at enrolment, gender | 1 | Demographics & fairness slice | Yes (with care) | Tier 1 (registers) |
| SES / resource dilution, cash-flow volatility | 1 | Household economic pressure | Yes | Tier 1–2 (proxy or short form) |
| Commute barrier, digital access, school feeding | 1 | Access & barriers | Yes | Tier 2 (school/ward map) |
| GPA trend, failed subjects, STEM signal | 1 | Academic momentum | Yes | Tier 1 (marks register) |
| Chronic health risk, health-related absences | 1 | Health & attendance pressure | Yes | Tier 1 absences; health note as available |
| Social integration, psychosocial support access | 1 | Belonging & buffers | Yes (missingness-aware) | Tier 3 (high-risk slice / survey) |
| County, school name / type (Day, Boarding) | 2 | Helper place filters | No (UI filter only) | Tier 1 (catalog) |
| Term fee arrears by category, gifts, allocations | 3 | Settlement books helpers and ops use | No (ops only) | Tier 1 (bursar / school books) |
| Human review flag, last payment timestamp | 3 | Trust & publish gate | No | Tier 1 (ops workflow) |

*How to read.* Layer 1 ranks who is at risk and why. Layer 2 is how helpers choose *place*. Layer 3 settles money against real arrears (and is not used as model input). Sixteen core Layer-1 predictors expand to thirty-seven modeling columns after engineering (indices, interactions, missingness flags). Orphan status, the synthetic risk oracle, post-outcome dropout reason, and catch-up status are omitted from this table because they are excluded or dropped by design (dignity, leakage, or redundancy). Full field documentation lives in `Data dic.docx` and exploration exports under `tableau_exports/data_dictionary.csv`; the database surface is browseable via `db/schema_dashboard.html`.

## Dynamic pressure and real-world collection realism

Retention is not only a fixed “poor household” label. Cash-flow volatility, learning gaps that require catch-up, and psychosocial support access are framed as retention-sensitivity ideas: shocks and buffers that change mid-year. In a live school, collecting every idealized field for every child is fantasy. A tiered acquisition strategy is therefore part of the data plan. Tier 1 administrative data (age, gender, marks and failures, GPA trend, absences) is usually already in registers or EMIS. Tier 2 institutional mapping (commute proxies, school feeding, school environment) can often be assigned once by school or ward. Tier 3 survey fields (precise income dynamics, psychosocial access, home digital access) are expensive and should be reserved for the top risk slice, or replaced with geospatial and asset-based proxies. That is how the venture stays ambitious in design without being naïve about teachers’ time.

---

<a id="sec-12"></a>

# 12. Data Preparation

Preparation is where the project either keeps its promises on leakage or quietly cheats. The pipeline excludes student identifiers as features, treats retention as the sole target, drops the oracle retention risk score used only to generate outcomes, drops post-outcome dropout reason, and drops academic catch-up status as redundant with failure counts. Fee payment fields remain off the modeling matrix. What remains is expanded deliberately: sixteen core predictors become thirty-seven modeling columns after engineering indices, interactions, and five missingness indicators that respect the fact that survey-like fields intentionally go missing (slightly more often at lower SES). The original CSV is therefore not “a 37-column dataset”; engineering creates the matrix the model sees.

**Figure 7.** Engineered-feature correlations after preparation (collinearity is expected and intentional among indices).

![Figure 7. Engineered feature correlations](visualizations/05_engineered_feature_correlations.png)

Training hygiene follows ordinary but non-negotiable practice. The split is stratified seventy-five / twenty-five. Median imputation and scaling are fit on train only. Class weighting and evaluation prioritize recall for students who drop out, because the business cost of missing an at-risk student is higher than the vanity of accuracy on a mostly retained population.

A second preparation story exists for operations. Modeling can live in CSV; gifts cannot. The SQLite proof of concept, rebuilt through `python db/init_db.py`, materializes schools, students, term fees by category, payments, allocations, risk snapshots, and a refresh log. Freshness is conceptualized honestly rather than sold as perpetual magic: fee balances are live when gifts post and when termly school syncs arrive; risk scores are periodic after scoring runs; model retrain is termly when outcomes lag; the modeling cohort itself remains illustrative synthetic data, not a Ministry of Education feed.

---

<a id="sec-13"></a>

# 13. Exploratory Data Analysis

This section shows what the synthetic cohort implies for product design - **what is visible in the data (finding)** and **what the organization should do (so what)** - before methods and modeling.

Exploratory analysis is not a separate academic exercise; it teaches why later modeling choices are rational. Roughly fourteen percent of the synthetic cohort drops out, which means a majority-class guess is already accurate-looking and completely useless for rescue.

**Figure 8.** Lower socioeconomic status coincides with lower retention - so fee and multi-barrier support must prioritize the bottom of the SES ladder.

![Figure 8. Retention by SES](visualizations/02_retention_by_ses.png)

*So what?* **Finding:** retention falls across lower SES quintiles. **Action:** treat fee-support targeting as an equity instrument, not only an accuracy exercise; expect weaker model separation among high-SES students where nearly everyone stays (see fairness section).

Health burden, absences, academic failure, and economic volatility co-travel, which is why personas later feel like recognizable groups rather than arbitrary clusters.

**Figure 9.** Health and economic pressure co-travel - interventions cannot be “fees only” for every high-risk student.

![Figure 9. Risk landscape scatter](visualizations/06_risk_landscape_scatter.png)

*So what?* **Finding:** risk dimensions cluster rather than acting independently. **Action:** keep multi-channel routing (health, tutoring, digital) in ops design even when the MVP helper path is fee-only.

Missingness is real enough on survey fields that the pipeline cannot pretend every row is pristine.

**Figure 10.** Survey fields go missing more often at lower SES - imputation and missingness flags are product requirements, not polish.

![Figure 10. Missingness by SES](visualizations/04_missingness_by_ses.png)

*So what?* **Finding:** missingness is structured, not random noise. **Action:** pilot data collection should start with Tier-1 registers and missingness-aware features, not a complete survey of every child.

On the operational side of the synthetic ledger, the fee-support primary queue sits on the order of a few hundred students from the thousand, with a smaller high-risk-plus-arrears investigation set. Term ageing, gift concentration, and settlement attempts become legible as organizational risks, not only as row counts. Those ops numbers are illustrative ledger statistics for a proof of concept. They are not ministry publications. The analytics dashboard at https://jesyldah.github.io/ElimuMatch/ remains the visual companion to this chapter.

---

<a id="sec-14"></a>

# 14. Methods and Frameworks

This section justifies *how* retention risk is scored and routed - and ends with what those choices mean for money and product ownership. Readers who want only the business conclusion can take: **rank with recall-aware models, explain with SHAP behind the wall, and settle fee gifts without inventing balances.**

The project follows a CRISP-DM arc in spirit even when the folders are more pragmatic: business understanding of Kenya’s retention and equity problem; data understanding of synthetic design and dictionary layers; preparation against leakage; modeling under a business selection rule; evaluation through metrics, SHAP, fairness, and cost narrative; and deployment as demos plus a ledger path rather than a fantasy of production already complete.

Predictive modeling asks a simple question that is hard to answer well: will this student remain enrolled? Training aims to rank students so fee support and other channels can prioritize. Feature families were informed by prior education machine learning (including Cortez & Silva’s student performance tradition and later dropout and success tasks such as Realinho et al., 2021) and by Kenya-focused reading on volatility and access. Candidate models included a majority baseline, Logistic Regression, Random Forest, and Histogram Gradient Boosting. The selection rule was deliberate. Highest test AUC wins when the field is clear; if models sit within about 0.015 AUC of each other, higher dropout recall wins, because an intervention organization is hurt more by missing a student who leaves than by a slightly prettier ranking curve.

### Error trade-offs (why recall is the business metric)

| Error type | What happens | Business cost |
|---|---|---|
| **False negative** (miss a student who drops) | No priority, no gift path, silent exit | High: retention failure the system was built to prevent |
| **False positive** (flag retained student) | Review time and possible gift competition | Medium: staff load and scarce gift budget if unchecked |
| **Majority baseline “accuracy”** | Predict everyone retained | Vanity metric; zero rescue |

Thresholds in a live pilot should be set with ops capacity (how many cases human review can clear per week), not only maximum AUC.

**Figure 11.** When AUC is nearly tied, choose Logistic Regression - it catches roughly twice as many dropouts as gradient boosting on this holdout.

![Figure 11. Selection rule](report_figures/08_selection_rule.png)

*So what?* **Finding:** LR dropout recall ≈ 0.67 vs ≈ 0.33 for boosting at similar AUC. **Action:** deploy LR for ranking; keep trees as challengers for termly re-bake.

Under that rule Logistic Regression was selected. On the holdout set it posts an AUC near 0.753 and dropout recall near 0.667. Gradient Boosting edges AUC slightly higher but catches only about a third of dropouts. Random Forest looks accurate because it hugs the retained majority and almost ignores dropouts. The majority baseline shows chance AUC at 0.5.

**Figure 12.** Holdout panel: accuracy alone would have wrongly crowned models that ignore dropouts.

![Figure 12. Modeling metrics panel](visualizations/25_modeling_metrics_panel.png)

**Figure 13.** ROC curves confirm discriminative ability - but AUC is only half of the selection rule.

![Figure 13. Modeling ROC curves](visualizations/21_modeling_roc.png)

Fairness by SES quintile shows weaker separation where retention is already nearly universal. Class imbalance is not a footnote; it is the reason accuracy was never allowed to become the hero metric.

**Figure 14.** Ranking is weaker in high-SES slices - monitor fairness termly or capital will silently fail the people who still drop out.

![Figure 14. Fairness by SES](visualizations/24_modeling_fairness_ses.png)

*So what?* **Finding:** AUC falls where almost everyone stays. **Action:** report stratified metrics; do not interpret a single national AUC as fair performance.

Explainability uses SHAP so that positive contributions align with higher dropout risk in stakeholder conversation. Global importance surfaces health risk and burden, academic interactions with SES, belonging and barriers, absences, and cash-flow volatility. Those explanations stay on the analytics surface. Helpers get a human reason framed for action, not a graduate seminar.

**Figure 15.** Health, academic×SES, and barriers lead global SHAP importance - so fee help alone cannot be the full theory of change.

![Figure 15. SHAP global importance](visualizations/31_shap_global_importance.png)

*So what?* **Finding:** chronic health and multi-barrier signals dominate. **Action:** surface non-fee needs on ops/school channels; keep SHAP off the helper screen.

**Figure 16.** SHAP beeswarm: driver effects vary across students - priority is local, not one-size-fits-all.

![Figure 16. SHAP beeswarm](visualizations/32_shap_beeswarm.png)

Beyond ranking, K-Means on behavioral features (not on the retention label) produces risk personas that suggest *what kind* of story a student is living: academic struggle, health constraint, relative stability.

**Figure 17.** Personas separate *kinds* of need - routing quality depends on this label as much as on risk score.

![Figure 17. Persona radar](visualizations/17_persona_radar.png)

An intervention matrix then scores actions from not-indicated to priority by combining persona policy, signal boosts, and dropout risk. Only students whose primary intervention is school fee support enter the helper portal queue. Other primaries remain design and ops objects for school and partner channels, which is an intentional product decision: the MVP proves one complete helper marketplace rather than four unfinished ones.

**Figure 18.** Intervention intensity differs by need type - MVP exposes only the fee-primary lane to helpers.

![Figure 18. Intervention matrix](visualizations/38_intervention_matrix_heatmap.png)

**Figure 19.** A few hundred fee-primary cases form a manageable queue out of one thousand - scope is pilot-sized by construction.

![Figure 19. Fee support priority](visualizations/19_fee_support_priority.png)

Finally, settlement algorithms are treated as method, not plumbing. Oldest selected term first, category order within a term, transactional locks, overpayment rejection, and stale-balance rejection matter because trust dies when money lands wrongly. Machine learning that cannot settle cleanly is half a product.

---

<a id="sec-15"></a>

# 15. Architect the Solution: Proof of Concept

Architecture is easiest to understand as a day in the life of a piece of support.

A calibrated synthetic student record (later, a Tier-1 school extract) enters feature engineering and scoring. The model and personas feed an intervention matrix. Non-fee recommendations surface for school and partner attention. Fee-priority students appear on a helper portal that filters by county and school type, including both Day and Boarding schools in every county. The helper chooses a student, selects term arrears, enters an amount, and pays. In a live local demo the ledger immediately reallocates; on GitHub Pages the gift is a personal offline demonstration so partners can feel the story without sharing a cloud database. Operations watches KPIs, pilot success panels, concentration, rejections, and freshness. Analytics tells the analytical origin story behind the routing. That end-to-end path is the same decision loop shown in Figure 5 - score, explain, assign, publish fee priority, settle, and monitor - now treated as product architecture rather than a second diagram.

**Figure 20.** Cohort profile used by demos and models (one-thousand student PoC).

![Figure 20. Cohort overview](visualizations/01_cohort_overview.png)

The demos that carry that narrative are open without ceremony at https://jesyldah.github.io/ElimuMatch/. The helper surface is `sponsor_portal.html`, operations is `ops_dashboard.html`, analytics is `dashboard.html`, and schema documentation lives under `db/schema_dashboard.html`. Technology choices are intentionally modest and pilot-appropriate: Python for science and pipelines, SQLite for the fee books, static HTML for the product faces so a stakeholder can open the stack in any browser, and GitHub for reproducibility. Optional Streamlit work remains experimental; the primary share path is the HTML site.

Settlement policy is where architecture earns moral weight. If a screen is stale because another gift just posted, the database rejects rather than invents a credit. If a helper types more than remains on the selected terms, overpayment is blocked. Concurrent writes are locked. Those rules sound technical; they are how the organization avoids proving that clever models are undone by careless money.

What the proof of concept demonstrates is not national implementation. It demonstrates that risk-informed matching, ethical feature design, multi-layer data architecture, an end-to-end fee path, and operational governance hooks can coexist in a package an investor or partner can open today.

---

<a id="sec-16"></a>

# 16. Evaluate Business Value: Cost Analysis

A social venture that only reports AUC has not finished its job. ElimuMatch’s money story is therefore told both as a transparent Year-1 platform cost-benefit case (full assumption stack in `COST_BENEFIT_ANALYSIS.md`) and in Social Return language that suits CSR audiences without pretending to produce audited P&L.

> **Integrity note.** Cost and benefit figures below are **illustrative** for a one-year pilot sized to the PoC cohort logic (~1,000 students / ~280 fee-support recommendations). They are not empirical results from a live Kenyan school system. The purpose is to show how ElimuMatch creates value and under what assumptions a pilot clears a positive case.

Value is framed along a triple line. Economically, keeping a student in school protects human capital, which the case models with modest, explicit proxies rather than cinematic lifetime earnings fantasies. Operationally, better targeting means the same donor shillings do more retention-relevant work, and staff time is spent on ranked queues rather than ad hoc lists. Socially, explainable ranking is a fairness instrument relative to network-based awards.

**Figure 21.** Illustrative Year-1 pilot platform cost versus base quantified benefit (bursaries pass through).

![Figure 21. Year-1 economics](report_figures/06_year1_economics.png)

### Year-1 pilot economics (self-contained base case)

**Pilot definition:** 8 partner secondary schools; ~800-1,000 students scored; fee-primary queue on the order of ~200-280 students; 12-month horizon; live payment rails replace simulated pay.

| Line | Base Year-1 (KES) | Notes |
|---|---:|---|
| Setup (MOU/ethics, platform harden, school onboarding) | 1,020,000 | Fixed / one-time |
| Operating (analyst, liaison, hosting, refresh, contingency) | 966,000 | Annualized |
| **Total platform cost (ex-bursary)** | **≈ 1,986,000** | Sponsor gifts are **not** org revenue or org opex |
| Targeting lift (same gift pool better allocated) | 1,000,000 | 25% of illustrative KES 4.0M gift volume |
| Avoided-dropout proxy (outcome benefit) | 4,000,000 | ~20 avoided dropouts × KES 200,000 Year-1 proxy |
| Ops productivity (ranked queue vs ad hoc) | 150,000 | ~0.25 FTE equivalent |
| **Quantified benefits (base)** | **≈ 5,150,000** | Excludes full pass-through value of clearing KES 4.0M fees |
| **Benefit-cost ratio (base)** | **≈ 2.6** | Conservative scenario near break-even; optimistic higher |

### Scenario analysis (do not treat one number as truth)

All amounts are **estimates / assumptions**, not observed Kenyan cash flows. Platform cost is held near **KES 2.0M**. Benefits move with targeting lift and count of avoided dropouts (see `COST_BENEFIT_ANALYSIS.md`).

| Scenario | Quantified benefits (KES) | Platform cost (KES) | Net (KES) | BCR | What it assumes |
|---|---:|---:|---:|---:|---|
| **Conservative** | ≈ 1.8M | ≈ 2.0M | ≈ **−0.2M** | ≈ **0.9×** | Weaker targeting lift; ~8 avoided dropouts |
| **Base** | ≈ 5.15M | ≈ 2.0M | ≈ **+3.2M** | ≈ **2.6×** | 25% targeting lift; ~20 avoided dropouts |
| **Optimistic** | ≈ 10.8M | ≈ 2.0M | ≈ **+8.8M** | ≈ **5.4×** | Stronger lift; ~36 avoided dropouts |

*Reading.* The pilot is **not free-money guaranteed**. Under conservative outcomes it is roughly break-even on platform cost alone; under base assumptions it clears a healthy surplus. That is why Section 9 operational metrics - not synthetic AUC - are the go/no-go language for funders.

Pass-through fee clearance (the KES 4.0M of gifts themselves) benefits schools and households even while it never appears as ElimuMatch profit. Sensitivity is dominated by the **count of avoided dropouts**: modest undercounts bring the case near break-even, which is exactly why the pilot success metrics in Section 9 exist - capital should re-decide after measured outcomes, not synthetic AUC theater.

The recommendation is therefore not “scale nationally tomorrow.” It is to fund an eight-school pilot near the platform cost above, measure fee-queue coverage, settlement integrity, scoring SLA, fairness cadence, and next-term retention, and only then decide how much of the product vision deserves further capital.

---

<a id="sec-17"></a>

# 17. Scale Up the POC: Recommendations

This section turns evidence into **ordered actions** - with owners and measures - then states what would reverse the recommendation. Investment only unlocks the next gate when the prior one clears; that sequence is the same road map in Figure 6 (Now → MOU gate → pilot → scale if earned).

### Prioritized recommendations (impact vs effort)

| Rank | Recommendation | Expected value | Feasibility | Urgency | Risk if skipped |
|---|---|---|---|---|---|
| **1** | Sign MOUs + DP/safeguarding before any live student data | Unlocks lawful pilot | High if schools engaged | Critical | Legal/ethical shutdown |
| **2** | Soft pilot: score + human review, **no public list** until quality gate | Protects dignity & trust | High on Tier-1 data | High | Stigma / bad first impression |
| **3** | Live fee lane with settlement hard rules + M-Pesa/bank rails | Donor conversion + school cash | Medium (payments integration) | High | Trust breaks permanently |
| **4** | Weekly/termly ops scorecard (Section 9 metrics) | Go/no-go discipline | High with RACI staffing | High | Capital without learning |
| **5** | Termly model retrain + fairness pack | Durable ranking quality | Medium (0.4 FTE analyst) | Medium | Silent bias / drift |
| **6** | Expand schools / add one non-fee channel **only after gates** | Scale leverage | Low until pilot clears | Low until Year-1 | Premature scale, brand risk |

Impact rises on rows 1-4; effort spikes on payments and school onboarding - so the sequence is legal → soft pilot → live fee → measure → *then* expand.

### Recommendation logic chains

For each major recommendation: **evidence → insight → action → owner → expected impact → measurement**.

**R1 - Legal and ethical gate** 
- *Evidence:* Minors; no production auth/DP rails in PoC. 
- *Insight:* Capital without MOUs is not ambitious; it is reckless. 
- *Action:* Sign MOUs, data-protection clauses, child safeguarding with 8 schools. 
- *Owner:* Founder / MD + legal + school liaison. 
- *Expected impact:* Permission to touch real extracts; funder confidence. 
- *Measure:* 8 signed packs before first MIS load (Phase 0).

**R2 - Soft pilot before public lists** 
- *Evidence:* Synthetic flattery risk; human review requirement. 
- *Insight:* Rankings can prioritize; they cannot absolve review. 
- *Action:* Internal scoring only; case review 100% of queue candidates before publish. 
- *Owner:* Ops case review + school liaison. 
- *Expected impact:* Fewer false priorities and dignity harms. 
- *Measure:* 100% review rate (Section 9); zero public publish of unreviewed IDs.

**R3 - Live fee gifts with settlement law** 
- *Evidence:* Trust dies on overpay/stale balances; PoC proves rules. 
- *Insight:* ML without settlement is half a product. 
- *Action:* Turn on payment rails; keep oldest-term-first, no overpay, reject stale. 
- *Owner:* Finance ops + platform + payment vendor. 
- *Expected impact:* Clear Term arrears for priority students; donor receipts. 
- *Measure:* 0 successful overpays; under 2% unresolved rejects; ≥40% queue coverage.

**R4 - Measure what synthetic data cannot prove** 
- *Evidence:* Avoided-dropout benefit dominates BCR sensitivity. 
- *Insight:* Finance story is a hypothesis until retention is observed. 
- *Action:* Termly scorecard + matched-peer retention report; restate BCR on real gifts. 
- *Owner:* Ops + analytics; board for go/no-go. 
- *Expected impact:* Evidence-based continue / kill / pivot. 
- *Measure:* Section 9 dashboard complete each term; board gate after Year-1.

**R5 - Expand only after gates** 
- *Evidence:* Conservative BCR near break-even; multi-channel unfinished by design. 
- *Insight:* Breadth is a reward for integrity, not a launch-day promise. 
- *Action:* Add schools or one new helper channel only after KPI clear. 
- *Owner:* Funders + founder board. 
- *Expected impact:* Controlled scale without brand blow-ups. 
- *Measure:* Explicit go/no-go memo against Section 9 targets.

### Roles and ownership (RACI-style)

| Workstream | Accountable (A) | Responsible (R) | Consulted (C) | Informed (I) |
|---|---|---|---|---|
| School MOUs, DP & safeguarding | Founder / MD | Legal counsel + school liaison | School heads, boards | Funders, staff |
| MIS fee / grade / attendance extracts | School liaison lead | School data clerks | Analytics lead | Funders |
| Model rescoring & fairness pack | Analytics lead | Data/ML analyst (0.4 FTE) | Ops review | Leadership, funders |
| Human review of public queue | Ops case review (0.5 FTE) | School liaison | Analytics | Helpers (indirect) |
| Helper portal & settlement rules | Product / engineering | Platform contractor | Finance/ops | Funders |
| Payment rails (M-Pesa/bank to fees) | Finance ops | Payment vendor + platform | Schools, legal | Helpers |
| Pilot KPI dashboard & term report | Ops + analytics | Ops lead | Funders | Schools |
| Go / no-go on expansion | Funders + founder board | Founder | All leads | Public claims only after gate |

**Adoption / change management.** Schools will supply Tier-1 extracts and join case review; helpers keep using a **simple gift UI** (no training as data scientists); ops staff need training on the ops dashboard, reject codes, and review protocol (school onboarding pack in setup budget). Process change is “ranked queue + human gate” replacing ad hoc lists - not a new theory of education.

### Implementation phases (practical roadmap)

| Phase | Timing | Outcomes | Resources (indicative) |
|---|---|---|---|
| **0. Gate legal** | Months 0-2 | Signed MOUs (8 schools); DP & safeguarding; ethics review complete | Legal/advisory within setup budget (~KES 250k line) |
| **1. Data & harden** | Months 1-4 | Tier-1 extracts live; platform auth/backup; payment stub→live path | Setup + contractor; school training line |
| **2. Soft pilot** | Term 1 | Internal scoring + human review only; no public student list until quality gate | Ops liaison + analyst |
| **3. Live fee gifts** | Terms 1-2 | Helpers gift live; settlement integrity tracked weekly; concentration alerts | Full opex footprint |
| **4. Measure** | End of year / each term | Scorecard vs Section 9 metrics; retention delta table; fairness pack | Analyst + ops termly refresh line |
| **5. Scale decision** | After Year-1 review | Expand schools / add one non-fee channel **only if** KPI gates clear | Separate capital ask |

### Monitoring after deployment

- **Weekly:** settlement rejects, gift concentration by school, broken balances 
- **Termly:** rescoring, fairness by SES/gender, fee-queue coverage, Term-1 ageing 
- **Annually:** full BCR restatement on *observed* (not synthetic) retention and gift volumes; board go/no-go 

Governance is part of product design: **data ownership** remains with schools under MOU; ElimuMatch processes extracts under purpose limitation (support allocation); **access** separates helper (anonymized gift UI), ops (queues, rejects), and analytics (full features/SHAP); **update cadence** is termly for models and live for fees; **escalation** if AUC by SES collapses, concentration spikes, or retention delta is non-positive for two terms is a board review (pause public lists; root-cause before more capital).

In the real world, synthetic CSVs become school extracts; simulated pay becomes mobile money or bank settlement to fee accounts; labels lag by term; scores drift and must be monitored; and public demo gifts that live offline become authenticated systems with privacy controls. This proof of concept is the rehearsal that makes those differences visible before money and reputations are on the line.

### What would change our mind

The pilot recommendation should be **revised or paused** if any of the following occur:

| Trigger | Revision |
|---|---|
| Partner holdout **dropout recall falls below ~0.40** after retrain on real admin fields with honest labeling | Replace or re-threshold model before public gift lists; do not claim PoC AUC ports |
| Fairness review shows **systematic under-ranking of a protected group** that human review cannot correct | Pause auto-publish; redesign features / review policy with schools |
| Settlement reject rate stays **above ~10%** after helper UX fixes | Fix ledger/UX before scaling helpers; capital may still fund integrity work |
| **Next-term retention** for helped students is **no better** (and not explained by selection bias) for two terms | Pivot theory of change (e.g. more health/tutoring capacity) or kill fee-lane expansion |
| Schools **cannot** deliver Tier-1 extracts on time for two consecutive terms | Shrink pilot or move to thinner campus footprint; do not pretend platform alone solves data voids |
| Conservative financial restatement on *observed* gifts still yields **net less than zero for two years** with high process integrity | Reassess platform cost structure or exit gracefully - mission is impact per shilling spent |

**Investment ask (pilot stage):** approve Year-1 platform ops for an eight-school pilot (**≈ KES 2.0M** platform cost, excluding pass-through bursaries), fund the roles above (part-time analytics + school liaison), unlock partner data under MOU, run the fee channel live with human review, and open a Series-appropriate or program-scale decision **only after** the Section 9 pilot scorecard clears - and only while the triggers above remain quiet.

---

<a id="sec-18"></a>

# 18. Reflective Statement(s)

*[Personalize before final submission. Starter narrative for individual contribution reflection:]*

Building ElimuMatch changed how I understand early-stage product work. The temptation is always to invent more surface: more channels, more dashboards, more claims. What actually earned seriousness was the opposite discipline: saying no to unfinished marketplaces, keeping helpers free of model clutter, admitting synthetic limits in plain language, and treating settlement rules as moral method rather than afterthought.

Research into Kenyan retention made the problem feel less like a contest dataset and more like a lived pressure of fees, distance, health, and equity gaps. Conversations about data collection tiers made the opposite point: a perfect sixteen-field survey for every student is a beautiful way to fail on the ground. The tiered strategy and the three-layer dictionary are my answers to that tension.

Selecting Logistic Regression over a slightly prettier booster was also a reflection point. For an intervention organization, missing a student who leaves is a different sin than slightly weaker AUC. Publishing the work on GitHub Pages completed the product lesson: access is part of integrity. A brilliant package that a partner cannot open is not a fundable company; it is a performance.

---

<a id="sec-19"></a>

# 19. References

*[Verify years, DOIs, and page details against source documents before final submission. Chicago author-date style as required.]*

Adhola, F., Ochola, J., & Tikoko, B. (2025). Relationship between donor funding and school operations in public secondary schools in Nakuru County, Kenya. *Editon Consortium Journal of Curriculum and Educational Studies, 7*(1), 1-15.

Adelman, C. (2006). *The toolbox revisited: Paths to degree completion from high school through college.* U.S. Department of Education.

Basch, C. E. (2011). Healthier students are better learners: A missing link in school reforms to close the achievement gap. *[confirm full venue]*.

Childress, M. (2015). Dynamics of education in Kenya: From school access to equity and quality. KERD.

Cortez, P., & Silva, A. (2008). Using data mining to predict secondary school student performance. In *Proceedings of the 5th Future Business Technology Conference* (UCI Student Performance dataset).

Glennerster, R., Kremer, M., Mbiti, I., & Takavarasha, K. (2011). Access and quality in the Kenyan education system: A review of the progress, challenges and potential solutions.

Gongera, E., & Okoth, N. O. (2013). Alternative sources of financing secondary school education in the rural counties of Kenya: A case study of Kisii County, Kenya. *Journal of Education and Practice, 4*(17), 78-85.

Jesyldah. (2026). *ElimuMatch* repository and Pages demo. https://github.com/Jesyldah/ElimuMatch ; https://jesyldah.github.io/ElimuMatch/

Kenya National Bureau of Statistics / Kenya Data Portal. (n.d.). Kenya Open Data resources. https://kenya.opendataforafrica.org/

Lundberg, S. M., & Lee, S.-I. (2017). A unified approach to interpreting model predictions. *Advances in Neural Information Processing Systems*.

Orodho, A. J. (2020). Implementation of the 100% Transition Policy in public secondary schools in Kenya. *[confirm full citation]*.

Quantic School of Business and Technology. (2025). *MSBA Capstone Handbook: Designing Analytics Solutions: From Strategy to Proof of Concept* (BSAN 590).

Realinho, V., et al. (2021). Predict students’ dropout and academic success (UCI dataset and related documentation).

Tarus, C. B. K. (2020). De-stigmatizing teenage motherhood: The re-entry policy implementation in Kenya. *International Journal of Research and Innovation in Social Science, 4*(2), 1-7.

Tinto, V. (1993). *Leaving college: Rethinking the causes and cures of student attrition* (2nd ed.). University of Chicago Press.

RELI Africa. 2020. *Study on the Status of Secondary Education in Kenya* (abridged version). https://reliafrica.org/wp-content/uploads/2024/02/Status-of-Secondary-School-Education-Abridged-Version-2020.pdf

UNESCO International Institute for Capacity Building in Africa (IICBA). 2025. *Kenya education data brief* (Data Brief 2025-20). https://www.iicba.unesco.org/

Forum for African Women Educationalists (FAWE). n.d. *Transitions from primary to secondary school and into higher education and work: girls’ expectations and experiences in Kenya*. ERIC ED658302. https://files.eric.ed.gov/fulltext/ED658302.pdf

Republic of Kenya. 2019b. Basic education statistical booklet / related MoE statistical series (as cited in RELI Africa 2020).

Republic of Kenya. 2021. Education statistical releases / annual education statistics (as cited in FAWE / ERIC ED658302).

World Bank. n.d. *World Bank Open Data* education indicators for Kenya (UNESCO Institute for Statistics series). https://data.worldbank.org/. Accessed August 2026.

Kenya National Bureau of Statistics (KNBS). 2025. *Economic Survey 2025* (Popular Version). https://www.knbs.or.ke/

Government of Kenya, Kenya National Bureau of Statistics, UNICEF, and UNFPA. 2023/24. *Situation Analysis of Kenyan Adolescents*. UNICEF Kenya. https://www.unicef.org/kenya/


---

<a id="sec-20"></a>

# 20. Appendix

The appendix remains deliberately denser: places for numbers, paths, and technical reproduction that would slow the main narrative.

## A. Key links and internal documents

The live demos open at https://jesyldah.github.io/ElimuMatch/. Source code is at https://github.com/Jesyldah/ElimuMatch. Start instructions live in `START_HERE.md`. Full data and limitation prose is in `DATA_AND_LIMITATIONS.md`. Cost-benefit tables are expanded in `COST_BENEFIT_ANALYSIS.md`. Concept exploration answers are in `CONCEPT_EXPLORATION_ANSWERS.md`. Engineering notes appear in `REPORT_NOTES.md`. Source materials for dictionary, research, and calibration notes include `Data dic.docx`, `Research.docx`, and `Other relevant info.docx`. Schema browsing is available via `db/schema_dashboard.html`. Modeling and SHAP write-ups sit under `modeling_outputs/` and `shap_outputs/`.

## B. Figure index (report narrative)

| Fig. | Subject | Path |
|---|---|---|
| 1-2 | **External grounding** (completion funnel; secondary enrolment 2020-2024) | `report_figures/ext_02_*.png`, `ext_03_*.png` |
| 3 | Product layers (helper / ops / analytics) | `report_figures/01_product_layers.png` |
| 4 | Perceptual map (substitutes) | `report_figures/09_perceptual_map.png` |
| 5 | Matching loop (score → gift → monitor) | `report_figures/02_matching_loop.png` |
| 6 | Pilot roadmap / scale gates | `report_figures/07_pilot_roadmap.png` |
| 7-10 | Preparation & EDA charts | `visualizations/05`, `02`, `06`, `04` |
| 11-14 | Model selection & fairness | `report_figures/08`, `visualizations/25`, `21`, `24` |
| 15-16 | SHAP | `visualizations/31`, `32` |
| 17-19 | Personas & interventions | `visualizations/17`, `38`, `19` |
| 20 | Cohort overview | `visualizations/01` |
| 21 | Year-1 economics | `report_figures/06_year1_economics.png` |

*Strategy diagrams use the simple pre-polish format (solid slabs / circles / stage boxes) for clarity. Data charts remain pipeline-generated.*


Additional charts (confusion matrices, dependence plots, waterfalls, full correlation heatmaps) live in `visualizations/` for insertion when the Word/PDF export needs denser technical appendices. Suggested extras for Appendix G: `22_modeling_confusion.png`, `34_shap_waterfall_high_risk.png`, `36_shap_dependence_cash_flow_volatility.png`, `07_correlation_heatmap.png`.

## C. Predictive feature families and dictionary snapshot

Feature families used for ranking: demographic and fairness (age at enrolment, gender); household and economic (resource dilution, SES, cash-flow volatility); access (commute barriers, digital equity, nutritional support); academic momentum (GPA trend, failed subjects, STEM strength); health and attendance (chronic health risk, health-related absences); belonging and protection (social integration, psychosocial support access). Layer 2 sponsor filters operate at county and school level. Layer 3 ledger fields stay outside training.

**Snapshot location in narrative:** Section 11 table “Data dictionary snapshot” (layer, model inclusion, pilot tier, exclusions). Full dictionary source files: `Data dic.docx`, `tableau_exports/data_dictionary.csv`, and `db/schema_dashboard.html`.

## D. Modeling snapshot

Selected model: Logistic Regression with `C = 0.1`. Approximate test AUC 0.753. Approximate dropout recall 0.667. Majority baseline AUC 0.50. Full leaderboard: `modeling_outputs/MODELING_REPORT.md`.

## E. Cost-benefit snapshot

Illustrative Year-1 platform cost near KES 2.0 million. Base quantified benefits near KES 5.2 million. Base benefit-cost ratio near 2.6. Conservative case near break-even. Full assumption tables in `COST_BENEFIT_ANALYSIS.md`.

## F. Optional reproduction steps

```text
pip install -r requirements.txt
python db/init_db.py
python preprocess_data.py
python modeling_phase.py
python shap_analysis.py
python cluster_personas.py
python intervention_matrix.py
python build_sponsor_portal.py
python build_ops_dashboard.py
python build_dashboard.py
```

Local live gifts: `OPEN_DEMO.bat` or `python db/portal_server.py --open`.

## G. Suggested ten-minute investor pitch arc

**Context (outside the clock):** pitch to impact / education investors and CSR or foundation partners, seeking pilot capital for an eight-school launch. 
**On the clock:** open with Kenya’s equity and retention problem and **Figures 1-2** (sector grounding); **Figure 3** (product layers) and **Figure 4** (substitutes map). Open the Pages homepage and walk one helper gift (Day and Boarding). Show ops on settlement integrity and one pilot KPI. Flash **Figure 11** (why Logistic Regression) and **Figure 15** (SHAP). Close with **Figure 21** (cost) and **Figure 6** (gates) and the pilot ask.

## H. Word / PDF export tip

When pasting into Google Docs or Word: keep figure numbers consecutive; paste images at full width on portrait pages or landscape for wide charts (SHAP beeswarm, correlation); place captions *below* images; ensure `report_figures/` and `visualizations/` images travel with the export folder rather than as broken links.

## I. Decision log (significant choices)

| Decision | Alternatives considered | Justification | Consequence |
|---|---|---|---|
| **Synthetic cohort (seed 2026)** | Wait for school microdata | Privacy, MOU lag, and need for a buildable PoC | All metrics are non-portable until partner validation |
| **Fee channel only for helper MVP** | Four helper marketplaces at once | Finish one end-to-end path with settlement integrity | Tutoring/health/digital stay ops/school design |
| **Exclude orphan status as feature** | Use as “need” proxy | Bias and dignity risk | SES / behavioral proxies carry need signal |
| **Keep fee arrears out of training matrix** | Predict dropout from balances only | Avoid “owe money → drop” shallow story; protect ledger role | Ranking from Layer 1 risk; money is Layer 3 ops |
| **Select Logistic Regression** | RF / HistGB higher or similar AUC | Business rule: dropout recall when AUC within ~0.015 | Lower vanity accuracy; higher catch of leavers |
| **HTML + GitHub Pages as primary share** | Streamlit-only / zip install | Accessibility for investors/partners; no install ritual | Offline gifts on Pages; live ledger is local option |
| **Pass-through gifts (not org revenue)** | Take cut of gifts as revenue | Trust and school relationship | Business case uses platform cost, not gift P&L |
| **8-school pilot before national scale** | National launch narrative | Scope discipline; measurable gates | Catalog is national; volume is pilot |

## J. Figures and sources note

**External grounding (Figures 1-2):** (1) UNESCO IICBA (2025) completion funnel estimates; (2) KNBS (2025) *Economic Survey* secondary enrolment **2020-2024** (no full-year **2025** national total in that release). Captions state sector context only - not ElimuMatch performance.

**Internal evidence:** Charts in `visualizations/` are generated from the project pipeline on the synthetic cohort. Conceptual / strategy graphics in `report_figures/` (product layers, matching loop, roadmap, perceptual map, selection rule, Year-1 economics) use the simple original report style. Live product UI: https://jesyldah.github.io/ElimuMatch/. Full financial assumptions: `COST_BENEFIT_ANALYSIS.md`.

---

*End of narrative draft. Insert author name, personalize the reflective statement, and finalize citations before formal submission as PDF.*
