"""
Intervention Matrix for Elimu Match.

Defines a policy matrix:
  Risk Persona × Intervention  →  priority (0–3)
  Risk Signal  × Intervention  →  eligibility weight

Then applies the matrix to each student to produce:
  - primary / secondary intervention recommendations
  - a sponsor-ready assignment table
  - heatmap visuals for the presentation

Run:
  python cluster_personas.py   # if personas missing
  python intervention_matrix.py
"""

from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from feature_engineering import engineer_features
from preprocess_data import DATA_PATH

ROOT = Path(__file__).parent
OUT = ROOT / 'intervention_outputs'
VIZ = ROOT / 'visualizations'
PERSONA_PATH = ROOT / 'clustering_outputs' / 'student_personas.csv'

# Priority scale used in the matrix
# 0 = Not indicated | 1 = Optional | 2 = Recommended | 3 = Priority
PRIORITY_LABELS = {
    0: 'Not indicated',
    1: 'Optional',
    2: 'Recommended',
    3: 'Priority',
}

INTERVENTIONS = {
    'school_fee_support': {
        'label': 'School Fee Support',
        'sponsor_action': 'Pay term fees / bursary',
        'unit_cost_kes': 15000,
        'owner': 'Sponsor / Bursary fund',
    },
    'academic_tutoring': {
        'label': 'Academic Tutoring',
        'sponsor_action': 'Fund remedial / catch-up classes',
        'unit_cost_kes': 8000,
        'owner': 'School + education NGO',
    },
    'transport_support': {
        'label': 'Transport / Boarding',
        'sponsor_action': 'Subsidize commute or boarding',
        'unit_cost_kes': 6000,
        'owner': 'Sponsor / County transport',
    },
    'health_support': {
        'label': 'Health & Attendance',
        'sponsor_action': 'Medical vouchers + attendance follow-up',
        'unit_cost_kes': 5000,
        'owner': 'School health partner',
    },
    'digital_access': {
        'label': 'Digital Access Kit',
        'sponsor_action': 'Shared device / data bundle',
        'unit_cost_kes': 7000,
        'owner': 'Sponsor / CSR partner',
    },
    'counseling': {
        'label': 'Psychosocial Counseling',
        'sponsor_action': 'Counselor hours / peer support',
        'unit_cost_kes': 4000,
        'owner': 'School counseling unit',
    },
    'enrichment': {
        'label': 'STEM Enrichment',
        'sponsor_action': 'Clubs, mentoring, competitions',
        'unit_cost_kes': 3000,
        'owner': 'School / alumni mentors',
    },
}

# ---------------------------------------------------------------------------
# PERSONA × INTERVENTION MATRIX  (policy design)
# Rows = risk personas from clustering; columns = interventions
# ---------------------------------------------------------------------------
PERSONA_MATRIX = {
    #                          fee  tutor  transport  health  digital  counsel  enrich
    'Health-Constrained':     [2,   1,     1,         3,      1,       2,       0],
    'Academic Strugglers':     [2,   3,     1,         1,      2,       1,       0],
    'Stable Achievers':       [0,   0,     0,         0,      1,       0,       3],
}

INTERVENTION_ORDER = [
    'school_fee_support',
    'academic_tutoring',
    'transport_support',
    'health_support',
    'digital_access',
    'counseling',
    'enrichment',
]

# ---------------------------------------------------------------------------
# SIGNAL × INTERVENTION weights  (feature triggers that boost fit)
# ---------------------------------------------------------------------------
def signal_boosts(row: pd.Series) -> dict[str, float]:
    """Extra points from observable risk signals (on top of persona matrix)."""
    boost = {k: 0.0 for k in INTERVENTION_ORDER}
    ses = row['socioeconomic_status_index']
    cash = row.get('cash_flow_volatility', np.nan)
    commute = row.get('commute_barrier_score', np.nan)
    digital = row.get('digital_equity_access_score', np.nan)

    # Fees
    if ses <= 2:
        boost['school_fee_support'] += 1.5
    if pd.notna(cash) and cash >= 0.26:
        boost['school_fee_support'] += 1.5
    elif pd.notna(cash) and cash >= 0.22:
        boost['school_fee_support'] += 0.75

    # Academic
    if row['failed_subjects_count'] >= 3:
        boost['academic_tutoring'] += 1.5
    elif row['failed_subjects_count'] >= 2:
        boost['academic_tutoring'] += 0.75
    if row['gpa_trend'] <= -1.5:
        boost['academic_tutoring'] += 1.0

    # Transport
    if pd.notna(commute) and commute > 8:
        boost['transport_support'] += 2.0
    elif pd.notna(commute) and commute > 6:
        boost['transport_support'] += 1.0

    # Health
    if row['health_related_absences'] >= 12:
        boost['health_support'] += 1.5
    elif row['health_related_absences'] >= 8:
        boost['health_support'] += 0.75
    if row['chronic_health_risk_score'] >= 2:
        boost['health_support'] += 1.0

    # Digital
    if pd.notna(digital) and digital == 0:
        boost['digital_access'] += 1.5 if ses <= 3 else 0.75

    # Counseling
    if row['social_integration_score'] == 0:
        boost['counseling'] += 1.0
    psych = row.get('psychosocial_support_access', np.nan)
    if pd.notna(psych) and psych == 0 and row.get('dropout_risk', 0) >= 0.30:
        boost['counseling'] += 1.0

    # Enrichment (only if already stable academically)
    if row.get('strength_science_indicator', 0) == 1 and row['gpa_trend'] > -1:
        boost['enrichment'] += 1.0

    return boost


