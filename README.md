# ElimuMatch — MSBA Capstone (MVP)

**→ Reviewers: open [`START_HERE.md`](START_HERE.md) first** (or `START_HERE.txt`).

EdTech proof of concept: **dropout-risk analytics**, multi-channel intervention routing, a working **fee helper portal** with term ledger, and **ops / analytics HTML dashboards**.

**Capstone scope = MVP only.** Full multi-channel marketplaces, live school feeds, and M-Pesa are roadmap — not required for this submission.

Synthetic cohort is **factually grounded** (Kenya secondary patterns) and documented; it is not live student records.

---

## Quick demo (no rebuild)

**First file to open:** `index.html` (project home) — or read `START_HERE.md`.

1. Double-click `OPEN_DEMO.bat`  
   **or** run: `python db/portal_server.py --open`
2. Browser opens `http://127.0.0.1:8765/`
3. Use **Helper portal**, **Ops monitor**, **Analytics dashboard**

Offline: open `index.html` (relative links work). Live gifts / ops API need the local server.

---

## How we share artefacts (reproducible)

### Recommended: private GitHub repo

| Audience | What they get |
|---|---|
| Instructor / reviewers | Clone → install → regenerate or open HTML demos |
| You | Version history + clear README |

**Steps**
1. Create a **private** GitHub repository (do not make public — Capstone / Quantic materials).
2. Push this project (see `.gitignore` — handbook PDF and caches stay local).
3. Share the private repo invite link with the instructor (or a release ZIP from GitHub).

### Fallback: Google Drive folder

Use Drive when the reviewer only needs to **open demos and read docs** (no coding).

Suggested Drive layout:

```text
ElimuMatch_Capstone/
  00_README.txt                 ← point to this README / how to open demos
  01_Concept_Brief.docx
  02_Report_notes_or_PDF/       ← when formal report exists
  03_Demos/
    index.html
    dashboard.html
    ops_dashboard.html
    sponsor_portal.html
    OPEN_DEMO.bat
    db/                         ← include elimu_match.db for live demo
  04_Data_and_code/             ← optional zip of full repo, or “see GitHub”
```

**Tip:** Prefer GitHub for code reproducibility; use Drive for a polished “open these HTML files” handoff if needed. Doing **both** is fine.

---

## Reproduce from source

```bash
# 1. Create a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate synthetic cohort (seed 2026)
python synthetic_data_v2.py

# 4. Preprocess + model + charts (as needed)
python preprocess_data.py
python train_retention_model.py
python visualize.py
python visualize_modeling.py
python shap_analysis.py
python cluster_personas.py
python intervention_matrix.py
python match_sponsors.py

# 5. Fee ledger DB + HTML surfaces
python db/init_db.py
python build_sponsor_portal.py
python build_ops_dashboard.py
python build_dashboard.py

# 6. Demo
python db/portal_server.py --open
```

Committed / shared HTML files already embed charts where needed, so reviewers can demo **without** re-running the full pipeline.

---

## Main artefacts

| Artefact | Role |
|---|---|
| `sponsor_portal.html` | Fee helper channel (MVP depth) |
| `ops_dashboard.html` | Ops KPIs, queues, school resource targets |
| `dashboard.html` | Analytics gallery (EDA / model / SHAP) |
| `index.html` | Project home |
| `db/` | SQLite schema, ledger, `portal_server.py` |
| `CONCEPT_EXPLORATION_ANSWERS.md` | Concept / MVP scope brief |
| `DATA_AND_LIMITATIONS.md` | Synthetic data integrity |
| `COST_BENEFIT_ANALYSIS.md` | Illustrative Year-1 CBA |
| `REPORT_NOTES.md` | Report paste-ready notes |

---

## Data note

- Cohort: `elimu_match_data_v4.csv` from `synthetic_data_v2.py` (seed **2026**)
- Details: `DATA_AND_LIMITATIONS.md`
- Do **not** present PoC metrics as validated national field results

---

## Instructor-confirmed Capstone constraints

- Synthetic OK if factually grounded  
- Capstone = **MVP scope**, not the full product  
- **HTML dashboards are acceptable** (Tableau optional, not required)
