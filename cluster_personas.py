"""
Identify student risk personas via K-Means clustering.

Groups students by behavioral and structural characteristics (not the
retention label), then profiles each cluster for intervention targeting.

Outputs:
  clustering_outputs/student_personas.csv
  clustering_outputs/persona_profiles.csv
  clustering_outputs/cluster_model.joblib
  visualizations/14–17 cluster charts
"""

from pathlib import Path
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from feature_engineering import engineer_features
from preprocess_data import DATA_PATH

RANDOM_STATE = 2026
OUTPUT_DIR = Path(__file__).with_name('clustering_outputs')
VIZ_DIR = Path(__file__).with_name('visualizations')
K_RANGE = range(2, 8)

# Behavioral / structural features for clustering (no retention label, no leakage)
CLUSTER_FEATURES = [
    'socioeconomic_status_index',
    'resource_dilution_index',
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
    'ses_disadvantage_score',
    'academic_risk_index',
    'health_burden_index',
    'household_pressure_index',
    'support_coverage_score',
    'economic_instability_index',
    'barrier_burden_index',
]

PROFILE_METRICS = [
    'socioeconomic_status_index',
    'gpa_trend',
    'failed_subjects_count',
    'commute_barrier_score',
    'health_related_absences',
    'cash_flow_volatility',
    'digital_equity_access_score',
    'social_integration_score',
    'support_coverage_score',
    'academic_risk_index',
    'barrier_burden_index',
    'economic_instability_index',
    'health_burden_index',
]

PERSONA_COLORS = {
    0: '#E76F51',
    1: '#F4A261',
    2: '#E9C46A',
    3: '#2A9D8F',
    4: '#264653',
    5: '#8D99AE',
}


def load_enriched() -> pd.DataFrame:
    return engineer_features(pd.read_csv(DATA_PATH))


def build_cluster_matrix(df: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray, Pipeline]:
    x = df[CLUSTER_FEATURES].copy()
    pipeline = Pipeline([
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
    ])
    x_scaled = pipeline.fit_transform(x)
    return x, x_scaled, pipeline


def choose_k(x_scaled: np.ndarray) -> tuple[int, pd.DataFrame]:
    rows = []
    for k in K_RANGE:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
        labels = km.fit_predict(x_scaled)
        rows.append({
            'k': k,
            'inertia': km.inertia_,
            'silhouette': silhouette_score(x_scaled, labels),
        })
    metrics = pd.DataFrame(rows)
    # Prefer silhouette, with a soft preference for 3–5 personas (interpretable)
    candidates = metrics[(metrics['k'] >= 3) & (metrics['k'] <= 5)]
    if candidates.empty:
        candidates = metrics
    best_k = int(candidates.loc[candidates['silhouette'].idxmax(), 'k'])
    return best_k, metrics


def fit_clusters(x_scaled: np.ndarray, k: int) -> tuple[KMeans, np.ndarray]:
    model = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=20)
    labels = model.fit_predict(x_scaled)
    return model, labels


def profile_clusters(df: pd.DataFrame) -> pd.DataFrame:
    profile = (
        df.groupby('persona_id')
        .agg(
            n=('student_id', 'count'),
            retention_rate=('retained', 'mean'),
            **{f'avg_{m}': (m, 'mean') for m in PROFILE_METRICS},
        )
        .round(3)
    )
    profile['share_pct'] = (profile['n'] / len(df) * 100).round(1)
    return profile


def assign_persona_names(profile: pd.DataFrame) -> dict[int, str]:
    """
    Name personas from relative risk signatures so labels stay interpretable
    even if cluster IDs shuffle across runs.
    """
    scored = profile.copy()
    scored['risk_score'] = (
        (1 - scored['retention_rate']) * 2.0
        + scored['avg_academic_risk_index'].rank(pct=True)
        + scored['avg_barrier_burden_index'].rank(pct=True)
        + scored['avg_economic_instability_index'].rank(pct=True)
        + scored['avg_health_burden_index'].rank(pct=True)
        - scored['avg_support_coverage_score'].rank(pct=True)
    )

    names: dict[int, str] = {}
    used = set()

    for persona_id, row in scored.sort_values('risk_score', ascending=False).iterrows():
        academic = row['avg_academic_risk_index']
        barriers = row['avg_barrier_burden_index']
        economic = row['avg_economic_instability_index']
        health = row['avg_health_burden_index']
        support = row['avg_support_coverage_score']
        retention = row['retention_rate']
        commute = row['avg_commute_barrier_score']

        if retention >= 0.93 and support >= scored['avg_support_coverage_score'].median():
            label = 'Stable Achievers'
        elif academic >= scored['avg_academic_risk_index'].quantile(0.6) and retention < 0.85:
            label = 'Academic Strugglers'
        elif economic >= scored['avg_economic_instability_index'].quantile(0.6) and barriers >= scored['avg_barrier_burden_index'].median():
            label = 'Economic Pressure'
        elif health >= scored['avg_health_burden_index'].quantile(0.6):
            label = 'Health-Constrained'
        elif commute >= scored['avg_commute_barrier_score'].quantile(0.6) and barriers >= scored['avg_barrier_burden_index'].median():
            label = 'Distance Barriers'
        elif retention < 0.80:
            label = 'Compound Risk'
        else:
            label = 'Moderate Risk'

        # Ensure unique labels
        base = label
        suffix = 2
        while label in used:
            label = f'{base} ({suffix})'
            suffix += 1
        used.add(label)
        names[int(persona_id)] = label

    return names


