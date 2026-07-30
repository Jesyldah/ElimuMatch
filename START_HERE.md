# START HERE — ElimuMatch Capstone

You do **not** need to run the full analytics pipeline to review this MVP.

---

## Option A — Fastest (recommended for instructors)

### If you received a **Google Drive zip**
1. Unzip the folder.
2. Open **`03_Demos/index.html`** in Chrome / Edge / Firefox.
3. Click the cards:
   - **Helper portal** — fee sponsorship flow  
   - **Ops monitor** — organization KPIs & school resource targets  
   - **Retention analytics** — model / SHAP / personas gallery  

**Optional live gifts / ledger:** in `03_Demos`, double-click `OPEN_DEMO.bat`  
(requires Python on the machine). Then use the browser page that opens.

### If you cloned / opened the **GitHub repo**
1. Open **`index.html`** in a browser  
   **or** double-click **`OPEN_DEMO.bat`** (Python required for live API).
2. Same three demos from the home page.

---

## Option B — Read the concept first

| File | What it is |
|---|---|
| `CONCEPT_EXPLORATION_ANSWERS.md` (or `.docx` in Drive `01_Docs`) | MVP scope, problem, analytics story |
| `DATA_AND_LIMITATIONS.md` | Synthetic data — factual grounding + limits |
| `COST_BENEFIT_ANALYSIS.md` | Illustrative Year-1 cost–benefit |
| `README.md` | Full reproduce steps (for technical reviewers) |

---

## What is in Capstone scope vs not

**In MVP:** risk analytics, fee helper channel + ledger, HTML dashboards, ops views, CBA.  
**Not required:** live school data, M-Pesa, full tutoring/health marketplaces.

Synthetic cohort is **factually grounded** and documented — not live student records.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Links from home page fail | Open `index.html` from disk (not email preview). Prefer unzipped folder. |
| “Connection refused” on localhost | Run `OPEN_DEMO.bat` / `python db/portal_server.py --open` |
| Analytics page slow | Normal — `dashboard.html` embeds charts (~5 MB). Wait a few seconds. |
| Want to rebuild everything | See `README.md` → “Reproduce from source” |
