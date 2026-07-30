"""
SHAP explainability analysis for the Elimu Match retention model.

Generates presentation-ready visuals:
  - Global feature importance (mean |SHAP|)
  - Beeswarm summary (direction of effects)
  - Waterfalls for high-risk / low-risk example students
  - Dependence plots for key drivers

Run:
  python modeling_phase.py   # if best_model.joblib missing
  python shap_analysis.py
"""

from pathlib import Path
import json
import warnings

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from train_retention_model import load_preprocessed

warnings.filterwarnings('ignore')

RANDOM_STATE = 2026
ROOT = Path(__file__).parent
MODEL_PATH = ROOT / 'modeling_outputs' / 'best_model.joblib'
OUT_DIR = ROOT / 'shap_outputs'
VIZ_DIR = ROOT / 'visualizations'
SAMPLE_SIZE = 250  # use full test set if smaller


def clean_name(col: str) -> str:
    return (
        str(col)
        .replace('impute_scale__', '')
        .replace('passthrough__', '')
        .replace('_', ' ')
        .title()
    )


def load_model_and_data():
    if not MODEL_PATH.exists():
        raise FileNotFoundError('Run modeling_phase.py first to create best_model.joblib')

    model = joblib.load(MODEL_PATH)
    data = load_preprocessed()
    x_train = data['x_train']
    x_test = data['x_test']
    y_test = data['y_test']
    meta_test = data['meta_test']

    x_train = x_train.loc[:, ~x_train.columns.str.contains('^Unnamed')]
    x_test = x_test.loc[:, ~x_test.columns.str.contains('^Unnamed')]

    feature_names_raw = list(x_test.columns)
    feature_names_clean = [clean_name(c) for c in feature_names_raw]

    return model, x_train, x_test, y_test, meta_test, feature_names_raw, feature_names_clean


def with_clean_names(shap_values, clean_names: list[str]):
    return shap.Explanation(
        values=np.array(shap_values.values),
        base_values=np.array(shap_values.base_values),
        data=np.array(shap_values.data),
        feature_names=clean_names,
    )


def compute_shap(model, x_train, x_explain):
    """
    Use LinearExplainer for logistic regression (fast, exact for linear models).
    Fall back to general Explainer for tree / other models.
    """
    model_name = type(model).__name__
    if 'Logistic' in model_name or 'Linear' in model_name:
        masker = shap.maskers.Independent(x_train, max_samples=min(200, len(x_train)))
        explainer = shap.LinearExplainer(model, masker)
        shap_values = explainer(x_explain)
    elif hasattr(model, 'feature_importances_') or 'Forest' in model_name or 'Boost' in model_name:
        explainer = shap.Explainer(model, x_train)
        shap_values = explainer(x_explain)
    else:
        # KernelExplainer on a background sample (slower)
        background = shap.sample(x_train, min(100, len(x_train)), random_state=RANDOM_STATE)
        explainer = shap.KernelExplainer(model.predict_proba, background)
        raw = explainer.shap_values(x_explain)
        # For binary classifiers KernelExplainer may return list [class0, class1]
        if isinstance(raw, list):
            values = np.array(raw[1])
        else:
            values = np.array(raw)
        shap_values = shap.Explanation(
            values=values,
            base_values=np.full(len(x_explain), explainer.expected_value[1]
                                if isinstance(explainer.expected_value, (list, np.ndarray))
                                else explainer.expected_value),
            data=x_explain.values,
            feature_names=list(x_explain.columns),
        )

    # For binary classification, prefer positive class (retained=1) contributions
    # LinearExplainer on LogisticRegression returns values for the model output (log-odds of class 1)
    return explainer, shap_values


def shap_for_dropout(shap_values):
    """
    Flip sign so positive SHAP = increases dropout risk (easier for sponsors/stakeholders).
    Model predicts P(retained); stakeholders care about dropout drivers.
    """
    values = -np.array(shap_values.values)
    base = -np.array(shap_values.base_values)
    return shap.Explanation(
        values=values,
        base_values=base,
        data=shap_values.data,
        feature_names=shap_values.feature_names,
    )


def mean_abs_importance(shap_values) -> pd.DataFrame:
    vals = np.abs(shap_values.values).mean(axis=0)
    return (
        pd.DataFrame({
            'feature': shap_values.feature_names,
            'mean_abs_shap': vals,
        })
        .sort_values('mean_abs_shap', ascending=False)
        .reset_index(drop=True)
    )


