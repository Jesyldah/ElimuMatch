"""
Build a self-contained HTML dashboard for the ElimuMatch capstone.

Embeds visualization PNGs as base64 so the file opens anywhere in a browser.

Usage:
  python build_dashboard.py
  # then open dashboard.html in your browser
"""

import base64
import json
from datetime import datetime
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from feature_engineering import engineer_features
from preprocess_data import DATA_PATH, PREPROCESSED_DIR, TARGET
from train_retention_model import RANDOM_STATE, load_preprocessed

import sys

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT / 'db'))
from freshness import freshness_report  # noqa: E402
VIZ_DIR = ROOT / 'visualizations'
CLUSTER_DIR = ROOT / 'clustering_outputs'
MODEL_DIR = ROOT / 'modeling_outputs'
OUTPUT = ROOT / 'dashboard.html'

CHART_SECTIONS = [
    ('Overview', [
        ('00_pipeline_summary.png', 'Analytics Pipeline', 'End-to-end workflow from synthetic cohort to intervention routing.'),
        ('01_cohort_overview.png', 'Cohort Overview', 'Retention split, SES distribution, and primary dropout drivers.'),
        ('02_retention_by_ses.png', 'Retention by SES', 'Socioeconomic gradient: disadvantage compounds dropout risk.'),
    ]),
    ('Data Exploration', [
        ('03_distributions_by_retention.png', 'Key Distributions', 'GPA trend, failures, commute, and health absences by status.'),
        ('04_missingness_by_ses.png', 'Missing Data Pattern', 'Survey field gaps are slightly higher in lower/middle SES bands.'),
        ('07_correlation_heatmap.png', 'Correlation Heatmap', 'Relationships among core predictors and the retention outcome.'),
    ]),
    ('Feature Engineering', [
        ('05_engineered_feature_correlations.png', 'Engineered Features', 'Domain-informed composites correlated with retention.'),
        ('06_risk_landscape_scatter.png', 'Risk Landscape', 'Academic risk vs. access barrier burden across students.'),
        ('08_intervention_risk_flags.png', 'Intervention Flags', 'Binary risk markers compared across dropped vs. retained students.'),
    ]),
    ('Model Performance', [
        ('29_modeling_selection_scatter.png', 'Why This Model', 'Near-tied AUC; prefer higher dropout recall for interventions.'),
        ('25_modeling_metrics_panel.png', 'Full Metric Panel', 'AUC, dropout recall/precision/F1, and accuracy across models.'),
        ('26_modeling_cv_vs_test.png', 'CV vs Test AUC', 'Generalization check from cross-validation to held-out test.'),
        ('20_modeling_comparison.png', 'AUC & Dropout Recall', 'Tuned models vs baseline: ranking vs business catch-rate.'),
        ('21_modeling_roc.png', 'ROC Curve (selected)', 'Selected model discrimination on the held-out test set.'),
        ('28_modeling_pr_threshold.png', 'PR & Thresholds', 'Precision-recall and threshold trade-offs for dropout flagging.'),
        ('27_modeling_score_distributions.png', 'Score Distributions', 'Predicted dropout probabilities by actual outcome.'),
        ('22_modeling_confusion.png', 'Confusion Matrix', 'Trade-off between catching dropouts and false alarms.'),
        ('23_modeling_feature_importance.png', 'Feature Importance', 'Top drivers from the selected retention model.'),
        ('24_modeling_fairness_ses.png', 'Fairness by SES', 'Test AUC across socioeconomic quintiles.'),
        ('30_modeling_fairness_detail.png', 'Fairness Detail', 'SES AUC with sample sizes annotated.'),
    ]),
    ('Explainability (SHAP)', [
        ('31_shap_global_importance.png', 'SHAP Global Importance', 'Which features move predicted dropout risk the most.'),
        ('32_shap_beeswarm.png', 'SHAP Beeswarm', 'Direction of each feature’s effect across students.'),
        ('33_shap_bar_summary.png', 'SHAP Bar Summary', 'Average magnitude of feature contributions.'),
        ('34_shap_waterfall_high_risk.png', 'Waterfall: High Risk', 'Why one at-risk student was flagged.'),
        ('35_shap_waterfall_low_risk.png', 'Waterfall: Low Risk', 'Why a low-risk student scores as likely to stay.'),
        ('36_shap_dependence_1.png', 'Dependence Plot 1', 'How a key driver’s value changes SHAP impact.'),
        ('37_shap_dependence_2.png', 'Dependence Plot 2', 'Second key driver dependence relationship.'),
    ]),
    ('Risk Personas', [
        ('14_cluster_k_selection.png', 'Choosing k', 'Elbow and silhouette scores used to select the number of personas.'),
        ('15_persona_pca_scatter.png', 'Persona Map', 'PCA projection of students colored by K-Means risk persona.'),
        ('16_persona_retention.png', 'Retention by Persona', 'Which personas need intervention first.'),
        ('17_persona_radar.png', 'Risk Signatures', 'Relative academic, economic, health, barrier, and support profiles.'),
    ]),
    ('Matching & targeting', [
        ('38_intervention_matrix_heatmap.png', 'Intervention Matrix', 'Persona × action priority. fees, tutoring, health, digital, enrichment.'),
        ('39_signal_intervention_matrix.png', 'Signal Eligibility Guide', 'Which risk signals unlock which help channels.'),
        ('40_intervention_assignment_mix.png', 'Assignments Applied', 'How the matrix maps onto the student cohort by channel.'),
        ('18_sponsor_matching.png', 'Budget Portfolio', 'Illustrative allocation across support types including school fees.'),
        ('19_fee_support_priority.png', 'Fee Channel Queue', 'Top students prioritized for term-fee support via the helper portal.'),
    ]),
]