def persona_base_scores(persona: str) -> dict[str, float]:
    row = PERSONA_MATRIX.get(persona)
    if row is None:
        # Unknown persona: mild defaults
        return {k: 1.0 for k in INTERVENTION_ORDER}
    return {k: float(v) for k, v in zip(INTERVENTION_ORDER, row)}


def estimate_dropout_risk(df: pd.DataFrame) -> pd.Series:
    return (
        0.25 * (6 - df['socioeconomic_status_index']) / 5
        + 0.20 * (df['failed_subjects_count'].clip(0, 8) / 8)
        + 0.15 * ((-df['gpa_trend']).clip(0, 4) / 4)
        + 0.15 * (df['commute_barrier_score'].fillna(df['commute_barrier_score'].median()) / 20)
        + 0.10 * (df['health_related_absences'].clip(0, 28) / 28)
        + 0.15 * (
            (df['cash_flow_volatility'].fillna(df['cash_flow_volatility'].median()) - 0.12) / 0.20
        ).clip(0, 1)
    ).clip(0, 1)


def build_persona_matrix_df() -> pd.DataFrame:
    records = []
    for persona, scores in PERSONA_MATRIX.items():
        for intervention_id, score in zip(INTERVENTION_ORDER, scores):
            records.append({
                'persona': persona,
                'intervention_id': intervention_id,
                'intervention': INTERVENTIONS[intervention_id]['label'],
                'priority_score': score,
                'priority_label': PRIORITY_LABELS[score],
                'sponsor_action': INTERVENTIONS[intervention_id]['sponsor_action'],
                'unit_cost_kes': INTERVENTIONS[intervention_id]['unit_cost_kes'],
                'owner': INTERVENTIONS[intervention_id]['owner'],
            })
    return pd.DataFrame(records)


def build_signal_matrix_df() -> pd.DataFrame:
    """Human-readable signal → intervention eligibility guide for slides."""
    rows = [
        ('Low SES (Q1–Q2)', 'school_fee_support', 3, 'Primary bursary eligibility'),
        ('High cash-flow volatility', 'school_fee_support', 3, 'Income shock → fee support'),
        ('≥3 failed subjects', 'academic_tutoring', 3, 'Remediation priority'),
        ('Steep GPA decline', 'academic_tutoring', 2, 'Catch-up classes'),
        ('Commute > 8 km', 'transport_support', 3, 'Transport / boarding'),
        ('High health absences', 'health_support', 3, 'Health & attendance'),
        ('Chronic health risk ≥ 2', 'health_support', 2, 'Medical follow-up'),
        ('No digital access', 'digital_access', 2, 'Device / data kit'),
        ('Low social integration', 'counseling', 2, 'Psychosocial support'),
        ('Science talent + stable GPA', 'enrichment', 3, 'STEM enrichment'),
    ]
    return pd.DataFrame(rows, columns=[
        'risk_signal', 'intervention_id', 'matrix_weight', 'policy_note',
    ]).assign(
        intervention=lambda d: d['intervention_id'].map(lambda i: INTERVENTIONS[i]['label'])
    )


