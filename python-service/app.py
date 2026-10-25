from flask import Flask, request, jsonify
import warnings
import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

from risk_rules import apply_rules

warnings.filterwarnings('ignore')

app = Flask(__name__)

DEFAULTS = {
    'BusinessTravel': 'Travel_Rarely',
    'Education': 3,
    'EnvironmentSatisfaction': 3,
    'JobInvolvement': 3,
    'JobSatisfaction': 3,
    'RelationshipSatisfaction': 3,
    'WorkLifeBalance': 3,
    'PerformanceRating': 3,
    'StockOptionLevel': 0,
    'NumCompaniesWorked': 2,
    'PercentSalaryHike': 15,
    'TrainingTimesLastYear': 2,
}

DEPARTMENT_TO_FIELD = {
    'Human Resources': 'Human Resources',
    'Sales': 'Marketing',
    'Research & Development': 'Life Sciences',
}

# Monthly income range (USD) present in the training data
MODEL_INCOME_MIN = 1009
MODEL_INCOME_MAX = 19999

DEPARTMENTS = ['Human Resources', 'Research & Development', 'Sales']
JOB_ROLES = [
    'Healthcare Representative', 'Human Resources', 'Laboratory Technician', 'Manager',
    'Manufacturing Director', 'Research Director', 'Research Scientist',
    'Sales Executive', 'Sales Representative'
]
MARITAL_STATUSES = ['Divorced', 'Married', 'Single']
GENDERS = ['Female', 'Male']
OVERTIME_OPTIONS = ['No', 'Yes']

FEATURE_COLUMNS = [
    'Age', 'BusinessTravel', 'DailyRate', 'Department', 'DistanceFromHome',
    'Education', 'EducationField', 'EnvironmentSatisfaction', 'Gender', 'HourlyRate',
    'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction', 'MaritalStatus',
    'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked', 'OverTime', 'PercentSalaryHike',
    'PerformanceRating', 'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
    'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany', 'YearsInCurrentRole',
    'YearsSinceLastPromotion', 'YearsWithCurrManager'
]

CATEGORICAL_MAPPINGS = {
    'BusinessTravel': ['Non-Travel', 'Travel_Frequently', 'Travel_Rarely'],
    'Department': DEPARTMENTS,
    'EducationField': ['Human Resources', 'Life Sciences', 'Marketing', 'Medical', 'Other', 'Technical Degree'],
    'Gender': GENDERS,
    'JobRole': JOB_ROLES,
    'MaritalStatus': MARITAL_STATUSES,
    'OverTime': OVERTIME_OPTIONS
}

# Load model once at startup, not on every request
MODEL = None
SCALER = None


def load_model():
    global MODEL, SCALER
    if not (os.path.exists('attrition_logistic_model.pkl') and os.path.exists('data_scaler.pkl')):
        raise FileNotFoundError("Missing model or scaler .pkl files in this directory.")
    MODEL = joblib.load('attrition_logistic_model.pkl')
    SCALER = joblib.load('data_scaler.pkl')


def derive_full_profile(essentials):
    age = essentials['Age']
    income = essentials['MonthlyIncome']
    dept = essentials['Department']
    total_years = essentials['TotalWorkingYears']
    years_at_company = essentials['YearsAtCompany']

    hourly_rate = round(income / (21 * 8), 2)
    daily_rate = round(income / 21, 2)
    monthly_rate = income * 2

    if income < 3000:
        job_level = 1
    elif income < 6000:
        job_level = 2
    elif income < 10000:
        job_level = 3
    elif income < 15000:
        job_level = 4
    else:
        job_level = 5

    years_in_role = min(years_at_company, max(0, years_at_company - 1))
    years_since_promotion = min(2, years_at_company)
    years_with_manager = min(years_at_company, max(0, years_at_company - 1))

    education_field = DEPARTMENT_TO_FIELD.get(dept, 'Other')

    return {
        'Age': age,
        'BusinessTravel': DEFAULTS['BusinessTravel'],
        'DailyRate': daily_rate,
        'Department': dept,
        'DistanceFromHome': essentials['DistanceFromHome'],
        'Education': DEFAULTS['Education'],
        'EducationField': education_field,
        'EnvironmentSatisfaction': DEFAULTS['EnvironmentSatisfaction'],
        'Gender': essentials['Gender'],
        'HourlyRate': hourly_rate,
        'JobInvolvement': DEFAULTS['JobInvolvement'],
        'JobLevel': job_level,
        'JobRole': essentials['JobRole'],
        'JobSatisfaction': DEFAULTS['JobSatisfaction'],
        'MaritalStatus': essentials['MaritalStatus'],
        'MonthlyIncome': income,
        'MonthlyRate': monthly_rate,
        'NumCompaniesWorked': DEFAULTS['NumCompaniesWorked'],
        'OverTime': essentials['OverTime'],
        'PercentSalaryHike': DEFAULTS['PercentSalaryHike'],
        'PerformanceRating': DEFAULTS['PerformanceRating'],
        'RelationshipSatisfaction': DEFAULTS['RelationshipSatisfaction'],
        'StockOptionLevel': DEFAULTS['StockOptionLevel'],
        'TotalWorkingYears': total_years,
        'TrainingTimesLastYear': DEFAULTS['TrainingTimesLastYear'],
        'WorkLifeBalance': DEFAULTS['WorkLifeBalance'],
        'YearsAtCompany': years_at_company,
        'YearsInCurrentRole': years_in_role,
        'YearsSinceLastPromotion': years_since_promotion,
        'YearsWithCurrManager': years_with_manager,
    }


