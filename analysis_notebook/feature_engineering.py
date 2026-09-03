"""
Domain-informed feature engineering for the Elimu Match retention model.

Creates composite indices, interaction terms, and risk flags aligned with
observed dropout drivers (economic, academic, health, commute, psychosocial).
"""

import pandas as pd
import numpy as np

ENGINEERED_FEATURES = [
  # Composite risk indices
    'ses_disadvantage_score',
    'academic_risk_index',
    'health_burden_index',
    'absence_intensity',
    'household_pressure_index',
    'support_coverage_score',
    'economic_instability_index',
    'barrier_burden_index',
    # Interaction terms
    'ses_commute_interaction',
    'academic_ses_interaction',
    'health_commute_interaction',
    # Binary risk flags
    'long_commute_flag',
    'high_academic_risk_flag',
    'no_digital_access_flag',
    'low_social_integration_flag',
    'stem_resilience_flag',
]


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features to a copy of the input frame."""
    out = df.copy()

    ses_disadvantage = 6 - out['socioeconomic_status_index']
    out['ses_disadvantage_score'] = ses_disadvantage

    # Academic: more failures and declining GPA increase risk
    out['academic_risk_index'] = (
        out['failed_subjects_count'] - out['gpa_trend']
    )

    # Health: chronic conditions amplified by missed school days
    out['health_burden_index'] = (
        out['chronic_health_risk_score'] * out['health_related_absences']
    )
    out['absence_intensity'] = (
        out['health_related_absences'] / out['chronic_health_risk_score']
    )

    # Household: crowding plus economic disadvantage
    out['household_pressure_index'] = (
        out['resource_dilution_index'] + ses_disadvantage
    )

    # Support: school feeding, counseling, and digital access (higher = more support)
    out['support_coverage_score'] = (
        out['nutritional_support_access']
        + out['psychosocial_support_access']
        + out['digital_equity_access_score'] / 2
    )

    # Economic volatility worsens with lower SES
    out['economic_instability_index'] = (
        out['cash_flow_volatility'] + 0.05 * ses_disadvantage
    )

    # Access barriers: distance, digital gap, and SES disadvantage
    commute = out['commute_barrier_score']
    digital = out['digital_equity_access_score']
    digital_gap = 2 - digital
    out['barrier_burden_index'] = (
        commute / 20 + digital_gap / 2 + ses_disadvantage / 5
    )

    # Interactions: disadvantage compounds across domains
    out['ses_commute_interaction'] = ses_disadvantage * commute
    out['academic_ses_interaction'] = out['failed_subjects_count'] * ses_disadvantage
    out['health_commute_interaction'] = out['health_related_absences'] * commute

    # Actionable risk flags for intervention routing
    out['long_commute_flag'] = _nullable_flag(commute > 8)
    out['high_academic_risk_flag'] = (out['failed_subjects_count'] >= 3).astype(float)
    out['no_digital_access_flag'] = _nullable_flag(digital == 0)
    out['low_social_integration_flag'] = (out['social_integration_score'] == 0).astype(float)
    out['stem_resilience_flag'] = (
        (out['strength_science_indicator'] == 1) & (out['gpa_trend'] > -1.0)
    ).astype(float)

    return out


def _nullable_flag(mask: pd.Series) -> pd.Series:
    """Preserve NaN where the underlying value was missing."""
    result = mask.astype(float)
    result[mask.isna()] = np.nan
    return result


def correlation_with_target(df: pd.DataFrame, target: str = 'retained') -> pd.Series:
    """Rank engineered features by absolute correlation with the target."""
    cols = [c for c in ENGINEERED_FEATURES if c in df.columns]
    return (
        df[cols + [target]]
        .corr(numeric_only=True)[target]
        .drop(target)
        .sort_values(key=abs, ascending=False)
    )


def summarize_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """Descriptive stats for all engineered features."""
    cols = [c for c in ENGINEERED_FEATURES if c in df.columns]
    return df[cols].describe().round(3)


def print_feature_report(df: pd.DataFrame) -> None:
    print('=' * 72)
    print('FEATURE ENGINEERING SUMMARY')
    print('=' * 72)
    print(f'Engineered features added: {len(ENGINEERED_FEATURES)}')
    print('\nFeature definitions:')
    definitions = {
        'ses_disadvantage_score': 'Inverted SES quintile (higher = more disadvantage)',
        'academic_risk_index': 'failed_subjects_count - gpa_trend',
        'health_burden_index': 'chronic_health_risk_score × health_related_absences',
        'absence_intensity': 'health_related_absences / chronic_health_risk_score',
        'household_pressure_index': 'resource_dilution_index + ses_disadvantage_score',
        'support_coverage_score': 'nutrition + counseling + digital/2',
        'economic_instability_index': 'cash_flow_volatility + 0.05 × ses_disadvantage',
        'barrier_burden_index': 'normalized commute + digital gap + SES disadvantage',
        'ses_commute_interaction': 'ses_disadvantage_score × commute_barrier_score',
        'academic_ses_interaction': 'failed_subjects_count × ses_disadvantage_score',
        'health_commute_interaction': 'health_related_absences × commute_barrier_score',
        'long_commute_flag': '1 if commute > 8 km',
        'high_academic_risk_flag': '1 if failed_subjects_count >= 3',
        'no_digital_access_flag': '1 if digital_equity_access_score == 0',
        'low_social_integration_flag': '1 if social_integration_score == 0',
        'stem_resilience_flag': '1 if science talent with GPA trend > -1',
    }
    for feat, desc in definitions.items():
        print(f'  {feat:30s} {desc}')

    print('\nDescriptive statistics:')
    print(summarize_engineered_features(df).to_string())

    if 'retained' in df.columns:
        print('\nCorrelation with retained (engineered features only):')
        corr = correlation_with_target(df)
        for feat, val in corr.items():
            print(f'  {feat:30s} {val:+.3f}')


if __name__ == '__main__':
    from pathlib import Path

    data_path = Path(__file__).with_name('elimu_match_data_v4.csv')
    raw = pd.read_csv(data_path)
    enriched = engineer_features(raw)
    print_feature_report(enriched)
