"""Generate the retention-risk analytics notebook."""
import json
from pathlib import Path

from notebook_synthetic_generation_cell import SYNTHETIC_GENERATION_CELL


def md(s: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [line + "\n" for line in s.strip().split("\n")]}


def code(s: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {
            "inputCollapsed": True,
            "jupyter": {"source_hidden": True},
        },
        "outputs": [],
        "execution_count": None,
        "source": [line + "\n" for line in s.strip().split("\n")],
    }


def code_header() -> dict:
    return md("#### Code")


def append_code_block(source: str) -> None:
    cells.append(code_header())
    cells.append(code(source))


def finding(s: str) -> dict:
    return md(f"#### Findings\n\n{s}")


cells = []

# --- Opening ---
cells.append(
    md(
        """# Secondary School Retention Risk Analytics
## Prioritizing fee support before students leave school

**Analyst:** Jesyldah Mwanyamba  
**Organization:** ElimuMatch (Kenya secondary education)  
**Dataset:** Synthetic student cohort, n = 1,000 (seed 2026)

---

### Executive summary

Kenyan secondary enrolment has expanded, but many students still leave before completing the year because of fees, health, distance, and academic pressure. ElimuMatch helps schools and sponsors **prioritize support** when resources are limited, instead of relying on visibility or personal networks.

This notebook walks through the analytics behind that ranking: synthetic data generation, exploration, modeling, fairness checks, and intervention sizing. Staff review the ranked list before any fee gift or referral goes out.

**Objective:** Rank secondary students by retention risk so schools and sponsors can target fee support and related interventions before dropout occurs. Fee support is one channel; health, commute, and academic factors are also modeled.

**Approach:** Model retention from academic, health, access, and socioeconomic signals. Fee arrears sit in the gift ledger, not as the sole predictor. When models are comparable on AUC, prefer the one with higher dropout recall; logistic regression is selected over gradient boosting in that case because it is easier to explain to staff.

**Data:** Synthetic cohort (n = 1,000, seed 2026). Results validate pipeline design and assumptions, not live national performance. Partner school data would replace this cohort before any public ranking is published."""
    )
)

cells.append(
    md(
        """## 1. Problem statement

Secondary enrolment in Kenya has expanded, but many students still leave before completing the year because of fees, health, distance, and academic pressure. Support is often allocated by visibility or personal networks rather than measured risk.

**Business question:** Which students are most likely to drop out, and can they be ranked early enough to target fee gifts and other support?

**Analytics requirements**
- Rank students for staff review (not full automation)
- Favor models that detect leavers, not only high overall accuracy
- Exclude leakage fields and post-outcome variables from training
- Support explainability for operations staff
- Monitor performance by socioeconomic group"""
    )
)

cells.append(
    md(
        """## 2. Analysis workflow

| Step | Task |
|---|---|
| 1 | Environment setup |
| 2 | Synthetic data generation (documented DGP) |
| 3 | Profile cohort |
| 4 | Data quality checks |
| 5-6 | Exploratory analysis |
| 7 | Feature engineering |
| 8 | Preprocessing (train/test split, imputation) |
| 9-10 | Model training, comparison, and selection |
| 11-12 | Evaluation (ROC, confusion matrix, fairness) |
| 13-14 | Explainability and intervention queue |
| 15 | Conclusion and recommendation |"""
    )
)

# --- Setup ---
cells.append(
    md(
        """### Step 1: Environment setup

*Before you run:* use the **`analysis_notebook/`** folder (portable bundle with only what this notebook needs). Clone or download that folder into your working directory, or unzip it if shared as a zip. You do not need the full ElimuMatch repository.

```bash
cd analysis_notebook
pip install -r requirements.txt
jupyter notebook ElimuMatch_Analysis.ipynb
```

The bundle includes `feature_engineering.py`, `preprocess_data.py`, and `kenya_schools.py`. *The cell below locates that folder and adds it to `sys.path` so imports work.*"""
    )
)

