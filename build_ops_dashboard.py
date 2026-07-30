"""
Build ElimuMatch organization ops dashboard (monitoring / issues / progress).

Usage:
  python build_ops_dashboard.py
  # Open ops_dashboard.html — or via server:
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
  <title>ElimuMatch — Ops Monitor</title>
  <style>
    :root {
      --bg: #f4f7f8;
      --surface: #ffffff;
      --ink: #1a2b32;
      --muted: #5b6b73;
      --line: #d7e0e4;
      --teal: #1f7a6c;
      --teal-soft: #e6f3f0;
      --coral: #c45c3e;
      --coral-soft: #f8ebe7;
      --amber: #b8860b;
      --amber-soft: #f7f0dc;
      --navy: #243b48;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: "Segoe UI", system-ui, sans-serif;
      background:
        radial-gradient(1200px 500px at 10% -10%, #dceeea 0%, transparent 55%),
        radial-gradient(900px 400px at 100% 0%, #e8eef2 0%, transparent 50%),
        var(--bg);
      color: var(--ink);
      line-height: 1.45;
    }
    header {
      background: linear-gradient(120deg, var(--navy), #1f5c55 70%);
      color: #f5faf9;
      padding: 1.75rem 1.5rem 1.4rem;
    }
    .wrap { max-width: 1180px; margin: 0 auto; padding: 0 1.25rem 2.5rem; }
    header .wrap { padding-bottom: 0; }
    .eyebrow {
      font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase;
      opacity: 0.8; margin-bottom: 0.35rem;
    }
    h1 { font-size: 1.7rem; font-weight: 700; margin-bottom: 0.35rem; }
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
    .btn.solid { background: #fff; color: var(--navy); border-color: #fff; font-weight: 600; }
    .btn:hover { background: rgba(255,255,255,0.12); }
    .btn.solid:hover { background: #e8f4f1; }

    .kpis {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 0.75rem;
      margin-top: -1.1rem;
      position: relative;
      z-index: 2;
    }
    .kpi {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 0.9rem 1rem;
    }
    .kpi .v { font-size: 1.35rem; font-weight: 700; color: var(--teal); }
    .kpi .v.warn { color: var(--coral); }
    .kpi .l { font-size: 0.72rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; margin-top: 0.15rem; }

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
      font-size: 0.95rem;
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
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 0.65rem;
      margin-top: 1rem;
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
      <div class="eyebrow">ElimuMatch · Organization</div>
      <h1>Ops Monitor</h1>
      <p class="sub">
        Track helper matching across channels, investigate cases, and see where schools need
        fee, tutoring, health, or digital resources — for ops teams and foundation targeting.
      </p>
      <div class="meta-row">
        <span class="pill" id="genAt">Generated —</span>
        <span class="pill" id="apiPill">API offline · embedded snapshot</span>
      </div>
      <div class="actions">
        <a class="btn solid" href="index.html">← Project home</a>
        <button class="btn" type="button" id="refreshBtn">Refresh from ledger</button>
        <a class="btn" href="sponsor_portal.html">Helper portal</a>
        <a class="btn" href="dashboard.html">Analytics dashboard</a>
        <a class="btn" href="db/schema_dashboard.html">Schema docs</a>
      </div>
    </div>
  </header>

  <div class="wrap">
    <section class="kpis" id="kpis"></section>

    <section class="panel full" style="margin-top:1rem">
      <h2>Pilot success criteria</h2>
      <p class="hint">What “good” looks like in a live pilot — current PoC progress where measurable.</p>
      <div class="pilot-strip" id="pilotKpis"></div>
      <p class="hint" id="fairnessCadence" style="margin:0.75rem 0 0"></p>
    </section>

    <section class="panel full">
      <h2>Illustrative impact</h2>
      <p class="hint">Retention (historical label) for students with vs without a completed gift.</p>
      <div id="impact"></div>
    </section>

    <div class="grid">
      <section class="panel">
        <h2>Needs attention</h2>
        <p class="hint">Automated investigation queue from ledger + risk thresholds.</p>
        <div id="issues"></div>
      </section>
      <section class="panel">
        <h2>Progress</h2>
        <p class="hint">Fee-channel coverage and full intervention mix (latest score run).</p>
        <div id="progress"></div>
      </section>
    </div>

    <div class="grid3">
      <section class="panel">
        <h2>Term aging</h2>
        <p class="hint">Outstanding arrears by term — older terms first for urgency.</p>
        <div id="termAging"></div>
      </section>
      <section class="panel">
        <h2>Other help channels</h2>
        <p class="hint">Tutoring, health, digital, enrichment — routed for schools and partners.</p>
        <div id="nonFee"></div>
      </section>
      <section class="panel">
        <h2>Fee-queue fairness</h2>
        <p class="hint">Gender and SES mix among school-fee-support recommendations.</p>
        <div id="fairness"></div>
      </section>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>Stuck partial pays</h2>
        <p class="hint">Students with ≥1 gift who still owe a large balance.</p>
        <div id="stuck"></div>
      </section>
      <section class="panel">
        <h2>Rejected settlements</h2>
        <p class="hint">Blocked pays (overpayment / stale balance) — trust &amp; UX friction.</p>
        <div id="rejections"></div>
      </section>
    </div>

    <div class="grid">
      <section class="panel">
        <h2>School concentration — arrears</h2>
        <p class="hint">Schools holding the most outstanding balances.</p>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>School</th><th>County</th><th>Students</th><th>Arrears</th></tr>
            </thead>
            <tbody id="schoolsArrears"></tbody>
          </table>
        </div>
      </section>
      <section class="panel">
        <h2>School concentration — gifts</h2>
        <p class="hint">Where sponsor KES is landing (equity check).</p>
        <div id="schoolsGiftWarn" class="hint"></div>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>School</th><th>Gifts</th><th>KES</th><th>Students</th></tr>
            </thead>
            <tbody id="schoolsGifts"></tbody>
          </table>
        </div>
      </section>
    </div>

    <section class="panel full">
      <h2>School resource targets</h2>
      <p class="hint">
        For foundations and CSR: where need clusters by school — fee, tutoring, health, digital, enrichment.
        Use this to place labs, clinic partnerships, tutoring contracts, or fee funds.
      </p>
      <div style="overflow-x:auto">
        <table>
          <thead>
            <tr>
              <th>School</th>
              <th>County</th>
              <th>Fee</th>
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

    <section class="panel full">
      <h2>County hotspots — fee support queue</h2>
      <p class="hint">Where arrears and recommended fee support concentrate (top 12).</p>
      <div style="overflow-x:auto">
        <table>
          <thead>
            <tr>
              <th>County</th>
              <th>Fee-support students</th>
              <th>Arrears (KES)</th>
              <th>Avg risk</th>
              <th>With gift</th>
            </tr>
          </thead>
          <tbody id="counties"></tbody>
        </table>
      </div>
    </section>

    <div class="grid">
      <section class="panel">
        <h2>Recent gifts</h2>
        <p class="hint">Latest completed helper payments (fee channel).</p>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>When</th><th>Student</th><th>School</th><th>KES</th><th>Sponsor</th></tr>
            </thead>
            <tbody id="activity"></tbody>
          </table>
        </div>
      </section>
      <section class="panel">
        <h2>Pipeline / refresh log</h2>
        <p class="hint">What ran recently (scoring vs payment imports).</p>
        <div style="overflow-x:auto">
          <table>
            <thead>
              <tr><th>ID</th><th>Type</th><th>Source</th><th>Finished</th><th>Status</th></tr>
            </thead>
            <tbody id="fresh"></tbody>
          </table>
        </div>
      </section>
    </div>

    <p class="footer-note">
      ElimuMatch PoC · synthetic cohort · fee ledger and gifts are live within this demo.
      School resource targets support foundation / CSR school-level planning.
      High-risk ≥ 60%; large arrears ≥ 40,000 KES; stuck partial ≥ 10,000 KES remaining;
      scoring SLA = 14 days. Analytics charts live in <code>dashboard.html</code>.
    </p>
  </div>

  <script>
    const EMBEDDED = __OPS_JSON__;

    const kes = (n) => Number(n || 0).toLocaleString('en-KE');
    const pct = (n) => `${Number(n || 0).toFixed(1)}%`;

    function render(data) {
      if (!data || !data.ok) {
        document.getElementById('issues').innerHTML =
          `<div class="issue high"><h3>Cannot load ops metrics</h3><p>${(data && data.error) || 'Unknown error'}</p></div>`;
        return;
      }
      const k = data.kpis || {};
      document.getElementById('genAt').textContent = `Generated ${data.generated_at || '—'}`;

      const slaWarn = k.score_sla_ok === false;
      const kpiItems = [
        ['Students', k.students, false],
        ['Fee-support queue', k.fee_support_recommended, false],
        ['High risk + arrears', k.high_risk_with_arrears, true],
        ['Total arrears (KES)', kes(k.total_arrears_kes), true],
        ['Oldest-term share', pct(k.oldest_term_arrears_pct), Number(k.oldest_term_arrears_pct) >= 40],
        ['Stuck partial pays', k.stuck_partial_pays, Number(k.stuck_partial_pays) > 0],
        ['Score age (days)', k.score_age_days ?? '—', slaWarn],
        ['Score SLA', slaWarn ? `Breach (>${k.score_sla_days}d)` : `OK (≤${k.score_sla_days}d)`, slaWarn],
        ['Rejected pays (7d)', k.rejected_settlements_7d, Number(k.rejected_settlements_7d) > 0],
        ['Gifts / raised', `${k.gifts_completed} · ${kes(k.gifts_kes)}`, false],
        ['Fee clearance', pct(k.fee_clearance_pct), false],
        ['Fee queue covered', pct((data.progress || {}).fee_support_coverage_pct), false],
      ];
      document.getElementById('kpis').innerHTML = kpiItems.map(([l, v, warn]) => `
        <div class="kpi"><div class="v ${warn ? 'warn' : ''}">${v ?? '—'}</div><div class="l">${l}</div></div>
      `).join('');

      const statusLabel = { on_track: 'On track', watch: 'Watch', n_a: 'Pilot measure' };
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
        `Fairness cadence: last check ${fc.last_check_at || '—'} · next due ${fc.next_due_date || '—'} · status ${fc.status || '—'} · ${fc.note || ''}`;

      const imp = data.illustrative_impact || {};
      const cell = (g, title) => {
        const h = (g && g.helped) || {};
        const n = (g && g.not_helped) || {};
        return `<div class="impact-box">
          <h4>${title}</h4>
          <table>
            <thead><tr><th></th><th>n</th><th>Retained %</th><th>Dropped</th></tr></thead>
            <tbody>
              <tr><td>With gift</td><td>${h.students ?? 0}</td><td>${h.retention_pct == null ? '—' : pct(h.retention_pct)}</td><td>${h.dropped ?? 0}</td></tr>
              <tr><td>No gift</td><td>${n.students ?? 0}</td><td>${n.retention_pct == null ? '—' : pct(n.retention_pct)}</td><td>${n.dropped ?? 0}</td></tr>
            </tbody>
          </table>
        </div>`;
      };
      document.getElementById('impact').innerHTML = `
        <div class="disclaimer">${imp.disclaimer || ''}${imp.small_n_warning ? ' Gifted sample is small — treat gaps as method demo only.' : ''}</div>
        <p style="font-size:0.88rem;margin-bottom:0.65rem">
          Cohort retention: <strong>${imp.cohort && imp.cohort.retention_pct != null ? pct(imp.cohort.retention_pct) : '—'}</strong>
          (${imp.cohort ? imp.cohort.retained : '—'} / ${imp.cohort ? imp.cohort.students : '—'})
          ${imp.fee_support_retention_gap_pp != null
            ? ` · Fee-support retention gap (gifted − not): <strong>${imp.fee_support_retention_gap_pp} pp</strong>`
            : ''}
        </p>
        <div class="impact-grid">
          ${cell(imp.fee_support, 'Fee-support recommended')}
          ${cell(imp.high_risk, 'High dropout risk (≥ 60%)')}
        </div>
      `;

      const issues = data.issues || [];
      document.getElementById('issues').innerHTML = issues.map(iss => {
        let sample = '';
        if (iss.sample && iss.sample.length) {
          sample = `<div style="overflow-x:auto;margin-top:0.5rem"><table>
            <thead><tr><th>Student</th><th>County</th><th>Risk</th><th>Arrears</th></tr></thead>
            <tbody>
              ${iss.sample.slice(0, 8).map(s => `<tr>
                <td>${s.display_name}</td>
                <td>${s.county_name || '—'}</td>
                <td>${s.dropout_risk == null ? '—' : Number(s.dropout_risk).toFixed(2)}</td>
                <td>${kes(s.total_outstanding_kes)}</td>
              </tr>`).join('')}
            </tbody></table></div>`;
        }
        return `<article class="issue ${iss.severity || ''}">
          <div class="top">
            <h3>${iss.title}</h3>
            <span class="sev">${iss.severity || 'flag'} · ${iss.count ?? 0}</span>
          </div>
          <p>${iss.detail || ''}</p>
          <p class="action"><strong>Next:</strong> ${iss.action || '—'}</p>
          ${sample}
        </article>`;
      }).join('');

      const p = data.progress || {};
      const mix = p.intervention_mix || [];
      const maxMix = Math.max(...mix.map(m => m.students || 0), 1);
      document.getElementById('progress').innerHTML = `
        <p style="font-size:0.9rem;margin-bottom:0.75rem">
          Fee-support with ≥1 gift:
          <strong>${p.fee_support_with_gift || 0}</strong> / ${p.fee_support_total || 0}
          (${pct(p.fee_support_coverage_pct)})
        </p>
        <div class="bars">
          ${mix.map(m => `
            <div class="bar-row">
              <span>${(m.code || 'none').replaceAll('_', ' ')}</span>
              <div class="bar-track"><div class="bar-fill" style="width:${100 * (m.students || 0) / maxMix}%"></div></div>
              <span>${m.students}</span>
            </div>
          `).join('')}
        </div>
        <p style="margin-top:0.9rem;font-size:0.8rem;color:var(--muted)">Personas</p>
        <div class="bars" style="margin-top:0.35rem">
          ${(p.persona_mix || []).map(m => `
            <div class="bar-row">
              <span>${m.persona || '—'}</span>
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
      ` : `<p class="muted">No arrears by term</p>`;

      const nf = data.non_fee_backlog || [];
      const maxNf = Math.max(...nf.map(m => m.students || 0), 1);
      document.getElementById('nonFee').innerHTML = nf.length ? `
        <div class="bars">
          ${nf.map(m => `
            <div class="bar-row wide">
              <span>${(m.code || '').replaceAll('_', ' ')}</span>
              <div class="bar-track"><div class="bar-fill" style="width:${100 * (m.students || 0) / maxNf}%;background:#2f6f8f"></div></div>
              <span>${m.students}</span>
            </div>
            <p class="muted" style="font-size:0.75rem;margin:-0.15rem 0 0.35rem 0">
              avg risk ${Number(m.avg_risk || 0).toFixed(2)} · high-risk ${m.high_risk || 0}
            </p>
          `).join('')}
        </div>
      ` : `<p class="muted">No other-channel recommendations</p>`;

      const targets = data.school_resource_targets || [];
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
        <table><thead><tr><th>Gender</th><th>n</th><th>Avg risk</th><th>Arrears</th></tr></thead>
        <tbody>
          ${gRows.map(r => `<tr>
            <td>${r.gender || '—'}</td><td>${r.students}</td>
            <td>${Number(r.avg_risk || 0).toFixed(2)}</td><td>${kes(r.arrears_kes)}</td>
          </tr>`).join('') || '<tr><td colspan="4">—</td></tr>'}
        </tbody></table>
        <p style="font-size:0.78rem;margin:0.7rem 0 0.35rem"><strong>By SES quintile</strong></p>
        <table><thead><tr><th>SES</th><th>n</th><th>Avg risk</th><th>Arrears</th></tr></thead>
        <tbody>
          ${sRows.map(r => `<tr>
            <td>Q${r.ses_quintile ?? '—'}</td><td>${r.students}</td>
            <td>${Number(r.avg_risk || 0).toFixed(2)}</td><td>${kes(r.arrears_kes)}</td>
          </tr>`).join('') || '<tr><td colspan="4">—</td></tr>'}
        </tbody></table>
      `;

      const stuck = data.stuck_partial_pays || {};
      document.getElementById('stuck').innerHTML = `
        <p style="font-size:0.88rem;margin-bottom:0.5rem">
          <strong>${stuck.count || 0}</strong> students still owe ≥ ${kes(stuck.threshold_kes)} KES after a gift
        </p>
        <div style="overflow-x:auto"><table>
          <thead><tr><th>Student</th><th>School</th><th>Gifted</th><th>Remaining</th></tr></thead>
          <tbody>
            ${(stuck.sample || []).map(s => `<tr>
              <td>${s.display_name}</td>
              <td>${s.school_name}<div class="muted" style="font-size:0.72rem">${s.county_name}</div></td>
              <td>${kes(s.gifted_kes)} <span class="muted">×${s.gift_count}</span></td>
              <td>${kes(s.remaining_kes)}</td>
            </tr>`).join('') || '<tr><td colspan="4">None above threshold</td></tr>'}
          </tbody>
        </table></div>
      `;

      const rej = data.rejected_settlements || {};
      document.getElementById('rejections').innerHTML = `
        <p style="font-size:0.88rem;margin-bottom:0.5rem">
          <strong>${rej.last_7d || 0}</strong> blocked in last 7 days ·
          <strong>${rej.total || 0}</strong> total logged
        </p>
        <div class="bars" style="margin-bottom:0.65rem">
          ${(rej.by_code || []).map(r => `
            <div class="bar-row">
              <span>${(r.code || '').replaceAll('_', ' ')}</span>
              <div class="bar-track"><div class="bar-fill" style="width:${100 * (r.attempts || 0) / Math.max(...(rej.by_code||[{attempts:1}]).map(x=>x.attempts),1)}%;background:var(--coral)"></div></div>
              <span>${r.attempts}</span>
            </div>
          `).join('') || '<p class="muted">No blocked settlements yet — will log on overpay / stale rejects.</p>'}
        </div>
        <div style="overflow-x:auto"><table>
          <thead><tr><th>When</th><th>Code</th><th>Student</th><th>Amount</th></tr></thead>
          <tbody>
            ${(rej.recent || []).map(r => `<tr>
              <td>${(r.created_at || '').slice(0, 16)}</td>
              <td>${r.code}</td>
              <td>${r.student_name || '—'}</td>
              <td>${kes(r.amount_kes)}</td>
            </tr>`).join('') || '<tr><td colspan="4">—</td></tr>'}
          </tbody>
        </table></div>
      `;

      const sc = data.school_concentration || {};
      document.getElementById('schoolsGiftWarn').textContent = sc.warn
        ? `Warning: ${sc.top_gift_school} holds ${sc.top_gift_share_pct}% of gift KES.`
        : (sc.top_gift_school
          ? `Top school: ${sc.top_gift_school} (${sc.top_gift_share_pct}% of gift KES).`
          : 'No gifts yet.');
      document.getElementById('schoolsArrears').innerHTML = (sc.by_arrears || []).map(r => `
        <tr>
          <td>${r.school_name}</td>
          <td>${r.county_name}</td>
          <td>${r.students_in_arrears}</td>
          <td>${kes(r.arrears_kes)}</td>
        </tr>
      `).join('') || `<tr><td colspan="4">—</td></tr>`;
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
          <td>${r.sponsor_name}</td>
        </tr>
      `).join('') || `<tr><td colspan="5">No gifts yet</td></tr>`;

      document.getElementById('fresh').innerHTML = (data.freshness || []).map(r => `
        <tr>
          <td>${r.run_id}</td>
          <td>${r.run_type}</td>
          <td>${r.source || '—'}</td>
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
        pill.textContent = 'API live · ledger';
        pill.classList.add('live');
        render(data);
      } catch (err) {
        pill.textContent = 'API offline · embedded snapshot';
        pill.classList.remove('live');
        render(EMBEDDED);
      }
    }

    document.getElementById('refreshBtn').addEventListener('click', refreshLive);
    render(EMBEDDED);
    refreshLive();
  </script>
</body>
</html>
"""


if __name__ == '__main__':
    path = build()
    snap = ops_snapshot()
    print(f'Ops dashboard saved: {path}')
    if snap.get('ok'):
        k = snap['kpis']
        print(
            f"KPIs: students={k['students']} fee_queue={k['fee_support_recommended']} "
            f"gifts={k['gifts_completed']} issues={len(snap.get('issues', []))}"
        )
        print('Top issue:', snap['issues'][0]['title'] if snap.get('issues') else '—')