def score_student(row: pd.Series) -> list[dict]:
    base = persona_base_scores(str(row.get('persona', 'Unknown')))
    boost = signal_boosts(row)
    risk = float(row.get('dropout_risk', 0))

    scored = []
    for intervention_id in INTERVENTION_ORDER:
        # Combine persona policy + signal boosts; scale by dropout risk for ranking
        fit = base[intervention_id] + boost[intervention_id]
        if fit <= 0:
            continue
        priority = round(fit * (0.6 + 0.8 * risk), 3)
        scored.append({
            'intervention_id': intervention_id,
            'intervention': INTERVENTIONS[intervention_id]['label'],
            'persona_priority': base[intervention_id],
            'signal_boost': boost[intervention_id],
            'fit_score': round(fit, 2),
            'priority_score': priority,
            'unit_cost_kes': INTERVENTIONS[intervention_id]['unit_cost_kes'],
            'sponsor_action': INTERVENTIONS[intervention_id]['sponsor_action'],
            'owner': INTERVENTIONS[intervention_id]['owner'],
        })
    scored.sort(key=lambda x: x['priority_score'], reverse=True)
    return scored


def assign_interventions(df: pd.DataFrame, top_n: int = 2) -> pd.DataFrame:
    rows = []
    for _, row in df.iterrows():
        scored = score_student(row)
        if not scored:
            continue
        for rank, item in enumerate(scored[:top_n], start=1):
            rows.append({
                'student_id': int(row['student_id']),
                'school_id': int(row['school_id']),
                'persona': row.get('persona', ''),
                'ses_quintile': int(row['socioeconomic_status_index']),
                'dropout_risk': round(float(row['dropout_risk']), 3),
                'retained': int(row['retained']),
                'match_rank': rank,
                **item,
            })
    return pd.DataFrame(rows).sort_values(
        ['match_rank', 'priority_score'], ascending=[True, False],
    )