def intervention_for_persona(name: str) -> str:
    mapping = {
        'Stable Achievers': 'Maintain engagement; STEM enrichment / peer mentoring',
        'Academic Strugglers': 'Remediation, tutoring, academic catch-up programs',
        'Economic Pressure': 'Fee support, cash-flow smoothing, school feeding',
        'Health-Constrained': 'Health screening, attendance support, counseling',
        'Distance Barriers': 'Transport subsidy, boarding options, flexible schedules',
        'Compound Risk': 'Multi-service case management (finance + academic + health)',
        'Moderate Risk': 'Light-touch monitoring and early-warning check-ins',
    }
    for key, value in mapping.items():
        if name.startswith(key):
            return value
    return 'Targeted case review'


def build_persona_summary(profile: pd.DataFrame, names: dict[int, str]) -> pd.DataFrame:
    summary = profile.copy()
    summary['persona'] = summary.index.map(names)
    summary['priority'] = summary['retention_rate'].rank(ascending=True).astype(int)
    summary['recommended_intervention'] = summary['persona'].map(intervention_for_persona)
    cols = [
        'persona', 'n', 'share_pct', 'retention_rate', 'priority',
        'avg_academic_risk_index', 'avg_barrier_burden_index',
        'avg_economic_instability_index', 'avg_health_burden_index',
        'avg_support_coverage_score', 'recommended_intervention',
    ]
    return summary[cols].sort_values('priority')


