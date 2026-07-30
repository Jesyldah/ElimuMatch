"""
Modeling phase — Elimu Match student retention classifier.

Full Quantic-ready modeling workflow:
  1. Load leakage-safe preprocessed features
  2. Train baseline + candidate models
  3. Cross-validate and tune
  4. Evaluate on held-out test set
  5. Fairness check by SES quintile
  6. Persist best model, metrics, and charts

Run:
  python preprocess_data.py   # if needed
  python modeling_phase.py
"""

from pathlib import Path
import json
import warnings

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_score

from train_retention_model import load_preprocessed

warnings.filterwarnings('ignore', category=UserWarning)

RANDOM_STATE = 2026
CV_FOLDS = 5
OUTPUT_DIR = Path(__file__).with_name('modeling_outputs')
VIZ_DIR = Path(__file__).with_name('visualizations')
TARGET = 'retained'

# Business priority: catch students who will drop (class 0)
DROPOUT_LABEL = 0


def clean_name(col: str) -> str:
    return (
        col.replace('impute_scale__', '')
        .replace('passthrough__', '')
        .replace('_', ' ')
        .title()
    )


def evaluate_predictions(y_true, y_prob, y_pred) -> dict:
    """Metrics oriented to retention (1) and dropout detection (0)."""
    return {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        'auc': float(roc_auc_score(y_true, y_prob)),
        'avg_precision_retained': float(average_precision_score(y_true, y_prob)),
        # Dropout = class 0: use 1 - prob as score for AP on dropout
        'avg_precision_dropout': float(average_precision_score(1 - y_true, 1 - y_prob)),
        'precision_dropout': float(precision_score(y_true, y_pred, pos_label=DROPOUT_LABEL, zero_division=0)),
        'recall_dropout': float(recall_score(y_true, y_pred, pos_label=DROPOUT_LABEL, zero_division=0)),
        'f1_dropout': float(f1_score(y_true, y_pred, pos_label=DROPOUT_LABEL, zero_division=0)),
        'precision_retained': float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
        'recall_retained': float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
        'f1_retained': float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)),
    }


def auc_by_ses(meta_test: pd.DataFrame, y_true: pd.Series, y_prob: np.ndarray) -> pd.DataFrame:
    rows = []
    ses = meta_test['socioeconomic_status_index'].values
    y = np.asarray(y_true)
    for q in sorted(np.unique(ses)):
        mask = ses == q
        y_q = y[mask]
        if len(np.unique(y_q)) < 2:
            auc = np.nan
        else:
            auc = roc_auc_score(y_q, y_prob[mask])
        rows.append({
            'ses_quintile': int(q),
            'n': int(mask.sum()),
            'retention_rate': round(float(y_q.mean()), 3),
            'auc': None if np.isnan(auc) else round(float(auc), 3),
        })
    return pd.DataFrame(rows)


def get_model_specs() -> dict:
    return {
        'Majority Class Baseline': {
            'estimator': DummyClassifier(strategy='most_frequent', random_state=RANDOM_STATE),
            'param_grid': None,
        },
        'Logistic Regression': {
            'estimator': LogisticRegression(
                max_iter=3000, random_state=RANDOM_STATE, class_weight='balanced',
            ),
            'param_grid': {
                'C': [0.1, 0.5, 1.0, 2.0],
            },
        },
        'Random Forest': {
            'estimator': RandomForestClassifier(random_state=RANDOM_STATE, class_weight='balanced'),
            'param_grid': {
                'n_estimators': [200, 400],
                'max_depth': [6, 10, None],
                'min_samples_leaf': [2, 5],
            },
        },
        'Gradient Boosting': {
            'estimator': HistGradientBoostingClassifier(
                random_state=RANDOM_STATE,
                class_weight='balanced',
            ),
            'param_grid': {
                'max_depth': [3, 6],
                'learning_rate': [0.05, 0.1],
                'max_iter': [150, 300],
            },
        },
    }


def train_and_tune(name: str, spec: dict, x_train, y_train, cv) -> tuple:
    estimator = spec['estimator']
    grid = spec['param_grid']

    if grid is None:
        estimator.fit(x_train, y_train)
        cv_auc = cross_val_score(estimator, x_train, y_train, cv=cv, scoring='roc_auc')
        return estimator, {
            'best_params': {},
            'cv_auc_mean': float(cv_auc.mean()),
            'cv_auc_std': float(cv_auc.std()),
        }

    search = GridSearchCV(
        estimator,
        grid,
        scoring='roc_auc',
        cv=cv,
        n_jobs=-1,
        refit=True,
    )
    search.fit(x_train, y_train)
    return search.best_estimator_, {
        'best_params': search.best_params_,
        'cv_auc_mean': float(search.best_score_),
        'cv_auc_std': float(search.cv_results_['std_test_score'][search.best_index_]),
    }