def plot_persona_matrix(matrix_df: pd.DataFrame) -> None:
    pivot = matrix_df.pivot(index='persona', columns='intervention', values='priority_score')
    # Order rows by retention urgency (Health, Academic, Stable)
    row_order = [p for p in PERSONA_MATRIX.keys() if p in pivot.index]
    col_order = [INTERVENTIONS[i]['label'] for i in INTERVENTION_ORDER]
    pivot = pivot.reindex(index=row_order, columns=col_order)

    fig, ax = plt.subplots(figsize=(12, 4.8))
    sns.heatmap(
        pivot, annot=True, fmt='.0f', cmap='YlOrRd', vmin=0, vmax=3,
        linewidths=1, linecolor='white', cbar_kws={'label': 'Priority (0–3)'},
        ax=ax,
    )
    ax.set_title('Intervention Matrix — Risk Persona × Sponsor Action', fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.xticks(rotation=25, ha='right')
    fig.tight_layout()
    fig.savefig(VIZ / '38_intervention_matrix_heatmap.png', dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_signal_matrix(signal_df: pd.DataFrame) -> None:
    pivot = signal_df.pivot_table(
        index='risk_signal', columns='intervention', values='matrix_weight', aggfunc='max',
    ).fillna(0)
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.heatmap(
        pivot, annot=True, fmt='.0f', cmap='Blues', vmin=0, vmax=3,
        linewidths=1, linecolor='white', ax=ax,
        cbar_kws={'label': 'Eligibility weight'},
    )
    ax.set_title('Signal → Intervention Eligibility Guide', fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('')
    plt.xticks(rotation=25, ha='right')
    fig.tight_layout()
    fig.savefig(VIZ / '39_signal_intervention_matrix.png', dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def plot_assignment_mix(assignments: pd.DataFrame) -> None:
    primary = assignments[assignments['match_rank'] == 1]
    counts = primary['intervention'].value_counts()

    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    colors = sns.color_palette('Set2', n_colors=len(counts))
    axes[0].barh(counts.index[::-1], counts.values[::-1], color=colors[::-1])
    axes[0].set_xlabel('Students (primary recommendation)')
    axes[0].set_title('Primary Interventions Assigned')

    by_persona = (
        primary.groupby(['persona', 'intervention']).size()
        .reset_index(name='n')
    )
    pivot = by_persona.pivot(index='persona', columns='intervention', values='n').fillna(0)
    pivot.plot(kind='bar', stacked=True, ax=axes[1], colormap='Set2')
    axes[1].set_title('Primary Intervention Mix by Persona')
    axes[1].set_xlabel('')
    axes[1].tick_params(axis='x', rotation=20)
    axes[1].legend(fontsize=7, loc='upper right')

    fig.suptitle('Intervention Matrix — Applied to Cohort', fontweight='bold', y=1.02)
    fig.tight_layout()
    fig.savefig(VIZ / '40_intervention_assignment_mix.png', dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)


def write_playbook(matrix_df: pd.DataFrame, assignments: pd.DataFrame) -> None:
    primary = assignments[assignments['match_rank'] == 1]
    lines = [
        '# Intervention Matrix Playbook — Elimu Match',
        '',
        '## Purpose',
        'Translate analytics (risk personas + signals) into **sponsor/school actions**.',
        'Sponsors should not see the matrix — they see a simple pay flow.',
        'Ops / schools use this matrix to decide *what* to offer each student.',
        '',
        '## Priority scale',
        '| Score | Meaning |',
        '|---|---|',
        '| 0 | Not indicated |',
        '| 1 | Optional |',
        '| 2 | Recommended |',
        '| 3 | Priority |',
        '',
        '## Persona × Intervention (policy)',
        '',
    ]
    for persona in PERSONA_MATRIX:
        lines.append(f'### {persona}')
        subset = matrix_df[matrix_df['persona'] == persona].sort_values('priority_score', ascending=False)
        for _, row in subset.iterrows():
            if row['priority_score'] <= 0:
                continue
            lines.append(
                f"- **{row['intervention']}** ({PRIORITY_LABELS[int(row['priority_score'])]}) — "
                f"{row['sponsor_action']} (~KES {int(row['unit_cost_kes']):,})"
            )
        lines.append('')

    lines += [
        '## How a student is assigned',
        '1. Start from persona row in the matrix',
        '2. Add signal boosts (SES, cash-flow, failures, commute, health, digital)',
        '3. Weight by dropout risk',
        '4. Rank interventions → primary + secondary recommendation',
        '',
        '## Cohort application (primary matches)',
        '',
    ]
    mix = primary['intervention'].value_counts()
    for name, count in mix.items():
        lines.append(f'- {name}: **{count}** students')
    lines += [
        '',
        '## Sponsor experience',
        'Students whose **primary** intervention is School Fee Support appear on `sponsor_portal.html`.',
        'Other interventions are routed to school partners (tutoring, health, transport).',
        '',
    ]
    (OUT / 'INTERVENTION_PLAYBOOK.md').write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    OUT.mkdir(exist_ok=True)
    VIZ.mkdir(exist_ok=True)

    print('=' * 72)
    print('INTERVENTION MATRIX — ELIMU MATCH')
    print('=' * 72)

    df = engineer_features(pd.read_csv(DATA_PATH))
    if PERSONA_PATH.exists():
        personas = pd.read_csv(PERSONA_PATH)[['student_id', 'persona', 'persona_id']]
        df = df.merge(personas, on='student_id', how='left')
    else:
        df['persona'] = 'Unknown'
        df['persona_id'] = -1

    df['dropout_risk'] = estimate_dropout_risk(df)

    matrix_df = build_persona_matrix_df()
    signal_df = build_signal_matrix_df()
    assignments = assign_interventions(df)

    matrix_df.to_csv(OUT / 'persona_intervention_matrix.csv', index=False)
    signal_df.to_csv(OUT / 'signal_intervention_matrix.csv', index=False)
    assignments.to_csv(OUT / 'student_intervention_assignments.csv', index=False)

    # Wide matrix for Tableau / slides
    wide = matrix_df.pivot(index='persona', columns='intervention', values='priority_score')
    wide.to_csv(OUT / 'intervention_matrix_wide.csv')

    primary = assignments[assignments['match_rank'] == 1]
    summary = (
        primary.groupby('intervention')
        .agg(
            students=('student_id', 'count'),
            avg_dropout_risk=('dropout_risk', 'mean'),
            pct_low_ses=('ses_quintile', lambda s: (s <= 2).mean()),
            total_cost_kes=('unit_cost_kes', 'sum'),
        )
        .reset_index()
    )
    summary['avg_dropout_risk'] = summary['avg_dropout_risk'].round(3)
    summary['pct_low_ses'] = (summary['pct_low_ses'] * 100).round(1)
    summary.to_csv(OUT / 'intervention_summary.csv', index=False)

    report = {
        'priority_scale': PRIORITY_LABELS,
        'interventions': INTERVENTIONS,
        'persona_matrix': PERSONA_MATRIX,
        'primary_mix': primary['intervention'].value_counts().to_dict(),
        'n_students_assigned': int(primary['student_id'].nunique()),
    }
    with open(OUT / 'intervention_matrix_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    plot_persona_matrix(matrix_df)
    plot_signal_matrix(signal_df)
    plot_assignment_mix(assignments)
    write_playbook(matrix_df, assignments)

    print('\nPersona x Intervention matrix:')
    print(wide.to_string())
    print('\nPrimary assignments:')
    print(primary['intervention'].value_counts().to_string())
    print(f'\nOutputs: {OUT}/')
    print('Charts: visualizations/38–40')
    print('Playbook: intervention_outputs/INTERVENTION_PLAYBOOK.md')


if __name__ == '__main__':
    main()
