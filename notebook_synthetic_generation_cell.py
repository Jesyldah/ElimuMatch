"""Documented synthetic cohort generation for the analysis notebook.

Mirrors synthetic_data_v2.py (seed 2026, n=1000) with per-feature assumption comments.
"""

SYNTHETIC_GENERATION_CELL = r'''
# Synthetic cohort generation (synthetic_data_v2.py logic, seed 2026)
# Partner records were unavailable — this DGP creates a realistic but fully synthetic cohort.
from kenya_schools import N_SCHOOLS

rng = np.random.default_rng(RANDOM_STATE)
n_students = 1000
n_schools = N_SCHOOLS  # 47 counties — one sample school per county in the catalog

DROPOUT_REASONS = [
    "financial_instability", "academic_performance", "health_related",
    "commute_distance", "psychosocial", "household_pressure", "other",
]
MISSINGNESS_CONFIG = {
    "cash_flow_volatility": 0.08,
    "commute_barrier_score": 0.06,
    "digital_equity_access_score": 0.06,
    "psychosocial_support_access": 0.07,
}


def _zscore(series):
    std = series.std()
    return np.zeros_like(series, dtype=float) if std == 0 else (series - series.mean()) / std


def _inject_missing(values, missing_rate, ses_index, rng):
    # Lower-SES students are slightly more likely to have missing survey fields (MAR).
    ses_weight = (6 - ses_index) / 5
    prob = np.clip(missing_rate * (0.75 + 0.50 * ses_weight), 0, 0.20)
    mask = rng.random(len(values)) < prob
    out = values.astype(object).copy()
    out[mask] = np.nan
    return out


def _assign_dropout_reasons(frame, rng):
    # Post-outcome label for simulation only — never used as a model feature.
    reasons = np.full(len(frame), np.nan, dtype=object)
    risk_matrix = np.column_stack([
        _zscore(frame["cash_flow_volatility"].fillna(frame["cash_flow_volatility"].median()).values)
        + _zscore((6 - frame["socioeconomic_status_index"]).values),
        _zscore(frame["failed_subjects_count"].values) - _zscore(frame["gpa_trend"].values),
        _zscore(frame["health_related_absences"].values) + _zscore(frame["chronic_health_risk_score"].values),
        _zscore(frame["commute_barrier_score"].fillna(frame["commute_barrier_score"].median()).values),
        -_zscore(frame["social_integration_score"].values)
        - _zscore(frame["psychosocial_support_access"].fillna(0).values),
        _zscore(frame["resource_dilution_index"].values) + _zscore((6 - frame["socioeconomic_status_index"]).values),
    ])
    risk_matrix += rng.normal(0, 0.15, risk_matrix.shape)
    dropped_idx = np.where(frame["retained"].values == 0)[0]
    reason_idx = risk_matrix[dropped_idx].argmax(axis=1)
    for i, row_idx in enumerate(dropped_idx):
        reasons[row_idx] = "other" if rng.random() < 0.08 else DROPOUT_REASONS[reason_idx[i]]
    return reasons


# --- Identifiers ---
# student_id: Sequential integer 1..n. Deterministic primary key for joins and ledger tables.
student_id = np.arange(1, n_students + 1)

# school_id: Random assignment across the national school catalog (1..47).
# Discrete uniform over schools — national design, not one-site concentration.
school_id = rng.integers(1, n_schools + 1, n_students)

# --- Base demographics ---
# age_at_enrollment: Secondary students typically age 13–17.
# Discrete uniform on [13, 17] — standard Form 1–4 age band.
age = rng.integers(13, 18, n_students)

# gender: Binary indicator (0/1) for modeling and fairness slices.
# Bernoulli with p=0.5 — balanced split in the synthetic cohort.
gender = rng.integers(0, 2, n_students)

# socioeconomic_status_index: Income/resource quintile proxy (1=most constrained, 5=least).
# Discrete distribution skewed toward lower quintiles to reflect sector equity pressure.
ses_index = rng.choice([1, 2, 3, 4, 5], size=n_students, p=[0.25, 0.25, 0.22, 0.18, 0.10])

# resource_dilution_index: Household size / crowding pressure.
# Poisson with mean rising as SES falls — larger households at lower quintiles.
resource_dilution = np.array([rng.poisson(lam=3.5 + 0.35 * (6 - ses)) for ses in ses_index])

# --- Institutional and environmental access ---
# digital_equity_access_score: 0=no reliable access, 1=shared, 2=personal device.
# SES-conditional categorical probabilities — better access at higher quintiles.
digital_probs = {
    1: [0.72, 0.20, 0.08], 2: [0.60, 0.28, 0.12], 3: [0.48, 0.32, 0.20],
    4: [0.35, 0.38, 0.27], 5: [0.22, 0.40, 0.38],
}
digital_equity = np.array([rng.choice([0, 1, 2], p=digital_probs[ses]) for ses in ses_index])

# nutritional_support_access: School feeding program available (0/1).
# Binomial with probability increasing as SES decreases — feeding targets needier students.
nutritional_support = np.array([
    rng.binomial(1, p=min(0.85, 0.40 + 0.10 * (6 - ses))) for ses in ses_index
])

# psychosocial_support_access: Counseling / psychosocial program access (0/1).
# Binomial with modest coverage rising slightly with SES (better-resourced schools).
psychosocial_support = np.array([rng.binomial(1, p=0.12 + 0.06 * ses) for ses in ses_index])

# commute_barrier_score: Distance / travel burden proxy in km-like units.
# Gamma distribution — many short commutes, long tail for rural day-school friction.
commute_barrier = np.array([rng.gamma(shape=2, scale=2.0 + 0.45 * (6 - ses)) for ses in ses_index])

# --- Academic and health ---
# chronic_health_risk_score: Underlying health intensity (1=low, 2=medium, 3=high).
# Categorical PMF: 70% low, 20% medium, 10% high — most students not chronically ill.
chronic_health = rng.choice([1, 2, 3], size=n_students, p=[0.7, 0.2, 0.1])

# health_related_absences: School days missed for health reasons.
# Poisson with rate scaled by chronic_health — worse health → more absences.
health_absences = rng.poisson(lam=chronic_health * 5, size=n_students)

# failed_subjects_count: Number of failed core subjects.
# Poisson with mean rising with lower SES and higher health risk.
failed_subjects = np.array([
    rng.poisson(lam=0.7 + 0.30 * (6 - ses) + 0.15 * (health - 1))
    for ses, health in zip(ses_index, chronic_health)
])

# gpa_trend: Year-on-year GPA change (negative = decline).
# Linear function of failures and SES plus Gaussian noise — academic momentum signal.
gpa_trend = (
    -0.55 * failed_subjects
    + 0.25 * (ses_index - 3)
    + rng.normal(0, 0.6, n_students)
)

# strength_science_indicator: STEM aptitude flag (0/1).
# Binomial — higher SES and fewer failures raise probability of science strength.
science_talent = np.array([
    rng.binomial(1, p=min(0.65, max(0.08, 0.12 + 0.05 * ses - 0.10 * failed)))
    for ses, failed in zip(ses_index, failed_subjects)
])

# social_integration_score: Extracurricular / belonging proxy (0–3).
# Normal draw clipped to range — higher SES and fewer absences improve integration.
social_integration = np.array([
    int(np.clip(rng.normal(1.2 + 0.15 * ses - 0.04 * absences, 0.9), 0, 3))
    for ses, absences in zip(ses_index, health_absences)
])

# --- Economic volatility ---
# cash_flow_volatility: Share of income variance from irregular sources (e.g. agriculture).
# Uniform band widens as SES falls — 0.12–0.32 after clipping.
cash_flow_volatility = np.array([
    rng.uniform(0.12 + 0.02 * (6 - ses), 0.22 + 0.03 * (6 - ses)) for ses in ses_index
])

# academic_catchup_status: Remediation flag (0/1).
# Deterministic rule: >3 failed subjects → catch-up required (dropped from model as redundant).
academic_catchup = np.where(failed_subjects > 3, 1, 0)

# --- School-level random effect ---
# Small random shift per school_id to mimic unobserved school context (not a modeled feature).
school_effect = {sid: rng.normal(0, 0.25) for sid in range(1, n_schools + 1)}
school_shift = np.array([school_effect[sid] for sid in school_id])

# --- Retention outcome (target) ---
# retention_risk_score: Latent probability from a logistic structural model (oracle for DGP only).
# Coefficients tuned so cohort retention ≈ 86–87%. Excluded from training (leakage).
retention_logit = (
    3.05
    + 0.22 * ses_index
    + 0.30 * gpa_trend
    - 0.09 * commute_barrier
    - 0.05 * health_absences
    - 0.28 * failed_subjects
    + 0.35 * nutritional_support
    + 0.30 * psychosocial_support
    + 0.18 * digital_equity
    + 0.20 * science_talent
    + 0.12 * social_integration
    - 1.5 * (cash_flow_volatility - 0.22)
    - 0.06 * (resource_dilution - 4)
    + school_shift
    + rng.normal(0, 0.35, n_students)
)
retention_risk_score = 1 / (1 + np.exp(-retention_logit))

# retained: Binary outcome (1=stayed enrolled, 0=dropped out).
# Bernoulli draw using retention_risk_score as probability — stochastic final outcome.
retained = rng.binomial(1, retention_risk_score)

df = pd.DataFrame({
    "student_id": student_id,
    "school_id": school_id,
    "age_at_enrollment": age,
    "gender": gender,
    "resource_dilution_index": resource_dilution,
    "socioeconomic_status_index": ses_index,
    "commute_barrier_score": commute_barrier,
    "digital_equity_access_score": digital_equity,
    "nutritional_support_access": nutritional_support,
    "gpa_trend": gpa_trend,
    "failed_subjects_count": failed_subjects,
    "strength_science_indicator": science_talent,
    "chronic_health_risk_score": chronic_health,
    "health_related_absences": health_absences,
    "social_integration_score": social_integration,
    "cash_flow_volatility": cash_flow_volatility,
    "academic_catchup_status": academic_catchup,
    "psychosocial_support_access": psychosocial_support,
    "retention_risk_score": retention_risk_score.round(4),
    "retained": retained,
})

# Clip to realistic bounds used in validation (descriptive_analysis.py ranges).
df["commute_barrier_score"] = df["commute_barrier_score"].clip(0, 20)
df["gpa_trend"] = df["gpa_trend"].clip(-4, 4)
df["failed_subjects_count"] = df["failed_subjects_count"].clip(0, 8)
df["cash_flow_volatility"] = df["cash_flow_volatility"].clip(0.12, 0.32)

# dropout_reason: Assigned only for retained==0 from dominant risk dimension (+ 8% "other").
df["dropout_reason"] = _assign_dropout_reasons(df, rng)

# Inject missing values on survey-like fields (rates in MISSINGNESS_CONFIG).
for column, rate in MISSINGNESS_CONFIG.items():
    df[column] = _inject_missing(
        df[column].values, rate, df["socioeconomic_status_index"].values, rng
    )

print(f"Generated synthetic cohort: {len(df):,} students | {n_schools} schools")
print(f"Retention rate: {df['retained'].mean():.1%}")
print("Missingness (survey fields):")
for column in MISSINGNESS_CONFIG:
    print(f"  {column}: {df[column].isna().mean():.1%}")

df.head()
'''.strip()
