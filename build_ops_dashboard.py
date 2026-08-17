"""
Build ElimuMatch organization ops dashboard (monitoring / issues / progress).

Usage:
  python build_ops_dashboard.py
  # Open ops_dashboard.html, or via server:
  #   python db/portal_server.py
  #   http://127.0.0.1:8765/ops_dashboard.html
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'db'))

from ops_metrics import ops_snapshot  # noqa: E402

OUTPUT = ROOT / 'ops_dashboard.html'


def build() -> Path:
    data = ops_snapshot()
    payload = json.dumps(data, ensure_ascii=False)
    html = TEMPLATE.replace('__OPS_JSON__', payload)
    OUTPUT.write_text(html, encoding='utf-8')
    return OUTPUT


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ElimuMatch | Support Hub</title>
  <link rel="icon" type="image/svg+xml" href="favicon.svg" />
  <link rel="apple-touch-icon" href="favicon.svg" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <style>
    :root {
      --bg: #f6f1e8;
      --surface: #ffffff;
      --ink: #14213d;
      --muted: #5c6570;
      --line: #e0d8cc;
      --teal: #1f7a6c;
      --leaf: #1f7a6c;
      --leaf-deep: #0f5c42;
      --teal-soft: #e6f3f0;
      --coral: #c45c3e;
      --coral-soft: #f8ebe7;
      --amber: #b8860b;
      --amber-soft: #f7f0dc;
      --navy: #14213d;
      --sand: #f6f1e8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html { scroll-behavior: smooth; }
    body {
      font-family: "Outfit", system-ui, sans-serif;
      background:
        radial-gradient(1200px 500px at 10% -10%, #dceeea 0%, transparent 55%),
        radial-gradient(900px 400px at 100% 0%, #efe6d6 0%, transparent 50%),
        var(--bg);
      color: var(--ink);
      line-height: 1.45;
    }
    header {
      background: linear-gradient(120deg, #14213d, #0f5c42 70%);
      color: #f5faf9;
      padding: 1.75rem 1.5rem 1.4rem;
    }
    .wrap { max-width: 1180px; margin: 0 auto; padding: 0 1.25rem 2.5rem; }
    header .wrap { padding-bottom: 0; }
    .eyebrow {
      font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
      opacity: 0.8; margin-bottom: 0.35rem;
    }
    h1 { font-family: "Fraunces", serif; font-size: 1.85rem; font-weight: 700; margin-bottom: 0.35rem; }
    .sub { opacity: 0.85; max-width: 42rem; font-size: 0.95rem; }
    .meta-row {
      display: flex; flex-wrap: wrap; gap: 0.75rem 1.25rem;
      margin-top: 1rem; font-size: 0.82rem; opacity: 0.9;
    }
    .pill {
      display: inline-flex; align-items: center; gap: 0.35rem;
      background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.18);
      padding: 0.25rem 0.65rem; border-radius: 999px;
    }
    .pill.live { background: rgba(42,157,143,0.35); }
    .actions { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
    .btn {
      appearance: none; border: 1px solid rgba(255,255,255,0.35);
      background: transparent; color: inherit; text-decoration: none;
      padding: 0.45rem 0.85rem; border-radius: 8px; font-size: 0.85rem; cursor: pointer;
    }
    .btn.solid { background: #f4b942; color: var(--navy); border-color: #f4b942; font-weight: 600; }
    .btn:hover { background: rgba(255,255,255,0.12); }
    .btn.solid:hover { background: #f7c65a; }

    .story-nav {
      position: sticky;
      top: 0;
      z-index: 8;
      background: rgba(246, 241, 232, 0.94);
      backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--line);
      margin: 0 -1.25rem 0.5rem;
      padding: 0.55rem 1.25rem;
    }
    .story-nav ul {
      list-style: none;
      display: flex;
      flex-wrap: wrap;
      gap: 0.4rem 0.85rem;
      font-size: 0.82rem;
    }
    .story-nav a {
      color: var(--leaf-deep);
      text-decoration: none;
      font-weight: 600;
    }
    .story-nav a:hover { text-decoration: underline; }

    .today {
      margin-top: 1rem;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 1.05rem 1.15rem 1.15rem;
      border-left: 5px solid var(--leaf);
    }
    .today h2 { font-family: "Fraunces", serif; font-size: 1.15rem; margin-bottom: 0.35rem; }
    .today .pulse { font-size: 0.98rem; margin-bottom: 0.65rem; }
    .today .next {
      font-size: 0.9rem;
      background: var(--teal-soft);
      color: var(--leaf-deep);
      border-radius: 10px;
      padding: 0.55rem 0.75rem;
    }
    .today .next a { color: var(--leaf-deep); font-weight: 700; }

    .kpis {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 0.75rem;
      margin-top: 1rem;
    }
    .kpi {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.9rem 1rem;
    }
    .kpi .v { font-family: "Fraunces", serif; font-size: 1.35rem; font-weight: 700; color: var(--teal); }
    .kpi .v.warn { color: var(--coral); }
    .kpi .l { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 0.15rem; }

    .section-kicker {
      font-size: 0.72rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--leaf-deep);
      font-weight: 700;
      margin: 1.6rem 0 0.35rem;
    }
    .section-lead {
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 0.75rem;
      max-width: 46rem;
    }

    .grid {
      display: grid;
      grid-template-columns: 1.25fr 0.95fr;
      gap: 1rem;
      margin-top: 1.25rem;
    }
    @media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }

    .panel {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 1.1rem 1.15rem 1.2rem;
    }
    .panel h2 {
      font-family: "Fraunces", serif;
      font-size: 1.05rem;
      margin-bottom: 0.25rem;
    }
    .panel .hint { color: var(--muted); font-size: 0.82rem; margin-bottom: 0.85rem; }

    .issue {
      border: 1px solid var(--line);
      border-left: 4px solid var(--muted);
      border-radius: 10px;
      padding: 0.75rem 0.85rem;
      margin-bottom: 0.65rem;
      background: #fafcfc;
    }
    .issue.high { border-left-color: var(--coral); background: var(--coral-soft); }
    .issue.medium { border-left-color: var(--amber); background: var(--amber-soft); }
    .issue.info { border-left-color: var(--teal); background: var(--teal-soft); }
    .issue .top {
      display: flex; justify-content: space-between; gap: 0.75rem; align-items: baseline;
      margin-bottom: 0.25rem;
    }
    .issue .sev {
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em; font-weight: 700;
      color: var(--muted);
    }
    .issue.high .sev { color: var(--coral); }
    .issue.medium .sev { color: var(--amber); }
    .issue h3 { font-size: 0.92rem; }
    .issue p { font-size: 0.82rem; color: var(--muted); margin: 0.2rem 0; }
    .issue .action { font-size: 0.8rem; color: var(--ink); }
    table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
    th, td { text-align: left; padding: 0.4rem 0.35rem; border-bottom: 1px solid var(--line); }
    th { color: var(--muted); font-weight: 600; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.04em; }
    .bars { display: grid; gap: 0.45rem; }
    .bar-row { display: grid; grid-template-columns: 9.5rem 1fr 3rem; gap: 0.5rem; align-items: center; font-size: 0.8rem; }
    .bar-track { height: 8px; background: #e8eef1; border-radius: 99px; overflow: hidden; }
    .bar-fill { height: 100%; background: var(--teal); border-radius: 99px; }
    .grid3 {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 1rem;
      margin-top: 1rem;
    }
    @media (max-width: 1000px) { .grid3 { grid-template-columns: 1fr; } }
    .bar-row.wide { grid-template-columns: 7.5rem 1fr 4.5rem; }
    .muted { color: var(--muted); }
    .full { margin-top: 1rem; }
    .pilot-strip {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.65rem;
      margin-top: 1rem;
    }
    @media (max-width: 900px) {
      .pilot-strip { grid-template-columns: 1fr; }
    }
    .pilot-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.75rem 0.85rem;
      border-top: 3px solid var(--teal);
    }
    .pilot-card.watch { border-top-color: var(--amber); }
    .pilot-card.n_a { border-top-color: var(--muted); }
    .pilot-card .status {
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em;
      font-weight: 700; color: var(--teal); margin-bottom: 0.25rem;
    }
    .pilot-card.watch .status { color: var(--amber); }
    .pilot-card.n_a .status { color: var(--muted); }
    .pilot-card h3 { font-size: 0.86rem; margin-bottom: 0.25rem; }
    .pilot-card .cur { font-size: 1.05rem; font-weight: 700; margin: 0.2rem 0; }
    .pilot-card .tgt, .pilot-card .note { font-size: 0.75rem; color: var(--muted); }
    .lane-note {
      font-size: 0.86rem;
      color: var(--muted);
      margin: 0 0 0.85rem;
      max-width: 46rem;
    }
    .fee-channel {
      background: linear-gradient(120deg, #e8f3f0, #eef4f7);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.85rem 1rem;
      margin-bottom: 0.85rem;
    }
    .fee-channel .status {
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em;
      font-weight: 700; color: var(--teal); margin-bottom: 0.2rem;
    }
    .fee-channel h3 { font-size: 0.95rem; margin-bottom: 0.2rem; }
    .fee-channel .meta { font-size: 0.8rem; color: var(--muted); margin-bottom: 0.35rem; }
    .fee-channel .action { font-size: 0.84rem; }
    .fee-channel a { color: var(--teal); font-weight: 600; }
    .lane-strip {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 0.65rem;
    }
    @media (max-width: 900px) {
      .lane-strip { grid-template-columns: 1fr; }
    }
    .lane-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.75rem 0.85rem;
      border-top: 3px solid #2f6f8f;
    }
    .lane-card.none_routed { opacity: 0.72; border-top-color: var(--muted); }
    .lane-card .status {
      font-size: 0.68rem; text-transform: uppercase; letter-spacing: 0.06em;
      font-weight: 700; color: #2f6f8f; margin-bottom: 0.25rem;
    }
    .lane-card.none_routed .status { color: var(--muted); }
    .lane-card h3 { font-size: 0.88rem; margin-bottom: 0.15rem; }
    .lane-card .cur { font-size: 1.05rem; font-weight: 700; margin: 0.15rem 0; }
    .lane-card .owner, .lane-card .schools, .lane-card .action {
      font-size: 0.75rem; color: var(--muted); margin-top: 0.25rem;
    }
    .lane-card .action { color: var(--ink); margin-top: 0.4rem; }
    .impact-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
    }
    @media (max-width: 700px) { .impact-grid { grid-template-columns: 1fr; } }
    .impact-box {
      background: #f7fafb;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 0.75rem;
    }
    .impact-box h4 { font-size: 0.82rem; margin-bottom: 0.45rem; }
    .issue .action a { color: var(--leaf-deep); font-weight: 700; }
    .spark {
      display: flex;
      align-items: flex-end;
      gap: 3px;
      height: 56px;
      margin: 0.55rem 0 0.35rem;
    }
    .spark i {
      display: block;
      flex: 1;
      min-width: 6px;
      background: var(--teal);
      border-radius: 3px 3px 0 0;
      opacity: 0.85;
    }
    .method-block { margin-top: 0.65rem; }
    .method-block[hidden] { display: none !important; }
    .method-toggle {
      appearance: none;
      border: none;
      background: none;
      color: var(--leaf-deep);
      font: inherit;
      font-weight: 700;
      font-size: 0.85rem;
      cursor: pointer;
      text-decoration: underline;
      text-underline-offset: 3px;
      padding: 0;
    }
    .callout {
      background: var(--teal-soft);
      border: 1px solid rgba(31, 122, 108, 0.25);
      border-radius: 12px;
      padding: 0.85rem 1rem;
      margin-bottom: 0.85rem;
    }
    .callout strong { color: var(--leaf-deep); }
    .disclaimer {
      font-size: 0.78rem; color: var(--coral); background: var(--coral-soft);
      border-radius: 8px; padding: 0.55rem 0.7rem; margin-bottom: 0.75rem;
    }
    .footer-note {
      margin-top: 1.25rem; color: var(--muted); font-size: 0.78rem;
    }
    code { font-size: 0.85em; background: #eef3f5; padding: 0.05rem 0.3rem; border-radius: 4px; }
  </style>
</head>
<body>
  <header>
    <div class="wrap">
      <div class="eyebrow">ElimuMatch</div>
      <h1>Support Hub</h1>
      <p class="sub">
        See what needs attention today, whether students recommended for fee help are getting gifts,
        and where schools need support.
      </p>
      <div class="meta-row">
        <span class="pill" id="genAt">Generated -</span>
        <span class="pill" id="apiPill">Saved snapshot</span>
      </div>
      <div class="actions">
        <a class="btn solid" href="index.html">Project home</a>
        <button class="btn" type="button" id="refreshBtn">Refresh numbers</button>
        <a class="btn" href="sponsor_portal.html">Helper portal</a>
        <a class="btn" href="dashboard.html">Analytics dashboard</a>
      </div>
    </div>
  </header>

  <div class="wrap">
    <nav class="story-nav" aria-label="Support Hub sections">
      <ul>
        <li><a href="#today">Today</a></li>
        <li><a href="#pilot">Progress</a></li>
        <li><a href="#issues">Cases</a></li>
        <li><a href="#schools">Channels</a></li>
        <li><a href="#ledger">Fees</a></li>
        <li><a href="#freshness">Activity</a></li>
      </ul>
    </nav>

    <section class="today" id="today">
      <div class="eyebrow" style="opacity:1;color:var(--leaf-deep)">Today</div>
      <h2>What needs attention</h2>
      <p class="pulse" id="todayPulse">Loading snapshot…</p>
      <p class="next" id="todayNext"></p>
    </section>

    <section class="kpis" id="kpis"></section>

    <p class="section-kicker" id="pilot">1. Are we helping the students we meant to help?</p>
    <p class="section-lead">These goals show whether recommended students are getting gifts, whether scores are current, and whether gifts land on school fees.</p>
    <section class="panel full" style="margin-top:0">
      <h2>Progress goals</h2>
      <p class="hint">What good looks like for the fee-support channel, with current progress.</p>
      <div class="pilot-strip" id="pilotKpis"></div>
      <p class="hint" id="fairnessCadence" style="margin:0.75rem 0 0"></p>
    </section>

    <p class="section-kicker" id="issues">2. What to work next</p>
    <p class="section-lead">Automatic alerts from unpaid fees and risk scores. Use the helper portal when a student needs a gift.</p>
    <div class="grid">
      <section class="panel">
        <h2>Cases needing attention</h2>
        <p class="hint">Urgent items first.</p>
        <div id="issuesList"></div>
      </section>
      <section class="panel">
        <h2>How support is moving</h2>
        <p class="hint">How many recommended students received a gift, recent gift activity, and recommended support types.</p>
        <div id="progress"></div>
      </section>
    </div>

    <p class="section-kicker" id="schools">3. Where to place resources</p>
    <p class="section-lead">Fee help goes to the Helper portal. Other needs go to school or partner owners, with the school table as the handoff worklist.</p>

    <section class="panel full" style="margin-top:0">
      <h2>Support channels</h2>
      <p class="hint">Who owns each need, what to do next, and whether students are listed for handoff.</p>
      <div id="supportLanes"></div>
    </section>

    <section class="panel full">
      <h2>School support needs</h2>
      <p class="hint">
        Worklist for handoffs: fees, tutoring, health, digital access, enrichment by school.
      </p>
      <div id="schoolAsk"></div>
      <div style="overflow-x:auto">
        <table>
          <thead>
            <tr>
              <th>School</th>
              <th>County</th>
              <th>Fee help</th>
              <th>Tutoring</th>
              <th>Health</th>
              <th>Digital</th>
              <th>Enrichment</th>
              <th>Avg risk</th>
            </tr>
          </thead>
          <tbody id="schoolTargets"></tbody>
        </table>
      </div>
    </section>

    <div class="grid">
      <section class="panel">
        <h2>Schools with the most unpaid fees</h2>
        <p class="hint">Where outstanding balances are highest.</p>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>School</th><th>County</th><th>Students</th><th>Unpaid fees</th></tr>
            </thead>
            <tbody id="schoolsArrears"></tbody>
          </table>
        </div>
      </section>
      <section class="panel">
        <h2>Where gifts are going</h2>
        <p class="hint">Check that help is not all landing at one school.</p>
        <div id="schoolsGiftWarn" class="hint"></div>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>School</th><th>Gifts</th><th>KES</th><th>Students helped</th></tr>
            </thead>
            <tbody id="schoolsGifts"></tbody>
          </table>
        </div>
      </section>
    </div>

    <section class="panel full">
      <h2>Counties with the most fee-support need</h2>
      <p class="hint">Where recommended fee support and unpaid fees concentrate (top 12).</p>
      <div style="overflow-x:auto">
        <table>
          <thead>
            <tr>
              <th>County</th>
              <th>Students needing fee help</th>
              <th>Unpaid fees (KES)</th>
              <th>Avg risk</th>
              <th>Already received a gift</th>
            </tr>
          </thead>
          <tbody id="counties"></tbody>
        </table>
      </div>
    </section>

    <p class="section-kicker" id="ledger">4. Fees and fairness</p>
    <p class="section-lead">Which terms are unpaid, who still needs help after a gift, and whether the fee-support list looks balanced.</p>
    <div class="grid">
      <section class="panel">
        <h2>Unpaid fees by school term</h2>
        <p class="hint">Older unpaid terms first, because they are more urgent.</p>
        <div id="termAging"></div>
      </section>
      <section class="panel">
        <h2>Who is recommended for fee help?</h2>
        <p class="hint">Gender and income mix among students recommended for school fee support.</p>
        <div id="fairness"></div>
      </section>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>Students who still need substantial support</h2>
        <p class="hint">Students who already received a gift but still have a large unpaid balance.</p>
        <div id="stuck"></div>
      </section>
      <section class="panel">
        <h2>Blocked gift attempts</h2>
        <p class="hint">Gifts that could not complete, usually because balances changed or the amount was too high.</p>
        <div id="rejections"></div>
      </section>
    </div>

    <p class="section-kicker" id="freshness">5. Recent activity</p>
    <p class="section-lead">Latest gifts and when data was last updated. Stay-in-school comparisons sit last so they do not overshadow the live support work.</p>
    <div class="grid">
      <section class="panel">
        <h2>Recent gifts</h2>
        <p class="hint">Latest completed fee gifts from helpers.</p>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>When</th><th>Student</th><th>School</th><th>KES</th><th>Helper</th></tr>
            </thead>
            <tbody id="activity"></tbody>
          </table>
        </div>
      </section>
      <section class="panel">
        <h2>Data updates</h2>
        <p class="hint">When risk scores, fee syncs, or payments were last refreshed.</p>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>ID</th><th>Update type</th><th>Source</th><th>Finished</th><th>Status</th></tr>
            </thead>
            <tbody id="fresh"></tbody>
          </table>
        </div>
      </section>
    </div>

    <section class="panel full">
      <h2>Stay-in-school comparison</h2>
      <p class="hint">Compare students who received a gift with similar students who have not. Treat small samples carefully. Hidden by default for walkthroughs.</p>
      <button class="method-toggle" type="button" id="impactToggle">Show stay-in-school tables</button>
      <div class="method-block" id="impact" hidden></div>
    </section>

    <p class="footer-note">
      ElimuMatch Support Hub · Fee gifts settle on the Helper portal · Other needs hand off to school and partner owners.
    </p>
  </div>

  <script>
    const EMBEDDED = __OPS_JSON__;

    const kes = (n) => Number(n || 0).toLocaleString('en-KE');
    const pct = (n) => `${Number(n || 0).toFixed(1)}%`;

    function render(data) {
      if (!data || !data.ok) {
        document.getElementById('issuesList').innerHTML =
          `<div class="issue high"><h3>Cannot load ops metrics</h3><p>${(data && data.error) || 'Unknown error'}</p></div>`;
        return;
      }
      const k = data.kpis || {};
      const p = data.progress || {};
      const issues = data.issues || [];
      document.getElementById('genAt').textContent = `Generated ${data.generated_at || '-'}`;

      const slaWarn = k.score_sla_ok === false;
      const coverage = p.fee_support_coverage_pct;
      const highIssues = issues.filter(i => i.severity === 'high').length;
      const kpiItems = [
        ['Students needing fee help', k.fee_support_recommended, false],
        ['Already received a gift', pct(coverage), Number(coverage) < 25],
        ['Urgent case groups', highIssues, highIssues > 0],
        ['Risk scores', slaWarn ? `Need update (${k.score_age_days}d old)` : `Current (≤${k.score_sla_days}d)`, slaWarn],
        ['Gifts so far', `${k.gifts_completed} · ${kes(k.gifts_kes)} KES`, false],
        ['Still need more support', k.stuck_partial_pays, Number(k.stuck_partial_pays) > 0],
      ];
      document.getElementById('kpis').innerHTML = kpiItems.map(([l, v, warn]) => `
        <div class="kpi"><div class="v ${warn ? 'warn' : ''}">${v ?? '-'}</div><div class="l">${l}</div></div>
      `).join('');

      const helped = p.fee_support_with_gift || 0;
      const totalFee = p.fee_support_total || k.fee_support_recommended || 0;
      const topIssue = issues[0];
      document.getElementById('todayPulse').textContent =
        `${helped} of ${totalFee} students recommended for fee support have received a gift (${pct(coverage)}). `
        + (slaWarn
          ? `Risk scores are ${k.score_age_days} days old and due for an update. `
          : 'Risk scores are up to date. ')
        + `${k.gifts_completed || 0} gift${k.gifts_completed === 1 ? '' : 's'} recorded so far.`;
      const nextEl = document.getElementById('todayNext');
      if (Number(coverage) < 25) {
        nextEl.innerHTML = `<strong>Next:</strong> Open the <a href="sponsor_portal.html">helper portal</a> and give toward a student. Fewer than 1 in 4 recommended students have received help yet. Then click Refresh numbers.`;
      } else if (topIssue && topIssue.code !== 'all_clear') {
        nextEl.innerHTML = `<strong>Next:</strong> ${topIssue.title}. ${topIssue.action || 'Review the cases below.'} <a href="#issues">See cases</a>`;
      } else {
        nextEl.innerHTML = `<strong>Next:</strong> Nothing urgent. Check school support needs for the next placement ask.`;
      }

      const statusLabel = { on_track: 'On track', watch: 'Needs attention', n_a: 'Not measured yet' };
      document.getElementById('pilotKpis').innerHTML = (data.pilot_kpis || []).map(p => `
        <article class="pilot-card ${p.status || ''}">
          <div class="status">${statusLabel[p.status] || p.status}</div>
          <h3>${p.label}</h3>
          <div class="cur">${p.current}</div>
          <div class="tgt">${p.target}</div>
          <div class="note">${p.note || ''}</div>
        </article>
      `).join('');

      const fc = data.fairness_cadence || {};
      document.getElementById('fairnessCadence').textContent =
        `Balance check: last review ${fc.last_check_at || '-'} · Next due ${fc.next_due_date || '-'} · ${fc.status === 'due' ? 'Update needed' : 'On schedule'}. ${fc.note || ''}`;

      const imp = data.illustrative_impact || {};
      const cell = (g, title) => {
        const h = (g && g.helped) || {};
        const n = (g && g.not_helped) || {};
        return `<div class="impact-box">
          <h4>${title}</h4>
          <table>
            <thead><tr><th></th><th>Students</th><th>Stayed in school %</th><th>Left</th></tr></thead>
            <tbody>
              <tr><td>Received a gift</td><td>${h.students ?? 0}</td><td>${h.retention_pct == null ? '-' : pct(h.retention_pct)}</td><td>${h.dropped ?? 0}</td></tr>
              <tr><td>No gift yet</td><td>${n.students ?? 0}</td><td>${n.retention_pct == null ? '-' : pct(n.retention_pct)}</td><td>${n.dropped ?? 0}</td></tr>
            </tbody>
          </table>
        </div>`;
      };
      document.getElementById('impact').innerHTML = `
        <div class="disclaimer">${imp.disclaimer || 'Treat outcome comparisons carefully when samples are small.'}${imp.small_n_warning ? ' The gifted group is small, so treat differences carefully.' : ''}</div>
        <p style="font-size:0.88rem;margin-bottom:0.65rem">
          Overall stay-in-school rate: <strong>${imp.cohort && imp.cohort.retention_pct != null ? pct(imp.cohort.retention_pct) : '-'}</strong>
          (${imp.cohort ? imp.cohort.retained : '-'} / ${imp.cohort ? imp.cohort.students : '-'})
        </p>
        <div class="impact-grid">
          ${cell(imp.fee_support, 'Students recommended for fee support')}
          ${cell(imp.high_risk, 'Students with high dropout risk (≥ 60%)')}
        </div>
      `;

      const sevLabel = { high: 'Urgent', medium: 'Watch', info: 'Note', low: 'Note' };
      document.getElementById('issuesList').innerHTML = issues.map(iss => {
        let sample = '';
        if (iss.sample && iss.sample.length) {
          sample = `<div style="overflow-x:auto;margin-top:0.5rem"><table>
            <thead><tr><th>Student</th><th>County</th><th>Risk</th><th>Unpaid fees</th></tr></thead>
            <tbody>
              ${iss.sample.slice(0, 8).map(s => `<tr>
                <td>${s.display_name}</td>
                <td>${s.county_name || '-'}</td>
                <td>${s.dropout_risk == null ? '-' : Number(s.dropout_risk).toFixed(2)}</td>
                <td>${kes(s.total_outstanding_kes)}</td>
              </tr>`).join('')}
            </tbody></table></div>`;
        }
        return `<article class="issue ${iss.severity || ''}">
          <div class="top">
            <h3>${iss.title}</h3>
            <span class="sev">${sevLabel[iss.severity] || 'Note'} · ${iss.count ?? 0}</span>
          </div>
          <p>${iss.detail || ''}</p>
          <p class="action"><strong>Next:</strong> ${iss.action || '-'}${['fee_queue_untouched','high_risk_large_arrears','stuck_partial_pay'].includes(iss.code) ? ' <a href="sponsor_portal.html">Open helper portal</a>' : ''}</p>
          ${sample}
        </article>`;
      }).join('') || '<p class="muted">Nothing urgent right now.</p>';

      const mix = p.intervention_mix || [];
      const maxMix = Math.max(...mix.map(m => m.students || 0), 1);
      const days = p.gifts_by_day || [];
      const maxDay = Math.max(...days.map(d => d.gifts || 0), 1);
      const supportLabel = (code) => ({
        academic_tutoring: 'Academic tutoring',
        school_fee_support: 'School fee support',
        tutoring_support: 'Tutoring',
        health_support: 'Health support',
        digital_access: 'Digital access',
        enrichment: 'Enrichment',
        counseling: 'Counseling',
        transport_support: 'Transport / boarding',
        none: 'No primary support',
      })[code] || String(code || 'other').replaceAll('_', ' ');
      const spark = days.length
        ? `<p style="font-size:0.8rem;color:var(--muted);margin-top:0.85rem">Gifts by day</p>
           <div class="spark" title="Completed gifts by day">
             ${days.map(d => `<i style="height:${Math.max(8, 100 * (d.gifts || 0) / maxDay)}%" title="${d.day}: ${d.gifts} gifts · ${kes(d.kes)} KES"></i>`).join('')}
           </div>`
        : '<p class="muted" style="margin-top:0.75rem">No gifts yet.</p>';
      document.getElementById('progress').innerHTML = `
        <p style="font-size:0.9rem;margin-bottom:0.75rem">
          Students recommended for fee support who received at least one gift:
          <strong>${p.fee_support_with_gift || 0}</strong> / ${p.fee_support_total || 0}
          (${pct(p.fee_support_coverage_pct)})
        </p>
        ${spark}
        <p style="margin-top:0.9rem;font-size:0.8rem;color:var(--muted)">Recommended support types</p>
        <div class="bars">
          ${mix.map(m => `
            <div class="bar-row">
              <span>${supportLabel(m.code)}</span>
              <div class="bar-track"><div class="bar-fill" style="width:${100 * (m.students || 0) / maxMix}%"></div></div>
              <span>${m.students}</span>
            </div>
          `).join('')}
        </div>
        <p style="margin-top:0.9rem;font-size:0.8rem;color:var(--muted)">Student groups</p>
        <div class="bars" style="margin-top:0.35rem">
          ${(p.persona_mix || []).map(m => `
            <div class="bar-row">
              <span>${m.persona || '-'}</span>
              <div class="bar-track"><div class="bar-fill" style="width:${100 * (m.students || 0) / Math.max(...(p.persona_mix||[{students:1}]).map(x=>x.students),1)}%;background:#2f6f8f"></div></div>
              <span>${m.students}</span>
            </div>
          `).join('')}
        </div>
      `;

      const terms = data.term_aging || [];
      const maxTerm = Math.max(...terms.map(t => t.arrears_kes || 0), 1);
      document.getElementById('termAging').innerHTML = terms.length ? `
        <div class="bars">
          ${terms.map(t => `
            <div class="bar-row wide">
              <span>T${t.term_number}</span>
              <div class="bar-track"><div class="bar-fill" style="width:${100 * (t.arrears_kes || 0) / maxTerm}%"></div></div>
              <span>${pct(t.share_pct)}</span>
            </div>
            <p class="muted" style="font-size:0.75rem;margin:-0.15rem 0 0.35rem 0">
              ${t.term_label}: ${kes(t.arrears_kes)} KES · ${t.students} students
            </p>
          `).join('')}
        </div>
      ` : `<p class="muted">No unpaid fees by term</p>`;

      const lanes = data.support_lanes || {};
      const feeCh = lanes.fee_channel || {};
      const otherLanes = lanes.other_lanes || [];
      const laneSchools = (list) => {
        if (!list || !list.length) return '';
        return `<p class="schools"><strong>Top schools:</strong> ${list.map(s =>
          `${s.school_name} (${s.students})`
        ).join(' · ')}</p>`;
      };
      const lanesEl = document.getElementById('supportLanes');
      if (lanesEl) {
        lanesEl.innerHTML = `
          <p class="lane-note">${lanes.note || ''}</p>
          <div class="fee-channel">
            <div class="status">${feeCh.handoff_label || 'Helper portal'}</div>
            <h3>${feeCh.label || 'School fee support'}</h3>
            <p class="meta">
              <strong>${feeCh.students || 0}</strong> students recommended ·
              Owner: ${feeCh.owner || 'Helpers via Helper portal'}
            </p>
            <p class="action">
              ${feeCh.action || ''}
              <a href="sponsor_portal.html">Open Helper portal</a>
            </p>
          </div>
          <div class="lane-strip">
            ${otherLanes.map(l => `
              <article class="lane-card ${l.handoff_status || ''}">
                <div class="status">${l.handoff_label || ''}</div>
                <h3>${l.label}</h3>
                <p class="cur">${l.students || 0} students${l.high_risk ? ` · ${l.high_risk} high risk` : ''}</p>
                <p class="owner"><strong>Owner:</strong> ${l.owner}</p>
                ${laneSchools(l.top_schools)}
                <p class="action"><strong>Next:</strong> ${l.action}</p>
              </article>
            `).join('')}
          </div>
        `;
      }

      const targets = data.school_resource_targets || [];
      const ranked = [...targets].sort((a, b) =>
        ((b.fee_support || 0) + (b.tutoring || 0) + (b.health || 0) + (b.digital || 0) + (b.enrichment || 0))
        - ((a.fee_support || 0) + (a.tutoring || 0) + (a.health || 0) + (a.digital || 0) + (a.enrichment || 0))
      );
      const topAsk = ranked[0];
      const askEl = document.getElementById('schoolAsk');
      if (askEl) {
        askEl.innerHTML = topAsk
          ? `<div class="callout"><strong>Top school ask:</strong> ${topAsk.school_name} (${topAsk.county_name}) · ${topAsk.fee_support || 0} fee help · ${topAsk.tutoring || 0} tutoring · ${topAsk.health || 0} health · ${topAsk.digital || 0} digital · ${topAsk.enrichment || 0} enrichment.</div>`
          : '';
      }
      document.getElementById('schoolTargets').innerHTML = targets.map(r => `
        <tr>
          <td>${r.school_name}<div class="muted" style="font-size:0.72rem">${r.school_type || ''}</div></td>
          <td>${r.county_name}</td>
          <td>${r.fee_support || 0}</td>
          <td>${r.tutoring || 0}</td>
          <td>${r.health || 0}</td>
          <td>${r.digital || 0}</td>
          <td>${r.enrichment || 0}</td>
          <td>${Number(r.avg_risk || 0).toFixed(2)}</td>
        </tr>
      `).join('') || `<tr><td colspan="8">No school targets yet</td></tr>`;

      const fair = data.fee_queue_fairness || {};
      const gRows = fair.by_gender || [];
      const sRows = fair.by_ses || [];
      document.getElementById('fairness').innerHTML = `
        <p style="font-size:0.78rem;margin-bottom:0.35rem"><strong>By gender</strong></p>
        <table><thead><tr><th>Gender</th><th>Students</th><th>Avg risk</th><th>Unpaid fees</th></tr></thead>
        <tbody>
          ${gRows.map(r => `<tr>
            <td>${r.gender || '-'}</td><td>${r.students}</td>
            <td>${Number(r.avg_risk || 0).toFixed(2)}</td><td>${kes(r.arrears_kes)}</td>
          </tr>`).join('') || '<tr><td colspan="4">-</td></tr>'}
        </tbody></table>
        <p style="font-size:0.78rem;margin:0.7rem 0 0.35rem"><strong>By income group</strong></p>
        <table><thead><tr><th>Income group</th><th>Students</th><th>Avg risk</th><th>Unpaid fees</th></tr></thead>
        <tbody>
          ${sRows.map(r => `<tr>
            <td>Group ${r.ses_quintile ?? '-'}</td><td>${r.students}</td>
            <td>${Number(r.avg_risk || 0).toFixed(2)}</td><td>${kes(r.arrears_kes)}</td>
          </tr>`).join('') || '<tr><td colspan="4">-</td></tr>'}
        </tbody></table>
      `;

      const stuck = data.stuck_partial_pays || {};
      document.getElementById('stuck').innerHTML = `
        <p style="font-size:0.88rem;margin-bottom:0.5rem">
          <strong>${stuck.count || 0}</strong> students still owe at least ${kes(stuck.threshold_kes)} KES after receiving a gift
        </p>
        <div style="overflow-x:auto"><table>
          <thead><tr><th>Student</th><th>School</th><th>Already gifted</th><th>Still unpaid</th></tr></thead>
          <tbody>
            ${(stuck.sample || []).map(s => `<tr>
              <td>${s.display_name}</td>
              <td>${s.school_name}<div class="muted" style="font-size:0.72rem">${s.county_name}</div></td>
              <td>${kes(s.gifted_kes)} <span class="muted">×${s.gift_count}</span></td>
              <td>${kes(s.remaining_kes)}</td>
            </tr>`).join('') || '<tr><td colspan="4">None above this threshold</td></tr>'}
          </tbody>
        </table></div>
      `;

      const rej = data.rejected_settlements || {};
      document.getElementById('rejections').innerHTML = `
        <p style="font-size:0.88rem;margin-bottom:0.5rem">
          <strong>${rej.last_7d || 0}</strong> blocked in the last 7 days ·
          <strong>${rej.total || 0}</strong> total logged
        </p>
        <div class="bars" style="margin-bottom:0.65rem">
          ${(rej.by_code || []).map(r => `
            <div class="bar-row">
              <span>${({overpayment:'Amount too high',stale_balance:'Balance changed',stale_screen:'Screen out of date'}[r.code] || String(r.code || '').replaceAll('_', ' '))}</span>
              <div class="bar-track"><div class="bar-fill" style="width:${100 * (r.attempts || 0) / Math.max(...(rej.by_code||[{attempts:1}]).map(x=>x.attempts),1)}%;background:var(--coral)"></div></div>
              <span>${r.attempts}</span>
            </div>
          `).join('') || '<p class="muted">No blocked gifts yet.</p>'}
        </div>
        <div style="overflow-x:auto"><table>
          <thead><tr><th>When</th><th>Reason</th><th>Student</th><th>Amount</th></tr></thead>
          <tbody>
            ${(rej.recent || []).map(r => `<tr>
              <td>${(r.created_at || '').slice(0, 16)}</td>
              <td>${({overpayment:'Amount too high',stale_balance:'Balance changed',stale_screen:'Screen out of date'}[r.code] || r.code)}</td>
              <td>${r.student_name || '-'}</td>
              <td>${kes(r.amount_kes)}</td>
            </tr>`).join('') || '<tr><td colspan="4">-</td></tr>'}
          </tbody>
        </table></div>
      `;

      const sc = data.school_concentration || {};
      document.getElementById('schoolsGiftWarn').textContent = sc.warn
        ? `Watch: ${sc.top_gift_school} received ${sc.top_gift_share_pct}% of all gift money.`
        : (sc.top_gift_school
          ? `Most gifts so far: ${sc.top_gift_school} (${sc.top_gift_share_pct}% of gift money).`
          : 'No gifts yet.');
      document.getElementById('schoolsArrears').innerHTML = (sc.by_arrears || []).map(r => `
        <tr>
          <td>${r.school_name}</td>
          <td>${r.county_name}</td>
          <td>${r.students_in_arrears}</td>
          <td>${kes(r.arrears_kes)}</td>
        </tr>
      `).join('') || `<tr><td colspan="4">-</td></tr>`;
      document.getElementById('schoolsGifts').innerHTML = (sc.by_gifts || []).map(r => `
        <tr>
          <td>${r.school_name}<div class="muted" style="font-size:0.72rem">${r.county_name}</div></td>
          <td>${r.gifts}</td>
          <td>${kes(r.gift_kes)}</td>
          <td>${r.students_helped}</td>
        </tr>
      `).join('') || `<tr><td colspan="4">No gifts yet</td></tr>`;

      document.getElementById('counties').innerHTML = (data.county_hotspots || []).map(r => `
        <tr>
          <td>${r.county_name}</td>
          <td>${r.fee_support_students}</td>
          <td>${kes(r.arrears_kes)}</td>
          <td>${Number(r.avg_risk || 0).toFixed(2)}</td>
          <td>${r.with_gift}</td>
        </tr>
      `).join('') || `<tr><td colspan="5">No fee-support rows</td></tr>`;

      document.getElementById('activity').innerHTML = (data.recent_activity || []).map(r => `
        <tr>
          <td>${(r.paid_at || '').slice(0, 16)}</td>
          <td>${r.student_name}</td>
          <td>${r.school_name}<div style="color:var(--muted);font-size:0.72rem">${r.county_name}</div></td>
          <td>${kes(r.amount_kes)}</td>
          <td>${(r.sponsor_name || 'Helper').replace(/^Demo Sponsor$/,'Anonymous helper').replace(/^Portal Sponsor$/,'Helper').replace(/^API Test$/,'Helper')}</td>
        </tr>
      `).join('') || `<tr><td colspan="5">No gifts yet</td></tr>`;

      document.getElementById('fresh').innerHTML = (data.freshness || []).map(r => `
        <tr>
          <td>${r.run_id}</td>
          <td>${r.run_type}</td>
          <td>${r.source || '-'}</td>
          <td>${(r.finished_at || r.started_at || '').slice(0, 16)}</td>
          <td>${r.status}</td>
        </tr>
      `).join('') || `<tr><td colspan="5">No refresh runs</td></tr>`;
    }

    async function refreshLive() {
      const pill = document.getElementById('apiPill');
      try {
        const apiBase = (location.protocol === 'file:')
          ? 'http://127.0.0.1:8765'
          : '';
        const res = await fetch(apiBase + '/api/ops', { cache: 'no-store' });
        if (!res.ok) throw new Error('HTTP ' + res.status);
        const data = await res.json();
        pill.textContent = 'Connected · live fee balances';
        pill.classList.add('live');
        render(data);
      } catch (err) {
        pill.textContent = 'Saved snapshot';
        pill.classList.remove('live');
        render(EMBEDDED);
      }
    }

    document.getElementById('refreshBtn').addEventListener('click', refreshLive);
    const impactToggle = document.getElementById('impactToggle');
    const impactBlock = document.getElementById('impact');
    if (impactToggle && impactBlock) {
      impactToggle.addEventListener('click', () => {
        const open = !impactBlock.hasAttribute('hidden');
        if (open) {
          impactBlock.setAttribute('hidden', '');
          impactToggle.textContent = 'Show stay-in-school tables';
        } else {
          impactBlock.removeAttribute('hidden');
          impactToggle.textContent = 'Hide stay-in-school tables';
        }
      });
    }
    render(EMBEDDED);
    refreshLive();
  </script>
</body>
</html>
"""


if __name__ == '__main__':
    path = build()
    snap = ops_snapshot()
    print(f'Support Hub saved: {path}')
    if snap.get('ok'):
        k = snap['kpis']
        print(
            f"KPIs: students={k['students']} fee_queue={k['fee_support_recommended']} "
            f"gifts={k['gifts_completed']} issues={len(snap.get('issues', []))}"
        )
        print('Top issue:', snap['issues'][0]['title'] if snap.get('issues') else '-')
