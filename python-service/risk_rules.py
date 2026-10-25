"""
Business-rule layer applied AFTER the Logistic Regression model.

Why this exists
---------------
The model was trained on the IBM HR dataset (~16% attrition). Two things make it
miss obvious real-world cases:
  1. The class imbalance pulls probabilities down: even a fairly risky profile
     often lands at 30-45%, below the 0.5 cut-off, so it is labelled STAY.
  2. Only 10 fields are collected; 20 others are filled with neutral defaults,
     so the model cannot "see" the usual risk signals.

Instead of retraining, we adjust the model's probability with transparent,
explainable HR rules. Every rule that fires is returned to the caller with a
plain-English reason, so the final decision can be defended in a viva.

All income thresholds are MONTHLY INCOME IN USD (the dataset's scale).
"""

# Decision thresholds on the (adjusted) turnover probability
LEAVE_THRESHOLD = 0.50
HIGH_RISK = 0.65
MEDIUM_RISK = 0.35

# If this many "early-career flight-risk" flags fire together, the combination
# is treated as high risk regardless of what the model said.
COMBO_FLAGS_FOR_OVERRIDE = 4
COMBO_FLOOR = 0.70

# Roles with historically higher / lower attrition in the training data
HIGH_TURNOVER_ROLES = {
    'Sales Representative': 0.10,
    'Laboratory Technician': 0.04,
    'Human Resources': 0.04,
}
LOW_TURNOVER_ROLES = {
    'Manager': -0.05,
    'Research Director': -0.05,
    'Manufacturing Director': -0.03,
}

# Rough "market" monthly pay (USD) below which a role is considered underpaid
ROLE_PAY_FLOOR = {
    'Manager': 9000,
    'Research Director': 9000,
    'Healthcare Representative': 5000,
    'Manufacturing Director': 5000,
    'Sales Executive': 4500,
    'Research Scientist': 3000,
    'Laboratory Technician': 3000,
    'Human Resources': 3000,
    'Sales Representative': 2500,
}


def apply_rules(e, model_prob):
    """
    e: dict of validated essentials (Age, MonthlyIncome[USD], JobRole, ...)
    model_prob: raw turnover probability from the model (0-1)

    Returns dict: adjustedProbability, riskLevel, prediction, riskFactors,
    protectiveFactors, ruleOverrideApplied.
    """
    age = e['Age']
    income = e['MonthlyIncome']
    total_years = e['TotalWorkingYears']
    tenure = e['YearsAtCompany']
    role = e['JobRole']
    single = e['MaritalStatus'] == 'Single'

    delta = 0.0
    risk, protect = [], []
    combo_flags = 0

    # ---- Early-career flight-risk flags (the "perfect storm" combination) ----
    if age <= 25:
        delta += 0.08
        combo_flags += 1
        risk.append(f'Young employee (age {age}) - early-career staff change jobs most often')
    elif age <= 30:
        delta += 0.04
        risk.append(f'Under 30 (age {age}) - above-average mobility')

    if total_years <= 2:
        delta += 0.08
        combo_flags += 1
        risk.append(f'Very little experience ({total_years} yr) - still exploring the market')
    elif total_years <= 4:
        delta += 0.03

    if income < 2000:
        delta += 0.20
        combo_flags += 1
        risk.append('Very low pay (below $2,000/month equivalent)')
    elif income < 3000:
        delta += 0.12
        combo_flags += 1
        risk.append('Low pay (below $3,000/month equivalent)')

    if single:
        delta += 0.07
        combo_flags += 1
        risk.append('Single - fewer personal ties to the current location/employer')

    # ---- Role-aware rules ----
    floor = ROLE_PAY_FLOOR.get(role)
    if floor and income < floor and income >= 3000:
        delta += 0.06
        risk.append(f'Pay is below the typical range for a {role}')

    if role in HIGH_TURNOVER_ROLES:
        delta += HIGH_TURNOVER_ROLES[role]
        risk.append(f'{role} is a historically high-turnover role')
    if role in LOW_TURNOVER_ROLES:
        delta += LOW_TURNOVER_ROLES[role]
        protect.append(f'{role} is a historically low-turnover role')

    # ---- Other real-world signals ----
    if tenure <= 1 and total_years >= 5:
        delta += 0.05
        risk.append('Recently joined despite prior experience - first-year exits are common')

    if e['DistanceFromHome'] >= 25 and e['OverTime'] == 'Yes':
        delta += 0.06
        risk.append('Long commute combined with overtime - burnout risk')

    # ---- Protective factors ----
    if age >= 40 and tenure >= 8 and income >= 5000:
        delta -= 0.10
        protect.append('Experienced, long-tenured and well paid - strong retention')
    elif tenure >= 5 and e['MaritalStatus'] == 'Married':
        delta -= 0.04
        protect.append('Settled employee (married, 5+ years at the company)')

    adjusted = min(0.99, max(0.01, model_prob + delta))

    override = False
    if combo_flags >= COMBO_FLAGS_FOR_OVERRIDE and adjusted < COMBO_FLOOR:
        adjusted = COMBO_FLOOR
        override = True
        risk.append(f'{combo_flags} early-career risk signals occur together '
                    '(young + inexperienced + low pay + single) - flagged as high risk')

    if adjusted >= HIGH_RISK:
        level = 'HIGH'
    elif adjusted >= MEDIUM_RISK:
        level = 'MEDIUM'
    else:
        level = 'LOW'

    return {
        'adjustedProbability': round(adjusted, 4),
        'prediction': 'LEAVE' if adjusted >= LEAVE_THRESHOLD else 'STAY',
        'riskLevel': level,
        'riskFactors': risk,
        'protectiveFactors': protect,
        'ruleOverrideApplied': override,
    }