append_code_block(
        """# Resolve project root so local .py modules import reliably
from pathlib import Path
import sys

def find_project_root() -> Path:
    markers = ("feature_engineering.py", "preprocess_data.py", "kenya_schools.py")
    here = Path.cwd().resolve()
    for candidate in [here, *here.parents]:
        if all((candidate / name).exists() for name in markers):
            return candidate
    raise FileNotFoundError(
        "analysis_notebook bundle not found. Open this notebook from the analysis_notebook/ "
        "folder, or download that folder from the ElimuMatch repo."
    )

ROOT = find_project_root()
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    RocCurveDisplay,
    classification_report,
    confusion_matrix,
    roc_auc_score,
)

from feature_engineering import ENGINEERED_FEATURES, engineer_features, correlation_with_target
from preprocess_data import LEAKAGE_COLUMNS, MISSINGNESS_COLS, TARGET, preprocess

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted")

DATA_FILE = ROOT / "elimu_match_data_v4.csv"
RANDOM_STATE = 2026
DROPOUT_LABEL = 0  # in our data, retained=0 means the student dropped out

print(f"Project root: {ROOT}")
print(f"Saved cohort on disk (optional until Step 3/8): {DATA_FILE.exists()}")"""
)

cells.append(
    finding(
        """Imports should succeed and `Project root` should point at the folder that contains `feature_engineering.py` and the other bundle modules. `RANDOM_STATE = 2026` is used for generation and for the train/test split in Step 8."""
    )
)

# --- Synthetic data generation ---
cells.append(
    md(
        """### Step 2: Synthetic data generation

Partner student records were not available for this project. **This section is included to show how the cohort is generated**: the logic, assumptions, and reasoning behind each variable (see comments in the code cell). The implementation mirrors `synthetic_data_v2.py` and builds `df` in memory for the steps that follow.

*Default path: run this step. Skip this step only if you already have `elimu_match_data_v4.csv` on disk and will load it in Step 3.*"""
    )
)

append_code_block(SYNTHETIC_GENERATION_CELL)

cells.append(
    finding(
        """The generator produces 1,000 students across 47 schools with retention near **86%**. Survey-style fields (`cash_flow_volatility`, `commute_barrier_score`, `digital_equity_access_score`, `psychosocial_support_access`) include intentional missing values at roughly 6-8%, with slightly higher missing rates at lower SES.

`retention_risk_score` and `dropout_reason` are created for simulation realism but are **excluded from modeling** (leakage / post-outcome). The saved file `elimu_match_data_v4.csv` is produced by the same logic when you run `python synthetic_data_v2.py` separately."""
    )
)

# --- Profile cohort ---
cells.append(
    md(
        """### Step 3: Profile the cohort

Confirm cohort size, retention rate, and leakage columns."""
    )
)

append_code_block(
        """# Use in-memory cohort from Step 2, or load the saved file
if "df" not in globals():
    if not DATA_FILE.exists():
        raise FileNotFoundError("Run Step 2 first, or run: python synthetic_data_v2.py")
    df = pd.read_csv(DATA_FILE)

print(f"Students in cohort: {len(df):,}")
print(f"Columns: {df.shape[1]}")
print(f"Share who stayed in school (retained=1): {df[TARGET].mean():.1%}")
print(f"Schools represented: {df['school_id'].nunique()}")

print("\\nColumns excluded from modeling (leakage / post-outcome):")
for col in sorted(LEAKAGE_COLUMNS):
    print(f"  - {col}")

df.head()"""
)

cells.append(
    finding(
        """The cohort has 1,000 students with a clear retention label. Retention is typically ~86%; class imbalance means accuracy alone is a poor metric.

Leakage columns (`retention_risk_score`, `dropout_reason`, `academic_catchup_status`) must not enter the model. The preview shows academic, health, commute, and socioeconomic fields; retention is multi-factor, not fees alone."""
    )
)

# --- Quality ---
cells.append(
    md(
        """### Step 4: Data quality checks

Validate duplicate IDs, dropout-reason logic, and expected missingness on survey-style fields."""
    )
)

append_code_block(
        """checks = []

# Each student should appear once
dup_ids = int(df["student_id"].duplicated().sum())
checks.append(("duplicate_student_id", dup_ids, "PASS" if dup_ids == 0 else "FAIL"))
checks.append(("retention_rate", round(df[TARGET].mean(), 3), "INFO"))

# Dropout reason should exist only when retained == 0
invalid_reason = ((df[TARGET] == 1) & df["dropout_reason"].notna()).sum()
missing_reason = ((df[TARGET] == 0) & df["dropout_reason"].isna()).sum()
checks.append(
    (
        "dropout_reason_only_when_dropped",
        f"invalid={invalid_reason}, missing={missing_reason}",
        "PASS" if invalid_reason == 0 and missing_reason == 0 else "FAIL",
    )
)

# Missingness on fields schools often do not have for every child
for col in MISSINGNESS_COLS:
    miss = df[col].isna().sum()
    checks.append((f"missing_{col}", f"{miss} ({miss / len(df):.1%})", "INFO"))

validation_df = pd.DataFrame(checks, columns=["check", "result", "status"])
validation_df"""
)

