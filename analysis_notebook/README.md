# ElimuMatch analysis notebook (portable bundle)

Self-contained folder for **ElimuMatch_Analysis.ipynb**. You do not need the full Capstone repository to reproduce the step-by-step analysis.

**Reviewers:** start at the repo root [`START_HERE.md`](../START_HERE.md). Use this folder when you want to walk the analytics path yourself (data → model → explainability → interventions).

## Get this folder

- **GitHub:** open or download the `analysis_notebook/` directory from the ElimuMatch repo, or
- **Zip:** unzip if your instructor shared `analysis_notebook.zip`.

## Run

```bash
cd analysis_notebook
pip install -r requirements.txt
jupyter notebook ElimuMatch_Analysis.ipynb
```

In Cursor or VS Code, open this folder and open `ElimuMatch_Analysis.ipynb`. Use the Python kernel for the environment where you ran `pip install`.

## Contents

| File | Purpose |
|------|---------|
| `ElimuMatch_Analysis.ipynb` | End-to-end retention-risk analysis (guided steps) |
| `feature_engineering.py` | Shared feature logic |
| `preprocess_data.py` | Train/test split and preprocessing |
| `kenya_schools.py` | School catalog for synthetic data |
| `elimu_match_data_v4.csv` | Optional saved cohort (skip Step 2 if present) |
| `shap_outputs/` | Optional precomputed SHAP table (Step 13) |
| `intervention_outputs/` | Optional intervention counts (Step 14) |

Step 2 generates the cohort in the notebook if you do not have the CSV. Steps 13-14 work without the optional files (fallbacks are built in).

## Refresh (maintainers)

From the full repo root:

```bash
python build_notebook_bundle.py
```