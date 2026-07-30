import pandas as pd
import numpy as np

# Set seed for reproducibility
np.random.seed(2026)
n_students = 1000

# 1. Base Demographic Features
# Age: Average 13-17 for secondary school students. 
# We use a discrete uniform distribution covering the standard secondary cycle.
age = np.random.randint(13, 18, n_students)

# Gender: Balanced 50/50 split. 
# We use a Bernoulli distribution to maintain demographic parity in the model.
gender = np.random.randint(0, 2, n_students)

# Resource Dilution: Average household size ~4. 
# We use a Poisson distribution centered around 4 to reflect realistic Kenyan household structures.
resource_dilution = np.random.poisson(lam=4, size=n_students)

# SES: Proxy for income quintiles (1-5). 
# We use a discrete uniform distribution to ensure equal representation of all economic strata in the sample.
ses_index = np.random.randint(1, 6, n_students)

# 2. Institutional & Environmental Features
# Commute Barrier: Avg 5-6km for rural walking, up to 12km for day schools. 
# We use a Gamma distribution to reflect that many students are close, but some have long commutes.
commute_barrier = np.random.gamma(shape=2, scale=2.5, size=n_students)

# Digital Equity: 0=None, 1=Shared, 2=Personal. 
# Weighted toward lower access (50% none) to reflect common barriers in resource-constrained schools.
digital_equity = np.random.choice([0, 1, 2], size=n_students, p=[0.5, 0.3, 0.2])

# Nutritional Support: Access is binary (0, 1). 
# We use a binomial distribution with a 60% probability of coverage by current school feeding programs.
nutritional_support = np.random.binomial(1, p=0.6, size=n_students)

# 3. Academic & Health Features
# GPA Trend: Change in GPA vs previous year, centered at 0. 
# We use a normal distribution to reflect standard academic fluctuations across a large cohort.
gpa_trend = np.random.normal(loc=0, scale=1.5, size=n_students)

# Failed Subjects: Count of failed core subjects. 
# We use a Poisson distribution centered at 1.5 to model the frequency of academic struggle.
failed_subjects = np.random.poisson(lam=1.5, size=n_students)

# Strength in Science: Binary flag (0, 1). 
# We use a 30% probability, aligned with historical STEM performance distributions in secondary schools.
science_talent = np.random.binomial(1, p=0.3, size=n_students)

# Chronic Health: Intensity of health condition (1-3). 
# We use a custom probability mass function where 70% of students have low risk (1).
chronic_health = np.random.choice([1, 2, 3], size=n_students, p=[0.7, 0.2, 0.1])

# Health Absences: Number of school days missed due to illness. 
# We use a Poisson distribution scaled by health risk (lam=chronic_health * 5) to link health and attendance.
health_absences = np.random.poisson(lam=chronic_health * 5, size=n_students)

# Social Integration: Scale 0-3 (ECA participation). 
# We use a uniform distribution to represent broad levels of engagement across the student body.
social_integration = np.random.randint(0, 4, n_students)

# 4. Retention Sensitivity Drivers
# Cash-Flow Volatility: 12-32% variance (0.12 - 0.32). 
# We use a uniform distribution calibrated to agricultural market price instability ranges.
cash_flow_volatility = np.random.uniform(0.12, 0.32, n_students)

# Academic Catch-up: Binary (0, 1). 
# Logically conditional: Students with >3 failed subjects are flagged for remediation.
academic_catchup = np.where(failed_subjects > 3, 1, 0)

# Psychosocial Support: Binary (0, 1). 
# Assigned at 30% to match current school-based counseling service coverage estimates.
psychosocial_support = np.random.binomial(1, p=0.3, size=n_students)

# Compile into DataFrame
df = pd.DataFrame({
    'age_at_enrollment': age, 'gender': gender, 'resource_dilution_index': resource_dilution,
    'socioeconomic_status_index': ses_index, 'commute_barrier_score': commute_barrier,
    'digital_equity_access_score': digital_equity, 'nutritional_support_access': nutritional_support,
    'gpa_trend': gpa_trend, 'failed_subjects_count': failed_subjects,
    'strength_science_indicator': science_talent, 'chronic_health_risk_score': chronic_health,
    'health_related_absences': health_absences, 'social_integration_score': social_integration,
    'cash_flow_volatility': cash_flow_volatility, 'academic_catchup_status': academic_catchup,
    'psychosocial_support_access': psychosocial_support
})

# Final Constraint Clipping
df['commute_barrier_score'] = df['commute_barrier_score'].clip(0, 20)
df['gpa_trend'] = df['gpa_trend'].clip(-4, 4)
df['failed_subjects_count'] = df['failed_subjects_count'].clip(0, 8)

df.to_csv('elimu_match_data_v2.csv', index=False)
print("Dataset generated with detailed logic-driven documentation.")