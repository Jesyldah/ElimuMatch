"""
Export Tableau-ready datasets for the Elimu Match data exploration section.

Creates clean, labeled CSVs (no model jargon in display fields) plus a
data dictionary you can paste into Tableau or your capstone appendix.

Usage:
  python export_tableau.py

Then in Tableau: Connect → Text file → tableau_exports/students_exploration.csv
"""

from pathlib import Path

import pandas as pd

from feature_engineering import engineer_features
from preprocess_data import DATA_PATH

ROOT = Path(__file__).parent
OUT = ROOT / 'tableau_exports'
PERSONA_PATH = ROOT / 'clustering_outputs' / 'student_personas.csv'
MATCH_PATH = ROOT / 'matching_outputs' / 'sponsor_match_list.csv'

SCHOOL_NAMES = {
    1: 'Kilimani Day Secondary',
    2: 'Nyandarua Mixed Secondary',
    3: 'Kisumu Lakeside Secondary',
    4: 'Machakos Hilltop Secondary',
    5: 'Nakuru Valley Secondary',
    6: 'Mombasa Coast Secondary',
    7: 'Eldoret Highlands Secondary',
    8: 'Thika Green Secondary',
    9: 'Kakamega Forest Secondary',
    10: 'Nyeri Ridge Secondary',
    11: 'Kitale Plains Secondary',
    12: 'Garissa Horizon Secondary',
    13: 'Meru Mountain Secondary',
    14: 'Bungoma West Secondary',
    15: 'Embu Sunrise Secondary',
    16: 'Kericho Highlands Secondary',
    17: 'Malindi Shore Secondary',
    18: 'Narok Savannah Secondary',
    19: 'Isiolo North Secondary',
    20: 'Busia Border Secondary',
}

GENDER_MAP = {0: 'Boy', 1: 'Girl'}
DIGITAL_MAP = {0: 'No access', 1: 'Shared device', 2: 'Personal device'}
YES_NO = {0: 'No', 1: 'Yes'}
HEALTH_MAP = {1: 'Low', 2: 'Moderate', 3: 'High'}
SES_MAP = {
    1: 'Q1 — Lowest',
    2: 'Q2 — Low',
    3: 'Q3 — Middle',
    4: 'Q4 — High',
    5: 'Q5 — Highest',
}


def label_dropout(reason) -> str:
    if pd.isna(reason) or reason == '':
        return 'Still enrolled'
    return str(reason).replace('_', ' ').title()


def build_students() -> pd.DataFrame:
    df = engineer_features(pd.read_csv(DATA_PATH))

    if PERSONA_PATH.exists():
        personas = pd.read_csv(PERSONA_PATH)[['student_id', 'persona', 'persona_id']]
        df = df.merge(personas, on='student_id', how='left')
    else:
        df['persona'] = 'Unknown'
        df['persona_id'] = -1

    primary = None
    if MATCH_PATH.exists():
        matches = pd.read_csv(MATCH_PATH)
        primary = (
            matches[matches['match_rank'] == 1]
            [['student_id', 'intervention', 'est_unit_cost_kes', 'priority_score', 'match_reason']]
            .rename(columns={
                'intervention': 'recommended_intervention',
                'est_unit_cost_kes': 'recommended_cost_kes',
                'priority_score': 'sponsor_priority_score',
                'match_reason': 'intervention_match_reason',
            })
        )
        df = df.merge(primary, on='student_id', how='left')

    out = pd.DataFrame({
        'Student ID': df['student_id'],
        'School ID': df['school_id'],
        'School Name': df['school_id'].map(SCHOOL_NAMES),
        'Age at Enrollment': df['age_at_enrollment'],
        'Gender': df['gender'].map(GENDER_MAP),
        'SES Quintile': df['socioeconomic_status_index'],
        'SES Label': df['socioeconomic_status_index'].map(SES_MAP),
        'Household Size Index': df['resource_dilution_index'],
        'Commute Distance (km)': df['commute_barrier_score'].round(2),
        'Digital Access': df['digital_equity_access_score'].map(DIGITAL_MAP),
        'Digital Access Score': df['digital_equity_access_score'],
        'School Feeding': df['nutritional_support_access'].map(YES_NO),
        'GPA Trend': df['gpa_trend'].round(3),
        'Failed Subjects': df['failed_subjects_count'],
        'Science Strength': df['strength_science_indicator'].map(YES_NO),
        'Chronic Health Risk': df['chronic_health_risk_score'].map(HEALTH_MAP),
        'Health Absences (days)': df['health_related_absences'],
        'Social Integration Score': df['social_integration_score'],
        'Cash Flow Volatility': df['cash_flow_volatility'].round(3),
        'Academic Catch-up Flag': df['academic_catchup_status'].map(YES_NO),
        'Counseling Access': df['psychosocial_support_access'].map(YES_NO),
        'Retained': df['retained'].map(YES_NO),
        'Retained Flag': df['retained'],
        'Dropout Reason': df['dropout_reason'].map(label_dropout),
        'Risk Persona': df['persona'],
        'Academic Risk Index': df['academic_risk_index'].round(3),
        'Barrier Burden Index': df['barrier_burden_index'].round(3),
        'Economic Instability Index': df['economic_instability_index'].round(3),
        'Health Burden Index': df['health_burden_index'].round(3),
        'Support Coverage Score': df['support_coverage_score'].round(3),
        'Long Commute Flag': df['long_commute_flag'].map(YES_NO),
        'High Academic Risk Flag': df['high_academic_risk_flag'].map(YES_NO),
        'No Digital Access Flag': df['no_digital_access_flag'].map(YES_NO),
        'Recommended Intervention': df.get('recommended_intervention', pd.Series([None] * len(df))),
        'Recommended Cost (KES)': df.get('recommended_cost_kes', pd.Series([None] * len(df))),
        'Sponsor Priority Score': df.get('sponsor_priority_score', pd.Series([None] * len(df))),
        # Keep oracle risk for ops exploration only — do not use as a Tableau "predictor"
        'Model Risk Score (oracle)': df['retention_risk_score'],
    })
    return out


