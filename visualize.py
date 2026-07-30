"""
Generate capstone-ready visualizations for the Elimu Match retention analytics pipeline.

Outputs saved to visualizations/

Run order:
  python synthetic_data_v2.py   (if needed)
  python preprocess_data.py     (if needed)
  python visualize.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    RocCurveDisplay,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)

from feature_engineering import ENGINEERED_FEATURES, engineer_features
from preprocess_data import DATA_PATH, PREPROCESSED_DIR, TARGET, preprocess
from train_retention_model import RANDOM_STATE, load_preprocessed

OUTPUT_DIR = Path(__file__).with_name('visualizations')

# Cohesive palette for capstone deck
COLORS = {
    'retained': '#2A9D8F',
    'dropped': '#E76F51',
    'accent': '#264653',
    'muted': '#8D99AE',
    'highlight': '#E9C46A',
    'ses_gradient': ['#d62828', '#f77f00', '#fcbf49', '#90be6d', '#277da1'],
}


def _setup_theme() -> None:
    sns.set_theme(style='whitegrid', context='talk', font_scale=0.85)
    plt.rcParams.update({
        'figure.facecolor': 'white',
        'axes.facecolor': '#FAFAFA',
        'axes.edgecolor': '#CCCCCC',
        'grid.alpha': 0.35,
        'font.family': 'sans-serif',
    })


def _save(fig: plt.Figure, name: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  saved {path.name}')


def _clean_feature_name(name: str) -> str:
    return (
        name.replace('impute_scale__', '')
        .replace('passthrough__', '')
        .replace('_', ' ')
        .title()
    )


def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(DATA_PATH)
    enriched = engineer_features(raw)
    return raw, enriched


def plot_cohort_overview(enriched: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    retained_pct = enriched['retained'].mean() * 100
    axes[0].pie(
        enriched['retained'].value_counts().sort_index(),
        labels=['Dropped', 'Retained'],
        colors=[COLORS['dropped'], COLORS['retained']],
        autopct='%1.1f%%',
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2},
    )
    axes[0].set_title(f'Cohort Retention\n(n = {len(enriched):,})')

    sns.countplot(
        data=enriched, x='socioeconomic_status_index', hue='retained',
        palette=[COLORS['dropped'], COLORS['retained']], ax=axes[1],
    )
    axes[1].set_title('Students by SES Quintile')
    axes[1].set_xlabel('SES Quintile (1 = lowest)')
    axes[1].set_ylabel('Count')
    axes[1].legend(title='Status', loc='upper right')

    dropout = enriched.loc[enriched['retained'] == 0, 'dropout_reason'].value_counts()
    dropout.index = [label.replace('_', ' ').title() for label in dropout.index]
    sns.barplot(x=dropout.values, y=dropout.index, color=COLORS['dropped'], ax=axes[2])
    axes[2].set_title('Dropout Drivers')
    axes[2].set_xlabel('Students')

    fig.suptitle('Elimu Match — Cohort Overview', fontsize=16, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save(fig, '01_cohort_overview.png')


def plot_retention_by_ses(enriched: pd.DataFrame) -> None:
    ses = (
        enriched.groupby('socioeconomic_status_index')['retained']
        .agg(['mean', 'count'])
        .reset_index()
    )
    ses['retention_pct'] = ses['mean'] * 100

    fig, ax = plt.subplots(figsize=(9, 5.5))
    bars = ax.bar(
        ses['socioeconomic_status_index'].astype(str),
        ses['retention_pct'],
        color=COLORS['ses_gradient'],
        edgecolor='white',
        linewidth=1.5,
    )
    for bar, (_, row) in zip(bars, ses.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2,
            f"{row['retention_pct']:.1f}%\n(n={int(row['count'])})",
            ha='center', va='bottom', fontsize=10,
        )
    ax.axhline(enriched['retained'].mean() * 100, color=COLORS['accent'],
               linestyle='--', linewidth=1.5, label=f"Cohort avg ({enriched['retained'].mean():.1%})")
    ax.set_ylim(0, 105)
    ax.set_xlabel('SES Quintile')
    ax.set_ylabel('Retention Rate (%)')
    ax.set_title('Retention Gradient by Socioeconomic Status', fontweight='bold')
    ax.legend()
    fig.tight_layout()
    _save(fig, '02_retention_by_ses.png')


def plot_key_distributions(enriched: pd.DataFrame) -> None:
    vars_to_plot = [
        ('gpa_trend', 'GPA Trend'),
        ('failed_subjects_count', 'Failed Subjects'),
        ('commute_barrier_score', 'Commute Distance (km)'),
        ('health_related_absences', 'Health Absences (days)'),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    for ax, (col, label) in zip(axes.ravel(), vars_to_plot):
        sns.kdeplot(
            data=enriched, x=col, hue='retained', fill=True, alpha=0.45,
            palette=[COLORS['dropped'], COLORS['retained']], ax=ax, common_norm=False,
        )
        ax.set_title(label)
        ax.set_xlabel(label)
        ax.legend(['Dropped', 'Retained'], title='Status')
    fig.suptitle('Key Variable Distributions by Retention Status', fontweight='bold', y=1.01)
    fig.tight_layout()
    _save(fig, '03_distributions_by_retention.png')


def plot_missingness(enriched: pd.DataFrame) -> None:
    miss_cols = [
        'cash_flow_volatility', 'commute_barrier_score',
        'digital_equity_access_score', 'psychosocial_support_access',
    ]
    records = []
    for col in miss_cols:
        for ses in sorted(enriched['socioeconomic_status_index'].unique()):
            mask = enriched['socioeconomic_status_index'] == ses
            rate = enriched.loc[mask, col].isna().mean() * 100
            records.append({'field': col.replace('_', ' ').title(), 'ses': f'Q{ses}', 'missing_pct': rate})
    miss_df = pd.DataFrame(records)

    fig, ax = plt.subplots(figsize=(11, 5.5))
    sns.barplot(data=miss_df, x='field', y='missing_pct', hue='ses', palette='YlOrRd', ax=ax)
    ax.set_title('Survey Field Missingness by SES Quintile', fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('Missing (%)')
    ax.legend(title='SES', bbox_to_anchor=(1.02, 1), loc='upper left')
    fig.tight_layout()
    _save(fig, '04_missingness_by_ses.png')


def plot_engineered_features(enriched: pd.DataFrame) -> None:
    corr = (
        enriched[ENGINEERED_FEATURES + ['retained']]
        .corr(numeric_only=True)['retained']
        .drop('retained')
        .sort_values()
    )
    corr.index = [_clean_feature_name(c) for c in corr.index]
    colors = [COLORS['retained'] if v > 0 else COLORS['dropped'] for v in corr.values]

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(corr.index, corr.values, color=colors, edgecolor='white')
    ax.axvline(0, color=COLORS['accent'], linewidth=1)
    ax.set_xlabel('Correlation with Retained')
    ax.set_title('Engineered Features vs. Retention Outcome', fontweight='bold')
    fig.tight_layout()
    _save(fig, '05_engineered_feature_correlations.png')

    fig, ax = plt.subplots(figsize=(9, 6))
    sns.scatterplot(
        data=enriched.sample(min(600, len(enriched)), random_state=RANDOM_STATE),
        x='academic_risk_index', y='barrier_burden_index',
        hue='retained', palette=[COLORS['dropped'], COLORS['retained']],
        alpha=0.55, ax=ax,
    )
    ax.set_title('Academic Risk vs. Access Barriers', fontweight='bold')
    ax.set_xlabel('Academic Risk Index')
    ax.set_ylabel('Barrier Burden Index')
    ax.legend(title='Retained', labels=['No', 'Yes'])
    fig.tight_layout()
    _save(fig, '06_risk_landscape_scatter.png')


def plot_correlation_heatmap(enriched: pd.DataFrame) -> None:
    predictors = [
        'socioeconomic_status_index', 'gpa_trend', 'failed_subjects_count',
        'commute_barrier_score', 'health_related_absences', 'cash_flow_volatility',
        'academic_risk_index', 'barrier_burden_index', 'support_coverage_score',
        'retained',
    ]
    labels = [_clean_feature_name(c) for c in predictors]
    corr = enriched[predictors].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
        vmin=-1, vmax=1, ax=ax, xticklabels=labels, yticklabels=labels,
        annot_kws={'size': 8},
    )
    ax.set_title('Predictor Correlation Heatmap', fontweight='bold')
    fig.tight_layout()
    _save(fig, '07_correlation_heatmap.png')


def plot_intervention_flags(enriched: pd.DataFrame) -> None:
    flags = [
        'high_academic_risk_flag', 'long_commute_flag', 'no_digital_access_flag',
        'low_social_integration_flag', 'stem_resilience_flag',
    ]
    dropped = enriched[enriched['retained'] == 0]
    retained = enriched[enriched['retained'] == 1]

    rates = pd.DataFrame({
        'Dropped': [dropped[f].mean() * 100 for f in flags],
        'Retained': [retained[f].mean() * 100 for f in flags],
    }, index=[_clean_feature_name(f) for f in flags])

    fig, ax = plt.subplots(figsize=(10, 6))
    rates.plot(kind='barh', ax=ax, color=[COLORS['dropped'], COLORS['retained']], width=0.75)
    ax.set_xlabel('% of Group Flagged')
    ax.set_title('Risk Flags: Dropped vs. Retained Students', fontweight='bold')
    ax.legend(title='Status')
    ax.set_xlim(0, rates.values.max() * 1.15)
    fig.tight_layout()
    _save(fig, '08_intervention_risk_flags.png')


def plot_model_performance() -> None:
    data = load_preprocessed()
    x_train, x_test = data['x_train'], data['x_test']
    y_train, y_test = data['y_train'], data['y_test']
    meta_test = data['meta_test']

    models = {
        'Logistic Regression': LogisticRegression(
            max_iter=2000, random_state=RANDOM_STATE, class_weight='balanced',
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=300, max_depth=8, random_state=RANDOM_STATE, class_weight='balanced',
        ),
    }

    results = {}
    for name, model in models.items():
        model.fit(x_train, y_train)
        prob = model.predict_proba(x_test)[:, 1]
        pred = model.predict(x_test)
        results[name] = {'model': model, 'prob': prob, 'pred': pred, 'auc': roc_auc_score(y_test, prob)}

    # Model AUC comparison
    fig, ax = plt.subplots(figsize=(8, 5))
    names = list(results.keys())
    aucs = [results[n]['auc'] for n in names]
    bars = ax.bar(names, aucs, color=[COLORS['accent'], COLORS['highlight']], edgecolor='white', width=0.55)
    for bar, val in zip(bars, aucs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f'{val:.3f}', ha='center')
    ax.set_ylim(0, 1)
    ax.set_ylabel('Test AUC')
    ax.set_title('Model Comparison — Retention Prediction', fontweight='bold')
    fig.tight_layout()
    _save(fig, '09_model_auc_comparison.png')

    # ROC curves
    fig, ax = plt.subplots(figsize=(8, 7))
    for name, res in results.items():
        fpr, tpr, _ = roc_curve(y_test, res['prob'])
        RocCurveDisplay(fpr=fpr, tpr=tpr, roc_auc=res['auc'], name=name).plot(ax=ax)
    ax.plot([0, 1], [0, 1], '--', color=COLORS['muted'], label='Random (AUC = 0.50)')
    ax.set_title('ROC Curves — Test Set', fontweight='bold')
    ax.legend(loc='lower right')
    fig.tight_layout()
    _save(fig, '10_roc_curves.png')

    # Confusion matrix — logistic regression (better dropout recall)
    lr_pred = results['Logistic Regression']['pred']
    cm = confusion_matrix(y_test, lr_pred)
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues', ax=ax,
        xticklabels=['Pred: Dropped', 'Pred: Retained'],
        yticklabels=['Actual: Dropped', 'Actual: Retained'],
    )
    ax.set_title('Confusion Matrix — Logistic Regression', fontweight='bold')
    fig.tight_layout()
    _save(fig, '11_confusion_matrix.png')

    # AUC by SES quintile
    ses_rows = []
    for name, res in results.items():
        ses = meta_test['socioeconomic_status_index'].values
        for q in sorted(np.unique(ses)):
            mask = ses == q
            y_q = y_test.values[mask]
            if len(np.unique(y_q)) < 2:
                ses_auc = np.nan
            else:
                ses_auc = roc_auc_score(y_q, res['prob'][mask])
            ses_rows.append({'model': name, 'ses_quintile': f'Q{q}', 'auc': ses_auc})
    ses_df = pd.DataFrame(ses_rows)

    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.barplot(data=ses_df, x='ses_quintile', y='auc', hue='model',
                palette=[COLORS['accent'], COLORS['highlight']], ax=ax)
    ax.axhline(0.5, color=COLORS['muted'], linestyle='--', linewidth=1)
    ax.set_ylim(0, 1)
    ax.set_ylabel('AUC')
    ax.set_xlabel('SES Quintile')
    ax.set_title('Model Fairness — AUC by SES Quintile (Test Set)', fontweight='bold')
    ax.legend(title='')
    fig.tight_layout()
    _save(fig, '12_auc_by_ses_quintile.png')

    # Feature importance — random forest
    rf = results['Random Forest']['model']
    importances = pd.Series(
        rf.feature_importances_,
        index=[_clean_feature_name(c) for c in x_train.columns],
    ).sort_values(ascending=False).head(15)

    fig, ax = plt.subplots(figsize=(10, 7))
    sns.barplot(x=importances.values, y=importances.index, color=COLORS['accent'], ax=ax)
    ax.set_xlabel('Importance')
    ax.set_title('Top 15 Features — Random Forest', fontweight='bold')
    fig.tight_layout()
    _save(fig, '13_feature_importance.png')

    return results


def plot_pipeline_summary() -> None:
    """Visual summary of the end-to-end analytics pipeline."""
    fig, ax = plt.subplots(figsize=(14, 3.5))
    ax.axis('off')

    stages = [
        ('Synthetic Cohort\nv4 · n=1,000', COLORS['muted']),
        ('Validation &\nEDA', COLORS['highlight']),
        ('Feature\nEngineering', COLORS['accent']),
        ('Preprocessing\nImpute + Scale', '#457B9D'),
        ('Retention Model\nAUC ≈ 0.75', COLORS['retained']),
        ('Intervention\nRouting', COLORS['dropped']),
    ]
    x_positions = np.linspace(0.05, 0.95, len(stages))
    for i, (x, (label, color)) in enumerate(zip(x_positions, stages)):
        box = mpatches.FancyBboxPatch(
            (x - 0.07, 0.25), 0.14, 0.5,
            boxstyle='round,pad=0.02,rounding_size=0.02',
            facecolor=color, edgecolor='white', linewidth=2, alpha=0.9,
            transform=ax.transAxes,
        )
        ax.add_patch(box)
        ax.text(x, 0.5, label, ha='center', va='center', fontsize=10,
                fontweight='bold', color='white', transform=ax.transAxes)
        if i < len(stages) - 1:
            ax.annotate(
                '', xy=(x_positions[i + 1] - 0.075, 0.5), xytext=(x + 0.075, 0.5),
                arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=2),
                xycoords='axes fraction',
            )
    ax.set_title('Elimu Match Analytics Pipeline', fontsize=15, fontweight='bold', pad=20)
    _save(fig, '00_pipeline_summary.png')


def main() -> None:
    _setup_theme()
    print('Generating visualizations...')

    if not PREPROCESSED_DIR.exists():
        preprocess()

    raw, enriched = load_data()
    plot_pipeline_summary()
    plot_cohort_overview(enriched)
    plot_retention_by_ses(enriched)
    plot_key_distributions(enriched)
    plot_missingness(enriched)
    plot_engineered_features(enriched)
    plot_correlation_heatmap(enriched)
    plot_intervention_flags(enriched)
    plot_model_performance()

    n_plots = len(list(OUTPUT_DIR.glob('*.png')))
    print(f'\nDone — {n_plots} charts saved to {OUTPUT_DIR}/')


if __name__ == '__main__':
    main()