def feature_importance(model, feature_names: list[str]) -> pd.DataFrame | None:
    if hasattr(model, 'feature_importances_'):
        vals = model.feature_importances_
    elif hasattr(model, 'coef_'):
        vals = np.abs(model.coef_).ravel()
    else:
        return None
    return (
        pd.DataFrame({'feature': feature_names, 'importance': vals})
        .assign(feature_clean=lambda d: d['feature'].map(clean_name))
        .sort_values('importance', ascending=False)
    )


def plot_model_comparison(leaderboard: pd.DataFrame) -> None:
    VIZ_DIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    plot_df = leaderboard[leaderboard['model'] != 'Majority Class Baseline'].copy()
    sns.barplot(data=plot_df, x='model', y='test_auc', color='#264653', ax=axes[0])
    axes[0].axhline(
        leaderboard.loc[leaderboard['model'] == 'Majority Class Baseline', 'test_auc'].values[0],
        color='#8D99AE', linestyle='--', label='Baseline AUC',
    )
    axes[0].set_ylim(0, 1)
    axes[0].set_title('Test AUC by Model')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('AUC')
    axes[0].tick_params(axis='x', rotation=15)
    axes[0].legend()

    sns.barplot(data=plot_df, x='model', y='recall_dropout', color='#E76F51', ax=axes[1])
    axes[1].set_ylim(0, 1)
    axes[1].set_title('Dropout Recall (business priority)')
    axes[1].set_xlabel('')
    axes[1].set_ylabel('Recall (class = dropped)')
    axes[1].tick_params(axis='x', rotation=15)

    fig.suptitle('Modeling Phase — Model Comparison', fontweight='bold')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '20_modeling_comparison.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def plot_best_diagnostics(y_test, y_prob, y_pred, importance: pd.DataFrame | None, ses_auc: pd.DataFrame, best_name: str) -> None:
    # ROC
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color='#2A9D8F', lw=2, label=f'{best_name} (AUC={roc_auc_score(y_test, y_prob):.3f})')
    ax.plot([0, 1], [0, 1], '--', color='#8D99AE')
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title(f'ROC Curve — {best_name}', fontweight='bold')
    ax.legend(loc='lower right')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '21_modeling_roc.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues', ax=ax,
        xticklabels=['Pred Dropped', 'Pred Retained'],
        yticklabels=['Actual Dropped', 'Actual Retained'],
    )
    ax.set_title(f'Confusion Matrix — {best_name}', fontweight='bold')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '22_modeling_confusion.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

    # Feature importance
    if importance is not None:
        top = importance.head(15)
        fig, ax = plt.subplots(figsize=(10, 7))
        sns.barplot(data=top, x='importance', y='feature_clean', color='#264653', ax=ax)
        ax.set_title(f'Top Features — {best_name}', fontweight='bold')
        ax.set_xlabel('Importance')
        ax.set_ylabel('')
        fig.tight_layout()
        fig.savefig(VIZ_DIR / '23_modeling_feature_importance.png', dpi=160, bbox_inches='tight')
        plt.close(fig)

    # Fairness
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=ses_auc, x='ses_quintile', y='auc', color='#E9C46A', ax=ax)
    ax.axhline(0.5, color='#8D99AE', linestyle='--')
    ax.set_ylim(0, 1)
    ax.set_xlabel('SES Quintile')
    ax.set_ylabel('AUC')
    ax.set_title(f'Fairness — AUC by SES ({best_name})', fontweight='bold')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '24_modeling_fairness_ses.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def df_to_md(df: pd.DataFrame) -> str:
    """Simple markdown table without tabulate dependency."""
    cols = list(df.columns)
    header = '| ' + ' | '.join(str(c) for c in cols) + ' |'
    sep = '| ' + ' | '.join('---' for _ in cols) + ' |'
    lines = [header, sep]
    for _, row in df.iterrows():
        lines.append('| ' + ' | '.join(str(row[c]) for c in cols) + ' |')
    return '\n'.join(lines)


