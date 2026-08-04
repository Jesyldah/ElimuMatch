"""Shared ElimuMatch look — mirrors sponsor_portal / index HTML brand."""

from __future__ import annotations

import streamlit as st

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Outfit:wght@400;500;600;700&display=swap');

:root {
  --ink: #14213d;
  --leaf: #1b7a5a;
  --leaf-deep: #0f5c42;
  --sun: #f4b942;
  --sand: #f7f1e8;
  --mist: #e8efe9;
  --muted: #5c6b73;
  --line: #e0d8cc;
  --white: #ffffff;
}

html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif;
  color: var(--ink);
}

.stApp {
  background:
    radial-gradient(900px 380px at 8% -8%, #dceeea 0%, transparent 55%),
    radial-gradient(700px 320px at 100% 0%, rgba(244,185,66,0.18) 0%, transparent 50%),
    var(--sand);
}

/* Hide Streamlit chrome clutter */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] {
  background: transparent;
}
div[data-testid="stToolbar"] { display: none; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #14213d 0%, #0f5c42 100%);
  border-right: none;
}
section[data-testid="stSidebar"] * {
  color: #f5faf9 !important;
}
section[data-testid="stSidebar"] .stRadio label {
  padding: 0.45rem 0.65rem;
  border-radius: 10px;
  margin-bottom: 0.15rem;
}
section[data-testid="stSidebar"] .stRadio label:hover {
  background: rgba(255,255,255,0.08);
}
section[data-testid="stSidebar"] hr {
  border-color: rgba(255,255,255,0.18);
}
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: rgba(245,250,249,0.78) !important;
}

/* Main typography */
h1, h2, h3, .em-brand {
  font-family: 'Fraunces', serif !important;
  color: var(--ink) !important;
  letter-spacing: -0.02em;
}
h1 { font-weight: 700 !important; }
h2, h3 { font-weight: 600 !important; }

/* Hero / page headers */
.em-hero {
  background:
    linear-gradient(120deg, rgba(20,33,61,0.92) 0%, rgba(15,92,66,0.82) 60%, rgba(27,122,90,0.75) 100%);
  color: #fff;
  border-radius: 18px;
  padding: 1.75rem 1.75rem 1.5rem;
  margin: 0 0 1.35rem 0;
  box-shadow: 0 12px 40px rgba(20,33,61,0.18);
  position: relative;
  overflow: hidden;
}
.em-hero::after {
  content: "";
  position: absolute;
  width: 280px; height: 280px;
  right: -60px; top: -80px;
  background: radial-gradient(circle, rgba(244,185,66,0.28), transparent 65%);
  pointer-events: none;
}
.em-hero .eyebrow {
  font-family: 'Outfit', sans-serif;
  font-size: 0.72rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  opacity: 0.8;
  margin-bottom: 0.45rem;
}
.em-hero .brand {
  font-family: 'Fraunces', serif;
  font-size: clamp(2rem, 4vw, 2.75rem);
  font-weight: 700;
  line-height: 1;
  margin: 0 0 0.55rem 0;
}
.em-hero h1 {
  font-family: 'Outfit', sans-serif !important;
  color: #fff !important;
  font-weight: 500 !important;
  font-size: 1.15rem !important;
  margin: 0 0 0.4rem 0 !important;
  max-width: 36ch;
  line-height: 1.35;
}
.em-hero p {
  color: rgba(255,255,255,0.82);
  margin: 0;
  max-width: 52ch;
  font-size: 0.98rem;
}

.em-page-head {
  margin: 0 0 1.1rem 0;
  padding-bottom: 0.85rem;
  border-bottom: 1px solid var(--line);
}
.em-page-head .eyebrow {
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--leaf);
  font-weight: 700;
  margin-bottom: 0.25rem;
}
.em-page-head h1 {
  margin: 0 0 0.35rem 0 !important;
  font-size: 1.85rem !important;
}
.em-page-head p {
  color: var(--muted);
  margin: 0;
  font-size: 0.95rem;
}

/* Cards / panels */
.em-card {
  background: var(--white);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.1rem 1.15rem;
  height: 100%;
  box-shadow: 0 1px 0 rgba(20,33,61,0.03);
}
.em-card .label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--leaf);
  font-weight: 700;
  margin-bottom: 0.35rem;
}
.em-card h3 {
  font-family: 'Fraunces', serif !important;
  font-size: 1.15rem !important;
  margin: 0 0 0.4rem 0 !important;
}
.em-card p {
  color: var(--muted);
  font-size: 0.9rem;
  margin: 0;
}

.em-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin: 0 0 1.25rem 0;
}
.em-kpi {
  background: var(--white);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.85rem 1rem;
  border-top: 3px solid var(--leaf);
}
.em-kpi .k {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--muted);
  font-weight: 600;
}
.em-kpi .v {
  font-family: 'Fraunces', serif;
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--leaf);
  margin-top: 0.2rem;
  line-height: 1.15;
}

