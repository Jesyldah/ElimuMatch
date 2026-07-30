"""
Modeling-phase visualizations + dedicated HTML gallery.

Creates additional charts beyond modeling_phase.py and builds
modeling_gallery.html for easy review.

Run:
  python modeling_phase.py      # if artifacts missing
  python visualize_modeling.py
"""

from pathlib import Path
import base64
import json
from datetime import datetime

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)

from train_retention_model import load_preprocessed

ROOT = Path(__file__).parent
OUT = ROOT / 'modeling_outputs'
VIZ = ROOT / 'visualizations'
GALLERY = ROOT / 'modeling_gallery.html'

COLORS = {
    'ink': '#264653',
    'teal': '#2A9D8F',
    'coral': '#E76F51',
    'gold': '#E9C46A',
    'muted': '#8D99AE',
}


def setup():
    sns.set_theme(style='whitegrid', context='talk', font_scale=0.85)
    VIZ.mkdir(exist_ok=True)


def load_artifacts():
    leaderboard = pd.read_csv(OUT / 'model_leaderboard.csv')
    preds = pd.read_csv(OUT / 'test_predictions.csv')
    importance = pd.read_csv(OUT / 'feature_importance.csv') if (OUT / 'feature_importance.csv').exists() else None
    fairness = pd.read_csv(OUT / 'fairness_auc_by_ses.csv')
    with open(OUT / 'modeling_report.json', encoding='utf-8') as f:
        report = json.load(f)
    model = joblib.load(OUT / 'best_model.joblib')
    data = load_preprocessed()
    x_test = data['x_test']
    x_test = x_test.loc[:, ~x_test.columns.str.contains('^Unnamed')]
    return leaderboard, preds, importance, fairness, report, model, x_test


def save(fig, name):
    path = VIZ / name
    fig.savefig(path, dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'  saved {name}')


def plot_leaderboard_detail(leaderboard: pd.DataFrame):
    plot_df = leaderboard[leaderboard['model'] != 'Majority Class Baseline'].copy()
    metrics = ['test_auc', 'recall_dropout', 'precision_dropout', 'f1_dropout', 'accuracy']
    labels = ['Test AUC', 'Dropout Recall', 'Dropout Precision', 'Dropout F1', 'Accuracy']

    long = plot_df.melt(id_vars='model', value_vars=metrics, var_name='metric', value_name='value')
    long['metric'] = long['metric'].map(dict(zip(metrics, labels)))

    fig, ax = plt.subplots(figsize=(12, 5.5))
    sns.barplot(data=long, x='metric', y='value', hue='model',
                palette=[COLORS['teal'], COLORS['ink'], COLORS['coral']], ax=ax)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel('')
    ax.set_ylabel('Score')
    ax.set_title('Modeling Phase — Full Metric Comparison', fontweight='bold')
    ax.legend(title='', loc='upper right')
    fig.tight_layout()
    save(fig, '25_modeling_metrics_panel.png')


def plot_cv_vs_test(leaderboard: pd.DataFrame):
    plot_df = leaderboard[leaderboard['model'] != 'Majority Class Baseline'].copy()
    x = np.arange(len(plot_df))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.bar(x - width / 2, plot_df['cv_auc_mean'], width, yerr=plot_df['cv_auc_std'],
           label='CV AUC (train)', color=COLORS['ink'], capsize=4)
    ax.bar(x + width / 2, plot_df['test_auc'], width, label='Test AUC', color=COLORS['teal'])
    ax.set_xticks(x)
    ax.set_xticklabels(plot_df['model'], rotation=15)
    ax.set_ylim(0, 1)
    ax.set_ylabel('AUC')
    ax.set_title('Cross-Validation vs Held-Out Test AUC', fontweight='bold')
    ax.legend()
    fig.tight_layout()
    save(fig, '26_modeling_cv_vs_test.png')