def plot_k_selection(metrics: pd.DataFrame, best_k: int) -> None:
    VIZ_DIR.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    axes[0].plot(metrics['k'], metrics['inertia'], 'o-', color='#264653', linewidth=2)
    axes[0].axvline(best_k, color='#E76F51', linestyle='--', label=f'Selected k={best_k}')
    axes[0].set_title('Elbow Method (Inertia)')
    axes[0].set_xlabel('Number of clusters (k)')
    axes[0].set_ylabel('Inertia')
    axes[0].legend()

    axes[1].plot(metrics['k'], metrics['silhouette'], 'o-', color='#2A9D8F', linewidth=2)
    axes[1].axvline(best_k, color='#E76F51', linestyle='--', label=f'Selected k={best_k}')
    axes[1].set_title('Silhouette Score')
    axes[1].set_xlabel('Number of clusters (k)')
    axes[1].set_ylabel('Silhouette')
    axes[1].legend()

    fig.suptitle('Choosing Risk Persona Count (K-Means)', fontweight='bold')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '14_cluster_k_selection.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def plot_pca_personas(x_scaled: np.ndarray, df: pd.DataFrame) -> None:
    pca = PCA(n_components=2, random_state=RANDOM_STATE)
    coords = pca.fit_transform(x_scaled)
    plot_df = df.copy()
    plot_df['pc1'] = coords[:, 0]
    plot_df['pc2'] = coords[:, 1]

    fig, ax = plt.subplots(figsize=(10, 7))
    for persona_id, group in plot_df.groupby('persona_id'):
        color = PERSONA_COLORS.get(persona_id, '#8D99AE')
        ax.scatter(
            group['pc1'], group['pc2'],
            s=35, alpha=0.65, color=color,
            label=f"{group['persona'].iloc[0]} (n={len(group)})",
        )
    ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% var)')
    ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% var)')
    ax.set_title('Student Risk Personas (PCA Projection)', fontweight='bold')
    ax.legend(fontsize=8, loc='best')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '15_persona_pca_scatter.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def plot_persona_retention(summary: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    colors = ['#E76F51' if r < 0.85 else '#E9C46A' if r < 0.93 else '#2A9D8F'
              for r in summary['retention_rate']]
    bars = ax.barh(summary['persona'], summary['retention_rate'] * 100, color=colors, edgecolor='white')
    for bar, (_, row) in zip(bars, summary.iterrows()):
        ax.text(
            bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
            f"{row['retention_rate']*100:.1f}%  ·  n={int(row['n'])}",
            va='center', fontsize=9,
        )
    ax.set_xlim(0, 110)
    ax.set_xlabel('Retention Rate (%)')
    ax.set_title('Retention by Risk Persona', fontweight='bold')
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '16_persona_retention.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def plot_persona_radar(summary: pd.DataFrame, profile: pd.DataFrame) -> None:
    dims = [
        'avg_academic_risk_index',
        'avg_barrier_burden_index',
        'avg_economic_instability_index',
        'avg_health_burden_index',
        'avg_support_coverage_score',
    ]
    labels = ['Academic Risk', 'Access Barriers', 'Economic Instability', 'Health Burden', 'Support Coverage']

    # Normalize each dimension 0–1 across personas for radar comparability
    norms = profile[dims].copy()
    for col in dims:
        mn, mx = norms[col].min(), norms[col].max()
        norms[col] = 0.05 if mx == mn else (norms[col] - mn) / (mx - mn)

    angles = np.linspace(0, 2 * np.pi, len(dims), endpoint=False).tolist()
    angles += angles[:1]

    n = len(summary)
    cols = 2
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(11, 4.2 * rows), subplot_kw=dict(polar=True))
    axes = np.atleast_1d(axes).ravel()

    for ax, (persona_id, row) in zip(axes, summary.iterrows()):
        values = norms.loc[persona_id, dims].tolist()
        values += values[:1]
        color = PERSONA_COLORS.get(int(persona_id), '#2A9D8F')
        ax.plot(angles, values, color=color, linewidth=2)
        ax.fill(angles, values, color=color, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_yticklabels([])
        ax.set_title(row['persona'], fontsize=11, fontweight='bold', pad=12)

    for ax in axes[n:]:
        ax.axis('off')

    fig.suptitle('Persona Risk Signatures', fontweight='bold', y=1.01)
    fig.tight_layout()
    fig.savefig(VIZ_DIR / '17_persona_radar.png', dpi=160, bbox_inches='tight')
    plt.close(fig)


def print_report(summary: pd.DataFrame, metrics: pd.DataFrame, best_k: int, sil: float) -> None:
    print('=' * 72)
    print('RISK PERSONA CLUSTERING')
    print('=' * 72)
    print(f'Algorithm:           K-Means')
    print(f'Selected k:          {best_k} (silhouette={sil:.3f})')
    print('k search results:')
    print(metrics.round(3).to_string(index=False))
    print('\nPersona profiles (sorted by intervention priority):')
    display = summary[[
        'persona', 'n', 'share_pct', 'retention_rate', 'priority', 'recommended_intervention'
    ]].copy()
    display['retention_rate'] = (display['retention_rate'] * 100).round(1).astype(str) + '%'
    print(display.to_string(index=False))
    print(f'\nOutputs saved to {OUTPUT_DIR}/')
    print('Charts: visualizations/14–17')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    VIZ_DIR.mkdir(exist_ok=True)

    df = load_enriched()
    _, x_scaled, pipeline = build_cluster_matrix(df)
    best_k, metrics = choose_k(x_scaled)
    model, labels = fit_clusters(x_scaled, best_k)

    df = df.copy()
    df['persona_id'] = labels
    profile = profile_clusters(df)
    names = assign_persona_names(profile)
    df['persona'] = df['persona_id'].map(names)
    summary = build_persona_summary(profile, names)

    # Persist
    keep_cols = [
        'student_id', 'school_id', 'socioeconomic_status_index', 'retained',
        'dropout_reason', 'persona_id', 'persona',
        'academic_risk_index', 'barrier_burden_index',
        'economic_instability_index', 'health_burden_index', 'support_coverage_score',
    ]
    df[keep_cols].to_csv(OUTPUT_DIR / 'student_personas.csv', index=False)
    summary.to_csv(OUTPUT_DIR / 'persona_profiles.csv')
    profile.to_csv(OUTPUT_DIR / 'persona_metrics_detail.csv')
    metrics.to_csv(OUTPUT_DIR / 'k_selection_metrics.csv', index=False)

    joblib.dump(
        {'model': model, 'pipeline': pipeline, 'features': CLUSTER_FEATURES, 'names': names},
        OUTPUT_DIR / 'cluster_model.joblib',
    )

    report = {
        'algorithm': 'KMeans',
        'selected_k': best_k,
        'silhouette': float(silhouette_score(x_scaled, labels)),
        'features_used': CLUSTER_FEATURES,
        'personas': summary.reset_index().to_dict(orient='records'),
    }
    with open(OUTPUT_DIR / 'clustering_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    # Visuals
    plot_k_selection(metrics, best_k)
    plot_pca_personas(x_scaled, df)
    plot_persona_retention(summary)
    plot_persona_radar(summary, profile)

    print_report(summary, metrics, best_k, report['silhouette'])


if __name__ == '__main__':
    main()