.em-note {
  background: var(--mist);
  border: 1px solid #d5e3d8;
  border-radius: 12px;
  padding: 0.85rem 1rem;
  color: var(--muted);
  font-size: 0.88rem;
  margin: 0 0 1rem 0;
}
.em-note strong { color: var(--ink); }

.em-issue {
  border-radius: 10px;
  padding: 0.75rem 0.9rem;
  margin: 0 0 0.5rem 0;
  border-left: 4px solid var(--leaf);
  background: #eef6f2;
  font-size: 0.92rem;
}
.em-issue.high {
  border-left-color: #c44b4b;
  background: #fceeee;
}
.em-issue.medium {
  border-left-color: #d4a017;
  background: #fff8e8;
}
.em-issue .t { font-weight: 700; color: var(--ink); }

/* Buttons */
div.stButton > button {
  background: var(--sun) !important;
  color: var(--ink) !important;
  border: none !important;
  border-radius: 999px !important;
  font-family: 'Outfit', sans-serif !important;
  font-weight: 700 !important;
  padding: 0.55rem 1.2rem !important;
  box-shadow: 0 4px 14px rgba(244,185,66,0.35);
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div.stButton > button:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(244,185,66,0.45);
  background: #f7c65a !important;
  color: var(--ink) !important;
}
div.stButton > button[kind="primary"],
div.stButton > button[data-testid="baseButton-primary"] {
  background: var(--leaf) !important;
  color: #fff !important;
  box-shadow: 0 4px 14px rgba(27,122,90,0.3);
}
div.stButton > button[kind="primary"]:hover,
div.stButton > button[data-testid="baseButton-primary"]:hover {
  background: var(--leaf-deep) !important;
  color: #fff !important;
}

/* Inputs */
.stSelectbox label, .stMultiSelect label, .stNumberInput label, .stTextInput label {
  font-weight: 600 !important;
  color: var(--ink) !important;
}
div[data-baseweb="select"] > div,
.stTextInput input, .stNumberInput input {
  border-radius: 10px !important;
  border-color: var(--line) !important;
  background: #fff !important;
}

/* Expanders / dataframes */
div[data-testid="stExpander"] {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
}
div[data-testid="stExpander"] details summary {
  font-weight: 600;
}

/* Metrics fallback */
div[data-testid="stMetric"] {
  background: #fff;
  border: 1px solid var(--line);
  border-top: 3px solid var(--leaf);
  border-radius: 12px;
  padding: 0.75rem 0.9rem;
}
div[data-testid="stMetric"] label {
  color: var(--muted) !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  font-family: 'Fraunces', serif;
  color: var(--leaf);
}

/* Radio pills on analytics */
div[role="radiogroup"] label {
  background: #fff;
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 0.25rem 0.75rem;
}

.em-footer {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.8rem;
}

.em-sidebar-brand {
  font-family: 'Fraunces', serif;
  font-size: 1.45rem;
  font-weight: 700;
  margin-bottom: 0.15rem;
}
.em-sidebar-sub {
  font-size: 0.78rem;
  opacity: 0.75;
  margin-bottom: 1rem;
}
"""


def apply() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def hero(brand: str, headline: str, sub: str, eyebrow: str = "Quantic MSBA Capstone · Proof of Concept") -> None:
    st.markdown(
        f"""
        <div class="em-hero">
          <div class="eyebrow">{eyebrow}</div>
          <div class="brand">{brand}</div>
          <h1>{headline}</h1>
          <p>{sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def page_header(eyebrow: str, title: str, sub: str) -> None:
    st.markdown(
        f"""
        <div class="em-page-head">
          <div class="eyebrow">{eyebrow}</div>
          <h1>{title}</h1>
          <p>{sub}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def note(html: str) -> None:
    st.markdown(f'<div class="em-note">{html}</div>', unsafe_allow_html=True)


def kpi_row(items: list[tuple[str, str]]) -> None:
    cells = "".join(
        f'<div class="em-kpi"><div class="k">{k}</div><div class="v">{v}</div></div>'
        for k, v in items
    )
    st.markdown(f'<div class="em-kpi-grid">{cells}</div>', unsafe_allow_html=True)


def nav_card(label: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="em-card">
          <div class="label">{label}</div>
          <h3>{title}</h3>
          <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def issue_card(title: str, detail: str, severity: str = "info") -> None:
    sev = severity.lower()
    cls = "high" if sev in ("high", "critical", "error") else (
        "medium" if sev in ("medium", "warn", "warning") else ""
    )
    st.markdown(
        f'<div class="em-issue {cls}"><span class="t">{title}</span> — {detail}</div>',
        unsafe_allow_html=True,
    )
