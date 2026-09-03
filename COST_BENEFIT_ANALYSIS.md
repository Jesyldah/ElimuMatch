# Evaluate Business Value — Cost–Benefit Analysis
## Elimu Match Capstone (Quantic MSBA)

**Section mapping:** Handbook → *Evaluate Business Value: Cost Analysis*  
**Framing:** Illustrative **Year-1 pilot** business case for a fictional / partner nonprofit using the PoC design.  
**Not** an audited financial forecast. Monetary benefits use transparent assumptions so examiners can stress-test them.

---

### Integrity note (paste near the top of this report section)

> Cost and benefit figures below are **illustrative** for a one-year pilot sized to the PoC cohort logic (~1,000 students / ~280 fee-support recommendations). They are not empirical results from a live Kenyan school system. The purpose is to show how Elimu Match creates value and under what assumptions a pilot clears a positive NPV.

---

## 1. Pilot definition (what we cost)

| Item | Pilot assumption |
|---|---|
| Scope | **8 partner secondary schools** (subset of national design; manageable ops) |
| Students in scoring cohort | **~800–1,000** (aligns with PoC n=1,000) |
| Fee-support queue (primary intervention) | **~200–280 students** (PoC: 282) |
| Horizon | **12 months** (one academic year + termly rescoring) |
| Payment rail | Simulated in PoC → **M-Pesa / bank to school fee account** in live pilot |
| Decision rule | Sponsor gifts target **school fee support** queue; other interventions stay school-owned |

---

## 2. Cost stack (Year 1) — organization / platform

All amounts in **KES**. Round figures for readability.

### 2.1 Fixed / setup

| Cost item | Assumption | Year-1 KES |
|---|---|---|
| MOU, ethics, data-protection setup | Legal/advisory + school onboarding packs | 250,000 |
| Platform hardening (hosting, auth, backups, M-Pesa webhook stub) | Cloud + contractor weeks on PoC codebase | 450,000 |
| School MIS fee/grade extract templates + training | 8 schools × onboarding | 320,000 |
| **Setup subtotal** | | **1,020,000** |

### 2.2 Operating (annualized)

| Cost item | Assumption | Year-1 KES |
|---|---|---|
| Part-time data / ML analyst | 0.4 FTE × 720,000 loaded | 288,000 |
| School liaison / ops case review | 0.5 FTE × 600,000 loaded | 300,000 |
| Hosting, monitoring, SMS/email notifications | Modest production footprint | 120,000 |
| Payment processing fees (org share) | ~1.5% on org-facilitated volume *or* flat ops buffer | 80,000 |
| Fairness + model refresh (termly) | 3 refresh cycles | 90,000 |
| Contingency (10%) | On opex | ~88,000 |
| **Opex subtotal** | | **~966,000** |

### 2.3 Total Year-1 platform cost (ex–bursary pool)

| | KES |
|---|---|
| Setup | 1,020,000 |
| Opex | 966,000 |
| **Total platform cost** | **≈ 1,986,000** |

**Important:** Sponsor **bursary / fee gifts** are treated as **pass-through capital** (donor → school fees), not as Elimu Match operating cost. The org’s job is **targeting + settlement integrity**. A separate “matched pool” scenario is in §5.

---

## 3. Benefit stack (Year 1)

Benefits are split into **cash-adjacent** (fee clearance via sponsors) and **outcome** (avoided dropouts). Outcome benefits are the most sensitive — shown with conservative assumptions.

### 3.1 Efficiency benefit — better targeting of fee support

Without analytics, bursaries often go to visible / connected cases. With Elimu Match:

- PoC identifies **~282** fee-support candidates from 1,000 students  
- High-risk + arrears investigation queue: **~111** students  

**Illustrative targeting lift:** assume a pilot moves **KES 4,000,000** of sponsor fee support in Year 1.

| Scenario | Share that would have been “mis-targeted” without model | Value of improved targeting |
|---|---|---|
| Conservative | 15% of gift volume better allocated | 0.15 × 4,000,000 = **600,000** |
| Base | 25% | **1,000,000** |
| Optimistic | 40% | **1,600,000** |

*Interpretation:* same donor money does more retention-relevant work (oldest arrears, high-risk students) — measured as the portion of gifts that would otherwise have missed the priority queue.

### 3.2 Direct fee clearance (pass-through, school/student benefit)

If sponsors clear **KES 4,000,000** of arrears:

- Schools receive fees that would have stayed unpaid  
- Students stay enrolled longer (mechanism the PoC is built to enable)

This is **real economic value to schools/households**, even though it is not Elimu Match revenue. Report it as **stakeholder benefit**, not org profit.

### 3.3 Outcome benefit — avoided fee-related dropouts

**Assumptions (explicit):**

| Assumption | Conservative | Base | Optimistic |
|---|---|---|---|
| Students receiving meaningful fee support (≥1 gift covering material arrears) | 40 | 80 | 120 |
| Of those, share who would have dropped without support | 20% | 25% | 30% |
| Avoided dropouts (count) | 8 | 20 | 36 |
| Social / economic value per avoided secondary dropout (KES, Year-1 proxy)* | 150,000 | 200,000 | 250,000 |
| **Outcome benefit (KES)** | **1,200,000** | **4,000,000** | **9,000,000** |

