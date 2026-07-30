import pandas as pd
import numpy as np

np.random.seed(2026)
n_students = 1000
n_schools = 20

student_id = np.arange(1, n_students + 1)
school_id = np.random.randint(1, n_schools + 1, n_students)

# 1. Base demographics
age = np.random.randint(13, 18, n_students)
gender = np.random.randint(0, 2, n_students)

# SES: weighted toward lower/middle quintiles (unequal population shares)
ses_index = np.random.choice([1, 2, 3, 4, 5], size=n_students, p=[0.25, 0.25, 0.22, 0.18, 0.10])

# Larger households are more common in lower-SES homes
resource_dilution = np.array([
    np.random.poisson(lam=3.5 + 0.35 * (6 - ses))
    for ses in ses_index
])

# 2. Institutional & environmental features (conditional on SES)
digital_probs = {
    1: [0.72, 0.20, 0.08],
    2: [0.60, 0.28, 0.12],
    3: [0.48, 0.32, 0.20],
    4: [0.35, 0.38, 0.27],
    5: [0.22, 0.40, 0.38],
}
digital_equity = np.array([
    np.random.choice([0, 1, 2], p=digital_probs[ses])
    for ses in ses_index
])

nutritional_support = np.array([
    np.random.binomial(1, p=min(0.85, 0.40 + 0.10 * (6 - ses)))
    for ses in ses_index
])

psychosocial_support = np.array([
    np.random.binomial(1, p=0.12 + 0.06 * ses)
    for ses in ses_index
])

commute_barrier = np.array([
    np.random.gamma(shape=2, scale=2.0 + 0.45 * (6 - ses))
    for ses in ses_index
])

# 3. Academic & health features
chronic_health = np.random.choice([1, 2, 3], size=n_students, p=[0.7, 0.2, 0.1])
health_absences = np.random.poisson(lam=chronic_health * 5, size=n_students)

failed_subjects = np.array([
    np.random.poisson(lam=0.7 + 0.30 * (6 - ses) + 0.15 * (health - 1))
    for ses, health in zip(ses_index, chronic_health)
])

gpa_trend = (
    -0.55 * failed_subjects
    + 0.25 * (ses_index - 3)
    + np.random.normal(0, 0.6, n_students)
)

science_talent = np.array([
    np.random.binomial(1, p=min(0.65, max(0.08, 0.12 + 0.05 * ses - 0.10 * failed)))
    for ses, failed in zip(ses_index, failed_subjects)
])

social_integration = np.array([
  int(np.clip(np.random.normal(1.2 + 0.15 * ses - 0.04 * absences, 0.9), 0, 3))
  for ses, absences in zip(ses_index, health_absences)
])

# 4. Retention sensitivity drivers
cash_flow_volatility = np.array([
    np.random.uniform(0.12 + 0.02 * (6 - ses), 0.22 + 0.03 * (6 - ses))
    for ses in ses_index
])

academic_catchup = np.where(failed_subjects > 3, 1, 0)

# School-level retention environment (latent cluster effect)
school_effect = {sid: np.random.normal(0, 0.25) for sid in range(1, n_schools + 1)}
school_shift = np.array([school_effect[sid] for sid in school_id])

# 5. Retention outcome (latent risk → realized retention)
retention_logit = (
    2.10
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
    + np.random.normal(0, 0.35, n_students)
)

retention_risk_score = 1 / (1 + np.exp(-retention_logit))
retained = np.random.binomial(1, retention_risk_score)

df = pd.DataFrame({
    'student_id': student_id,
    'school_id': school_id,
    'age_at_enrollment': age,
    'gender': gender,
    'resource_dilution_index': resource_dilution,
    'socioeconomic_status_index': ses_index,
    'commute_barrier_score': commute_barrier,
    'digital_equity_access_score': digital_equity,
    'nutritional_support_access': nutritional_support,
    'gpa_trend': gpa_trend,
    'failed_subjects_count': failed_subjects,
    'strength_science_indicator': science_talent,
    'chronic_health_risk_score': chronic_health,
    'health_related_absences': health_absences,
    'social_integration_score': social_integration,
    'cash_flow_volatility': cash_flow_volatility,
    'academic_catchup_status': academic_catchup,
    'psychosocial_support_access': psychosocial_support,
    'retention_risk_score': retention_risk_score.round(4),
    'retained': retained,
})

df['commute_barrier_score'] = df['commute_barrier_score'].clip(0, 20)
df['gpa_trend'] = df['gpa_trend'].clip(-4, 4)
df['failed_subjects_count'] = df['failed_subjects_count'].clip(0, 8)
df['cash_flow_volatility'] = df['cash_flow_volatility'].clip(0.12, 0.32)

output_path = 'elimu_match_data_v3.csv'
df.to_csv(output_path, index=False)

print(f"Dataset saved to {output_path}")
print(f"Students: {len(df):,} | Schools: {n_schools} | Retention rate: {df['retained'].mean():.1%}")
