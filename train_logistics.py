import warnings
import numpy as np 
import pandas as pd 
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler	
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

warnings.filterwarnings('ignore')

def train_production_model():
    csv_file = "data.csv" 
    target_column = "Attrition" 
    
    print(f"🔄 Loading dataset: {csv_file}...")
    df = pd.read_csv(csv_file)

    print("🛠️ Cleaning and preprocessing data...")
    # Drop columns that provide no variance or predictive utility
    cols_to_drop = ['EmployeeCount', 'EmployeeNumber', 'Over18', 'StandardHours']
    cols_to_drop = [c for c in cols_to_drop if c in df.columns]
    df = df.drop(columns=cols_to_drop)

    # Separate features and target
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Convert text features to numeric categories
    le = LabelEncoder()
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = le.fit_transform(X[col])

    # Safely force-convert target labels to 1/0 numbers
    y = y.map({'Yes': 1, 'No': 0})

    # Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale numeric features to maintain balanced weightings
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Train our winning standalone Logistic Regression model
    print("🚀 Training the production Logistic Regression model...")
    model = LogisticRegression()
    model.fit(X_train, y_train)

    # Evaluate performance
    y_pred = model.predict(X_test)
    print(f"\n✅ Production Model Accuracy: {accuracy_score(y_test, y_pred):.2%}")
    
    print("\n📊 Detailed Classification Report:")
    print(classification_report(y_test, y_pred))
    
    print("\n📦 Confusion Matrix (Stayed vs Left):")
    print(confusion_matrix(y_test, y_pred))

    # Save the architecture and formatting configurations
    print("\n💾 Archiving model and data scale weights...")
    joblib.dump(model, 'attrition_logistic_model.pkl')
    joblib.dump(scaler, 'data_scaler.pkl')
    print("✨ Generated files: 'attrition_logistic_model.pkl' and 'data_scaler.pkl'")

if __name__ == "__main__":
    train_production_model()
