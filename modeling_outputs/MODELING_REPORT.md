# Modeling Phase Report — Elimu Match

## Objective
Predict whether a secondary student will be **retained** (`retained = 1`) using leakage-safe features,
so sponsors and schools can prioritize support (especially school-fee assistance).

## Data
- Source: preprocessed train/test splits (`preprocessed/`)
- Target: `retained`
- Excluded from features: `retention_risk_score`, `dropout_reason`, `academic_catchup_status`, `student_id`
- Class balance: ~86% retained / ~14% dropped (imbalanced)

## Models
1. Majority-class baseline
2. Logistic Regression (balanced, tuned `C`)
3. Random Forest (balanced, tuned depth / trees / leaf size)
4. Histogram Gradient Boosting (balanced, tuned depth / LR / iterations)

Selection rule: highest test AUC; if models are within **0.015 AUC**, prefer higher **dropout recall**
(business priority = find students who need help).

## Leaderboard (test set)

| model | cv_auc_mean | cv_auc_std | test_auc | accuracy | recall_dropout | precision_dropout | f1_dropout | recall_retained |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Gradient Boosting | 0.7354 | 0.0363 | 0.7543 | 0.808 | 0.3333 | 0.3333 | 0.3333 | 0.8879 |
| Logistic Regression | 0.7621 | 0.0418 | 0.7527 | 0.708 | 0.6667 | 0.2824 | 0.3967 | 0.715 |
| Random Forest | 0.7694 | 0.0428 | 0.7421 | 0.844 | 0.0833 | 0.3333 | 0.1333 | 0.972 |
| Majority Class Baseline | 0.5 | 0.0 | 0.5 | 0.856 | 0.0 | 0.0 | 0.0 | 1.0 |

## Selected model: **Logistic Regression**
- Test AUC: **0.753**
- Dropout recall: **0.667**
- Dropout precision: **0.282**
- CV AUC (train): **0.762 ± 0.042**
- Best params: `{'C': 0.1}`

## Fairness — AUC by SES quintile

| ses_quintile | n | retention_rate | auc |
| --- | --- | --- | --- |
| 1.0 | 62.0 | 0.742 | 0.66 |
| 2.0 | 64.0 | 0.797 | 0.739 |
| 3.0 | 55.0 | 0.945 | 0.667 |
| 4.0 | 37.0 | 0.919 | 0.647 |
| 5.0 | 32.0 | 0.969 | 0.548 |

## Business interpretation
- Use predicted dropout probability (1 − P(retained)) to rank students for outreach.
- Route high-risk + low-SES students to **school fee support** via the sponsor portal.
- Pair Academic Strugglers / Health-Constrained personas with non-fee interventions when fees are not the primary barrier.

## Limitations
- Synthetic cohort PoC — validate on partner data before deployment.
- Class imbalance: accuracy alone is misleading; prefer AUC + dropout recall.
- Engineered features can be collinear with base features; tree models handle this better than unregularized linear models.