cells.append(
    finding(
        """Structural checks should show **PASS** for duplicate IDs and dropout-reason logic. **INFO** rows on missing survey fields are expected; those gaps are handled later with missing indicators, not by dropping students.

Do not proceed to modeling if any check shows **FAIL**."""
    )
)

# --- EDA part 1 ---
cells.append(
    md(
        """### Step 5: Class balance and retention by socioeconomic group

Check target imbalance and whether retention varies by socioeconomic index (1 = most constrained)."""
    )
)

append_code_block(
        """fig, axes = plt.subplots(1, 2, figsize=(11, 4))

# How many dropped vs stayed
retention_counts = df[TARGET].value_counts().sort_index()
axes[0].bar(["Dropped", "Stayed"], retention_counts.values, color=["#E76F51", "#2A9D8F"])
axes[0].set_title("How many students left vs stayed")
axes[0].set_ylabel("Number of students")

# Retention rate by socioeconomic group (1 = lowest resources in this scale)
ses_ret = df.groupby("socioeconomic_status_index")[TARGET].mean().sort_index()
axes[1].plot(ses_ret.index, ses_ret.values, marker="o", color="#264653", linewidth=2)
axes[1].set_xlabel("Socioeconomic group (1 = most constrained)")
axes[1].set_ylabel("Share who stayed in school")
axes[1].set_title("Staying in school rises with socioeconomic position")
axes[1].set_ylim(0, 1)

plt.tight_layout()
plt.show()"""
)

cells.append(
    finding(
        """Most students are retained (left chart), so a model that always predicts "stayed" can appear accurate while missing all dropouts.

Retention increases with socioeconomic group (right chart). Model performance should be reported by group, not only in aggregate. Downstream metrics will emphasize dropout recall and AUC rather than accuracy."""
    )
)

# --- EDA part 2 ---
cells.append(
    md(
        """### Step 6: Compare retained vs dropped students

Compare grade trend, failures, absences, commute, belonging, and income volatility between students who stayed and those who left."""
    )
)

append_code_block(
        """compare_cols = [
    "gpa_trend",
    "failed_subjects_count",
    "health_related_absences",
    "commute_barrier_score",
    "social_integration_score",
    "cash_flow_volatility",
]
plot_df = df[[TARGET] + compare_cols].copy()
plot_df[TARGET] = plot_df[TARGET].map({0: "Left school", 1: "Stayed"})

melted = plot_df.melt(id_vars=TARGET, var_name="measure", value_name="value")
plt.figure(figsize=(12, 5))
sns.boxplot(data=melted, x="measure", y="value", hue=TARGET, showfliers=False)
plt.xticks(rotation=25, ha="right")
plt.title("Students who left tend to show worse academic, health, and access signals")
plt.tight_layout()
plt.show()"""
)

cells.append(
    finding(
        """Students who left school show worse values on most measures: lower GPA trend, more failures, more health-related absences, longer commutes, weaker social integration, and higher cash-flow volatility.

Dropout is associated with multiple domains, which supports a multi-feature model rather than ranking on fee arrears alone. Fee balances are handled separately in the gift ledger."""
    )
)

# --- Feature engineering ---
cells.append(
    md(
        """### Step 7: Feature engineering

Create composite indices and interaction terms via `engineer_features()` (aligned with `preprocess_data.py`)."""
    )
)

append_code_block(
        """enriched = engineer_features(df)

print(f"New features created: {len(ENGINEERED_FEATURES)}")

corr = correlation_with_target(enriched)
print("\\nStrongest relationships with staying in school (engineered features):")
display(corr.head(10).to_frame("correlation_with_stayed"))

top_feats = corr.head(8).index.tolist()
plt.figure(figsize=(7, 5))
sns.heatmap(enriched[top_feats + [TARGET]].corr(), annot=True, fmt=".2f", cmap="RdBu_r", center=0)
plt.title("How the top engineered signals relate to each other and to retention")
plt.tight_layout()
plt.show()"""
)

