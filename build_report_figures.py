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
    fig, ax = plt.subplots(figsize=(10.5, 5.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.25, 5.85, "ElimuMatch product layers", fontsize=14, fontweight="bold", color=INK, va="top")

    layers = [
        (0.4, 3.85, 9.2, 1.55, GREEN,
         "Donors",
         "Pick a place  >  see a student  >  pay school fees  >  get a receipt",
         "A simple path. No model detail on this screen."),
        (0.4, 2.15, 9.2, 1.45, TEAL,
         "Operations",
         "Who is waiting, where gifts land, payment errors, and data freshness",
         "Keeps the pilot honest and auditable."),
        (0.4, 0.45, 9.2, 1.45, SLATE,
         "Analytics",
         "Who is at risk of leaving, and why",
         "For school staff only, not for public donor screens."),
    ]
    for x, y, w, h, c, title, body, note in layers:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15",
                                    facecolor=c, edgecolor="none", zorder=2))
        ax.text(x + 0.35, y + h - 0.38, title, fontsize=15, fontweight="bold", color="white", va="top", zorder=3)
        ax.text(x + 0.35, y + h * 0.48, body, fontsize=12, color="white", va="center", zorder=3)
        ax.text(x + 0.35, y + 0.22, note, fontsize=11, color="#d0e0d8", style="italic", va="bottom", zorder=3)

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
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    labels = ["What the platform costs", "Estimated Year-1 benefits"]
    values = [2.0, 5.15]
    colors = [NAVY, GREEN]
    bars = ax.bar(labels, values, width=0.55, color=colors, edgecolor="none", zorder=3)
    for bar, lab in zip(bars, ["KES 2.0M", "KES 5.2M"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, lab,
                ha="center", va="bottom", fontsize=14, fontweight="bold", color=INK)

    ax.set_ylim(0, 6.2)
    ax.set_ylabel("KES millions (illustrative)", color=MUTED, fontsize=12)
    ax.set_title("Year-1 pilot: spend vs estimated benefit", fontsize=15, fontweight="bold", color=INK, loc="left", pad=10)
    ax.tick_params(axis="x", labelsize=12)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors=MUTED)
    ax.text(
        0.5, -0.14,
        "Donor gifts go to school fee accounts and are not counted as platform cost.",
        transform=ax.transAxes, ha="center", fontsize=11, color=MUTED, style="italic",
    )
    fig.tight_layout()
    _save(fig, "06_year1_economics.png")


# ---------------------------------------------------------------------------
# Pilot roadmap (original four stage boxes)
# ---------------------------------------------------------------------------
def fig_pilot_roadmap() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.3, 4.15, "From proof of concept to pilot.", fontsize=13, fontweight="bold", color=INK, va="top")

    stages = [
        (SLATE, "Now", ["Synthetic PoC", "HTML demos", "Fee ledger"]),
        (ORANGE, "Gate 1", ["School MOUs", "Tier-1 data", "Human review"]),
        (GREEN, "Pilot", ["8 schools", "Live fee gifts", "KPI dashboard"]),
        (NAVY, "Scale if earned", ["Extra channel", "payment rails", "foundations"]),
    ]
    xs = [0.45, 3.4, 6.35, 9.3]
    w, h, y = 2.55, 2.85, 0.55
    for i, (x, (c, title, items)) in enumerate(zip(xs, stages)):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    facecolor=c, edgecolor="none", zorder=2))
        ax.text(x + w / 2, y + h - 0.45, title, ha="center", va="top", fontsize=12,
                fontweight="bold", color="white", zorder=3)
        for j, it in enumerate(items):
            ax.text(x + w / 2, y + h - 1.15 - j * 0.45, it, ha="center", va="top",
                    fontsize=9.5, color="white", zorder=3)
        if i < 3:
            ax.annotate(
                "",
                xy=(xs[i + 1] - 0.05, y + h / 2),
                xytext=(x + w + 0.05, y + h / 2),
                arrowprops=dict(arrowstyle="->", color=INK, lw=1.3),
                zorder=1,
            )

    _save(fig, "07_pilot_roadmap.png")


# ---------------------------------------------------------------------------
# Selection rule (original scatter)
# ---------------------------------------------------------------------------
def fig_selection_rule() -> None:
    fig, ax = plt.subplots(figsize=(8.8, 6.0))
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    models = [
        ("Majority baseline", 0.50, 0.0, NAVY, 90, False),
        ("Random Forest", 0.74, 0.08, NAVY, 100, False),
        ("Gradient Boosting", 0.75, 0.33, NAVY, 110, False),
        ("Logistic Regression\n(selected)", 0.753, 0.667, GREEN, 220, True),
    ]
    for name, auc, rec, c, s, bold in models:
        ax.scatter(auc, rec, s=s, c=c, zorder=5, edgecolors="white", linewidths=1.0)
        ax.annotate(
            name,
            xy=(auc, rec),
            xytext=(10 if bold else 8, 8),
            textcoords="offset points",
            fontsize=12 if bold else 11,
            fontweight="bold" if bold else "normal",
            color=GREEN if bold else MUTED,
            ha="left",
            va="bottom",
        )

    ax.set_xlim(0.45, 0.82)
    ax.set_ylim(-0.05, 0.85)
    ax.set_xlabel("How well students are ranked  (0.50 = chance)", color=MUTED, fontsize=12)
    ax.set_ylabel("Share of dropouts found", color=MUTED, fontsize=12)
    ax.set_title("We chose the model that finds more students who would leave", fontsize=14, fontweight="bold",
                 color=INK, loc="left", pad=10)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors=MUTED)
    ax.text(
        0.0, -0.12,
        "Proof-of-concept results on 1,000 students. Higher on this chart is better.",
        transform=ax.transAxes, ha="left", fontsize=11, color=MUTED, style="italic",
    )
    fig.tight_layout()
    _save(fig, "08_selection_rule.png")


