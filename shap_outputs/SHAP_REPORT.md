# SHAP Explainability — Elimu Match

Model explained: **LogisticRegression** (selected retention classifier).

SHAP values are oriented so **positive = higher dropout risk** (easier for sponsor/school audiences).

## Top global drivers

1. **Chronic Health Risk Score** — mean |SHAP| = 0.322
2. **Health Burden Index** — mean |SHAP| = 0.296
3. **Academic Ses Interaction** — mean |SHAP| = 0.284
4. **Social Integration Score** — mean |SHAP| = 0.222
5. **Barrier Burden Index** — mean |SHAP| = 0.214
6. **Health Related Absences** — mean |SHAP| = 0.209
7. **Cash Flow Volatility** — mean |SHAP| = 0.206
8. **Long Commute Flag** — mean |SHAP| = 0.144

## Presentation visuals
- Global importance bar
- Beeswarm (direction of effects)
- Waterfall: high-risk vs low-risk student
- Dependence plots for key economic/academic drivers

## Talking point
SHAP shows *why* a student is flagged — e.g. cash-flow volatility and low SES push fee-support
candidates up the list, while strong academics and support coverage pull risk down.