cells.append(
    finding(
        """Sixteen engineered features were added. Academic risk, health burden, and economic instability indices correlate with retention in the expected direction.

Some features are correlated with each other (visible in the heatmap), which is expected when pressures cluster. A regularized linear model is a reasonable candidate alongside tree-based models. Correlations on the full cohort are exploratory; holdout evaluation follows after preprocessing."""
    )
)

# --- Preprocess ---
cells.append(
    md(
        """### Step 8: Preprocessing

Remove leakage columns, add missing indicators, stratified 75/25 train/test split (seed 2026), median imputation and scaling fit on train only. Uses `preprocess()` from the project pipeline, which reads `elimu_match_data_v4.csv` from disk. *If you generated `df` in Step 2, the cell below writes it to that file first.*"""
    )
)

append_code_block(
        """# preprocess() loads elimu_match_data_v4.csv; sync disk if df came from Step 2
if "df" in globals():
    df.to_csv(DATA_FILE, index=False)

bundle = preprocess(test_size=0.25, random_state=RANDOM_STATE)

x_train = bundle["x_train"]
x_test = bundle["x_test"]
y_train = bundle["y_train"]
y_test = bundle["y_test"]
meta_test = bundle["meta_test"]
report = bundle["report"]

print("Preparation summary:")
for k in [
    "rows_train",
    "rows_test",
    "target_train_positive_rate",
    "target_test_positive_rate",
    "processed_feature_count",
]:
    print(f"  {k}: {report[k]}")

x_train.iloc[:3, :6].round(3)"""
)

cells.append(
    finding(
        """Expect ~750 training and ~250 test rows with similar retention rates in each split. Processed feature count is ~37 after engineering, missing flags, and scaling.

All model evaluation from this point uses the held-out test set only."""
    )
)

# --- Modeling leaderboard ---
cells.append(
    md(
        """### Step 9: Model comparison

Train four models: majority baseline, logistic regression, random forest, and gradient boosting. Compare test AUC, accuracy, and dropout recall."""
    )
)

append_code_block(
        """x_train = x_train.loc[:, ~x_train.columns.str.contains("^Unnamed")]
x_test = x_test.loc[:, ~x_test.columns.str.contains("^Unnamed")]

models = {
    "Majority baseline (always stayed)": DummyClassifier(strategy="most_frequent", random_state=RANDOM_STATE),
    "Logistic regression": LogisticRegression(
        max_iter=3000, random_state=RANDOM_STATE, class_weight="balanced", C=0.1
    ),
    "Random forest": RandomForestClassifier(
        n_estimators=400, max_depth=10, min_samples_leaf=2,
        random_state=RANDOM_STATE, class_weight="balanced",
    ),
    "Gradient boosting": HistGradientBoostingClassifier(
        max_depth=6, learning_rate=0.05, max_iter=150,
        random_state=RANDOM_STATE, class_weight="balanced",
    ),
}

rows = []
fitted = {}

for name, model in models.items():
    model.fit(x_train, y_train)
    if "Majority" in name:
        y_prob = np.full(len(y_test), float(y_train.mean()))
        y_pred = model.predict(x_test)
    else:
        y_prob = model.predict_proba(x_test)[:, 1]
        y_pred = model.predict(x_test)

    dropped_mask = y_test == DROPOUT_LABEL
    rows.append({
        "model": name,
        "test_auc": round(roc_auc_score(y_test, y_prob), 4),
        "accuracy": round((y_pred == y_test).mean(), 4),
        "recall_dropouts": round(((y_pred == 0) & dropped_mask).sum() / max(dropped_mask.sum(), 1), 4),
        "recall_stayed": round(((y_pred == 1) & (y_test == 1)).sum() / max((y_test == 1).sum(), 1), 4),
    })
    fitted[name] = {"model": model, "y_prob": y_prob, "y_pred": y_pred}

leaderboard = pd.DataFrame(rows).sort_values("test_auc", ascending=False)
leaderboard"""
)

cells.append(
    finding(
        """The majority baseline may show the highest accuracy but zero dropout recall; it never flags a leaver.

Logistic regression and gradient boosting typically lead on AUC. Random forest often has high accuracy but low dropout recall. The next step applies a selection rule rather than picking the top accuracy."""
    )
)

