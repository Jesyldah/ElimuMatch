"""
Data preprocessing for the Elimu Match retention model.

Steps:
  1. Load raw cohort and drop leakage / post-outcome columns
  2. Add missing-value indicators for survey fields
  3. Stratified train/test split (fit preprocessing on train only)
  4. Median imputation + standard scaling
  5. Save processed splits and fitted preprocessor for modeling
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from feature_engineering import ENGINEERED_FEATURES, engineer_features

DATA_PATH = Path(__file__).with_name('elimu_match_data_v4.csv')
OUTPUT_DIR = Path(__file__).with_name('preprocessed')
PREPROCESSED_DIR = OUTPUT_DIR
RANDOM_STATE = 2026
TEST_SIZE = 0.25

TARGET = 'retained'
ID_COLUMNS = ['student_id', 'school_id']
LEAKAGE_COLUMNS = {
    'retention_risk_score',
    'dropout_reason',
    'academic_catchup_status',
}
MISSINGNESS_COLS = [
    'cash_flow_volatility',
    'commute_barrier_score',
    'digital_equity_access_score',
    'psychosocial_support_access',
]

FEATURE_COLUMNS = [
    'school_id',
    'age_at_enrollment',
    'gender',
    'resource_dilution_index',
    'socioeconomic_status_index',
    'commute_barrier_score',
    'digital_equity_access_score',
    'nutritional_support_access',
    'gpa_trend',
    'failed_subjects_count',
    'strength_science_indicator',
    'chronic_health_risk_score',
    'health_related_absences',
    'social_integration_score',
    'cash_flow_volatility',
    'psychosocial_support_access',
]


def load_raw_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f'Missing {path.name}. Run synthetic_data_v2.py first.')
    return pd.read_csv(path)


def add_missing_indicators(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in MISSINGNESS_COLS:
        out[f'{col}_missing'] = out[col].isna().astype(int)
    out['any_survey_missing'] = out[[f'{c}_missing' for c in MISSINGNESS_COLS]].max(axis=1)
    return out


def build_feature_frame(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Return features, target, and metadata (ids + ses for evaluation)."""
    engineered = engineer_features(df)
    engineered = add_missing_indicators(engineered)
    indicator_cols = [f'{c}_missing' for c in MISSINGNESS_COLS] + ['any_survey_missing']
    feature_cols = FEATURE_COLUMNS + ENGINEERED_FEATURES + indicator_cols

    x = engineered[feature_cols].copy()
    y = engineered[TARGET].astype(int)
    meta = engineered[ID_COLUMNS + ['socioeconomic_status_index']].copy()
    return x, y, meta


def build_preprocessor(feature_names: list[str]) -> ColumnTransformer:
    impute_scale_cols = [
        c for c in feature_names
        if c not in {f'{col}_missing' for col in MISSINGNESS_COLS} | {'any_survey_missing'}
    ]
    passthrough_cols = [c for c in feature_names if c not in impute_scale_cols]

    return ColumnTransformer(
        transformers=[
            (
                'impute_scale',
                Pipeline([
                    ('imputer', SimpleImputer(strategy='median')),
                    ('scaler', StandardScaler()),
                ]),
                impute_scale_cols,
            ),
            ('passthrough', 'passthrough', passthrough_cols),
        ],
        remainder='drop',
    )