\*Proxy for one year of continued schooling value (fees retained by school + household continuity + avoided disruption). **Not** a full lifetime earnings NPV — keep claims modest for the capstone.

### 3.4 Ops productivity (optional, smaller)

Human review of a ranked queue vs ad-hoc lists: estimate **0.25 FTE saved** at school/NGO (~150,000 KES/year). Include in base case only as a secondary line.

---

## 4. Summary — Year-1 cost vs benefit (base case)

| Line | KES |
|---|---|
| **Platform cost (setup + opex)** | **(1,986,000)** |
| Targeting efficiency benefit | 1,000,000 |
| Outcome benefit (avoided dropouts) | 4,000,000 |
| Ops productivity | 150,000 |
| **Total quantified benefits** | **5,150,000** |
| **Net benefit (base)** | **≈ +3,164,000** |
| **Benefit / cost ratio** | **≈ 2.6×** |

**Plus (not in org P&L):** KES 4,000,000 sponsor pass-through clearing school arrears.

---

## 5. Sensitivity

| Case | Benefits | Cost | Net | BCR |
|---|---|---|---|---|
| Conservative | 600k + 1.2M + 0 = 1.8M | 2.0M | **−0.2M** | ~0.9× |
| Base | 5.15M | 2.0M | **+3.2M** | ~2.6× |
| Optimistic | 1.6M + 9.0M + 0.15M ≈ 10.8M | 2.0M | **+8.8M** | ~5.4× |

**Reading for the report:**  
The pilot is **not free-money guaranteed**. Under conservative outcome assumptions it is roughly break-even on platform cost alone; under base assumptions it clears a healthy surplus. That is why **measuring next-term retention for helped vs matched peers** is a pilot success criterion (ElimuMatch Support Hub).

### Optional matched-bursary scenario

If Elimu Match also **seeds** a matched gift pool of KES 2,000,000:

- Year-1 cost rises to ≈ 4.0M  
- Base benefits still ≈ 5.15M + stronger fee clearance  
- Net still positive if ≥ ~15–20 avoided dropouts materialize  

Use this only if the org’s model includes matching funds.

---

## 6. Non-financial / strategic benefits (handbook “value”)

These matter for a consultancy score even when money is uncertain:

1. **Ledger trust** — overpayment blocked; stale balances rejected → sponsor confidence  
2. **Equity visibility** — SES/gender mix on the fee queue; fairness cadence with rescoring  
3. ** intervening routing** — fee vs tutoring vs health (not one-size bursary)  
4. **National design, local pilot** — 47-county catalog in PoC; start with 8 schools  
5. **Data scarcity fit** — MVP on fees/grades/attendance schools already have  

---

## 7. Cost of *not* doing the analytics

| Without Elimu Match | Risk |
|---|---|
| Untargeted bursaries | Money misses highest-arrears / highest-risk students |
| Spreadsheet fee tracking | Double-pay / overpay / disputes |
| No rescoring cadence | Stale priorities mid-year |
| No pilot KPIs | Cannot prove retention lift to donors |

---

## 8. Recommendation (paste-ready)

> **Year-1 recommendation:** Proceed with an **8-school pilot** funded at roughly **KES 2.0 million** platform cost (setup + ops), with sponsor fee gifts as pass-through. Under **base assumptions**, quantified benefits (~KES 5.2M from targeting lift, avoided dropouts, and light ops savings) yield a **benefit–cost ratio ≈ 2.6×**. The investment clears a positive case if the pilot converts even a modest share of fee-supported at-risk students into continued enrollment — which must be **measured**, not assumed. Conservative assumptions show near break-even, so governance should gate scale-up on the ops success criteria (fee-queue coverage, settlement integrity, scoring SLA, and next-term retention).

---

## 9. Numbers tied to the PoC (for credibility)

| PoC evidence | Use in CBA |
|---|---|
| 1,000 students, 47 counties (sample schools) | Cohort / design scale |
| 282 fee-support recommendations | Pilot queue sizing |
| 111 high-risk + arrears | Urgency segment |
| ~KES 52M total arrears in synthetic ledger | Shows fee problem magnitude (illustrative) |
| Settlement rules (no overpay / stale reject) | Reduces financial/reputation risk in benefit case |
| Pilot KPI strip on `ops_dashboard.html` | How benefits will be verified live |

---

## 10. What to put in the Appendix

- This file’s tables  
- One tornado chart (optional): vary avoided-dropout count and value/dropout  
- Link to ops pilot success criteria  
- Note: USD readers may convert at a stated rate (e.g. cite rate + date); keep **KES as primary**

---

*Prepared for Quantic MSBA Capstone report section “Evaluate Business Value: Cost Analysis.” Update assumptions with partner quotes when an MOU exists.*
