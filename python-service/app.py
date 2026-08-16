from flask import Flask, request, jsonify
import warnings
import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

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


@app.route('/predict', methods=['POST'])
def predict():
    try:
        essentials = request.get_json()
        required = [
            'Age', 'MonthlyIncome', 'Department', 'JobRole', 'OverTime',
            'DistanceFromHome', 'MaritalStatus', 'Gender',
            'TotalWorkingYears', 'YearsAtCompany'
        ]
        missing = [k for k in required if k not in essentials]
        if missing:
            return jsonify({'error': f'Missing fields: {missing}'}), 400

        profile = derive_full_profile(essentials)
        result = run_prediction(profile)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200


if __name__ == '__main__':
    load_model()
    app.run(host='0.0.0.0', port=5000)