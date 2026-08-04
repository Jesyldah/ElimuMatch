"""Ops monitor: KPIs, pilot criteria, investigation queue."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from elimu_streamlit.paths import ensure_paths
from elimu_streamlit import theme

ensure_paths()

from ops_metrics import ops_snapshot  # noqa: E402


@st.cache_data(ttl=15, show_spinner="Refreshing ops snapshot…")
def _cached_ops() -> dict:
    return ops_snapshot()


def render() -> None:
    theme.page_header(
        "Organization",
        "Ops monitor",
        "KPIs, pilot criteria, settlement health, and school resource targets.",
    )

    if st.button("Refresh now", key="ops_refresh"):
        _cached_ops.clear()
        st.rerun()

    data = _cached_ops()
    if not data.get("ok"):
        st.error(data.get("error") or "Ops snapshot unavailable. Ensure db/elimu_match.db exists.")
        return

    st.caption(f"Generated at {data.get('generated_at', '-')}")

    kpis = data.get("kpis") or {}
    age = kpis.get("score_age_days")
    theme.kpi_row([
        ("Fee-support queue", f"{kpis.get('portal_fee_queue', kpis.get('fee_support_recommended', 0)):,}"),
        ("Total arrears (KES)", f"{kpis.get('total_arrears_kes', 0):,}"),
        ("Gifts completed", f"{kpis.get('gifts_completed', 0):,}"),
        ("Students helped", f"{kpis.get('students_helped', 0):,}"),
        ("Fee clearance", f"{kpis.get('fee_clearance_pct', 0)}%"),
        ("High risk + arrears", f"{kpis.get('high_risk_with_arrears', 0):,}"),
        ("Gift volume (KES)", f"{kpis.get('gifts_kes', 0):,}"),
        ("Score age (days)", "-" if age is None else str(age)),
        ("Score SLA OK", "Yes" if kpis.get("score_sla_ok") else "No"),
    ])

    st.markdown("### Pilot success criteria")
    pilot = data.get("pilot_kpis") or []
    if pilot:
        rows = []
        for p in pilot:
            if isinstance(p, dict):
                rows.append({
                    "Criterion": p.get("label") or p.get("name") or p.get("title") or "-",
                    "Status": p.get("status") or p.get("state") or ("OK" if p.get("ok") else "Watch"),
                    "Value": p.get("value") or p.get("current") or p.get("count") or p.get("detail") or "",
                    "Target": p.get("target") or "",
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
        else:
            st.json(pilot[:5])
    else:
        st.caption("No pilot KPI strip in snapshot.")

    impact = data.get("illustrative_impact") or {}
    if impact:
        st.markdown("### Illustrative impact (synthetic labels, not causal)")
        theme.kpi_row([
            (
                "Helped retained",
                str(impact.get("helped_retained_pct", impact.get("with_gift_retention_pct", "-"))),
            ),
            (
                "Peer retained",
                str(impact.get("peer_retained_pct", impact.get("without_gift_retention_pct", "-"))),
            ),
        ])
        note = impact.get("note") or impact.get("disclaimer") or ""
        if note:
            st.caption(str(note)[:400])

    st.markdown("### Needs attention")
    issues = data.get("issues") or []
    if not issues:
        st.success("No open issues flagged.")
    else:
        for issue in issues[:12]:
            if not isinstance(issue, dict):
                st.write(issue)
                continue
            sev = str(issue.get("severity") or issue.get("level") or "info").lower()
            title = issue.get("title") or issue.get("label") or "Issue"
            detail = issue.get("detail") or issue.get("message") or issue.get("why") or ""
            theme.issue_card(title, detail, sev)

    left, right = st.columns(2)
    with left:
        st.markdown("### Term aging")
        aging = data.get("term_aging") or []
        if aging:
            df = pd.DataFrame(aging)
            rename = {}
            for c in df.columns:
                if "term" in c.lower() and "label" in c.lower():
                    rename[c] = "Term"
                elif "arrears" in c.lower() or "outstanding" in c.lower() or "kes" in c.lower():
                    rename[c] = "Arrears (KES)"
                elif "share" in c.lower() or "pct" in c.lower():
                    rename[c] = "Share %"
            st.dataframe(df.rename(columns=rename), hide_index=True, use_container_width=True)

        st.markdown("### Fee-queue fairness")
        fair = data.get("fee_queue_fairness") or {}
        if fair:
            st.json(fair)

    with right:
        st.markdown("### County hotspots")
        counties = data.get("county_hotspots") or []
        if counties:
            st.dataframe(pd.DataFrame(counties), hide_index=True, use_container_width=True)

        st.markdown("### Stuck partial pays")
        stuck = data.get("stuck_partial_pays") or {}
        if stuck:
            if isinstance(stuck.get("rows"), list):
                st.dataframe(pd.DataFrame(stuck["rows"]), hide_index=True, use_container_width=True)
            else:
                st.json(stuck)

    st.markdown("### School resource targets")
    targets = data.get("school_resource_targets") or []
    if targets:
        st.dataframe(pd.DataFrame(targets), hide_index=True, use_container_width=True)

    st.markdown("### School concentration")
    conc = data.get("school_concentration") or {}
    if conc:
        for key in ("by_arrears", "by_gifts", "top_schools", "rows"):
            if isinstance(conc.get(key), list) and conc[key]:
                st.markdown(f"*{key.replace('_', ' ')}*")
                st.dataframe(pd.DataFrame(conc[key]), hide_index=True, use_container_width=True)
                break
        else:
            st.json({k: v for k, v in conc.items() if not isinstance(v, list)})

    st.markdown("### Recent gifts")
    recent = data.get("recent_activity") or []
    if recent:
        st.dataframe(pd.DataFrame(recent), hide_index=True, use_container_width=True)

    st.markdown("### Pipeline / freshness")
    fresh = data.get("freshness") or []
    if fresh:
        st.dataframe(pd.DataFrame(fresh) if isinstance(fresh, list) else pd.DataFrame([fresh]),
                     hide_index=True, use_container_width=True)

    rejected = data.get("rejected_settlements") or {}
    if rejected:
        st.markdown("### Rejected settlements")
        if isinstance(rejected.get("rows"), list) and rejected["rows"]:
            st.dataframe(pd.DataFrame(rejected["rows"]), hide_index=True, use_container_width=True)
        else:
            st.json(rejected)