def build_schools(students: pd.DataFrame) -> pd.DataFrame:
    g = students.groupby(['School ID', 'School Name'], as_index=False).agg(
        Students=('Student ID', 'count'),
        Retention_Rate=('Retained Flag', 'mean'),
        Avg_SES=('SES Quintile', 'mean'),
        Avg_Commute_km=('Commute Distance (km)', 'mean'),
        Avg_Failed_Subjects=('Failed Subjects', 'mean'),
        Dropped_Students=('Retained Flag', lambda s: int((s == 0).sum())),
        Fee_Support_Candidates=('Recommended Intervention', lambda s: int((s == 'School Fee Support').sum())),
    )
    g['Retention_Rate'] = (g['Retention_Rate'] * 100).round(1)
    g['Avg_SES'] = g['Avg_SES'].round(2)
    g['Avg_Commute_km'] = g['Avg_Commute_km'].round(2)
    g['Avg_Failed_Subjects'] = g['Avg_Failed_Subjects'].round(2)
    g = g.rename(columns={
        'Retention_Rate': 'Retention Rate (%)',
        'Avg_SES': 'Avg SES Quintile',
        'Avg_Commute_km': 'Avg Commute (km)',
        'Avg_Failed_Subjects': 'Avg Failed Subjects',
        'Dropped_Students': 'Dropped Students',
        'Fee_Support_Candidates': 'Fee Support Candidates',
    })
    return g.sort_values('School ID')


def build_persona_summary(students: pd.DataFrame) -> pd.DataFrame:
    g = students.groupby('Risk Persona', as_index=False).agg(
        Students=('Student ID', 'count'),
        Retention_Rate=('Retained Flag', 'mean'),
        Avg_Academic_Risk=('Academic Risk Index', 'mean'),
        Avg_Barrier_Burden=('Barrier Burden Index', 'mean'),
        Avg_Economic_Instability=('Economic Instability Index', 'mean'),
        Avg_Health_Burden=('Health Burden Index', 'mean'),
    )
    g['Share (%)'] = (g['Students'] / g['Students'].sum() * 100).round(1)
    g['Retention Rate (%)'] = (g['Retention_Rate'] * 100).round(1)
    for col in ['Avg_Academic_Risk', 'Avg_Barrier_Burden', 'Avg_Economic_Instability', 'Avg_Health_Burden']:
        g[col] = g[col].round(3)
    return g.drop(columns=['Retention_Rate']).sort_values('Retention Rate (%)')