def write_markdown_report(leaderboard: pd.DataFrame, best: dict, ses_auc: pd.DataFrame) -> None:
    lines = [
        '# Modeling Phase Report — Elimu Match',
        '',
        '## Objective',
        'Predict whether a secondary student will be **retained** (`retained = 1`) using leakage-safe features,',
        'so sponsors and schools can prioritize support (especially school-fee assistance).',
        '',
        '## Data',
        '- Source: preprocessed train/test splits (`preprocessed/`)',
        '- Target: `retained`',
        '- Excluded from features: `retention_risk_score`, `dropout_reason`, `academic_catchup_status`, `student_id`',
        '- Class balance: ~86% retained / ~14% dropped (imbalanced)',
        '',
        '## Models',
        '1. Majority-class baseline',
        '2. Logistic Regression (balanced, tuned `C`)',
        '3. Random Forest (balanced, tuned depth / trees / leaf size)',
        '4. Histogram Gradient Boosting (balanced, tuned depth / LR / iterations)',
        '',
        'Selection rule: highest test AUC; if models are within **0.015 AUC**, prefer higher **dropout recall**',
        '(business priority = find students who need help).',
        '',
        '## Leaderboard (test set)',
        '',
        df_to_md(leaderboard),
        '',
        f"## Selected model: **{best['model']}**",
        f"- Test AUC: **{best['test_auc']:.3f}**",
        f"- Dropout recall: **{best['recall_dropout']:.3f}**",
        f"- Dropout precision: **{best['precision_dropout']:.3f}**",
        f"- CV AUC (train): **{best['cv_auc_mean']:.3f} ± {best['cv_auc_std']:.3f}**",
        f"- Best params: `{best['best_params']}`",
        '',
        '## Fairness — AUC by SES quintile',
        '',
        df_to_md(ses_auc),
        '',
        '## Business interpretation',
        '- Use predicted dropout probability (1 − P(retained)) to rank students for outreach.',
        '- Route high-risk + low-SES students to **school fee support** via the sponsor portal.',
        '- Pair Academic Strugglers / Health-Constrained personas with non-fee interventions when fees are not the primary barrier.',
        '',
        '## Limitations',
        '- Synthetic cohort PoC — validate on partner data before deployment.',
        '- Class imbalance: accuracy alone is misleading; prefer AUC + dropout recall.',
        '- Engineered features can be collinear with base features; tree models handle this better than unregularized linear models.',
        '',
    ]
    (OUTPUT_DIR / 'MODELING_REPORT.md').write_text('\n'.join(lines), encoding='utf-8')