# --- Model selection ---
cells.append(
    md(
        """### Step 10: Model selection

**Rule:** If top models are within 0.015 AUC, select the one with highest dropout recall; otherwise select highest AUC. Rationale: missing a dropout is costlier than extra review for a false positive."""
    )
)

append_code_block(
        """AUC_TIE_BAND = 0.015
candidates = leaderboard[~leaderboard["model"].str.contains("Majority")].copy()
top_auc = candidates["test_auc"].max()
near_best = candidates[candidates["test_auc"] >= top_auc - AUC_TIE_BAND]
best_name = near_best.sort_values(["recall_dropouts", "test_auc"], ascending=[False, False]).iloc[0]["model"]
best = fitted[best_name]

print(f"Chosen model: {best_name}")
print(f"  Test AUC: {roc_auc_score(y_test, best['y_prob']):.3f}")
print(f"  Dropout recall: {near_best.loc[near_best['model'] == best_name, 'recall_dropouts'].values[0]:.3f}")
print("\\nDetailed errors on the test set:")
print(classification_report(y_test, best["y_pred"], target_names=["left school", "stayed"]))"""
)

cells.append(
    finding(
        """When gradient boosting and logistic regression are within 0.015 AUC, logistic regression is usually selected because it has higher dropout recall (~0.67 vs ~0.33 on this cohort).

Logistic regression is also easier to explain to school staff (coefficients / SHAP). Random forest is not selected despite higher accuracy because it under-detects dropouts. Lower precision on the dropout class is accepted because human review gates any live list."""
    )
)

# --- ROC + confusion ---
cells.append(
    md(
        """### Step 11: ROC and confusion matrix

Visualize ranking quality (ROC) and classification errors for the selected model."""
    )
)

append_code_block(
        """fig, ax = plt.subplots(figsize=(6, 5))
RocCurveDisplay.from_predictions(y_test, best["y_prob"], ax=ax, color="#2A9D8F", name=best_name)
ax.plot([0, 1], [0, 1], "--", color="gray", label="Random guessing")
ax.set_title(f"Ranking quality: {best_name}")
ax.legend()
plt.tight_layout()
plt.show()

cm = confusion_matrix(y_test, best["y_pred"])
plt.figure(figsize=(5.5, 4.5))
sns.heatmap(
    cm, annot=True, fmt="d", cmap="Blues",
    xticklabels=["Predicted left", "Predicted stayed"],
    yticklabels=["Actually left", "Actually stayed"],
)
plt.title("Where the chosen model is right and wrong")
plt.tight_layout()
plt.show()"""
)

cells.append(
    finding(
        """The ROC curve sits above the diagonal; ranking is better than random guessing, though not perfect on synthetic data.

Confusion matrix: top-left = correctly flagged dropouts; top-right = missed dropouts (false negatives); bottom-left = false alarms (extra review); bottom-right = correctly identified stayers. This error profile is acceptable for a review queue where scores allocate support, not deny enrolment."""
    )
)

# --- Fairness ---
cells.append(
    md(
        """### Step 12: Fairness by socioeconomic group

Compute ranking AUC on each socioeconomic slice of the test set."""
    )
)

append_code_block(
        """ses = meta_test["socioeconomic_status_index"].values
fair_rows = []
for q in sorted(np.unique(ses)):
    mask = ses == q
    y_q = y_test.values[mask]
    p_q = best["y_prob"][mask]
    auc = roc_auc_score(y_q, p_q) if len(np.unique(y_q)) > 1 else np.nan
    fair_rows.append({
        "socioeconomic_group": int(q),
        "students_in_test": int(mask.sum()),
        "share_who_stayed": round(float(y_q.mean()), 3),
        "ranking_auc": auc,
    })

fair_df = pd.DataFrame(fair_rows)
display(fair_df)

plt.figure(figsize=(7, 4))
sns.barplot(data=fair_df, x="socioeconomic_group", y="ranking_auc", color="#E9C46A")
plt.axhline(0.5, color="gray", linestyle="--", label="No better than chance")
plt.ylim(0, 1)
plt.xlabel("Socioeconomic group (1 = most constrained)")
plt.ylabel("Ranking AUC on test slice")
plt.title("Model ranking is weaker where retention is already very high")
plt.tight_layout()
plt.show()"""
)