def write_data_dictionary() -> None:
    rows = [
        ('Student ID', 'students_exploration.csv', 'Unique student identifier', 'Dimension'),
        ('School Name', 'students_exploration.csv', 'Named secondary school (synthetic)', 'Dimension'),
        ('Gender', 'students_exploration.csv', 'Boy / Girl', 'Dimension'),
        ('SES Label', 'students_exploration.csv', 'Socioeconomic quintile label', 'Dimension'),
        ('SES Quintile', 'students_exploration.csv', '1 (lowest) to 5 (highest)', 'Dimension / Measure'),
        ('Commute Distance (km)', 'students_exploration.csv', 'Estimated travel distance to school', 'Measure'),
        ('Digital Access', 'students_exploration.csv', 'No access / Shared / Personal', 'Dimension'),
        ('GPA Trend', 'students_exploration.csv', 'Year-over-year GPA change', 'Measure'),
        ('Failed Subjects', 'students_exploration.csv', 'Count of failed core subjects', 'Measure'),
        ('Health Absences (days)', 'students_exploration.csv', 'School days missed due to illness', 'Measure'),
        ('Cash Flow Volatility', 'students_exploration.csv', 'Household income instability (0.12–0.32)', 'Measure'),
        ('Retained', 'students_exploration.csv', 'Yes = still enrolled; No = dropped out', 'Dimension'),
        ('Dropout Reason', 'students_exploration.csv', 'Primary reason if dropped; else Still enrolled', 'Dimension'),
        ('Risk Persona', 'students_exploration.csv', 'K-Means persona label', 'Dimension'),
        ('Academic Risk Index', 'students_exploration.csv', 'Engineered: failures − GPA trend', 'Measure'),
        ('Barrier Burden Index', 'students_exploration.csv', 'Engineered access/SES barrier composite', 'Measure'),
        ('Recommended Intervention', 'students_exploration.csv', 'Primary sponsor action match', 'Dimension'),
        ('Recommended Cost (KES)', 'students_exploration.csv', 'Illustrative unit cost of intervention', 'Measure'),
        ('Model Risk Score (oracle)', 'students_exploration.csv', 'Synthetic generator probability — exploration only, not for modeling claims', 'Measure'),
        ('Retention Rate (%)', 'schools_summary.csv', 'Share retained at school', 'Measure'),
        ('Fee Support Candidates', 'schools_summary.csv', 'Students whose primary match is school fee support', 'Measure'),
    ]
    pd.DataFrame(rows, columns=['Field', 'Table', 'Description', 'Tableau Role']).to_csv(
        OUT / 'data_dictionary.csv', index=False
    )


def write_tableau_readme() -> None:
    text = """# Tableau setup — Elimu Match (Data Exploration)

## Files to connect

| File | Grain | Use for |
|---|---|---|
| `students_exploration.csv` | 1 row per student | Main exploration workbook |
| `schools_summary.csv` | 1 row per school | School comparison dashboards |
| `persona_summary.csv` | 1 row per persona | Persona overview |
| `data_dictionary.csv` | Field list | Documentation / calculated-field notes |

## Suggested Tableau sheets (data exploration section)

1. **Cohort overview** — `Retained` pie/donut; count of students
2. **Retention by SES** — bar: `SES Label` vs AVG(`Retained Flag`) or % retained
3. **Dropout reasons** — filter `Retained` = No; bar of `Dropout Reason`
4. **School comparison** — use `schools_summary.csv` or dual-axis on student table
5. **Distributions** — histograms of `GPA Trend`, `Commute Distance (km)`, `Health Absences (days)` colored by `Retained`
6. **Risk personas** — stacked bar: `Risk Persona` × `Retained`
7. **Fee support map (table)** — filter `Recommended Intervention` = School Fee Support; by `School Name`

## Tips

- Set **Retained Flag** as a measure (0/1) for easy % calculations: `AVG([Retained Flag])`
- Hide or exclude **Model Risk Score (oracle)** from stakeholder views — it is synthetic leakage for ops QA only
- Geographic map: schools are synthetic names without lat/long; use bar charts by school instead unless you add coordinates
- Relationships: if you load multiple tables, relate on `School ID` / `School Name`

## Refresh

```bash
python export_tableau.py
```
"""
    (OUT / 'README_TABLEAU.md').write_text(text, encoding='utf-8')


def main() -> None:
    OUT.mkdir(exist_ok=True)
    students = build_students()
    schools = build_schools(students)
    personas = build_persona_summary(students)

    students.to_csv(OUT / 'students_exploration.csv', index=False)
    schools.to_csv(OUT / 'schools_summary.csv', index=False)
    personas.to_csv(OUT / 'persona_summary.csv', index=False)
    write_data_dictionary()
    write_tableau_readme()

    print('Tableau exports ready:')
    print(f'  {OUT / "students_exploration.csv"}  ({len(students):,} rows)')
    print(f'  {OUT / "schools_summary.csv"}       ({len(schools):,} rows)')
    print(f'  {OUT / "persona_summary.csv"}       ({len(personas):,} rows)')
    print(f'  {OUT / "data_dictionary.csv"}')
    print(f'  {OUT / "README_TABLEAU.md"}')
    print('\nIn Tableau: Connect -> Text file -> students_exploration.csv')


if __name__ == '__main__':
    main()