def plot_global_importance(shap_drop, top_n: int = 15):
    importance = mean_abs_importance(shap_drop).head(top_n)
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(importance['feature'][::-1], importance['mean_abs_shap'][::-1], color='#264653')
    ax.set_xlabel('Mean |SHAP| (impact on dropout risk)')
    ax.set_title('SHAP Global Feature Importance\nWhat drives predicted dropout risk?', fontweight='bold')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '31_shap_global_importance.png', dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return importance


def plot_beeswarm(shap_drop):
    plt.figure(figsize=(10, 8))
    shap.plots.beeswarm(shap_drop, max_display=15, show=False)
    plt.title('SHAP Beeswarm — Feature Effects on Dropout Risk', fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(VIZ_DIR / '32_shap_beeswarm.png', dpi=160, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_bar_summary(shap_drop):
    plt.figure(figsize=(10, 7))
    shap.plots.bar(shap_drop, max_display=15, show=False)
    plt.title('SHAP Summary Bar — Average Impact Magnitude', fontweight='bold', pad=12)
    plt.tight_layout()
    plt.savefig(VIZ_DIR / '33_shap_bar_summary.png', dpi=160, bbox_inches='tight', facecolor='white')
    plt.close()


def plot_waterfalls(shap_drop, y_test, meta_test, probs_dropout):
    """Waterfalls for one high-risk and one low-risk student."""
    y = np.asarray(y_test)
    # Highest predicted dropout among actual dropouts (or overall if none)
    dropped_idx = np.where(y == 0)[0]
    if len(dropped_idx):
        high_i = dropped_idx[np.argmax(probs_dropout[dropped_idx])]
    else:
        high_i = int(np.argmax(probs_dropout))

    retained_idx = np.where(y == 1)[0]
    if len(retained_idx):
        low_i = retained_idx[np.argmin(probs_dropout[retained_idx])]
    else:
        low_i = int(np.argmin(probs_dropout))

    cases = [
        (high_i, '34_shap_waterfall_high_risk.png',
         'SHAP Waterfall — High Dropout Risk Student'),
        (low_i, '35_shap_waterfall_low_risk.png',
         'SHAP Waterfall — Low Dropout Risk Student'),
    ]

    case_rows = []
    for idx, filename, title in cases:
        plt.figure(figsize=(10, 7))
        shap.plots.waterfall(shap_drop[idx], max_display=12, show=False)
        sid = int(meta_test.iloc[idx]['student_id']) if 'student_id' in meta_test.columns else int(idx)
        school = int(meta_test.iloc[idx]['school_id']) if 'school_id' in meta_test.columns else ''
        plt.title(f'{title}\nStudent #{sid} · School {school} · P(dropout)={probs_dropout[idx]:.2f}',
                  fontweight='bold', pad=12)
        plt.tight_layout()
        plt.savefig(VIZ_DIR / filename, dpi=160, bbox_inches='tight', facecolor='white')
        plt.close()

        # Top contributing features for this case
        sv = shap_drop.values[idx]
        names = shap_drop.feature_names
        order = np.argsort(-np.abs(sv))[:8]
        case_rows.append({
            'student_id': sid,
            'school_id': school,
            'prob_dropout': round(float(probs_dropout[idx]), 4),
            'actual_retained': int(y[idx]),
            'case': 'high_risk' if idx == high_i else 'low_risk',
            'top_features': [
                {'feature': str(names[j]), 'shap': round(float(sv[j]), 4)}
                for j in order
            ],
        })

    return case_rows


def plot_dependence(shap_drop, feature_candidates: list[str]):
    available = list(shap_drop.feature_names)
    plotted = []
    for feat in feature_candidates:
        if feat not in available:
            continue
        plt.figure(figsize=(8, 5.5))
        shap.plots.scatter(shap_drop[:, feat], color=shap_drop, show=False)
        plt.title(f'SHAP Dependence — {feat}', fontweight='bold')
        plt.tight_layout()
        slug = feat.lower().replace(' ', '_').replace('/', '_')[:40]
        fname = f'36_shap_dependence_{slug}.png'
        # Keep only first 2 dependence plots with fixed names for dashboard
        plotted.append((feat, fname))
        plt.savefig(VIZ_DIR / fname, dpi=160, bbox_inches='tight', facecolor='white')
        plt.close()
        if len(plotted) >= 2:
            break

    # Also save canonical names for dashboard wiring
    if plotted:
        # Copy/rename first two to stable filenames
        import shutil
        stable = [
            '36_shap_dependence_1.png',
            '37_shap_dependence_2.png',
        ]
        for i, (_, fname) in enumerate(plotted[:2]):
            src = VIZ_DIR / fname
            dst = VIZ_DIR / stable[i]
            if src != dst and src.exists():
                shutil.copy(src, dst)
    return plotted


def main():
    OUT_DIR.mkdir(exist_ok=True)
    VIZ_DIR.mkdir(exist_ok=True)

    print('=' * 72)
    print('SHAP EXPLAINABILITY — ELIMU MATCH')
    print('=' * 72)

    model, x_train, x_test, y_test, meta_test, feature_names_raw, feature_names_clean = load_model_and_data()
    print(f'Model: {type(model).__name__}')
    print(f'Test rows: {len(x_test)} | Features: {len(feature_names_raw)}')

    # Explain on test set (capped)
    n = min(SAMPLE_SIZE, len(x_test))
    x_explain = x_test.iloc[:n].copy()
    y_explain = y_test.iloc[:n].reset_index(drop=True)
    meta_explain = meta_test.iloc[:n].reset_index(drop=True)

    print('Computing SHAP values...')
    explainer, shap_values = compute_shap(model, x_train, x_explain)
    shap_values = with_clean_names(shap_values, feature_names_clean)
    shap_drop = shap_for_dropout(shap_values)

    # Dropout probabilities from model (original feature names)
    probs_retained = model.predict_proba(x_explain)[:, 1]
    probs_dropout = 1 - probs_retained

    print('Generating plots...')
    importance = plot_global_importance(shap_drop)
    plot_beeswarm(shap_drop)
    plot_bar_summary(shap_drop)
    cases = plot_waterfalls(shap_drop, y_explain, meta_explain, probs_dropout)

    # Dependence on top drivers that exist
    top_feats = importance['feature'].head(8).tolist()
    preferred = [
        f for f in [
            'Socioeconomic Status Index',
            'Cash Flow Volatility',
            'Failed Subjects Count',
            'Gpa Trend',
            'Commute Barrier Score',
            'Health Related Absences',
            'Academic Risk Index',
            'Barrier Burden Index',
            'Health Burden Index',
        ] if f in top_feats or f in shap_drop.feature_names
    ]
    dep = plot_dependence(shap_drop, preferred[:4] if preferred else top_feats[:2])

    # Persist tables
    importance.to_csv(OUT_DIR / 'shap_global_importance.csv', index=False)
    with open(OUT_DIR / 'shap_example_cases.json', 'w', encoding='utf-8') as f:
        json.dump(cases, f, indent=2)

    report = {
        'model': type(model).__name__,
        'n_explained': n,
        'orientation': 'SHAP values flipped so positive = increases dropout risk',
        'top_features': importance.head(10).to_dict(orient='records'),
        'example_cases': cases,
        'dependence_features': [f for f, _ in dep],
        'plots': [
            '31_shap_global_importance.png',
            '32_shap_beeswarm.png',
            '33_shap_bar_summary.png',
            '34_shap_waterfall_high_risk.png',
            '35_shap_waterfall_low_risk.png',
            '36_shap_dependence_1.png',
            '37_shap_dependence_2.png',
        ],
    }
    with open(OUT_DIR / 'shap_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Short markdown for slides
    md = [
        '# SHAP Explainability — Elimu Match',
        '',
        f'Model explained: **{type(model).__name__}** (selected retention classifier).',
        '',
        'SHAP values are oriented so **positive = higher dropout risk** (easier for sponsor/school audiences).',
        '',
        '## Top global drivers',
        '',
    ]
    for i, row in importance.head(8).iterrows():
        md.append(f"{i+1}. **{row['feature']}** — mean |SHAP| = {row['mean_abs_shap']:.3f}")
    md += [
        '',
        '## Presentation visuals',
        '- Global importance bar',
        '- Beeswarm (direction of effects)',
        '- Waterfall: high-risk vs low-risk student',
        '- Dependence plots for key economic/academic drivers',
        '',
        '## Talking point',
        'SHAP shows *why* a student is flagged — e.g. cash-flow volatility and low SES push fee-support',
        'candidates up the list, while strong academics and support coverage pull risk down.',
        '',
    ]
    (OUT_DIR / 'SHAP_REPORT.md').write_text('\n'.join(md), encoding='utf-8')

    print('\nTop SHAP drivers (dropout risk):')
    print(importance.head(10).to_string(index=False))
    print(f'\nOutputs: {OUT_DIR}/')
    print('Charts: visualizations/31–37')


if __name__ == '__main__':
    main()
