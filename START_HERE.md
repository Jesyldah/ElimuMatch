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

## Option B — Read the concept first

| File | What it is |
|---|---|
| `CONCEPT_EXPLORATION_ANSWERS.md` (or `.docx` in Drive `01_Docs`) | MVP scope, problem, analytics story |
| `DATA_AND_LIMITATIONS.md` | Synthetic data — factual grounding + limits |
| `COST_BENEFIT_ANALYSIS.md` | Illustrative Year-1 cost–benefit |
| `README.md` | Full reproduce steps (for technical reviewers) |
| `ElimuMatch_Analysis.ipynb` | Narrative notebook: *Secondary School Retention Risk Analytics* (problem → decision) |

---

## Option C — Offline HTML / live local ledger

### Google Drive zip
1. Unzip the folder.
2. Open **`03_Demos/index.html`**.
3. Optional live gifts: double-click `OPEN_DEMO.bat` (needs Python).

### Cloned GitHub repo
1. Open **`index.html`** or run **`OPEN_DEMO.bat`**.
2. Same three demos from the home page.

---

## Optional — Streamlit (experimental)

```bash
pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

HTML via GitHub Pages is the preferred share link.

---

## What is in Capstone scope vs not

**In MVP:** risk analytics, fee helper channel + ledger, HTML dashboards (Pages + offline), ElimuMatch Support Hub, CBA.  
**Not required:** live school data, M-Pesa, full tutoring/health marketplaces.

Synthetic cohort is **factually grounded** and documented — not live student records.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Pages link 404 / old content | Wait 1–2 minutes after a push; hard-refresh the browser |
| Gift not shared across reviewers | Expected on Pages — offline/local demo mode |
| Want live local ledger | Run `OPEN_DEMO.bat` / `python db/portal_server.py --open` |
| Want to rebuild everything | See `README.md` → “Reproduce from source” |