def img_to_base64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode('ascii')


def compute_metrics() -> dict:
    df = engineer_features(pd.read_csv(DATA_PATH))
    data = load_preprocessed()
    x_train, x_test = data['x_train'], data['x_test']
    y_train, y_test = data['y_train'], data['y_test']

    lr = LogisticRegression(max_iter=2000, random_state=RANDOM_STATE, class_weight='balanced')
    rf = RandomForestClassifier(
        n_estimators=300, max_depth=8, random_state=RANDOM_STATE, class_weight='balanced',
    )
    lr.fit(x_train, y_train)
    rf.fit(x_train, y_train)
    lr_auc = roc_auc_score(y_test, lr.predict_proba(x_test)[:, 1])
    rf_auc = roc_auc_score(y_test, rf.predict_proba(x_test)[:, 1])

    ses_ret = (
        df.groupby('socioeconomic_status_index')['retained']
        .mean()
        .mul(100)
        .round(1)
        .to_dict()
    )
    dropout = (
        df.loc[df['retained'] == 0, 'dropout_reason']
        .value_counts()
        .head(3)
        .to_dict()
    )

    personas = []
    persona_path = CLUSTER_DIR / 'persona_profiles.csv'
    if persona_path.exists():
        persona_df = pd.read_csv(persona_path)
        personas = persona_df.to_dict(orient='records')

    selected_model = 'Logistic Regression'
    selected_auc = round(max(lr_auc, rf_auc), 3)
    dropout_recall = None
    report_path = MODEL_DIR / 'modeling_report.json'
    if report_path.exists():
        with open(report_path, encoding='utf-8') as f:
            mreport = json.load(f)
        selected_model = mreport.get('selected_model', selected_model)
        selected_auc = round(float(mreport.get('test_metrics', {}).get('auc', selected_auc)), 3)
        dr = mreport.get('test_metrics', {}).get('recall_dropout')
        dropout_recall = None if dr is None else round(float(dr), 3)

    return {
        'students': len(df),
        'schools': int(df['school_id'].nunique()),
        'retention_pct': round(df['retained'].mean() * 100, 1),
        'dropped': int((df['retained'] == 0).sum()),
        'features_raw': 16,
        'features_engineered': 16,
        'features_total': 37,
        'lr_auc': round(lr_auc, 3),
        'rf_auc': round(rf_auc, 3),
        'selected_model': selected_model,
        'selected_auc': selected_auc,
        'dropout_recall': dropout_recall,
        'ses_retention': ses_ret,
        'top_dropout_reasons': dropout,
        'missing_pct': round(df[['cash_flow_volatility', 'commute_barrier_score']].isna().mean().mean() * 100, 1),
        'personas': personas,
        'n_personas': len(personas),
    }


