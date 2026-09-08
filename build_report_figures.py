# -*- coding: utf-8 -*-
"""
Original-style ElimuMatch strategy figures (pre-redesign look).

Solid filled bands/circles on cream paper — simple matplotlib style.
Regenerate:  python build_report_figures.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle
import numpy as np

OUT = Path(__file__).resolve().parent / "report_figures"
OUT.mkdir(exist_ok=True)

# Portal brand (sponsor portal / Streamlit theme)
CREAM = "#f7f1e8"
INK = "#14213d"
MUTED = "#5c6b73"
GREEN = "#1b7a5a"
TEAL = "#0f5c42"
SLATE = "#14213d"
NAVY = "#14213d"
ORANGE = "#f4b942"
BLUE = "#1b7a5a"


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 12,
            "text.color": INK,
            "figure.facecolor": CREAM,
            "savefig.facecolor": CREAM,
        }
    )


def _save(fig: plt.Figure, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=CREAM, edgecolor="none")
    plt.close(fig)
    print(f"  wrote {path.name}")


# ---------------------------------------------------------------------------
# Product layers (original: three solid slabs, white text)
# ---------------------------------------------------------------------------
def fig_product_layers() -> None:
    fig, ax = plt.subplots(figsize=(10.5, 7.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8.0)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # Clear gap between figure title and first layer box
    ax.text(0.25, 7.75, "ElimuMatch product layers", fontsize=16, fontweight="bold", color=INK, va="top")

    layers = [
        (0.4, 4.55, 9.2, 2.10, GREEN,
         "Helpers",
         "Pick a place  >  see a student  >  pay school fees  >  get a receipt",
         "A simple path. No model detail on this screen."),
        (0.4, 2.30, 9.2, 2.10, TEAL,
         "Operations",
         "Who is waiting, where gifts land, payment errors, and data freshness",
         "Keeps the pilot honest and auditable."),
        (0.4, 0.05, 9.2, 2.10, SLATE,
         "Analytics",
         "Who is at risk of leaving, and why",
         "For school staff only, not for public helper screens."),
    ]
    for x, y, w, h, c, title, body, note in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    facecolor=c, edgecolor="none", zorder=2))
        # Header near top; process line mid; italic narration near bottom
        ax.text(x + 0.40, y + h - 0.40, title, fontsize=17, fontweight="bold", color="white", va="top", zorder=3)
        ax.text(x + 0.40, y + 1.05, body, fontsize=13, color="white", va="center", zorder=3)
        ax.text(x + 0.40, y + 0.28, note, fontsize=12, color="#eef5f0", style="italic", va="bottom", zorder=3)

    _save(fig, "01_product_layers.png")


# ---------------------------------------------------------------------------
# Matching loop (original: six circles + arrows)
# ---------------------------------------------------------------------------
def fig_matching_loop() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.3, 4.6, "The matching loop (how support is decided).", fontsize=13, fontweight="bold", color=INK, va="top")

    steps = [
        "Score\nrisk",
        "Explain\ndrivers",
        "Assign\nintervention",
        "Publish fee\npriority",
        "Settle\ngift",
        "Monitor\nfairness",
    ]
    xs = np.linspace(1.0, 11.0, 6)
    y = 2.55
    colors = [GREEN, TEAL, GREEN, TEAL, GREEN, TEAL]

    for i in range(5):
        ax.annotate(
            "",
            xy=(xs[i + 1] - 0.72, y),
            xytext=(xs[i] + 0.72, y),
            arrowprops=dict(arrowstyle="->", color="#555555", lw=1.4),
            zorder=1,
        )

    for label, x, c in zip(steps, xs, colors):
        ax.add_patch(Circle((x, y), 0.72, facecolor=c, edgecolor="none", zorder=2))
        ax.text(x, y, label, ha="center", va="center", fontsize=9, fontweight="bold",
                color="white", zorder=3, linespacing=1.15)

    ax.text(
        6.0,
        0.55,
        "Only fee-primary students enter the helper queue. Tutoring, health, digital, and enrichment stay school/partner channels in the MVP.",
        ha="center",
        va="center",
        fontsize=8.5,
        color=MUTED,
        style="italic",
    )
    _save(fig, "02_matching_loop.png")


# ---------------------------------------------------------------------------
# Who sees what (original card grid)
# ---------------------------------------------------------------------------
def fig_who_sees() -> None:
    fig, ax = plt.subplots(figsize=(11.0, 5.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.5)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.3, 6.15, "Who sees what", fontsize=13, fontweight="bold", color=INK, va="top")

    cards = [
        (0.3, 3.35, 3.6, 2.5, GREEN, "Helper",
         ["County & school", "Student (anonymized)", "Term arrears", "Gift receipt"]),
        (4.2, 3.35, 3.6, 2.5, TEAL, "Ops / school",
         ["Queues & pilot KPIs", "Settlement rejects", "Concentration", "Data freshness"]),
        (8.1, 3.35, 3.6, 2.5, NAVY, "Analyst / leadership",
         ["Model metrics", "SHAP drivers", "Personas", "Fairness by SES"]),
        (1.4, 0.4, 4.4, 2.5, ORANGE, "Students & families",
         ["Dignity first: anonymized display,", "support not stigma", "No public risk score as a label."]),
        (6.4, 0.4, 4.4, 2.5, BLUE, "Future institutions",
         ["CSR shortlists & foundation school maps", "Same engine; later portals"]),
    ]
    for x, y, w, h, c, title, items in cards:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor="white", edgecolor=c, linewidth=2.0, zorder=2))
        ax.text(x + 0.25, y + h - 0.4, title, fontsize=11, fontweight="bold", color=c, va="top", zorder=3)
        for j, it in enumerate(items):
            ax.text(x + 0.3, y + h - 0.95 - j * 0.4, f"•  {it}", fontsize=9, color=INK, va="top", zorder=3)

    _save(fig, "03_who_sees_what.png")


# ---------------------------------------------------------------------------
# Data layers (original solid slabs)
# ---------------------------------------------------------------------------
def fig_data_layers() -> None:
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.5)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.25, 5.15, "Three-layer data design", fontsize=13, fontweight="bold", color=INK, va="top")

    layers = [
        (0.4, 3.35, 9.2, 1.35, SLATE,
         "Layer 1 · Train retention risk",
         "Demographics, household shock, access, academics, health, belonging, protective support — not fee arrears alone"),
        (0.4, 1.85, 9.2, 1.25, TEAL,
         "Layer 2 · Helper filters",
         "County, school, preference signals to choose place and type"),
        (0.4, 0.45, 9.2, 1.15, ORANGE,
         "Layer 3 · Ledger (ops only)",
         "Term arrears, gifts, allocations, review flags — authoritative books"),
    ]
    for x, y, w, h, c, title, body in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=c, edgecolor="none", zorder=2))
        ax.text(x + 0.35, y + h - 0.4, title, fontsize=11, fontweight="bold", color="white", va="top", zorder=3)
        ax.text(x + 0.35, y + 0.3, body, fontsize=9.5, color="white", va="bottom", zorder=3)

    _save(fig, "04_data_layers.png")


# ---------------------------------------------------------------------------
# Three buyers (original cards)
# ---------------------------------------------------------------------------
def fig_three_buyers() -> None:
    fig, ax = plt.subplots(figsize=(10.5, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.3, 4.15, "One analytics backbone, three buyers", fontsize=13, fontweight="bold", color=INK, va="top")

    buyers = [
        (0.5, 1, "Individuals", "Fast preference gift", "Fee channel MVP"),
        (2, 2, "Banks / CSR", "Ranked shortlists", "Explainable priority"),
        (3, 3, "Foundations", "School-level need", "Multi-channel ops view"),
    ]
    for i, (n, title, a, b) in enumerate([(1, "Individuals", "Fast preference gift", "Fee channel MVP"),
                                           (2, "Banks / CSR", "Ranked shortlists", "Explainable priority"),
                                           (3, "Foundations", "School-level need", "Multi-channel ops view")]):
        x = 0.6 + i * 3.85
        ax.add_patch(FancyBboxPatch((x, 0.55), 3.5, 3.0, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor="white", edgecolor=GREEN, linewidth=1.8, zorder=2))
        ax.add_patch(Circle((x + 1.75, 2.85), 0.38, facecolor=GREEN, edgecolor="none", zorder=3))
        ax.text(x + 1.75, 2.85, str(n), ha="center", va="center", fontsize=12, fontweight="bold", color="white", zorder=4)
        ax.text(x + 1.75, 2.15, title, ha="center", va="center", fontsize=12, fontweight="bold", color=INK, zorder=3)
        ax.text(x + 1.75, 1.55, a, ha="center", va="center", fontsize=10, color=MUTED, zorder=3)
        ax.text(x + 1.75, 1.15, b, ha="center", va="center", fontsize=10, color=MUTED, zorder=3)

    _save(fig, "05_three_buyers.png")


# ---------------------------------------------------------------------------
# Year-1 economics (original simple bars)
# ---------------------------------------------------------------------------
def fig_year1_economics() -> None:
    fig, ax = plt.subplots(figsize=(8.8, 5.5))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    labels = ["What the platform costs", "Estimated Year-1 benefits"]
    values = [2.0, 5.15]
    colors = [NAVY, GREEN]
    bars = ax.bar(labels, values, width=0.55, color=colors, edgecolor="none", zorder=3)
    for bar, lab in zip(bars, ["KES 2.0M", "KES 5.2M"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, lab,
                ha="center", va="bottom", fontsize=16, fontweight="bold", color=INK)

    ax.set_ylim(0, 6.2)
    ax.set_ylabel("KES millions (illustrative)", color=INK, fontsize=14, labelpad=8)
    ax.set_title("Year-1 pilot: spend vs estimated benefit", fontsize=16, fontweight="bold", color=INK, loc="left", pad=12)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors=INK, labelsize=13, width=1.1, length=5)
    ax.text(
        0.5, -0.14,
        "Helper gifts go to school fee accounts and are not counted as platform cost.",
        transform=ax.transAxes, ha="center", fontsize=12, color=INK, style="italic",
    )
    fig.tight_layout()
    _save(fig, "06_year1_economics.png")


# ---------------------------------------------------------------------------
# Pilot roadmap (six stages — matches executive pitch)
# ---------------------------------------------------------------------------
def fig_pilot_roadmap() -> None:
    fig, ax = plt.subplots(figsize=(12.2, 4.4))
    ax.set_xlim(0, 12.4)
    ax.set_ylim(0, 4.6)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.25, 4.3, "From proof of concept to pilot (six earned stages).", fontsize=12.5,
            fontweight="bold", color=INK, va="top")

    stages = [
        (INK, "1. Legal Gate", ["MOUs (8 schools)", "DP & safeguarding", "Months 0-4"]),
        (ORANGE, "2. Partner Data", ["Extracts under MOU", "Quality + validate", "Months 1-4"]),
        (TEAL, "3. Soft Pilot", ["Rank on real data", "Human review", "Term 1"]),
        (GREEN, "4. Live Giving", ["Fee gifts live", "Settle to schools", "Terms 1-2"]),
        (MUTED, "5. Measure", ["Section 9 KPIs", "Fairness pack", "Each term"]),
        (INK, "6. Scale Decision", ["More schools /", "one new channel", "End of Year 1"]),
    ]

    n = len(stages)
    gap = 0.12
    w = (11.8 - (n - 1) * gap) / n
    y, h = 0.45, 3.35
    xs = [0.3 + i * (w + gap) for i in range(n)]
    for i, (x, (c, title, items)) in enumerate(zip(xs, stages)):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=c, edgecolor="none", zorder=2))
        ax.text(x + w / 2, y + h - 0.35, title, ha="center", va="top", fontsize=9.5,
                fontweight="bold", color="white", zorder=3)
        for j, it in enumerate(items):
            ax.text(x + w / 2, y + h - 1.05 - j * 0.55, it, ha="center", va="top",
                    fontsize=8.5, color="white", zorder=3)
        if i < n - 1:
            ax.annotate(
                "",
                xy=(xs[i + 1] - 0.02, y + h / 2),
                xytext=(x + w + 0.02, y + h / 2),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.1),
                zorder=1,
            )

    _save(fig, "07_pilot_roadmap.png")


# ---------------------------------------------------------------------------
# Selection rule (original scatter)
# ---------------------------------------------------------------------------
def fig_selection_rule() -> None:
    fig, ax = plt.subplots(figsize=(10.0, 6.4))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    # (name, auc, recall, color, size, bold, dx, dy, ha)
    models = [
        ("Majority baseline", 0.50, 0.0, NAVY, 110, False, 10, 10, "left"),
        ("Random Forest", 0.74, 0.08, NAVY, 120, False, -12, -18, "right"),
        ("Gradient Boosting", 0.75, 0.33, NAVY, 130, False, 12, 6, "left"),
        ("Logistic Regression\n(selected)", 0.753, 0.667, GREEN, 240, True, 12, 8, "left"),
    ]
    for name, auc, rec, c, s, bold, dx, dy, ha in models:
        ax.scatter(auc, rec, s=s, c=c, zorder=5, edgecolors="white", linewidths=1.2)
        ax.annotate(
            name,
            xy=(auc, rec),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=14 if bold else 13,
            fontweight="bold" if bold else "normal",
            color=GREEN if bold else INK,
            ha=ha,
            va="bottom",
        )

    ax.set_xlim(0.45, 0.88)
    ax.set_ylim(-0.08, 0.88)
    ax.set_xticks([0.50, 0.60, 0.70, 0.80])
    ax.set_yticks([0.0, 0.2, 0.4, 0.6, 0.8])
    ax.set_xlabel("How well students are ranked  (0.50 = chance)", color=INK, fontsize=14, labelpad=10)
    ax.set_ylabel("Share of dropouts found", color=INK, fontsize=14, labelpad=10)
    ax.set_title("We chose the model that finds more students who would leave", fontsize=16, fontweight="bold",
                 color=INK, loc="left", pad=12)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors=INK, labelsize=13, width=1.1, length=5)
    # Offset in points so bbox_inches='tight' keeps a visible gap under the axis label
    ax.annotate(
        "Proof-of-concept results on 1,000 students. Higher on this chart is better.",
        xy=(0.0, 0.0),
        xycoords=("axes fraction", "axes fraction"),
        xytext=(0, -90),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=12,
        color=INK,
        style="italic",
        annotation_clip=False,
    )
    fig.tight_layout()
    _save(fig, "08_selection_rule.png")


# ---------------------------------------------------------------------------
# Perceptual map (original 2x2 style — kept as preferred style)
# ---------------------------------------------------------------------------
def fig_perceptual_map() -> None:
    fig, ax = plt.subplots(figsize=(9.8, 7.4))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.add_patch(Rectangle((0, 0), 1.15, 1.15, facecolor="#dceeea", edgecolor="none", alpha=0.85, zorder=0))
    ax.add_patch(Rectangle((-1.15, 0), 1.15, 1.15, facecolor="#e8eef2", edgecolor="none", alpha=0.5, zorder=0))
    ax.add_patch(Rectangle((-1.15, -1.15), 1.15, 1.15, facecolor="#f0f0ee", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0, -1.15), 1.15, 1.15, facecolor="#f5eee8", edgecolor="none", alpha=0.7, zorder=0))
    ax.axhline(0, color="#aaaaaa", lw=1.0, zorder=1)
    ax.axvline(0, color="#aaaaaa", lw=1.0, zorder=1)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    ax.set_title(
        "Where ElimuMatch sits among other ways people give",
        fontsize=16, fontweight="bold", color=INK, loc="left", pad=12,
    )

    ax.text(1.1, -0.08, "Easy for helpers  →", ha="right", va="top", fontsize=13, color=INK, fontweight="bold")
    ax.text(-1.1, -0.08, "←  Hard for helpers", ha="left", va="top", fontsize=13, color=INK, fontweight="bold")
    ax.text(-0.04, 1.08, "Finds the right students  ↑", ha="right", va="top", fontsize=13, color=INK, fontweight="bold")
    ax.text(-0.04, -1.08, "Guesswork  ↓", ha="right", va="bottom", fontsize=13, color=INK, fontweight="bold")
    ax.text(0.55, 0.88, "Where funders should sit", ha="center", fontsize=13, fontweight="bold", color=GREEN)

    points = [
        (0.72, 0.78, "ElimuMatch\n(fee support)", GREEN, 240, True),
        (-0.72, 0.62, "Yearly bursary\ncontests", NAVY, 90, False),
        (-0.35, 0.05, "Church / alumni\nlists", NAVY, 80, False),
        (-0.15, -0.18, "One-off gifts\nto a school", NAVY, 80, False),
        (0.45, -0.55, "Giving through\nfriends", ORANGE, 90, False),
        (0.78, -0.78, "Public campaigns\n(most visible cases)", ORANGE, 90, False),
    ]
    for x, y, lab, c, s, bold in points:
        ax.scatter(x, y, s=s, c=c, zorder=5, edgecolors="white", linewidths=1.2)
        ax.text(
            x, y - 0.15, lab, ha="center", va="top",
            fontsize=13 if bold else 12, fontweight="bold" if bold else "normal",
            color=INK, linespacing=1.25, zorder=6,
        )

    ax.set_xlabel("How easy it is for a helper to complete a gift", fontsize=13, color=INK, labelpad=10)
    ax.set_ylabel("How well support is aimed at students who may leave", fontsize=13, color=INK, labelpad=10)
    fig.tight_layout()
    _save(fig, "09_perceptual_map.png")


# ---------------------------------------------------------------------------
# Day in the life of one gift (roadmap — plain language)
# ---------------------------------------------------------------------------
def fig_gift_journey() -> None:
    fig, ax = plt.subplots(figsize=(11.8, 4.6))
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 4.8)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.3, 4.45, "From place to gift in four steps.", fontsize=16, fontweight="bold", color=INK, va="top")

    stages = [
        (GREEN, "1  Choose place", ["Pick a county", "Day or boarding", "Open the school"], "white"),
        (TEAL, "2  See a student", ["First name only", "Fee balance shown", "Already on the list"], "white"),
        (ORANGE, "3  Give", ["Pay part or all", "Oldest term first", "Get a receipt"], INK),
        (NAVY, "4  Confirm", ["Funds reach school", "Team sees it land", "Gift is tracked"], "white"),
    ]
    xs = [0.35, 3.35, 6.35, 9.35]
    w, h, y = 2.65, 3.05, 0.45
    for i, (x, (c, title, items, fg)) in enumerate(zip(xs, stages)):
        ax.add_patch(
            FancyBboxPatch(
                (x, y),
                w,
                h,
                boxstyle="round,pad=0.02,rounding_size=0.12",
                facecolor=c,
                edgecolor="none",
                zorder=2,
            )
        )
        ax.text(
            x + w / 2,
            y + h - 0.42,
            title,
            ha="center",
            va="top",
            fontsize=14,
            fontweight="bold",
            color=fg,
            zorder=3,
        )
        for j, it in enumerate(items):
            ax.text(
                x + w / 2,
                y + h - 1.15 - j * 0.50,
                it,
                ha="center",
                va="top",
                fontsize=12.5,
                color=fg,
                zorder=3,
            )
        if i < 3:
            ax.annotate(
                "",
                xy=(xs[i + 1] - 0.05, y + h / 2),
                xytext=(x + w + 0.05, y + h / 2),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.3),
                zorder=1,
            )

    _save(fig, "10_gift_journey.png")


def fig_kenya_completion() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)
    labels = ["Primary", "Lower secondary", "Upper secondary"]
    values = [98, 85, 46]
    colors = [TEAL, GREEN, ORANGE]
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.55, edgecolor="none")
    for bar, val in zip(bars, values[::-1]):
        ax.text(val + 1.5, bar.get_y() + bar.get_height() / 2, f"{val}%",
                va="center", fontsize=14, fontweight="bold", color=INK)
    ax.set_xlim(0, 110)
    ax.axvline(50, color="#c8c4b8", ls="--", lw=1)
    ax.set_xlabel("Share who complete that level", fontsize=13, color=INK, labelpad=8)
    ax.set_title("Nearly all finish primary. Fewer than half finish secondary.",
                 fontsize=15, fontweight="bold", color=INK, loc="left", pad=10)
    ax.tick_params(colors=INK, labelsize=13, width=1.1, length=5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    fig.tight_layout()
    _save(fig, "ext_02_kenya_completion_funnel.png")


def fig_kenya_enrolment() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)
    years = [2020, 2021, 2022, 2023, 2024]
    values = [3.52, 3.69, 3.92, 4.11, 4.32]
    ax.fill_between(years, values, color=TEAL, alpha=0.18)
    ax.plot(years, values, color=TEAL, lw=2.6, marker="o", ms=8)
    for x, y in zip(years, values):
        ax.text(x, y + 0.08, f"{y:.2f}M", ha="center", va="bottom", fontsize=13, fontweight="bold", color=INK)
    ax.set_ylim(3.2, 4.7)
    ax.set_xticks(years)
    ax.set_ylabel("Secondary enrolment (millions)", fontsize=13, color=INK, labelpad=8)
    ax.set_title("More students are in secondary school, so more can still leave mid-course",
                 fontsize=14, fontweight="bold", color=INK, loc="left", pad=10)
    ax.tick_params(colors=INK, labelsize=13, width=1.1, length=5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    fig.tight_layout()
    _save(fig, "ext_03_kenya_access_progress.png")


def main() -> None:
    _style()
    print("Building original-style report figures...")
    fig_product_layers()
    fig_matching_loop()
    fig_gift_journey()
    fig_who_sees()
    fig_data_layers()
    fig_three_buyers()
    fig_year1_economics()
    fig_pilot_roadmap()
    fig_selection_rule()
    fig_perceptual_map()
    fig_kenya_completion()
    fig_kenya_enrolment()
    print("Done.")


if __name__ == "__main__":
    main()