cells.append(
    finding(
        """AUC is often lower in higher socioeconomic groups where almost all students stay (little variation to rank). Lower groups show more dropout variation and more stable AUC.

This does not by itself prove bias, but it requires termly fairness reporting by SES and gender before publishing ranked lists. Retrain or adjust thresholds if slice metrics worsen on partner data."""
    )
)

# --- SHAP ---
cells.append(
    md(
        """### Step 13: Global feature importance (SHAP)

Show which features drive risk scores for operations staff. Uses precomputed SHAP output if available; otherwise model coefficients."""
    )
)

append_code_block(
        """shap_csv = ROOT / "shap_outputs" / "shap_global_importance.csv"
if shap_csv.exists():
    shap_imp = pd.read_csv(shap_csv).head(12)
    if "feature_clean" not in shap_imp.columns:
        shap_imp["feature_clean"] = shap_imp["feature"]
    plt.figure(figsize=(9, 5))
    sns.barplot(data=shap_imp, x="mean_abs_shap", y="feature_clean", color="#264653")
    plt.xlabel("Average influence on risk score")
    plt.title("What drives dropout risk across the cohort")
    plt.tight_layout()
    plt.show()
else:
    print("Full SHAP charts: run python shap_analysis.py after modeling_phase.py")
    m = best["model"]
    if hasattr(m, "coef_"):
        imp = pd.Series(np.abs(m.coef_).ravel(), index=x_test.columns).sort_values(ascending=False).head(12)
        display(imp.to_frame("abs_coefficient"))"""
)

cells.append(
    finding(
        """Top drivers are typically health burden, academic performance combined with SES, commute/barrier measures, and belonging, not fee arrears alone.

Operations should route non-fee needs (health, tutoring) through school/partner channels. Explainability is shown to staff on the analytics surface, not on the helper gift screen. Run `shap_analysis.py` for full beeswarm and dependence plots."""
    )
)

# --- Intervention ---
cells.append(
    md(
        """### Step 14: Intervention queue size

Read intervention summary counts if `intervention_matrix.py` has been run (shows how many students route to each support type)."""
    )
)

append_code_block(
        """intervention_path = ROOT / "intervention_outputs" / "intervention_summary.csv"
if intervention_path.exists():
    inter = pd.read_csv(intervention_path)
    display(inter.sort_values("students", ascending=False))
    fee_row = inter.loc[inter["intervention"] == "School Fee Support"]
    if not fee_row.empty:
        n_fee = int(fee_row["students"].iloc[0])
        print(f"\\nFee-support lane: about {n_fee} students from {len(df):,} in the cohort.")
        print("That scale is intentional: a pilot queue, not a national roll call.")
else:
    print("Build routing tables with: python cluster_personas.py && python intervention_matrix.py")"""
)

cells.append(
    finding(
        """School Fee Support typically covers ~280 students from 1,000, a manageable pilot queue. Other interventions (tutoring, health, digital) have separate counts and are owned by schools/partners.

If the CSV is missing, run `cluster_personas.py` and `intervention_matrix.py` to generate routing tables."""
    )
)

# --- Closing ---
cells.append(
    md(
        """## 15. Conclusion and recommendation

### Summary
1. Retention is imbalanced (~86% stay); use AUC and dropout recall, not accuracy alone.
2. Risk is multi-factor (academic, health, access, SES); fee arrears belong in the ledger, not as the sole model input.
3. Logistic regression is selected when AUC is tied with boosting; higher dropout recall and easier to explain.
4. AUC varies by socioeconomic slice; require termly fairness monitoring.
5. Fee support is one intervention lane; health and academic drivers imply non-fee routing for operations.

### Recommendation
- Deploy logistic regression for an eight-school pilot with human review before any live list.
- Monitor pilot KPIs: gift coverage, settlement integrity, fairness cadence, retention among helped students.
- Retrain on partner school data before scaling beyond the pilot.

### Reproduce full pipeline
```text
python synthetic_data_v2.py
python preprocess_data.py
python modeling_phase.py
python shap_analysis.py
python cluster_personas.py
python intervention_matrix.py
```

**Demo:** https://jesyldah.github.io/ElimuMatch/"""
    )
)

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    },
    "cells": cells,
}

out = Path(__file__).with_name("ElimuMatch_Analysis.ipynb")
out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
print(f"Wrote {out.name} with {len(cells)} cells")
