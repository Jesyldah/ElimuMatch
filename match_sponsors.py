"""
Sponsor intervention matching for Elimu Match.

Links retention risk + risk personas to concrete sponsor actions
(e.g. school-fee support, tutoring, transport, health).

Outputs:
  matching_outputs/sponsor_match_list.csv   — prioritized student → action list
  matching_outputs/sponsor_portfolio.csv    — budget allocation by intervention
  visualizations/18_sponsor_matching.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from feature_engineering import engineer_features
from preprocess_data import DATA_PATH
from train_retention_model import RANDOM_STATE, load_preprocessed
from sklearn.linear_model import LogisticRegression

OUTPUT_DIR = Path(__file__).with_name('matching_outputs')
VIZ_DIR = Path(__file__).with_name('visualizations')
CLUSTER_PATH = Path(__file__).with_name('clustering_outputs') / 'student_personas.csv'

# Sponsor action catalog — what funders / NGOs / schools can actually do
INTERVENTIONS = {
    'school_fee_support': {
        'label': 'School Fee Support',
        'sponsor_action': 'Cover term fees / bursary for high cash-flow volatility + low SES students',
        'unit_cost_kes': 15000,  # illustrative term fee support
        'signals': 'low SES, high cash_flow_volatility, economic persona pressure',
    },
    'academic_tutoring': {
        'label': 'Academic Tutoring / Catch-up',
        'sponsor_action': 'Fund after-school tutoring or remedial classes',
        'unit_cost_kes': 8000,
        'signals': 'high failed subjects, declining GPA, Academic Strugglers persona',
    },
    'transport_support': {
        'label': 'Transport / Boarding Support',
        'sponsor_action': 'Subsidize commute costs or boarding for long-distance students',
        'unit_cost_kes': 6000,
        'signals': 'long commute barrier',
    },
    'health_support': {
        'label': 'Health & Attendance Support',
        'sponsor_action': 'Fund school nurse visits, medical vouchers, attendance follow-up',
        'unit_cost_kes': 5000,
        'signals': 'high health absences / Health-Constrained persona',
    },
    'digital_access': {
        'label': 'Digital Access Kit',
        'sponsor_action': 'Provide shared device / data bundle for learning continuity',
        'unit_cost_kes': 7000,
        'signals': 'no digital access',
    },
    'counseling': {
        'label': 'Psychosocial Counseling',
        'sponsor_action': 'Sponsor school counselor hours or peer support groups',
        'unit_cost_kes': 4000,
        'signals': 'low social integration, no psychosocial support',
    },
}


def score_interventions(row: pd.Series) -> list[tuple[str, float, str]]:
    """
    Score each intervention for a student.
    Higher score = stronger need match for that sponsor action.
    """
    scores = []

    # --- School fees: the core sponsor ask ---
    fee_score = 0.0
    reasons = []
    ses = row['socioeconomic_status_index']
    cash = row.get('cash_flow_volatility', np.nan)
    if ses <= 2:
        fee_score += 2.0
        reasons.append('low SES')
    elif ses == 3:
        fee_score += 1.0
        reasons.append('mid-low SES')
    if pd.notna(cash) and cash >= 0.26:
        fee_score += 2.0
        reasons.append('high cash-flow volatility')
    elif pd.notna(cash) and cash >= 0.22:
        fee_score += 1.0
        reasons.append('elevated cash-flow volatility')
    if row.get('economic_instability_index', 0) >= 0.45:
        fee_score += 1.0
        reasons.append('economic instability')
    if row.get('dropout_risk', 0) >= 0.35:
        fee_score += 1.0
        reasons.append('elevated dropout risk')
    if fee_score > 0:
        scores.append(('school_fee_support', fee_score, ', '.join(reasons)))

    # --- Academic tutoring ---
    acad = 0.0
    acad_reasons = []
    if row['failed_subjects_count'] >= 3:
        acad += 2.5
        acad_reasons.append(f"{int(row['failed_subjects_count'])} failed subjects")
    elif row['failed_subjects_count'] >= 2:
        acad += 1.5
        acad_reasons.append('multiple failed subjects')
    if row['gpa_trend'] <= -1.5:
        acad += 1.5
        acad_reasons.append('steep GPA decline')
    elif row['gpa_trend'] <= -0.5:
        acad += 0.8
        acad_reasons.append('declining GPA')
    if row.get('persona') == 'Academic Strugglers':
        acad += 1.0
        acad_reasons.append('Academic Strugglers persona')
    if acad > 0:
        scores.append(('academic_tutoring', acad, ', '.join(acad_reasons)))

    # --- Transport ---
    commute = row.get('commute_barrier_score', np.nan)
    if pd.notna(commute) and commute > 8:
        scores.append((
            'transport_support',
            2.0 + min(commute / 10, 2.0),
            f'commute {commute:.1f} km',
        ))
    elif pd.notna(commute) and commute > 6:
        scores.append(('transport_support', 1.2, f'commute {commute:.1f} km'))

    # --- Health ---
    health = 0.0
    health_reasons = []
    if row['health_related_absences'] >= 12:
        health += 2.5
        health_reasons.append(f"{int(row['health_related_absences'])} health absences")
    elif row['health_related_absences'] >= 8:
        health += 1.5
        health_reasons.append('elevated health absences')
    if row['chronic_health_risk_score'] >= 2:
        health += 1.0
        health_reasons.append('chronic health risk')
    if row.get('persona') == 'Health-Constrained':
        health += 1.5
        health_reasons.append('Health-Constrained persona')
    if health > 0:
        scores.append(('health_support', health, ', '.join(health_reasons)))

    # --- Digital ---
    digital = row.get('digital_equity_access_score', np.nan)
    if pd.notna(digital) and digital == 0 and ses <= 3:
        scores.append(('digital_access', 2.0, 'no device access + constrained SES'))
    elif pd.notna(digital) and digital == 0:
        scores.append(('digital_access', 1.0, 'no device access'))

    # --- Counseling ---
    counsel = 0.0
    counsel_reasons = []
    if row['social_integration_score'] == 0:
        counsel += 1.2
        counsel_reasons.append('no ECA / low social integration')
    psych = row.get('psychosocial_support_access', np.nan)
    if pd.notna(psych) and psych == 0 and row.get('dropout_risk', 0) >= 0.30:
        counsel += 1.0
        counsel_reasons.append('no counseling + elevated risk')
    if counsel > 0:
        scores.append(('counseling', counsel, ', '.join(counsel_reasons)))

    scores.sort(key=lambda x: x[1], reverse=True)
    return scores


def estimate_dropout_risk(df: pd.DataFrame) -> pd.Series:
    """Use the trained-style logistic model on full cohort for ranking (PoC)."""
    data = load_preprocessed()
    # Fit on train, score all students via a simple model on engineered frame
    # For matching we use a transparent risk score from key drivers
    risk = (
        0.25 * (6 - df['socioeconomic_status_index']) / 5
        + 0.20 * (df['failed_subjects_count'].clip(0, 8) / 8)
        + 0.15 * ((-df['gpa_trend']).clip(0, 4) / 4)
        + 0.15 * (df['commute_barrier_score'].fillna(df['commute_barrier_score'].median()) / 20)
        + 0.10 * (df['health_related_absences'].clip(0, 28) / 28)
        + 0.15 * (
            (df['cash_flow_volatility'].fillna(df['cash_flow_volatility'].median()) - 0.12) / 0.20
        ).clip(0, 1)
    )
    return risk.clip(0, 1)


def build_match_list(df: pd.DataFrame, top_n_per_student: int = 2) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        scored = score_interventions(row)
        if not scored:
            continue
        for rank, (action_id, score, reason) in enumerate(scored[:top_n_per_student], start=1):
            meta = INTERVENTIONS[action_id]
            rows.append({
                'student_id': int(row['student_id']),
                'school_id': int(row['school_id']),
                'persona': row.get('persona', ''),
                'ses_quintile': int(row['socioeconomic_status_index']),
                'dropout_risk': round(float(row['dropout_risk']), 3),
                'retained': int(row['retained']),
                'match_rank': rank,
                'intervention_id': action_id,
                'intervention': meta['label'],
                'sponsor_action': meta['sponsor_action'],
                'need_score': round(score, 2),
                'match_reason': reason,
                'est_unit_cost_kes': meta['unit_cost_kes'],
                'priority_score': round(float(row['dropout_risk']) * score, 3),
            })
    matches = pd.DataFrame(rows)
    # Primary recommendation = rank 1, sorted by priority for sponsors
    return matches.sort_values(['match_rank', 'priority_score'], ascending=[True, False])


def build_portfolio(matches: pd.DataFrame, budget_kes: int = 2_000_000) -> pd.DataFrame:
    """
    Allocate a sponsor budget to primary (rank-1) matches by priority score.
    """
    primary = matches[matches['match_rank'] == 1].copy()
    primary = primary.sort_values('priority_score', ascending=False)

    spent = 0
    funded = []
    for _, row in primary.iterrows():
        cost = row['est_unit_cost_kes']
        if spent + cost > budget_kes:
            continue
        spent += cost
        funded.append(row)

    funded_df = pd.DataFrame(funded)
    if funded_df.empty:
        return pd.DataFrame()

    portfolio = (
        funded_df.groupby('intervention')
        .agg(
            students_funded=('student_id', 'count'),
            total_cost_kes=('est_unit_cost_kes', 'sum'),
            avg_dropout_risk=('dropout_risk', 'mean'),
            pct_low_ses=('ses_quintile', lambda s: (s <= 2).mean()),
        )
        .reset_index()
    )
    portfolio['budget_share_pct'] = (portfolio['total_cost_kes'] / spent * 100).round(1)
    portfolio['avg_dropout_risk'] = portfolio['avg_dropout_risk'].round(3)
    portfolio['pct_low_ses'] = (portfolio['pct_low_ses'] * 100).round(1)
    portfolio.attrs['total_spent'] = spent
    portfolio.attrs['students_funded'] = len(funded_df)
    portfolio.attrs['budget'] = budget_kes
    return portfolio


def plot_sponsor_matching(matches: pd.DataFrame, portfolio: pd.DataFrame) -> None:
    VIZ_DIR.mkdir(exist_ok=True)
    primary = matches[matches['match_rank'] == 1]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))

    counts = primary['intervention'].value_counts()
    colors = ['#E76F51' if 'Fee' in i else '#2A9D8F' if 'Tutoring' in i else '#264653' for i in counts.index]
    axes[0].barh(counts.index, counts.values, color=colors)
    axes[0].set_title('Primary Recommended Interventions\n(all at-risk matches)', fontweight='bold')
    axes[0].set_xlabel('Students (rank-1 match)')

    if not portfolio.empty:
        axes[1].barh(
            portfolio['intervention'],
            portfolio['total_cost_kes'] / 1000,
            color='#E9C46A',
        )
        axes[1].set_title(
            f"Sponsor Portfolio under KES {portfolio.attrs['budget']/1e6:.1f}M budget\n"
            f"{portfolio.attrs['students_funded']} students funded",
            fontweight='bold',
        )
        axes[1].set_xlabel('Allocated budget (KES thousands)')
    else:
        axes[1].text(0.5, 0.5, 'No portfolio', ha='center')

    fig.suptitle('From Risk Signals → Sponsor Actions', fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '18_sponsor_matching.png', dpi=160, bbox_inches='tight')
    plt.close(fig)

    # Fee-support focus chart
    fee = primary[primary['intervention_id'] == 'school_fee_support'].head(20)
    if not fee.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        plot_df = fee.sort_values('priority_score')
        ax.barh(
            [f"Student {sid}" for sid in plot_df['student_id']],
            plot_df['priority_score'],
            color='#E76F51',
        )
        ax.set_xlabel('Priority score (dropout risk × fee need)')
        ax.set_title('Top 20 Candidates for School Fee Support', fontweight='bold')
        fig.tight_layout()
        fig.savefig(VIZ_DIR / '19_fee_support_priority.png', dpi=160, bbox_inches='tight')
        plt.close(fig)


def main(budget_kes: int = 2_000_000) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = engineer_features(pd.read_csv(DATA_PATH))
    if CLUSTER_PATH.exists():
        personas = pd.read_csv(CLUSTER_PATH)[['student_id', 'persona', 'persona_id']]
        df = df.merge(personas, on='student_id', how='left')
    else:
        df['persona'] = 'Unknown'

    df['dropout_risk'] = estimate_dropout_risk(df)

    # Focus matching on students who are not "safe" — risk above median or already dropped
    risk_cutoff = df['dropout_risk'].median()
    focus = df[(df['dropout_risk'] >= risk_cutoff) | (df['retained'] == 0)].copy()

    matches = build_match_list(focus)
    portfolio = build_portfolio(matches, budget_kes=budget_kes)

    matches.to_csv(OUTPUT_DIR / 'sponsor_match_list.csv', index=False)
    if not portfolio.empty:
        portfolio.to_csv(OUTPUT_DIR / 'sponsor_portfolio.csv', index=False)

    primary = matches[matches['match_rank'] == 1]
    fee_primary = primary[primary['intervention_id'] == 'school_fee_support']

    plot_sponsor_matching(matches, portfolio)

    print('=' * 72)
    print('SPONSOR INTERVENTION MATCHING')
    print('=' * 72)
    print(f'Students in matching pool:     {len(focus):,}')
    print(f'Primary recommendations:       {len(primary):,}')
    print(f'  -> School fee support:        {len(fee_primary):,}')
    print()
    print('Primary intervention mix:')
    print(primary['intervention'].value_counts().to_string())
    print()
    if not portfolio.empty:
        print(f'Illustrative budget: KES {budget_kes:,.0f}')
        print(f'Students fundable:   {portfolio.attrs["students_funded"]}')
        print(f'Total allocated:     KES {portfolio.attrs["total_spent"]:,.0f}')
        print()
        print(portfolio.to_string(index=False))
    print()
    print('How sponsors use this:')
    print('  1. Filter sponsor_match_list.csv where intervention = School Fee Support')
    print('  2. Sort by priority_score (highest first)')
    print('  3. Fund down the list until the bursary budget is spent')
    print('  4. Route other students to tutoring / transport / health partners')
    print(f'\nOutputs: {OUTPUT_DIR}/')


if __name__ == '__main__':
    main()
