"""Build the portable analysis_notebook/ folder for reviewers.

Contains only what is needed to run ElimuMatch_Analysis.ipynb.
Run from the Capstone repo root: python build_notebook_bundle.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUNDLE = ROOT / "analysis_notebook"

NOTEBOOK = "ElimuMatch_Analysis.ipynb"
PY_MODULES = (
    "feature_engineering.py",
    "preprocess_data.py",
    "kenya_schools.py",
)
OPTIONAL_PATHS = (
    "elimu_match_data_v4.csv",
    Path("shap_outputs") / "shap_global_importance.csv",
    Path("intervention_outputs") / "intervention_summary.csv",
)

REQUIREMENTS = """# Minimal dependencies for ElimuMatch_Analysis.ipynb
pandas>=2.0
numpy>=1.24
scikit-learn>=1.3
matplotlib>=3.7
seaborn>=0.13
joblib>=1.3
jupyter>=1.0
ipykernel>=6.0
"""

README = """# ElimuMatch analysis notebook (portable bundle)

Self-contained folder for **ElimuMatch_Analysis.ipynb**. You do not need the full Capstone repository.

## Get this folder

- **GitHub:** clone or download only the `analysis_notebook/` directory from the ElimuMatch repo, or
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
| `ElimuMatch_Analysis.ipynb` | End-to-end retention-risk analysis |
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
"""


def main() -> None:
    subprocess.run([sys.executable, "build_analysis_notebook.py"], cwd=ROOT, check=True)

    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    BUNDLE.mkdir()

    shutil.copy2(ROOT / NOTEBOOK, BUNDLE / NOTEBOOK)
    for name in PY_MODULES:
        shutil.copy2(ROOT / name, BUNDLE / name)

    for rel in OPTIONAL_PATHS:
        src = ROOT / rel
        if src.is_file():
            dest = BUNDLE / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    (BUNDLE / "requirements.txt").write_text(REQUIREMENTS, encoding="utf-8")
    (BUNDLE / "README.md").write_text(README, encoding="utf-8")

    print(f"Wrote {BUNDLE.relative_to(ROOT)}/")
    print(f"  {NOTEBOOK}")
    for name in PY_MODULES:
        print(f"  {name}")
    print("  requirements.txt, README.md")
    for rel in OPTIONAL_PATHS:
        if (BUNDLE / rel).exists():
            print(f"  {rel}")


if __name__ == "__main__":
    main()