def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    VIZ_DIR.mkdir(exist_ok=True)

    data = load_preprocessed()
    x_train = data['x_train']
    x_test = data['x_test']
    y_train = data['y_train']
    y_test = data['y_test']
    meta_test = data['meta_test']

    # Drop unnamed index columns if present from CSV round-trip
    x_train = x_train.loc[:, ~x_train.columns.str.contains('^Unnamed')]
    x_test = x_test.loc[:, ~x_test.columns.str.contains('^Unnamed')]

    print('=' * 72)
    print('MODELING PHASE — ELIMU MATCH RETENTION')
    print('=' * 72)
    print(f'Train: {len(x_train):,} | Test: {len(x_test):,} | Features: {x_train.shape[1]}')
    print(f'Train retention rate: {y_train.mean():.1%} | Test: {y_test.mean():.1%}')

    cv = StratifiedKFold(n_splits=CV_FOLDS, shuffle=True, random_state=RANDOM_STATE)
    specs = get_model_specs()

    rows = []
    fitted = {}

    for name, spec in specs.items():
        print(f'\nTraining {name}...')
        model, tune_info = train_and_tune(name, spec, x_train, y_train, cv)

        if name == 'Majority Class Baseline':
            # Dummy most_frequent has no useful probabilities for minority class
            y_pred = model.predict(x_test)
            # Constant retained probability = train base rate
            y_prob = np.full(len(y_test), float(y_train.mean()))
        else:
            y_prob = model.predict_proba(x_test)[:, 1]
            y_pred = model.predict(x_test)

        metrics = evaluate_predictions(y_test, y_prob, y_pred)
        row = {
            'model': name,
            'cv_auc_mean': round(tune_info['cv_auc_mean'], 4),
            'cv_auc_std': round(tune_info['cv_auc_std'], 4),
            'test_auc': round(metrics['auc'], 4),
            'accuracy': round(metrics['accuracy'], 4),
            'recall_dropout': round(metrics['recall_dropout'], 4),
            'precision_dropout': round(metrics['precision_dropout'], 4),
            'f1_dropout': round(metrics['f1_dropout'], 4),
            'recall_retained': round(metrics['recall_retained'], 4),
            'best_params': tune_info['best_params'],
        }
        rows.append(row)
        fitted[name] = {'model': model, 'y_prob': y_prob, 'y_pred': y_pred, 'metrics': metrics, **tune_info}

        print(f"  CV AUC: {row['cv_auc_mean']:.3f} ± {row['cv_auc_std']:.3f}")
        print(f"  Test AUC: {row['test_auc']:.3f} | Dropout recall: {row['recall_dropout']:.3f}")
        if tune_info['best_params']:
            print(f"  Best params: {tune_info['best_params']}")

    leaderboard = pd.DataFrame(rows).sort_values('test_auc', ascending=False)
    # Business-aware selection: among near-tied AUC models, prefer dropout recall
    candidates = leaderboard[leaderboard['model'] != 'Majority Class Baseline'].copy()
    top_auc = candidates['test_auc'].max()
    near_best = candidates[candidates['test_auc'] >= top_auc - 0.015]
    best_name = near_best.sort_values(
        ['recall_dropout', 'test_auc'], ascending=[False, False],
    ).iloc[0]['model']
    best_row = candidates[candidates['model'] == best_name].iloc[0].to_dict()
    best_fit = fitted[best_name]

    print('\n' + '=' * 72)
    print('LEADERBOARD')
    print('=' * 72)
    print(leaderboard.drop(columns=['best_params']).to_string(index=False))
    print(f"\nSelected model: {best_name}")

    print('\nClassification report (selected model):')
    print(classification_report(
        y_test, best_fit['y_pred'], target_names=['dropped', 'retained'],
    ))

    ses_auc = auc_by_ses(meta_test, y_test, best_fit['y_prob'])
    print('AUC by SES quintile:')
    print(ses_auc.to_string(index=False))

    importance = feature_importance(best_fit['model'], x_train.columns.tolist())
    if importance is not None:
        importance.to_csv(OUTPUT_DIR / 'feature_importance.csv', index=False)
        print('\nTop 10 features:')
        print(importance.head(10)[['feature_clean', 'importance']].to_string(index=False))

    # Persist artifacts
    joblib.dump(best_fit['model'], OUTPUT_DIR / 'best_model.joblib')
    leaderboard.to_csv(OUTPUT_DIR / 'model_leaderboard.csv', index=False)
    ses_auc.to_csv(OUTPUT_DIR / 'fairness_auc_by_ses.csv', index=False)

    pred_out = meta_test.copy()
    pred_out['y_true'] = y_test.values
    pred_out['y_pred'] = best_fit['y_pred']
    pred_out['prob_retained'] = best_fit['y_prob']
    pred_out['prob_dropout'] = 1 - best_fit['y_prob']
    pred_out.to_csv(OUTPUT_DIR / 'test_predictions.csv', index=False)

    report = {
        'objective': 'Predict student retention (binary classification)',
        'selected_model': best_name,
        'best_params': best_row['best_params'],
        'test_metrics': best_fit['metrics'],
        'cv_auc_mean': best_row['cv_auc_mean'],
        'cv_auc_std': best_row['cv_auc_std'],
        'leaderboard': leaderboard.to_dict(orient='records'),
        'fairness_by_ses': ses_auc.to_dict(orient='records'),
        'n_train': int(len(x_train)),
        'n_test': int(len(x_test)),
        'n_features': int(x_train.shape[1]),
        'random_state': RANDOM_STATE,
    }
    with open(OUTPUT_DIR / 'modeling_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)

    write_markdown_report(leaderboard.drop(columns=['best_params']), best_row, ses_auc)
    plot_model_comparison(leaderboard)
    plot_best_diagnostics(
        y_test, best_fit['y_prob'], best_fit['y_pred'],
        importance, ses_auc, best_name,
    )

    print(f'\nArtifacts saved to {OUTPUT_DIR}/')
    print('Charts: visualizations/20–24')
    print('Report: modeling_outputs/MODELING_REPORT.md')


if __name__ == '__main__':
    main()
