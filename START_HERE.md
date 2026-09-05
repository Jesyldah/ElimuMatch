# START HERE — ElimuMatch Capstone

You do **not** need to run the full analytics pipeline to review this MVP.

---

## Option A — GitHub Pages (recommended for instructors)

**One link. No zip. Same HTML dashboards.**

Open: **https://jesyldah.github.io/ElimuMatch/**

Then click:
- **Helper portal** — fee sponsorship flow  
- **ElimuMatch Support Hub** — whether fee help is reaching students & school support needs  
- **Retention analytics** — model / SHAP / personas  

Gifts on the hosted site use **offline demo mode** (browser localStorage) — not live M-Pesa and not a permanent shared cloud ledger.  
For a local live SQLite ledger, use Option C below.

---

## Option B — Read the brief and limits

| File | What it is |
|---|---|
| `ElimuMatch_Investor_Brief.docx` | Full investor / partner brief |
| `ElimuMatch_Executive_Pitch.pptx` | 10-minute executive pitch deck |
| `ElimuMatch_Proposal_Articulation_Concept_Exploration.md` | Proposal articulation + concept exploration (MVP vs vision) |
| `DATA_AND_LIMITATIONS.md` | Synthetic data — factual grounding + limits |
| `COST_BENEFIT_ANALYSIS.md` | Illustrative Year-1 cost–benefit |
| `README.md` | Full repo map and reproduce-from-source steps |

---

## Option C — Step-by-step analysis notebook (reproduce the analytics)

To walk the retention-risk analysis yourself (data → model → SHAP → interventions), open the portable notebook bundle:

1. Go to **`analysis_notebook/`**
2. Read **`analysis_notebook/README.md`**
3. Install and launch:

```bash
cd analysis_notebook
pip install -r requirements.txt
jupyter notebook ElimuMatch_Analysis.ipynb
```

Or open `analysis_notebook/ElimuMatch_Analysis.ipynb` in Cursor / VS Code with a Python kernel.

That notebook is the guided, cell-by-cell path. You do **not** need the rest of the repo for those steps (the folder is self-contained).

---

## Option D — Offline HTML / live local ledger

### Cloned GitHub repo
1. Open **`index.html`** or run **`OPEN_DEMO.bat`**.
2. Use **Helper portal**, **ElimuMatch Support Hub**, and **Analytics** from the home page.

Live gifts / ops API need the local server (`OPEN_DEMO.bat` or `python db/portal_server.py --open`).

---

## What is in Capstone scope vs not

**In MVP:** risk analytics, fee helper channel + ledger, HTML dashboards (Pages + offline), ElimuMatch Support Hub, CBA, analysis notebook.  
**Not required for review:** live school data, M-Pesa, full tutoring/health marketplaces.

Synthetic cohort is **factually grounded** and documented — not live student records.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Pages link 404 / old content | Wait 1–2 minutes after a push; hard-refresh the browser |
| Gift not shared across reviewers | Expected on Pages — offline/local demo mode |
| Want live local ledger | Run `OPEN_DEMO.bat` / `python db/portal_server.py --open` |
| Want step-by-step analytics | Use Option C → `analysis_notebook/` |
| Want to rebuild everything | See `README.md` → “Reproduce from source” |