def render_chart_card(filename: str, title: str, caption: str) -> str:
    path = VIZ_DIR / filename
    if not path.exists():
        return f'<div class="card error">Missing chart: {filename}</div>'
    b64 = img_to_base64(path)
    anchor = filename.replace('.png', '')
    return f"""
    <article class="chart-card" id="{anchor}">
      <div class="chart-meta">
        <h3>{title}</h3>
        <p>{caption}</p>
      </div>
      <img src="data:image/png;base64,{b64}" alt="{title}" loading="lazy" />
    </article>
    """


def build_html(metrics: dict) -> str:
    ses_rows = ''.join(
        f'<tr><td>Q{q}</td><td>{pct}%</td></tr>'
        for q, pct in sorted(metrics['ses_retention'].items())
    )
    dropout_rows = ''.join(
        f'<li><span>{reason.replace("_", " ").title()}</span><strong>{count}</strong></li>'
        for reason, count in metrics['top_dropout_reasons'].items()
    )

    persona_cards = ''
    for p in metrics.get('personas', []):
        ret = float(p.get('retention_rate', 0)) * 100
        tone = 'warn' if ret < 85 else ('gold' if ret < 93 else 'ok')
        persona_cards += f"""
        <div class="persona-card {tone}">
          <div class="persona-name">{p.get('persona', '')}</div>
          <div class="persona-stats">
            <span>{int(p.get('n', 0))} students</span>
            <span>{p.get('share_pct', 0)}% of cohort</span>
            <span>{ret:.1f}% retained</span>
          </div>
          <div class="persona-action">{p.get('recommended_intervention', '')}</div>
        </div>
        """

    fresh = freshness_report()
    if fresh.get('ok'):
        fresh_layer_rows = ''.join(
            f"<tr><td>{l['label']}</td><td>{l['mode']}</td><td>{l['cadence']}</td>"
            f"<td>{l.get('last_updated') or '-'}</td></tr>"
            for l in fresh.get('layers', [])
        )
        cov = fresh.get('coverage', {})
        fresh_panel = f"""
        <h3 style="font-size:0.85rem;color:var(--muted);margin:1.25rem 0 0.5rem;">DATA FRESHNESS &amp; COVERAGE</h3>
        <p style="color:var(--muted);font-size:0.9rem;margin-bottom:0.75rem;">{cov.get('honesty', '')}</p>
        <table>
          <thead><tr><th>Layer</th><th>Mode</th><th>Cadence</th><th>Last updated</th></tr></thead>
          <tbody>{fresh_layer_rows}</tbody>
        </table>
        <p style="color:var(--muted);font-size:0.85rem;margin-top:0.75rem;">
          Coverage: {cov.get('students', 0):,} students · {cov.get('schools', 0)} schools ·
          {cov.get('counties', 0)} counties · {cov.get('geography', '')}
        </p>
        """
    else:
        fresh_panel = """
        <div class="callout"><strong>Freshness:</strong> Run <code>python db/init_db.py</code> to enable DB timestamps.</div>
        """

    sections_html = []
    for section_title, charts in CHART_SECTIONS:
        section_id = section_title.lower().replace(' ', '-')
        cards = ''.join(render_chart_card(f, t, c) for f, t, c in charts)
        sections_html.append(f"""
        <section class="section" id="{section_id}">
          <h2>{section_title}</h2>
          <div class="chart-grid">{cards}</div>
        </section>
        """)
    sections = '\n'.join(sections_html)

    nav_blocks = []
    for section_title, charts in CHART_SECTIONS:
        section_id = section_title.lower().replace(' ', '-')
        chart_links = ''.join(
            f'<a class="nav-chart" href="#{filename.replace(".png", "")}">{title}</a>'
            for filename, title, _ in charts
        )
        nav_blocks.append(f"""
        <div class="nav-group">
          <a class="nav-section" href="#{section_id}">{section_title}</a>
          {chart_links}
        </div>
        """)
    nav_links = ''.join(nav_blocks)

    generated = datetime.now().strftime('%B %d, %Y')

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ElimuMatch | Retention Analytics</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="apple-touch-icon" href="favicon.svg" />
  <style>
    :root {{
      --bg: #0f1419;
      --surface: #1a2332;
      --surface2: #243044;
      --text: #e8edf4;
      --muted: #94a3b8;
      --teal: #2a9d8f;
      --coral: #e76f51;
      --gold: #e9c46a;
      --navy: #264653;
      --border: rgba(255,255,255,0.08);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
    }}
    .hero {{
      background: linear-gradient(135deg, #1a2332 0%, #264653 50%, #1a3a4a 100%);
      padding: 2.5rem 2rem 2rem;
      border-bottom: 1px solid var(--border);
    }}
    .hero-inner {{ max-width: 1200px; margin: 0 auto; }}
    .badge {{
      display: inline-block;
      background: rgba(42,157,143,0.2);
      color: var(--teal);
      padding: 0.3rem 0.75rem;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      margin-bottom: 0.75rem;
    }}
    h1 {{ font-size: 2rem; font-weight: 700; margin-bottom: 0.4rem; }}
    .subtitle {{ color: var(--muted); max-width: 680px; font-size: 1.05rem; }}
    .meta {{ color: var(--muted); font-size: 0.85rem; margin-top: 1rem; }}
    .home-link {{
      display: inline-block;
      margin-bottom: 0.85rem;
      color: var(--teal);
      text-decoration: none;
      font-size: 0.9rem;
      font-weight: 600;
    }}
    .home-link:hover {{ text-decoration: underline; }}
    .hero-actions {{
      display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 1rem;
    }}
    .hero-actions a {{
      display: inline-block;
      padding: 0.4rem 0.85rem;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.25);
      color: #e8edf4;
      text-decoration: none;
      font-size: 0.85rem;
    }}
    .hero-actions a.primary {{
      background: rgba(42,157,143,0.25);
      border-color: var(--teal);
      color: var(--teal);
      font-weight: 600;
    }}
    .hero-actions a:hover {{ background: rgba(255,255,255,0.1); }}

    .kpi-row {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 1rem;
      max-width: 1200px;
      margin: -1.5rem auto 0;
      padding: 0 2rem;
      position: relative;
      z-index: 2;
    }}
    .kpi {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.1rem 1.25rem;
      text-align: center;
    }}
    .kpi .value {{ font-size: 1.75rem; font-weight: 700; color: var(--teal); }}
    .kpi .value.warn {{ color: var(--coral); }}
    .kpi .label {{ font-size: 0.8rem; color: var(--muted); margin-top: 0.2rem; text-transform: uppercase; letter-spacing: 0.05em; }}

    .layout {{
      display: grid;
      grid-template-columns: 260px 1fr;
      gap: 2rem;
      max-width: 1200px;
      margin: 2rem auto;
      padding: 0 2rem 3rem;
    }}
    @media (max-width: 900px) {{
      .layout {{ grid-template-columns: 1fr; }}
      .sidebar {{ position: static !important; }}
    }}

    .sidebar {{
      position: sticky;
      top: 1.5rem;
      align-self: start;
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem;
      max-height: calc(100vh - 3rem);
      overflow-y: auto;
    }}
    .sidebar h2 {{ font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 0.75rem; }}
    .nav-group {{
      margin-bottom: 0.85rem;
      padding-bottom: 0.65rem;
      border-bottom: 1px solid var(--border);
    }}
    .nav-group:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
    .nav-section {{
      display: block;
      color: var(--gold) !important;
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 700;
      letter-spacing: 0.02em;
      padding: 0.35rem 0 0.45rem;
    }}
    .nav-section:hover {{ color: var(--teal) !important; }}
    .nav-chart {{
      display: block;
      color: var(--muted);
      text-decoration: none;
      font-size: 0.8rem;
      padding: 0.28rem 0 0.28rem 0.65rem;
      border-left: 2px solid var(--border);
    }}
    .nav-chart:hover {{ color: var(--teal); border-left-color: var(--teal); }}
    .section {{ margin-bottom: 2.5rem; scroll-margin-top: 1.25rem; }}
    .section > h2 {{
      font-size: 1.35rem;
      margin-bottom: 1.25rem;
      padding-bottom: 0.5rem;
      border-bottom: 2px solid var(--teal);
      display: inline-block;
    }}

    .panel {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.25rem;
      margin-bottom: 1.5rem;
    }}
    .panel h2 {{ font-size: 1rem; margin-bottom: 1rem; color: var(--gold); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
    th, td {{ padding: 0.5rem 0.75rem; text-align: left; border-bottom: 1px solid var(--border); }}
    th {{ color: var(--muted); font-weight: 500; }}
    ul.stats {{ list-style: none; }}
    ul.stats li {{
      display: flex; justify-content: space-between;
      padding: 0.45rem 0; border-bottom: 1px solid var(--border);
      font-size: 0.9rem;
    }}
    .callout {{
      background: rgba(231,111,81,0.1);
      border-left: 3px solid var(--coral);
      padding: 0.85rem 1rem;
      border-radius: 0 8px 8px 0;
      font-size: 0.88rem;
      color: var(--muted);
      margin-top: 1rem;
    }}
    .persona-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 0.85rem;
      margin-top: 1rem;
    }}
    .persona-card {{
      background: var(--surface2);
      border-radius: 10px;
      padding: 1rem;
      border-top: 3px solid var(--teal);
    }}
    .persona-card.warn {{ border-top-color: var(--coral); }}
    .persona-card.gold {{ border-top-color: var(--gold); }}
    .persona-card.ok {{ border-top-color: var(--teal); }}
    .persona-name {{ font-weight: 700; margin-bottom: 0.45rem; }}
    .persona-stats {{
      display: flex; flex-wrap: wrap; gap: 0.45rem;
      font-size: 0.78rem; color: var(--muted); margin-bottom: 0.55rem;
    }}
    .persona-stats span {{
      background: rgba(255,255,255,0.05);
      padding: 0.15rem 0.45rem;
      border-radius: 999px;
    }}
    .persona-action {{ font-size: 0.82rem; color: var(--text); }}

    .chart-grid {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }}
    .chart-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      scroll-margin-top: 1.25rem;
    }}
    .chart-meta {{ padding: 1.1rem 1.25rem 0.5rem; }}
    .chart-meta h3 {{ font-size: 1.05rem; margin-bottom: 0.3rem; }}
    .chart-meta p {{ font-size: 0.88rem; color: var(--muted); }}
    .chart-card img {{
      width: 100%;
      display: block;
      background: #fafafa;
    }}
    footer {{
      text-align: center;
      color: var(--muted);
      font-size: 0.8rem;
      padding: 2rem;
      border-top: 1px solid var(--border);
    }}
  </style>
