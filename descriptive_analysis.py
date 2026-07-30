"""
Descriptive analysis, data validation, and correlation review for elimu_match_data_v4.csv.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DATA_PATH = Path(__file__).with_name('elimu_match_data_v4.csv')
OUTPUT_DIR = Path(__file__).with_name('analysis_outputs')

KEY_NUMERIC = [
    'socioeconomic_status_index',
    'commute_barrier_score',
    'gpa_trend',
    'failed_subjects_count',
    'health_related_absences',
    'cash_flow_volatility',
    'resource_dilution_index',
    'social_integration_score',
    'retention_risk_score',
]

KEY_CATEGORICAL = [
    'gender',
    'digital_equity_access_score',
    'nutritional_support_access',
    'strength_science_indicator',
    'chronic_health_risk_score',
    'psychosocial_support_access',
    'academic_catchup_status',
    'retained',
]

MISSINGNESS_COLS = [
    'cash_flow_volatility',
    'commute_barrier_score',
    'digital_equity_access_score',
    'psychosocial_support_access',
]

EXPECTED_RANGES = {
    'age_at_enrollment': (13, 17),
    'socioeconomic_status_index': (1, 5),
    'digital_equity_access_score': (0, 2),
    'chronic_health_risk_score': (1, 3),
    'social_integration_score': (0, 3),
    'gpa_trend': (-4, 4),
    'failed_subjects_count': (0, 8),
    'commute_barrier_score': (0, 20),
    'cash_flow_volatility': (0.12, 0.32),
    'retained': (0, 1),
}


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    rows = []

    rows.append({'check': 'row_count', 'result': len(df), 'status': 'INFO'})
    rows.append({'check': 'duplicate_student_id', 'result': int(df['student_id'].duplicated().sum()), 'status': 'PASS' if df['student_id'].duplicated().sum() == 0 else 'FAIL'})
    rows.append({'check': 'duplicate_rows', 'result': int(df.duplicated().sum()), 'status': 'PASS' if df.duplicated().sum() == 0 else 'FAIL'})

    for col, (lo, hi) in EXPECTED_RANGES.items():
        out_of_range = ((df[col] < lo) | (df[col] > hi)).sum()
        rows.append({
            'check': f'{col}_in_range[{lo},{hi}]',
            'result': int(out_of_range),
            'status': 'PASS' if out_of_range == 0 else 'FAIL',
        })

    # dropout_reason should be null when retained == 1
    invalid_reason = ((df['retained'] == 1) & df['dropout_reason'].notna()).sum()
    missing_reason = ((df['retained'] == 0) & df['dropout_reason'].isna()).sum()
    rows.append({
        'check': 'dropout_reason_present_only_when_dropped',
        'result': f'invalid={invalid_reason}, missing={missing_reason}',
        'status': 'PASS' if invalid_reason == 0 and missing_reason == 0 else 'FAIL',
    })

    missing_total = int(df.isna().sum().sum())
    rows.append({'check': 'total_missing_cells', 'result': missing_total, 'status': 'INFO'})

    for col in MISSINGNESS_COLS:
        miss = int(df[col].isna().sum())
        rows.append({
            'check': f'missing_{col}',
            'result': f'{miss} ({miss / len(df):.1%})',
            'status': 'INFO',
        })

    return pd.DataFrame(rows)


def print_section(title: str) -> None:
    print('\n' + '=' * 72)
    print(title)
    print('=' * 72)


def descriptive_summary(df: pd.DataFrame) -> None:
    print_section('DESCRIPTIVE STATISTICS — KEY NUMERIC VARIABLES')
    print(df[KEY_NUMERIC].describe().round(3).to_string())

    print_section('CATEGORICAL DISTRIBUTIONS')
    for col in KEY_CATEGORICAL:
        print(f'\n{col}:')
        counts = df[col].value_counts(dropna=False).sort_index()
        pct = (counts / len(df) * 100).round(1)
        summary = pd.DataFrame({'count': counts, 'pct': pct})
        print(summary.to_string())

    print_section('DROPOUT REASONS (non-retained students only)')
    dropped = df.loc[df['retained'] == 0, 'dropout_reason']
    print(dropped.value_counts().to_string())
    print(f'\nTotal dropped: {len(dropped)} ({len(dropped) / len(df):.1%} of cohort)')

    print_section('RETENTION BY SES QUINTILE')
    ses_summary = (
        df.groupby('socioeconomic_status_index')
        .agg(
            n=('student_id', 'count'),
            retention_rate=('retained', 'mean'),
            avg_failed_subjects=('failed_subjects_count', 'mean'),
            avg_gpa_trend=('gpa_trend', 'mean'),
            avg_commute=('commute_barrier_score', 'mean'),
        )
        .round(3)
    )
    print(ses_summary.to_string())

    print_section('RETENTION BY SCHOOL (summary)')
    school_summary = df.groupby('school_id')['retained'].agg(['count', 'mean']).rename(columns={'mean': 'retention_rate'})
    print(f"Schools: {school_summary.shape[0]}")
    print(f"Retention rate — min: {school_summary['retention_rate'].min():.3f}, "
          f"max: {school_summary['retention_rate'].max():.3f}, "
          f"std: {school_summary['retention_rate'].std():.3f}")


def correlation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    print_section('CORRELATION WITH TARGET (retained)')
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    target_corr = (
        df[numeric_cols]
        .corr()['retained']
        .drop('retained')
        .sort_values(key=abs, ascending=False)
    )
    for col, val in target_corr.items():
        print(f'  {col:35s} {val:+.3f}')

    print_section('STRONG FEATURE CORRELATIONS (|r| >= 0.40)')
    corr = df[numeric_cols].corr()
    pairs = []
    for i, a in enumerate(numeric_cols):
        for b in numeric_cols[i + 1:]:
            r = corr.loc[a, b]
            if abs(r) >= 0.40:
                pairs.append((abs(r), r, a, b))
    pairs.sort(reverse=True)
    if pairs:
        for _, r, a, b in pairs:
            print(f'  {a} vs {b}: {r:+.3f}')
    else:
        print('  None above threshold.')

    print_section('MISSINGNESS vs SES (validation of MAR pattern)')
    miss_ses = (
        df.assign(any_missing=df[MISSINGNESS_COLS].isna().any(axis=1))
        .groupby('socioeconomic_status_index')['any_missing']
        .mean()
        .round(3)
    )
    print(miss_ses.to_string())

    return corr


def save_plots(df: pd.DataFrame, corr: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    sns.set_theme(style='whitegrid', palette='muted')

    # 1. Numeric distributions
    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    axes = axes.ravel()
    plot_cols = KEY_NUMERIC + ['age_at_enrollment']
    for ax, col in zip(axes, plot_cols):
        sns.histplot(df[col].dropna(), kde=True, ax=ax, bins=20)
        ax.set_title(col)
    fig.suptitle('Distribution of Key Numeric Variables', fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'distributions_numeric.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    # 2. Categorical bar charts
    fig, axes = plt.subplots(2, 4, figsize=(14, 7))
    axes = axes.ravel()
    for ax, col in zip(axes, KEY_CATEGORICAL):
        order = sorted(df[col].dropna().unique())
        sns.countplot(data=df, x=col, order=order, ax=ax)
        ax.set_title(col)
        ax.set_xlabel('')
    fig.suptitle('Distribution of Key Categorical Variables', fontsize=14, y=1.01)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'distributions_categorical.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    # 3. Correlation heatmap (predictors only)
    predictors = [c for c in corr.columns if c not in ('student_id', 'retention_risk_score', 'retained')]
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        corr.loc[predictors, predictors],
        annot=True,
        fmt='.2f',
        cmap='RdBu_r',
        center=0,
        vmin=-1,
        vmax=1,
        ax=ax,
        annot_kws={'size': 7},
    )
    ax.set_title('Feature Correlation Heatmap (excluding leakage columns)')
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'correlation_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    # 4. Retention by SES
    fig, ax = plt.subplots(figsize=(8, 5))
    ses_ret = df.groupby('socioeconomic_status_index')['retained'].mean().reset_index()
    sns.barplot(data=ses_ret, x='socioeconomic_status_index', y='retained', ax=ax)
    ax.set_ylabel('Retention rate')
    ax.set_xlabel('SES quintile')
    ax.set_title('Retention Rate by SES Quintile')
    ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / 'retention_by_ses.png', dpi=150, bbox_inches='tight')
    plt.close(fig)

    print_section('PLOTS SAVED')
    for path in sorted(OUTPUT_DIR.glob('*.png')):
        print(f'  {path.name}')


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    print_section('DATA VALIDATION CHECKS')
    validation = validate_data(df)
    print(validation.to_string(index=False))
    failed = validation[validation['status'] == 'FAIL']
    if not failed.empty:
        print('\nWARNING: Validation failures detected.')
    else:
        print('\nAll hard validation checks passed.')

    descriptive_summary(df)
    corr = correlation_analysis(df)
    save_plots(df, corr)


if __name__ == '__main__':
    main()