def run_prediction(profile):
    input_df = pd.DataFrame([profile], columns=FEATURE_COLUMNS)

    le = LabelEncoder()
    for col in input_df.select_dtypes(include=['object']).columns:
        le.fit(CATEGORICAL_MAPPINGS[col])
        input_df[col] = le.transform(input_df[col])

    input_scaled = SCALER.transform(input_df)
    prediction = MODEL.predict(input_scaled)[0]
    probabilities = MODEL.predict_proba(input_scaled)[0]

    return {
        'prediction': 'LEAVE' if prediction == 1 else 'STAY',
        'turnoverProbability': round(float(probabilities[1]), 4),
        'retentionProbability': round(float(probabilities[0]), 4)
    }


def validate_essentials(essentials):
    """Returns a list of error messages; empty list means input is valid."""
    errors = []

    required = [
        'Age', 'MonthlyIncome', 'Department', 'JobRole', 'OverTime',
        'DistanceFromHome', 'MaritalStatus', 'Gender',
        'TotalWorkingYears', 'YearsAtCompany'
    ]
    missing = [k for k in required if k not in essentials]
    if missing:
        errors.append(f'Missing fields: {missing}')
        return errors  # no point checking further if fields are missing

    if not isinstance(essentials['Age'], int) or not (18 <= essentials['Age'] <= 65):
        errors.append('Age must be an integer between 18 and 65')

    if not isinstance(essentials['MonthlyIncome'], (int, float)) or essentials['MonthlyIncome'] <= 0:
        errors.append('MonthlyIncome must be a positive number')

    if essentials['Department'] not in DEPARTMENTS:
        errors.append(f'Department must be one of {DEPARTMENTS}')

    if essentials['JobRole'] not in JOB_ROLES:
        errors.append(f'JobRole must be one of {JOB_ROLES}')

    if essentials['OverTime'] not in OVERTIME_OPTIONS:
        errors.append(f'OverTime must be one of {OVERTIME_OPTIONS}')

    if not isinstance(essentials['DistanceFromHome'], int) or not (0 <= essentials['DistanceFromHome'] <= 100):
        errors.append('DistanceFromHome must be an integer between 0 and 100')

    if essentials['MaritalStatus'] not in MARITAL_STATUSES:
        errors.append(f'MaritalStatus must be one of {MARITAL_STATUSES}')

    if essentials['Gender'] not in GENDERS:
        errors.append(f'Gender must be one of {GENDERS}')

    if not isinstance(essentials['TotalWorkingYears'], int) or not (0 <= essentials['TotalWorkingYears'] <= 50):
        errors.append('TotalWorkingYears must be an integer between 0 and 50')

    if not isinstance(essentials['YearsAtCompany'], int) or not (0 <= essentials['YearsAtCompany'] <= 50):
        errors.append('YearsAtCompany must be an integer between 0 and 50')

    if isinstance(essentials.get('YearsAtCompany'), int) and isinstance(essentials.get('TotalWorkingYears'), int):
        if essentials['YearsAtCompany'] > essentials['TotalWorkingYears']:
            errors.append('YearsAtCompany cannot exceed TotalWorkingYears')

    return errors


@app.route('/predict', methods=['POST'])
def predict():
    try:
        essentials = request.get_json(silent=True)
        if essentials is None:
            return jsonify({'error': 'Request body must be valid JSON'}), 400

        errors = validate_essentials(essentials)
        if errors:
            return jsonify({'error': 'Validation failed', 'details': errors}), 400

        # Keep the model input inside the range it was trained on (1009-19999 USD/month);
        # the business rules still see the real, unclamped income.
        model_input = dict(essentials)
        model_input['MonthlyIncome'] = min(max(essentials['MonthlyIncome'], MODEL_INCOME_MIN), MODEL_INCOME_MAX)

        profile = derive_full_profile(model_input)
        raw = run_prediction(profile)

        # Post-model business rules (see risk_rules.py)
        rules = apply_rules(essentials, raw['turnoverProbability'])
        adjusted = rules['adjustedProbability']

        return jsonify({
            'prediction': rules['prediction'],
            'turnoverProbability': adjusted,
            'retentionProbability': round(1 - adjusted, 4),
            'riskLevel': rules['riskLevel'],
            'riskFactors': rules['riskFactors'],
            'protectiveFactors': rules['protectiveFactors'],
            'ruleOverrideApplied': rules['ruleOverrideApplied'],
            'modelPrediction': raw['prediction'],
            'modelTurnoverProbability': raw['turnoverProbability'],
        }), 200

    except Exception as e:
        return jsonify({'error': 'Unexpected server error', 'details': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5000)