</head>
<body>
  <header class="hero">
    <div class="hero-inner">
      <span class="badge">Predicting secondary school dropout risk</span>
      <h1>ElimuMatch Retention Analytics</h1>
      <p class="subtitle">
        Dropout-risk scoring that routes students to the right help channel (fees, tutoring,
        health, digital access, enrichment) and rolls up to schools for foundation targeting.
        Synthetic cohort (n={metrics['students']:,}) · documented pipeline · equity-aware evaluation.
      </p>
      <p class="meta">Generated {generated} · Data: elimu_match_data_v4.csv</p>
      <div class="hero-actions">
        <a class="primary" href="index.html">← Project home</a>
        <a href="ops_dashboard.html">Support Hub</a>
        <a href="sponsor_portal.html">Helper portal</a>
        <a href="db/schema_dashboard.html">Schema docs</a>
      </div>
    </div>
  </header>

  <div class="kpi-row">
    <div class="kpi"><div class="value">{metrics['students']:,}</div><div class="label">Students</div></div>
    <div class="kpi"><div class="value">{metrics['schools']}</div><div class="label">Schools</div></div>
    <div class="kpi"><div class="value">{metrics['retention_pct']}%</div><div class="label">Retention Rate</div></div>
    <div class="kpi"><div class="value warn">{metrics['dropped']}</div><div class="label">Dropped Out</div></div>
    <div class="kpi"><div class="value">{metrics['lr_auc']}</div><div class="label">LR Test AUC</div></div>
    <div class="kpi"><div class="value">{metrics['rf_auc']}</div><div class="label">RF Test AUC</div></div>
    <div class="kpi"><div class="value">{metrics['selected_auc']}</div><div class="label">Selected AUC</div></div>
    <div class="kpi"><div class="value">{'{:.0%}'.format(metrics['dropout_recall']) if metrics.get('dropout_recall') is not None else '-'}</div><div class="label">Dropout Recall</div></div>
    <div class="kpi"><div class="value">{metrics['features_total']}</div><div class="label">Features</div></div>
    <div class="kpi"><div class="value">{metrics['n_personas']}</div><div class="label">Risk Personas</div></div>
  </div>

  <div class="layout">
    <aside class="sidebar">
      <h2>Jump to Section</h2>
      {nav_links}
    </aside>

    <main>
      <div class="panel">
        <h2>Key Insights</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem;">
          <div>
            <h3 style="font-size:0.85rem;color:var(--muted);margin-bottom:0.5rem;">RETENTION BY SES QUINTILE</h3>
            <table>
              <thead><tr><th>Quintile</th><th>Retention</th></tr></thead>
              <tbody>{ses_rows}</tbody>
            </table>
          </div>
          <div>
            <h3 style="font-size:0.85rem;color:var(--muted);margin-bottom:0.5rem;">TOP DROPOUT DRIVERS</h3>
            <ul class="stats">{dropout_rows}</ul>
          </div>
        </div>
        <div class="callout">
          <strong>How ElimuMatch uses this:</strong>
          Predict dropout risk → explain drivers → assign a primary channel
          (fees · tutoring · health · digital · enrichment) → match helpers to students
          and surface school-level need for foundations. The helper portal deepens the fee channel;
          the Support Hub tracks every channel and school support needs.
        </div>
        <div class="callout">
          <strong>Data note:</strong> Documented synthetic cohort for proof-of-concept demonstration.
          ~{metrics['missing_pct']}% average missingness on survey fields. Exclude <code>retention_risk_score</code> from training (label leakage).
        </div>
        {fresh_panel}
        <h3 style="font-size:0.85rem;color:var(--muted);margin:1.25rem 0 0.35rem;">K-MEANS RISK PERSONAS</h3>
        <div class="persona-grid">
          {persona_cards}
        </div>
      </div>

      {sections}
    </main>
  </div>

  <footer>
    ElimuMatch · Retention analytics and intervention evidence
  </footer>
</body>
</html>"""


def main() -> None:
    if not VIZ_DIR.exists():
        raise FileNotFoundError('Run visualize.py first to generate charts in visualizations/')

    metrics = compute_metrics()
    html = build_html(metrics)
    OUTPUT.write_text(html, encoding='utf-8')
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f'Dashboard saved: {OUTPUT}')
    print(f'File size: {size_mb:.1f} MB (images embedded)')
    print(f'Open in browser: file:///{OUTPUT.as_posix()}')


if __name__ == '__main__':
    main()