def plot_score_distributions(preds: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    for label, name, color in [(0, 'Dropped', COLORS['coral']), (1, 'Retained', COLORS['teal'])]:
        subset = preds.loc[preds['y_true'] == label, 'prob_dropout']
        axes[0].hist(subset, bins=18, alpha=0.55, label=name, color=color, edgecolor='white')
    axes[0].set_xlabel('Predicted dropout probability')
    axes[0].set_ylabel('Students (test set)')
    axes[0].set_title('Risk Score Separation')
    axes[0].legend()

    sns.boxplot(
        data=preds.assign(Status=preds['y_true'].map({0: 'Dropped', 1: 'Retained'})),
        x='Status', y='prob_dropout', hue='Status',
        palette=[COLORS['coral'], COLORS['teal']], ax=axes[1], legend=False,
    )
    axes[1].set_ylabel('Predicted dropout probability')
    axes[1].set_title('Score Distribution by Outcome')
    axes[1].set_xlabel('')

    fig.suptitle('Selected Model — Probability Diagnostics', fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, '27_modeling_score_distributions.png')


def plot_pr_and_threshold(preds: pd.DataFrame, selected_name: str):
    y_true = preds['y_true'].values
    # Treat dropout as positive for PR curve
    y_dropout = 1 - y_true
    scores = preds['prob_dropout'].values

    precision, recall, thresholds = precision_recall_curve(y_dropout, scores)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(recall, precision, color=COLORS['coral'], lw=2)
    axes[0].set_xlabel('Recall (dropped students found)')
    axes[0].set_ylabel('Precision (of flagged students)')
    axes[0].set_title(f'Precision–Recall — Dropout ({selected_name})')
    axes[0].set_xlim(0, 1)
    axes[0].set_ylim(0, 1)

    # Threshold sweep using decision thresholds on dropout prob
    ths = np.linspace(0.05, 0.95, 37)
    recs, precs = [], []
    for t in ths:
        pred_drop = (scores >= t).astype(int)
        # Map to retained labels: dropped=0 means pred retained = 1 - pred_drop
        y_pred = 1 - pred_drop
        recs.append(recall_score(y_true, y_pred, pos_label=0, zero_division=0))
        precs.append(precision_score(y_true, y_pred, pos_label=0, zero_division=0))

    axes[1].plot(ths, recs, color=COLORS['coral'], lw=2, label='Dropout recall')
    axes[1].plot(ths, precs, color=COLORS['ink'], lw=2, label='Dropout precision')
    axes[1].axvline(0.5, color=COLORS['muted'], linestyle='--', label='Default threshold 0.5')
    axes[1].set_xlabel('Dropout probability threshold')
    axes[1].set_ylabel('Score')
    axes[1].set_ylim(0, 1)
    axes[1].set_title('Threshold Trade-off')
    axes[1].legend(fontsize=8)

    fig.suptitle('Operating Point for Intervention Flagging', fontweight='bold', y=1.02)
    fig.tight_layout()
    save(fig, '28_modeling_pr_threshold.png')


def plot_selection_story(leaderboard: pd.DataFrame, selected: str):
    plot_df = leaderboard[leaderboard['model'] != 'Majority Class Baseline'].copy()
    fig, ax = plt.subplots(figsize=(8.5, 6.5))
    for _, row in plot_df.iterrows():
        color = COLORS['teal'] if row['model'] == selected else COLORS['muted']
        size = 220 if row['model'] == selected else 120
        ax.scatter(row['test_auc'], row['recall_dropout'], s=size, color=color, zorder=3)
        ax.annotate(
            row['model'],
            (row['test_auc'], row['recall_dropout']),
            textcoords='offset points', xytext=(8, 6), fontsize=9,
            fontweight='bold' if row['model'] == selected else 'normal',
        )
    ax.set_xlabel('Test AUC (ranking quality)')
    ax.set_ylabel('Dropout Recall (catch at-risk students)')
    ax.set_xlim(0.70, 0.80)
    ax.set_ylim(0, 0.85)
    ax.axhline(0.5, color=COLORS['muted'], linestyle=':', alpha=0.7)
    ax.set_title('Why We Selected the Model\n(near-tied AUC → prefer dropout recall)', fontweight='bold')
    fig.tight_layout()
    save(fig, '29_modeling_selection_scatter.png')


def plot_fairness_detail(fairness: pd.DataFrame, selected: str):
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = [COLORS['coral'] if r < 0.85 else COLORS['gold'] if r < 0.93 else COLORS['teal']
              for r in fairness['retention_rate']]
    bars = ax.bar(
        fairness['ses_quintile'].astype(str),
        fairness['auc'],
        color=COLORS['ink'],
        edgecolor='white',
    )
    for bar, (_, row) in zip(bars, fairness.iterrows()):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
            f"AUC {row['auc']:.2f}\nn={int(row['n'])}",
            ha='center', va='bottom', fontsize=8,
        )
    ax.axhline(0.5, color=COLORS['muted'], linestyle='--')
    ax.set_ylim(0, 1.08)
    ax.set_xlabel('SES Quintile (1 = lowest)')
    ax.set_ylabel('Test AUC')
    ax.set_title(f'Fairness Check — {selected}', fontweight='bold')
    fig.tight_layout()
    save(fig, '30_modeling_fairness_detail.png')


