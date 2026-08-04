"""
ElimuMatch Capstone — Streamlit demo entry point.

Local:
  python -m streamlit run streamlit_app.py

Cloud:
  Deploy this file from the GitHub repo (Jesyldah/ElimuMatch).
"""

from __future__ import annotations

import streamlit as st

from elimu_streamlit import analytics, helper, ops
from elimu_streamlit.paths import ensure_paths
from elimu_streamlit import theme

ensure_paths()

st.set_page_config(
    page_title="ElimuMatch Capstone",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

PAGES = [
    "Home",
    "Helper portal",
    "Ops monitor",
    "Retention analytics",
]


def _home() -> None:
    theme.hero(
        brand="ElimuMatch",
        headline="Help a student stay in school — with risk scoring and ops behind the scenes.",
        sub="Retention analytics, helper matching, and a working fee ledger for Kenyan secondary schools.",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        theme.nav_card(
            "Helpers",
            "Sponsor portal",
            "County → school → student → term arrears → gift.",
        )
        if st.button("Open Helper portal", use_container_width=True, key="home_helper"):
            st.session_state["nav"] = "Helper portal"
            st.rerun()
    with c2:
        theme.nav_card(
            "Organization",
            "Ops monitor",
            "KPIs, investigation queue, pilot criteria, progress.",
        )
        if st.button("Open Ops monitor", use_container_width=True, key="home_ops"):
            st.session_state["nav"] = "Ops monitor"
            st.rerun()
    with c3:
        theme.nav_card(
            "Analytics",
            "Retention analytics",
            "EDA, model, SHAP, personas, intervention matrix.",
        )
        if st.button("Open Analytics", use_container_width=True, key="home_analytics"):
            st.session_state["nav"] = "Retention analytics"
            st.rerun()

    theme.note(
        "<strong>Demo gifts</strong> are simulated settlements on a shared ledger — not live M-Pesa. "
        "Synthetic cohort metrics are factually grounded PoC outputs, not field-validated results."
    )
    st.markdown(
        '<div class="em-footer">Repo: github.com/Jesyldah/ElimuMatch · '
        "HTML demos remain available offline via index.html</div>",
        unsafe_allow_html=True,
    )


def main() -> None:
    theme.apply()

    st.sidebar.markdown(
        '<div class="em-sidebar-brand">ElimuMatch</div>'
        '<div class="em-sidebar-sub">MSBA Capstone PoC</div>',
        unsafe_allow_html=True,
    )

    default = st.session_state.get("nav", "Home")
    if default not in PAGES:
        default = "Home"
    choice = st.sidebar.radio(
        "Navigate",
        PAGES,
        index=PAGES.index(default),
        label_visibility="collapsed",
    )
    st.session_state["nav"] = choice

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Shared demo ledger may reset when the cloud app sleeps or redeploys."
    )

    if choice == "Home":
        _home()
    elif choice == "Helper portal":
        helper.render()
    elif choice == "Ops monitor":
        ops.render()
    else:
        analytics.render()


if __name__ == "__main__":
    main()
else:
    main()