# ---------------------------------------------------------------------------
# Perceptual map (original 2x2 style — kept as preferred style)
# ---------------------------------------------------------------------------
def fig_perceptual_map() -> None:
    fig, ax = plt.subplots(figsize=(9.5, 7.2))
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
        fontsize=15, fontweight="bold", color=INK, loc="left", pad=14,
    )
    ax.text(
        0.0, 1.08,
        "Illustrative map for funders. ElimuMatch works alongside bursaries; it does not replace them.",
        transform=ax.transAxes, fontsize=11, color=MUTED, va="bottom",
    )

    ax.text(1.1, -0.08, "Easy for donors  →", ha="right", va="top", fontsize=11, color=MUTED)
    ax.text(-1.1, -0.08, "←  Hard for donors", ha="left", va="top", fontsize=11, color=MUTED)
    ax.text(-0.04, 1.08, "Finds the right students  ↑", ha="right", va="top", fontsize=11, color=MUTED)
    ax.text(-0.04, -1.08, "Guesswork  ↓", ha="right", va="bottom", fontsize=11, color=MUTED)
    ax.text(0.55, 0.88, "Where funders should sit", ha="center", fontsize=12, fontweight="bold", color=GREEN)

    points = [
        (0.72, 0.78, "ElimuMatch\n(fee support)", GREEN, 220, True),
        (-0.72, 0.62, "Yearly bursary\ncontests", NAVY, 80, False),
        (-0.35, 0.05, "Church / alumni\nlists", NAVY, 70, False),
        (-0.15, -0.18, "One-off gifts\nto a school", NAVY, 70, False),
        (0.45, -0.55, "Giving through\nfriends", ORANGE, 80, False),
        (0.78, -0.78, "Public campaigns\n(most visible cases)", ORANGE, 80, False),
    ]
    for x, y, lab, c, s, bold in points:
        ax.scatter(x, y, s=s, c=c, zorder=5, edgecolors="white", linewidths=1.0)
        ax.text(
            x, y - 0.14, lab, ha="center", va="top",
            fontsize=11 if bold else 10, fontweight="bold" if bold else "normal",
            color=INK if bold else MUTED, linespacing=1.15, zorder=6,
        )

    ax.set_xlabel("How easy it is for a donor to complete a gift", fontsize=12, color=MUTED, labelpad=8)
    ax.set_ylabel("How well support is aimed at students who may leave", fontsize=12, color=MUTED, labelpad=8)
    fig.tight_layout()
    _save(fig, "09_perceptual_map.png")


# ---------------------------------------------------------------------------
# Day in the life of one gift (roadmap — plain language)
# ---------------------------------------------------------------------------
def fig_gift_journey() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 4.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    fig.patch.set_facecolor(CREAM)
    ax.set_facecolor(CREAM)

    ax.text(0.3, 4.15, "From place to gift in four steps.", fontsize=15, fontweight="bold", color=INK, va="top")

    stages = [
        (GREEN, "1  Choose place", ["Pick a county", "Day or boarding", "Open the school"], "white"),
        (TEAL, "2  See a student", ["Name is hidden", "Fee balance shown", "Already on the list"], "white"),
        (ORANGE, "3  Give", ["Pay part or all", "Oldest term first", "Get a receipt"], INK),
        (NAVY, "4  Confirm", ["Money reaches school", "Team sees it landed", "Help is tracked"], "white"),
    ]
    xs = [0.45, 3.4, 6.35, 9.3]
    w, h, y = 2.55, 2.85, 0.55
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
            y + h - 0.45,
            title,
            ha="center",
            va="top",
            fontsize=13,
            fontweight="bold",
            color=fg,
            zorder=3,
        )
        for j, it in enumerate(items):
            ax.text(
                x + w / 2,
                y + h - 1.15 - j * 0.45,
                it,
                ha="center",
                va="top",
                fontsize=12,
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
    ax.set_xlabel("Share who complete that level", fontsize=12, color=MUTED)
    ax.set_title("Nearly all finish primary. Fewer than half finish secondary.",
                 fontsize=14, fontweight="bold", color=INK, loc="left", pad=10)
    ax.tick_params(colors=INK, labelsize=12)
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
        ax.text(x, y + 0.08, f"{y:.2f}M", ha="center", va="bottom", fontsize=12, fontweight="bold", color=INK)
    ax.set_ylim(3.2, 4.7)
    ax.set_xticks(years)
    ax.set_ylabel("Secondary enrolment (millions)", fontsize=12, color=MUTED)
    ax.set_title("More students are in secondary school, so more can still leave mid-course",
                 fontsize=13, fontweight="bold", color=INK, loc="left", pad=10)
    ax.tick_params(colors=INK, labelsize=12)
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
