"""Helper portal: county to school to student to gift."""

from __future__ import annotations

import streamlit as st

from elimu_streamlit.paths import ensure_paths
from elimu_streamlit import theme

ensure_paths()

from build_sponsor_portal import build_payload  # noqa: E402
from record_payment import (  # noqa: E402
    OverpaymentError,
    StaleBalanceError,
    apply_payment,
    connect,
    list_receipts,
    payment_receipt,
    term_arrears_summary,
)


@st.cache_data(ttl=30, show_spinner="Loading fee-support queue…")
def _cached_payload() -> dict:
    return build_payload()


def render() -> None:
    theme.page_header(
        "Helpers",
        "Help a student",
        "County → school type → school → student → select terms → gift.",
    )
    theme.note(
        "<strong>Shared demo ledger.</strong> Gifts from other reviewers may appear here, "
        "and the database can reset when the cloud app sleeps or redeploys. Not live M-Pesa."
    )

    try:
        payload = _cached_payload()
    except Exception as exc:
        st.error(f"Could not load portal data: {exc}")
        return

    counties = payload.get("counties") or []
    schools = payload.get("schools") or []
    students = payload.get("students") or []
    source = payload.get("source", "unknown")

    st.caption(f"Balances source: **{source}** · {len(students):,} students in fee-support queue")

    c1, c2, c3 = st.columns(3)
    with c1:
        county = st.selectbox("County", [""] + counties, format_func=lambda x: x or "Select a county…")
    with c2:
        school_type = st.selectbox("School type", ["", "Day", "Boarding"], format_func=lambda x: x or "Day or Boarding…")
    with c3:
        school_opts = [
            s for s in schools
            if (not county or s["county"] == county)
            and (not school_type or s["type"] == school_type)
            and s.get("count", 0) > 0
        ]
        school_labels = {s["id"]: f"{s['name']} ({s['count']} students)" for s in school_opts}
        school_id = st.selectbox(
            "School",
            [None] + [s["id"] for s in school_opts],
            format_func=lambda x: "Select a school…" if x is None else school_labels.get(x, str(x)),
        )

    if not county or not school_type or school_id is None:
        theme.note("Select a <strong>county</strong>, <strong>school type</strong>, and <strong>school</strong> to see students.")
        _render_recent_receipts()
        return

    school_students = [s for s in students if s["school_id"] == school_id and s["amount"] > 0]
    if not school_students:
        st.warning("No students with outstanding fee-support needs at this school right now.")
        _render_recent_receipts()
        return

    st.markdown("### Students needing fee support")
    for s in school_students:
        with st.expander(
            f"{s['display_name']} · {s['gender']}, {s['age']} · "
            f"KES {s['amount']:,} outstanding · priority {s['priority']}",
            expanded=False,
        ):
            st.write(s.get("why") or "Recommended for fee support")
            terms = s.get("terms") or []
            if terms:
                st.dataframe(
                    [
                        {
                            "Term": t["term_label"],
                            "Outstanding (KES)": t["outstanding"],
                        }
                        for t in terms
                        if t["outstanding"] > 0
                    ],
                    hide_index=True,
                    use_container_width=True,
                )

            open_terms = [t for t in terms if t["outstanding"] > 0]
            if not open_terms:
                st.success("Fully cleared on the current ledger.")
                continue

            term_labels = [t["term_label"] for t in open_terms]
            selected_terms = st.multiselect(
                "Terms to support",
                term_labels,
                default=term_labels,
                key=f"terms_{s['id']}",
            )
            max_amt = sum(t["outstanding"] for t in open_terms if t["term_label"] in selected_terms)
            if max_amt <= 0:
                st.warning("Select at least one term with a balance.")
                continue

            amount = st.number_input(
                "Gift amount (KES)",
                min_value=100,
                max_value=int(max_amt),
                value=min(5000, int(max_amt)),
                step=100,
                key=f"amt_{s['id']}",
            )
            sponsor = st.text_input(
                "Your name (optional)",
                value="Anonymous Helper",
                key=f"sp_{s['id']}",
            )

            if st.button(f"Pay KES {int(amount):,}", key=f"pay_{s['id']}", type="primary"):
                if not selected_terms:
                    st.error("Select at least one term.")
                else:
                    _do_pay(
                        student_id=int(s["id"]),
                        amount=int(amount),
                        term_labels=selected_terms,
                        sponsor_name=sponsor or "Anonymous Helper",
                    )


def _do_pay(
    student_id: int,
    amount: int,
    term_labels: list[str],
    sponsor_name: str,
) -> None:
    try:
        conn = connect()
        try:
            live = term_arrears_summary(conn, student_id)
            live_sel = sum(
                t["outstanding"] for t in live if t["term_label"] in term_labels
            )
            payment_id = apply_payment(
                conn,
                student_id=student_id,
                amount=amount,
                term_labels=term_labels,
                sponsor_name=sponsor_name,
                expected_outstanding=live_sel,
            )
            receipt = payment_receipt(conn, payment_id)
        finally:
            conn.close()
    except FileNotFoundError as exc:
        st.error(str(exc))
        return
    except OverpaymentError as exc:
        st.error(str(exc))
        return
    except StaleBalanceError as exc:
        st.warning(str(exc))
        _cached_payload.clear()
        st.rerun()
        return
    except Exception as exc:
        st.error(f"Payment failed: {exc}")
        return

    _cached_payload.clear()
    st.success(
        f"Gift recorded · {receipt['receipt_id']} · "
        f"KES {receipt['amount']:,} · remaining KES {receipt['remaining_after']:,}"
    )
    if receipt.get("allocations"):
        st.dataframe(
            [
                {"Term": a["term_label"], "Allocated (KES)": a["amount"]}
                for a in receipt["allocations"]
            ],
            hide_index=True,
            use_container_width=True,
        )
    st.balloons()


def _render_recent_receipts() -> None:
    st.divider()
    st.markdown("### Recent gifts")
    try:
        conn = connect()
        try:
            receipts = list_receipts(conn, limit=10)
        finally:
            conn.close()
    except Exception:
        st.caption("Ledger unavailable. Run `python db/init_db.py` if local.")
        return

    if not receipts:
        st.caption("No gifts yet.")
        return

    st.dataframe(
        [
            {
                "Receipt": r["receipt_id"],
                "When": r["paid_at"],
                "Student": r["display_name"],
                "School": r["school"],
                "KES": r["amount"],
            }
            for r in receipts
        ],
        hide_index=True,
        use_container_width=True,
    )
