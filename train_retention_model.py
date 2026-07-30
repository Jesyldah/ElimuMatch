"""
Train and evaluate a student retention classifier using preprocessed data.

Run preprocess_data.py first to generate preprocessed/ artifacts.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

from preprocess_data import PREPROCESSED_DIR, preprocess

TARGET = 'retained'
RANDOM_STATE = 2026


def load_preprocessed() -> dict:
    pre_dir = PREPROCESSED_DIR
    required = [
        'X_train.csv', 'X_test.csv', 'y_train.csv', 'y_test.csv',
        'meta_test.csv', 'preprocessor.joblib',
    ]
    if not all((pre_dir / f).exists() for f in required):
        return preprocess()

    return {
        'x_train': pd.read_csv(pre_dir / 'X_train.csv'),
        'x_test': pd.read_csv(pre_dir / 'X_test.csv'),
        'y_train': pd.read_csv(pre_dir / 'y_train.csv')[TARGET],
        'y_test': pd.read_csv(pre_dir / 'y_test.csv')[TARGET],
        'meta_test': pd.read_csv(pre_dir / 'meta_test.csv'),
        'preprocessor': joblib.load(pre_dir / 'preprocessor.joblib'),
    }


def auc_by_ses_quintile(meta_test: pd.DataFrame, y_test: pd.Series, y_prob: np.ndarray) -> pd.DataFrame:
    rows = []
    ses = meta_test['socioeconomic_status_index'].values
    for quintile in sorted(np.unique(ses)):
        mask = ses == quintile
        y_q = y_test[mask]
        if y_q.nunique() < 2:
            auc = np.nan
        else:
            auc = roc_auc_score(y_q, y_prob[mask])
        rows.append({
            'ses_quintile': int(quintile),
            'n': int(mask.sum()),
            'retention_rate': round(float(y_q.mean()), 3),
            'auc': round(auc, 3) if not np.isnan(auc) else np.nan,
        })
    return pd.DataFrame(rows)


def evaluate_model(name: str, model, x_test: pd.DataFrame, y_test: pd.Series, meta_test: pd.DataFrame) -> dict:
    y_prob = model.predict_proba(x_test)[:, 1]
    y_pred = model.predict(x_test)

    print(f'\n{"=" * 60}')
    print(name)
    print('=' * 60)
    print(f'Accuracy:  {accuracy_score(y_test, y_pred):.3f}')
    print(f'AUC:       {roc_auc_score(y_test, y_prob):.3f}')
    print('\nClassification report:')
    print(classification_report(y_test, y_pred, target_names=['dropped', 'retained']))

    quintile_auc = auc_by_ses_quintile(meta_test, y_test, y_prob)
    print('AUC by SES quintile (test set):')
    print(quintile_auc.to_string(index=False))

    return {'model': name, 'accuracy': accuracy_score(y_test, y_pred), 'auc': roc_auc_score(y_test, y_prob)}


def main() -> None:
    data = load_preprocessed()
    x_train, x_test = data['x_train'], data['x_test']
    y_train, y_test = data['y_train'], data['y_test']
    meta_test = data['meta_test']

    print(f'Train: {len(x_train):,} rows | Test: {len(x_test):,} rows | Features: {x_test.shape[1]}')

    models = {
        'Logistic Regression': LogisticRegression(
            max_iter=2000, random_state=RANDOM_STATE, class_weight='balanced',
        ),
        'Random Forest': RandomForestClassifier(
            n_estimators=300, max_depth=8, random_state=RANDOM_STATE, class_weight='balanced',
        ),
    }

    results = []
    for name, model in models.items():
        model.fit(x_train, y_train)
        results.append(evaluate_model(name, model, x_test, y_test, meta_test))

    print(f'\n{"=" * 60}')
    print('Summary (preprocessed features)')
    print('=' * 60)
    for result in results:
        print(f"{result['model']:22s}  AUC={result['auc']:.3f}  Accuracy={result['accuracy']:.3f}")


if __name__ == '__main__':
    main()
