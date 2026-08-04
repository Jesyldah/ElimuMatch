"""Retention analytics — model, SHAP, personas, interventions."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from elimu_streamlit.paths import ROOT, ensure_paths
from elimu_streamlit import theme

ensure_paths()


def _load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_csv(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def render() -> None:
    theme.page_header(
        "Analytics",
        "Retention analytics",
        "Proof-of-concept outputs from a documented synthetic cohort — not validated field results.",
    )

    section = st.radio(
        "Section",
        [
            "Overview",
            "Model performance",
            "Explainability (SHAP)",
            "Risk personas",
            "Interventions & matching",
            "Cohort exploration",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if section == "Overview":
        _overview()
    elif section == "Model performance":
        _model()
    elif section == "Explainability (SHAP)":
        _shap()
    elif section == "Risk personas":
        _personas()
    elif section == "Interventions & matching":
        _interventions()
    else:
        _exploration()


def _overview() -> None:
    report = _load_json(ROOT / "modeling_outputs" / "modeling_report.json") or {}
    personas = _load_csv(ROOT / "clustering_outputs" / "persona_profiles.csv")
    interventions = _load_csv(ROOT / "intervention_outputs" / "intervention_summary.csv")
    metrics = report.get("test_metrics") or {}

    auc = metrics.get("auc")
    theme.kpi_row([
        ("Selected model", str(report.get("selected_model", "—"))),
        ("Test AUC", f"{auc:.3f}" if isinstance(auc, (int, float)) else "—"),
        ("Dropout recall", f"{metrics.get('recall_dropout', 0):.1%}" if metrics else "—"),
        ("Accuracy", f"{metrics.get('accuracy', 0):.1%}" if metrics else "—"),
    ])

    theme.note(
        report.get("objective")
        or "Predict student retention and route helpers to fee-support and related actions."
    )

    if personas is not None:
        st.markdown("### Personas at a glance")
        st.dataframe(personas, hide_index=True, use_container_width=True)

    if interventions is not None:
        st.markdown("### Intervention mix")
        chart_df = interventions.set_index("intervention")[["students"]]
        st.bar_chart(chart_df)


def _model() -> None:
    report = _load_json(ROOT / "modeling_outputs" / "modeling_report.json") or {}
    leaderboard = _load_csv(ROOT / "modeling_outputs" / "model_leaderboard.csv")
    importance = _load_csv(ROOT / "modeling_outputs" / "feature_importance.csv")
    fairness = _load_csv(ROOT / "modeling_outputs" / "fairness_auc_by_ses.csv")
    preds = _load_csv(ROOT / "modeling_outputs" / "test_predictions.csv")

    st.markdown("### Selected model")
    st.write(f"**{report.get('selected_model', '—')}**")
    if report.get("best_params"):
        st.json(report["best_params"])

    metrics = report.get("test_metrics") or {}
    if metrics:
        st.markdown("### Test metrics")
        st.dataframe(
            pd.DataFrame([{"metric": k, "value": v} for k, v in metrics.items()]),
            hide_index=True,
            use_container_width=True,
        )

    if leaderboard is not None:
        st.markdown("### Model leaderboard")
        st.dataframe(leaderboard, hide_index=True, use_container_width=True)
        if "test_auc" in leaderboard.columns and "model" in leaderboard.columns:
            st.bar_chart(leaderboard.set_index("model")[["test_auc"]])

    if importance is not None:
        st.markdown("### Feature importance")
        cols = [c for c in importance.columns if c.lower() not in ("unnamed: 0",)]
        top = importance[cols].head(15)
        st.dataframe(top, hide_index=True, use_container_width=True)
        # Prefer numeric importance column for chart
        num_cols = top.select_dtypes("number").columns.tolist()
        label_col = next((c for c in top.columns if c not in num_cols), None)
        if label_col and num_cols:
            st.bar_chart(top.set_index(label_col)[num_cols[:1]])

    if fairness is not None:
        st.markdown("### Fairness — AUC by SES")
        st.dataframe(fairness, hide_index=True, use_container_width=True)

    if preds is not None:
        st.markdown("### Test predictions (sample)")
        st.dataframe(preds.head(25), hide_index=True, use_container_width=True)


def _shap() -> None:
    report = _load_json(ROOT / "shap_outputs" / "shap_report.json") or {}
    importance = _load_csv(ROOT / "shap_outputs" / "shap_global_importance.csv")
    examples = _load_json(ROOT / "shap_outputs" / "shap_example_cases.json")

    if report:
        st.markdown("### SHAP summary")
        # Show compact keys only
        summary = {
            k: report[k]
            for k in ("model", "objective", "n_samples", "n_features", "note", "method")
            if k in report
        }
        if summary:
            st.json(summary)
        elif isinstance(report, dict):
            st.caption("Full SHAP report available in shap_outputs/shap_report.json")

    if importance is not None:
        st.markdown("### Global mean |SHAP|")
        top = importance.head(20)
        st.dataframe(top, hide_index=True, use_container_width=True)
        if {"feature", "mean_abs_shap"} <= set(top.columns):
            st.bar_chart(top.set_index("feature")[["mean_abs_shap"]])

    if examples:
        st.markdown("### Example explanations")
        if isinstance(examples, list):
            for i, case in enumerate(examples[:5]):
                with st.expander(f"Case {i + 1}"):
                    st.json(case)
        else:
            st.json(examples)


def _personas() -> None:
    profiles = _load_csv(ROOT / "clustering_outputs" / "persona_profiles.csv")
    detail = _load_csv(ROOT / "clustering_outputs" / "persona_metrics_detail.csv")
    k_sel = _load_csv(ROOT / "clustering_outputs" / "k_selection_metrics.csv")
    report = _load_json(ROOT / "clustering_outputs" / "clustering_report.json")

    if report:
        st.markdown("### Clustering report")
        keep = {
            k: report[k]
            for k in ("n_students", "selected_k", "algorithm", "features", "note", "summary")
            if k in report
        }
        st.json(keep or {k: report[k] for k in list(report)[:8]})

    if profiles is not None:
        st.markdown("### Persona profiles")
        st.dataframe(profiles, hide_index=True, use_container_width=True)
        if "persona" in profiles.columns and "retention_rate" in profiles.columns:
            st.bar_chart(profiles.set_index("persona")[["retention_rate"]])
        if "persona" in profiles.columns and "n" in profiles.columns:
            st.bar_chart(profiles.set_index("persona")[["n"]])

    if detail is not None:
        st.markdown("### Persona metrics detail")
        st.dataframe(detail, hide_index=True, use_container_width=True)

    if k_sel is not None:
        st.markdown("### k selection")
        st.dataframe(k_sel, hide_index=True, use_container_width=True)


def _interventions() -> None:
    summary = _load_csv(ROOT / "intervention_outputs" / "intervention_summary.csv")
    persona_m = _load_csv(ROOT / "intervention_outputs" / "persona_intervention_matrix.csv")
    signal_m = _load_csv(ROOT / "intervention_outputs" / "signal_intervention_matrix.csv")
    assign = _load_csv(ROOT / "intervention_outputs" / "student_intervention_assignments.csv")
    matches = _load_csv(ROOT / "matching_outputs" / "sponsor_match_list.csv")

    if summary is not None:
        st.markdown("### Intervention summary")
        st.dataframe(summary, hide_index=True, use_container_width=True)
        if "intervention" in summary.columns and "students" in summary.columns:
            st.bar_chart(summary.set_index("intervention")[["students"]])

    if persona_m is not None:
        st.markdown("### Persona × intervention matrix")
        st.dataframe(persona_m, hide_index=True, use_container_width=True)

    if signal_m is not None:
        st.markdown("### Signal × intervention matrix")
        st.dataframe(signal_m, hide_index=True, use_container_width=True)

    if assign is not None:
        st.markdown("### Assignments (sample)")
        st.dataframe(assign.head(40), hide_index=True, use_container_width=True)
        if "intervention_id" in assign.columns:
            mix = assign["intervention_id"].value_counts().rename_axis("intervention").reset_index(name="students")
            st.bar_chart(mix.set_index("intervention"))

    if matches is not None:
        st.markdown("### Sponsor match list (sample)")
        st.dataframe(matches.head(40), hide_index=True, use_container_width=True)


def _exploration() -> None:
    students = _load_csv(ROOT / "tableau_exports" / "students_exploration.csv")
    schools = _load_csv(ROOT / "tableau_exports" / "schools_summary.csv")
    dictionary = _load_csv(ROOT / "tableau_exports" / "data_dictionary.csv")

    if students is not None:
        st.markdown("### Student exploration table")
        st.dataframe(students.head(100), hide_index=True, use_container_width=True)
        numeric = students.select_dtypes("number")
        if not numeric.empty:
            pick = st.selectbox("Distribution column", numeric.columns.tolist())
            st.bar_chart(students[pick].value_counts().sort_index())

    if schools is not None:
        st.markdown("### Schools summary")
        st.dataframe(schools, hide_index=True, use_container_width=True)

    if dictionary is not None:
        st.markdown("### Data dictionary")
        st.dataframe(dictionary, hide_index=True, use_container_width=True)