def build_gallery_html(report: dict, chart_specs: list[tuple[str, str, str]]) -> str:
    cards = []
    for filename, title, caption in chart_specs:
        path = VIZ / filename
        if not path.exists():
            continue
        b64 = base64.b64encode(path.read_bytes()).decode('ascii')
        cards.append(f"""
        <article class="card">
          <h3>{title}</h3>
          <p>{caption}</p>
          <img src="data:image/png;base64,{b64}" alt="{title}" />
        </article>""")

    selected = report.get('selected_model', 'Selected model')
    metrics = report.get('test_metrics', {})
    generated = datetime.now().strftime('%B %d, %Y')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Elimu Match — Modeling Phase Gallery</title>
  <style>
    :root {{
      --bg: #0f1419; --surface: #1a2332; --text: #e8edf4;
      --muted: #94a3b8; --teal: #2a9d8f; --coral: #e76f51; --gold: #e9c46a;
      --border: rgba(255,255,255,0.08);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: var(--bg); color: var(--text); }}
    header {{
      padding: 2.5rem 2rem 1.5rem;
      background: linear-gradient(135deg, #1a2332, #264653);
      border-bottom: 1px solid var(--border);
    }}
    header h1 {{ font-size: 1.8rem; margin-bottom: 0.4rem; }}
    header p {{ color: var(--muted); max-width: 720px; }}
    .kpis {{
      display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 0.85rem; max-width: 1100px; margin: -1.2rem auto 0; padding: 0 2rem; position: relative; z-index: 2;
    }}
    .kpi {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
      padding: 1rem; text-align: center;
    }}
    .kpi .v {{ font-size: 1.5rem; font-weight: 700; color: var(--teal); }}
    .kpi .l {{ font-size: 0.75rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.2rem; }}
    main {{ max-width: 1100px; margin: 2rem auto; padding: 0 2rem 3rem; }}
    .card {{
      background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
      padding: 1.1rem 1.1rem 0.5rem; margin-bottom: 1.4rem;
    }}
    .card h3 {{ margin-bottom: 0.3rem; }}
    .card p {{ color: var(--muted); font-size: 0.9rem; margin-bottom: 0.8rem; }}
    .card img {{ width: 100%; border-radius: 8px; background: #fafafa; display: block; }}
    footer {{ text-align: center; color: var(--muted); font-size: 0.8rem; padding: 1.5rem; border-top: 1px solid var(--border); }}
  </style>
</head>
<body>
  <header>
    <h1>Modeling Phase Gallery</h1>
    <p>
      Retention classifier results for Elimu Match. Selected model: <strong>{selected}</strong>.
      Charts cover comparison, diagnostics, fairness, and why this model was chosen for sponsor matching.
    </p>
    <p style="margin-top:0.6rem;font-size:0.85rem;">Generated {generated}</p>
  </header>
  <div class="kpis">
    <div class="kpi"><div class="v">{metrics.get('auc', 0):.3f}</div><div class="l">Test AUC</div></div>
    <div class="kpi"><div class="v">{metrics.get('recall_dropout', 0):.0%}</div><div class="l">Dropout Recall</div></div>
    <div class="kpi"><div class="v">{metrics.get('precision_dropout', 0):.0%}</div><div class="l">Dropout Precision</div></div>
    <div class="kpi"><div class="v">{metrics.get('accuracy', 0):.0%}</div><div class="l">Accuracy</div></div>
    <div class="kpi"><div class="v">{report.get('n_features', '—')}</div><div class="l">Features</div></div>
  </div>
  <main>
    {''.join(cards)}
  </main>
  <footer>Elimu Match · Quantic MSBA Capstone · Modeling Phase</footer>
</body>
</html>"""


def main():
    setup()
    if not (OUT / 'modeling_report.json').exists():
        raise FileNotFoundError('Run modeling_phase.py first.')

    print('Building modeling visualizations...')
    leaderboard, preds, importance, fairness, report, model, x_test = load_artifacts()
    selected = report['selected_model']

    # Core charts already exist from modeling_phase; refresh extras + selection story
    plot_leaderboard_detail(leaderboard)
    plot_cv_vs_test(leaderboard)
    plot_score_distributions(preds)
    plot_pr_and_threshold(preds, selected)
    plot_selection_story(leaderboard, selected)
    plot_fairness_detail(fairness, selected)

    chart_specs = [
        ('29_modeling_selection_scatter.png', 'Model Selection Story',
         'Near-tied AUC — Logistic Regression wins on dropout recall for intervention targeting.'),
        ('25_modeling_metrics_panel.png', 'Full Metric Comparison',
         'AUC, dropout recall/precision/F1, and accuracy across tuned models.'),
        ('26_modeling_cv_vs_test.png', 'CV vs Test AUC',
         'Checks generalization from cross-validation to the held-out test set.'),
        ('20_modeling_comparison.png', 'AUC & Dropout Recall',
         'Side-by-side business and ranking metrics.'),
        ('21_modeling_roc.png', 'ROC Curve',
         f'Discrimination curve for {selected}.'),
        ('28_modeling_pr_threshold.png', 'PR Curve & Thresholds',
         'How changing the cutoff trades precision vs recall for dropout flagging.'),
        ('27_modeling_score_distributions.png', 'Score Distributions',
         'Do predicted dropout probabilities separate retained vs dropped students?'),
        ('22_modeling_confusion.png', 'Confusion Matrix',
         'Classification outcomes at the default decision threshold.'),
        ('23_modeling_feature_importance.png', 'Feature Importance',
         'Top drivers used by the selected model.'),
        ('24_modeling_fairness_ses.png', 'Fairness by SES',
         'AUC across socioeconomic quintiles.'),
        ('30_modeling_fairness_detail.png', 'Fairness Detail',
         'SES quintile AUC with sample sizes annotated.'),
    ]

    html = build_gallery_html(report, chart_specs)
    GALLERY.write_text(html, encoding='utf-8')
    print(f'\nGallery saved: {GALLERY}')
    print(f'Size: {GALLERY.stat().st_size / 1024 / 1024:.1f} MB')


if __name__ == '__main__':
    main()
