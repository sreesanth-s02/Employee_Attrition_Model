import warnings
import os
import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder

warnings.filterwarnings('ignore')

def predict_attrition(new_employee_data):
    # 1. Verify and Load the Saved Model and Scaler Components
    if not (os.path.exists('attrition_logistic_model.pkl') and os.path.exists('data_scaler.pkl')):
        print("❌ Error: Missing saved model or scaler components. Run train_logistic.py first!")
        return

    model = joblib.load('attrition_logistic_model.pkl')
    scaler = joblib.load('data_scaler.pkl')

    # 2. Load Data Structure Template to match feature shapes
    # (Ensures columns stay aligned in the exact order the model learned them)
    df_template = pd.read_csv("data.csv").drop(columns=['Attrition'], errors='ignore')
    cols_to_drop = ['EmployeeCount', 'EmployeeNumber', 'Over18', 'StandardHours']
    cols_to_drop = [c for c in cols_to_drop if c in df_template.columns]
    df_template = df_template.drop(columns=cols_to_drop)

    # Convert dictionary input to a single-row DataFrame matching training structure
    input_df = pd.DataFrame([new_employee_data], columns=df_template.columns)

    # 3. Match historical text encoding rules using data template properties
    # Re-applies LabelEncoding structure precisely across text features
    df_raw = pd.read_csv("data.csv").drop(columns=['Attrition'], errors='ignore').drop(columns=cols_to_drop)
    le = LabelEncoder()
    for col in input_df.select_dtypes(include=['object']).columns:
        le.fit(df_raw[col])  # Fit on original column options to catch valid text states
        input_df[col] = le.transform(input_df[col])

    # 4. Standardize Data Weights & Execute Evaluation
    input_scaled = scaler.transform(input_df)
    
    prediction = model.predict(input_scaled)[0]
    probabilities = model.predict_proba(input_scaled)[0] # Grab percentage split

    # 5. Output Results
    print("\n🔮 Attrition Prediction Results:")
    print("-" * 35)
    if prediction == 1:
        print(f"⚠️ Alert: High Risk! Employee is likely to LEAVE.")
        print(f"📊 Turnover Probability: {probabilities[1]:.2%}")
    else:
        print(f"✅ Secure: Low Risk. Employee is likely to STAY.")
        print(f"📊 Retention Confidence: {probabilities[0]:.2%}")
    print("-" * 35)

# Example profile simulating a real employee entry
# Customize these values below to test different attrition scenarios!
sample_employee = {
    'Age': 35,
    'BusinessTravel': 'Travel_Rarely',
    'DailyRate': 800,
    'Department': 'Research & Development',
    'DistanceFromHome': 5,
    'Education': 3,
    'EducationField': 'Life Sciences',
    'EnvironmentSatisfaction': 4,
    'Gender': 'Female',
    'HourlyRate': 70,
    'JobInvolvement': 3,
    'JobLevel': 3,
    'JobRole': 'Manager',
    'JobSatisfaction': 4,
    'MaritalStatus': 'Married',
    'MonthlyIncome': 8000,
    'MonthlyRate': 12000,
    'NumCompaniesWorked': 1,
    'OverTime': 'No',
    'PercentSalaryHike': 20,
    'PerformanceRating': 4,
    'RelationshipSatisfaction': 4,
    'StockOptionLevel': 1,
    'TotalWorkingYears': 10,
    'TrainingTimesLastYear': 3,
    'WorkLifeBalance': 3,
    'YearsAtCompany': 8,
    'YearsInCurrentRole': 5,
    'YearsSinceLastPromotion': 2,
    'YearsWithCurrManager': 4
}

if __name__ == "__main__":
    predict_attrition(sample_employee)
