import warnings
import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

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


def prompt_choice(label, options):
    print(f"\n{label}:")
    for i, opt in enumerate(options, 1):
        print(f"  {i}. {opt}")
    while True:
        choice = input(f"Select {label} (1-{len(options)}): ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return options[int(choice) - 1]
        print("Invalid choice, try again.")


def prompt_number(label, cast=int):
    while True:
        raw = input(f"{label}: ").strip()
        try:
            return cast(raw)
        except ValueError:
            print("Please enter a valid number.")


def collect_essentials():
    print("=== Employee Attrition Predictor ===")
    age = prompt_number("Age")
    income = prompt_number("Monthly Income")
    department = prompt_choice("Department", DEPARTMENTS)
    job_role = prompt_choice("Job Role", JOB_ROLES)
    overtime = prompt_choice("Works Overtime", OVERTIME_OPTIONS)
    distance = prompt_number("Distance From Home (km)")
    marital_status = prompt_choice("Marital Status", MARITAL_STATUSES)
    gender = prompt_choice("Gender", GENDERS)
    total_years = prompt_number("Total Working Years")
    years_at_company = prompt_number("Years At This Company")

    return {
        'Age': age,
        'MonthlyIncome': income,
        'Department': department,
        'JobRole': job_role,
        'OverTime': overtime,
        'DistanceFromHome': distance,
        'MaritalStatus': marital_status,
        'Gender': gender,
        'TotalWorkingYears': total_years,
        'YearsAtCompany': years_at_company,
    }


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


def predict_attrition(new_employee_data):
    if not (os.path.exists('attrition_logistic_model.pkl') and os.path.exists('data_scaler.pkl')):
        print("❌ Error: Missing saved model or scaler components. Run train_logistic.py first!")
        return

    model = joblib.load('attrition_logistic_model.pkl')
    scaler = joblib.load('data_scaler.pkl')

    feature_columns = [
        'Age', 'BusinessTravel', 'DailyRate', 'Department', 'DistanceFromHome',
        'Education', 'EducationField', 'EnvironmentSatisfaction', 'Gender', 'HourlyRate',
        'JobInvolvement', 'JobLevel', 'JobRole', 'JobSatisfaction', 'MaritalStatus',
        'MonthlyIncome', 'MonthlyRate', 'NumCompaniesWorked', 'OverTime', 'PercentSalaryHike',
        'PerformanceRating', 'RelationshipSatisfaction', 'StockOptionLevel', 'TotalWorkingYears',
        'TrainingTimesLastYear', 'WorkLifeBalance', 'YearsAtCompany', 'YearsInCurrentRole',
        'YearsSinceLastPromotion', 'YearsWithCurrManager'
    ]

    input_df = pd.DataFrame([new_employee_data], columns=feature_columns)

    categorical_mappings = {
        'BusinessTravel': ['Non-Travel', 'Travel_Frequently', 'Travel_Rarely'],
        'Department': DEPARTMENTS,
        'EducationField': ['Human Resources', 'Life Sciences', 'Marketing', 'Medical', 'Other', 'Technical Degree'],
        'Gender': GENDERS,
        'JobRole': JOB_ROLES,
        'MaritalStatus': MARITAL_STATUSES,
        'OverTime': OVERTIME_OPTIONS
    }

    le = LabelEncoder()
    for col in input_df.select_dtypes(include=['object']).columns:
        le.fit(categorical_mappings[col])
        input_df[col] = le.transform(input_df[col])

    input_scaled = scaler.transform(input_df)
    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0]

    print("\n🔮 Attrition Prediction Results:")
    print("-" * 35)
    if prediction == 1:
        print("⚠️ Alert: High Risk! Employee is likely to LEAVE.")
        print(f"📊 Turnover Probability: {probabilities[1]:.2%}")
    else:
        print("✅ Secure: Low Risk. Employee is likely to STAY.")
        print(f"📊 Retention Confidence: {probabilities[0]:.2%}")
    print("-" * 35)


if __name__ == "__main__":
    essentials = collect_essentials()
    full_profile = derive_full_profile(essentials)
    predict_attrition(full_profile)