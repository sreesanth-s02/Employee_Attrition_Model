# ==========================================
# 1. IMPORT PACKAGES
# ==========================================
import warnings
import numpy as np 
import pandas as pd 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler	
from sklearn.metrics import accuracy_score

# Machine Learning Algorithms
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier

warnings.filterwarnings('ignore')

def run_ml_pipeline():
    # ==========================================
    # 2. LOAD DATA
    # ==========================================
    # CHANGE THIS: Replace with your actual CSV file name (e.g., "attrition.csv")
    csv_file = "data.csv" 
    target_column = "Attrition" 
    
    print(f"🔄 Loading dataset: {csv_file}...")
    try:
        df = pd.read_csv(csv_file)
    except FileNotFoundError:
        print(f"❌ Error: Could not find '{csv_file}' in the current directory.")
        return

    # ==========================================
    # 3. CLEAN & PREPROCESS DATA
    # ==========================================
    print("🛠️ Droping useless columns & preprocessing data...")
    
    # Drop columns that don't help predict attrition (ids, constants, etc.)
    cols_to_drop = ['EmployeeCount', 'EmployeeNumber', 'Over18', 'StandardHours']
    # Filter out columns that might not exist just in case
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Split into features (X) and target (y)
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Force-convert target 'Yes'/'No' to numeric 1/0
    y = y.map({'Yes': 1, 'No': 0})

    # Convert text features (like Department, BusinessTravel, Gender, OverTime) to numbers
    le = LabelEncoder()
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = le.fit_transform(X[col])

    # Split into Training (80%) and Testing (20%) sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale numeric features so 'MonthlyIncome' doesn't dominate fields like 'EnvironmentSatisfaction'
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # ==========================================
    # 4. DEFINE MODELS TO EVALUATE
    # ==========================================
    models = {
        "Logistic Regression": LogisticRegression(),
        "Random Forest": RandomForestClassifier(random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(random_state=42),
        "XGBoost": XGBClassifier(eval_metric='logloss', random_state=42),
        "Support Vector Machine": SVC(),
        "K-Nearest Neighbors": KNeighborsClassifier(),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "AdaBoost": AdaBoostClassifier(random_state=42),
        "Naive Bayes": GaussianNB()
    }

    # ==========================================
    # 5. TRAIN AND COMPARE ALL MODELS
    # ==========================================
    print("\n🚀 Training models on your HR data...\n" + "-"*45)
    
    best_accuracy = 0
    best_model_name = ""

    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        print(f"| {name:<25} | Accuracy: {acc:.2%}")

        if acc > best_accuracy:
            best_accuracy = acc
            best_model_name = name

    print("-"*45)
    print(f"🏆 Winner: {best_model_name} with {best_accuracy:.2%}\n")

if __name__ == "__main__":
    run_ml_pipeline()