def preprocess(
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
) -> dict:
    raw = load_raw_data()
    x, y, meta = build_feature_frame(raw)

    x_train, x_test, y_train, y_test, meta_train, meta_test = train_test_split(
        x, y, meta,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    preprocessor = build_preprocessor(x.columns.tolist())
    x_train_processed = preprocessor.fit_transform(x_train)
    x_test_processed = preprocessor.transform(x_test)

    processed_feature_names = preprocessor.get_feature_names_out().tolist()
    x_train_df = pd.DataFrame(x_train_processed, columns=processed_feature_names, index=x_train.index)
    x_test_df = pd.DataFrame(x_test_processed, columns=processed_feature_names, index=x_test.index)

    OUTPUT_DIR.mkdir(exist_ok=True)
    x_train_df.to_csv(OUTPUT_DIR / 'X_train.csv')
    x_test_df.to_csv(OUTPUT_DIR / 'X_test.csv')
    y_train.to_csv(OUTPUT_DIR / 'y_train.csv', header=True)
    y_test.to_csv(OUTPUT_DIR / 'y_test.csv', header=True)
    meta_train.to_csv(OUTPUT_DIR / 'meta_train.csv', index=False)
    meta_test.to_csv(OUTPUT_DIR / 'meta_test.csv', index=False)

    joblib.dump(preprocessor, OUTPUT_DIR / 'preprocessor.joblib')

    report = build_report(raw, x, x_train, x_test, y_train, y_test, processed_feature_names)
    with open(OUTPUT_DIR / 'preprocessing_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    return {
        'x_train': x_train_df,
        'x_test': x_test_df,
        'y_train': y_train,
        'y_test': y_test,
        'meta_train': meta_train,
        'meta_test': meta_test,
        'preprocessor': preprocessor,
        'report': report,
    }


def build_report(
    raw: pd.DataFrame,
    x: pd.DataFrame,
    x_train: pd.DataFrame,
    x_test: pd.DataFrame,
    y_train: pd.Series,
    y_test: pd.Series,
    processed_features: list[str],
) -> dict:
    missing_before = {
        col: int(raw[col].isna().sum()) for col in MISSINGNESS_COLS if col in raw.columns
    }
    return {
        'source_file': DATA_PATH.name,
        'rows_total': len(raw),
        'rows_train': len(x_train),
        'rows_test': len(x_test),
        'target_train_positive_rate': round(float(y_train.mean()), 4),
        'target_test_positive_rate': round(float(y_test.mean()), 4),
        'dropped_columns': sorted(LEAKAGE_COLUMNS | {TARGET}),
        'raw_feature_count': len(FEATURE_COLUMNS),
        'engineered_feature_count': len(ENGINEERED_FEATURES),
        'total_feature_count_before_processing': x.shape[1],
        'processed_feature_count': len(processed_features),
        'engineered_features': ENGINEERED_FEATURES,
        'missing_before_imputation': missing_before,
        'missing_indicators_added': [f'{c}_missing' for c in MISSINGNESS_COLS] + ['any_survey_missing'],
        'imputation_strategy': 'median (fit on train only)',
        'scaling': 'StandardScaler on imputed numeric features; missing indicators left unscaled',
        'split': f'stratified {int((1 - TEST_SIZE) * 100)}/{int(TEST_SIZE * 100)}',
        'random_state': RANDOM_STATE,
        'processed_features': processed_features,
    }


def print_report(report: dict) -> None:
    print('=' * 72)
    print('DATA PREPROCESSING SUMMARY')
    print('=' * 72)
    print(f"Source:              {report['source_file']}")
    print(f"Train / test rows:   {report['rows_train']} / {report['rows_test']}")
    print(f"Retention rate:      train {report['target_train_positive_rate']:.1%} | "
          f"test {report['target_test_positive_rate']:.1%}")
    print(f"Features:            {report['raw_feature_count']} raw + "
          f"{report['engineered_feature_count']} engineered = "
          f"{report['total_feature_count_before_processing']} total -> "
          f"{report['processed_feature_count']} processed")
    print(f"Dropped columns:     {', '.join(report['dropped_columns'])}")

    print('\nMissing values before imputation:')
    for col, count in report['missing_before_imputation'].items():
        print(f'  {col}: {count}')

    print('\nMissing indicators added:')
    for col in report['missing_indicators_added']:
        print(f'  {col}')

    print(f"\nImputation:          {report['imputation_strategy']}")
    print(f"Scaling:             {report['scaling']}")
    print(f"Split:               {report['split']} (random_state={report['random_state']})")

    print('\nOutputs saved to preprocessed/:')
    print('  X_train.csv, X_test.csv, y_train.csv, y_test.csv')
    print('  meta_train.csv, meta_test.csv')
    print('  preprocessor.joblib, preprocessing_report.json')


def main() -> None:
    result = preprocess()
    print_report(result['report'])

    print('\n' + '=' * 72)
    print('PROCESSED TRAIN SET PREVIEW (first 5 rows, first 8 columns)')
    print('=' * 72)
    print(result['x_train'].iloc[:5, :8].round(3).to_string())


if __name__ == '__main__':
    main()
