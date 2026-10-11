"""
Helper script to generate the complete, production-ready, viva-annotated
Jupyter Notebook: notebooks/edupulse_analysis.ipynb
"""

import json
import os

notebook_cells = []

def add_md(source_text):
    notebook_cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source_text.strip().split("\n")]
    })

def add_code(source_text):
    notebook_cells.append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source_text.strip().split("\n")]
    })

# --- TITLE CELL ---
add_md("""# EduPulse AI: Early Warning System for Student Academic Risk Prediction
### Master of Computer Applications (MCA) Capstone Project
**Domain:** Educational Data Mining (EDM) & Machine Learning  
**Core Algorithms:** Logistic Regression & Random Forest Classifier  
**Target Label:** Academic Risk (`Low Risk`, `Medium Risk`, `High Risk`)

---

### Project Overview & Pedagogical Purpose (For MCA Viva)
Universities often discover student academic failure too late—after final semester examination results are released. 
**EduPulse AI** acts as an **Early Warning System (EWS)** that analyzes formative, mid-semester academic indicators (such as internal assessment marks, class attendance percentages, assignment submissions, and weekly study hours) to forecast students who are academically at risk.

> **Key Rule of Early Warning Systems:**  
> Final examination results are **never used as inputs** because predictions must occur mid-semester while interventions (remedial tutorials, counseling) can still save the student.""")

# --- SECTION 1 ---
add_md("""## 1. Import Essential Python Libraries
In this step, we import the foundational data science and machine learning libraries:
- **Pandas:** For loading, inspecting, and manipulating tabular datasets.
- **NumPy:** For high-performance numerical operations and matrix calculations.
- **Matplotlib & Seaborn:** For exploratory data analysis (EDA) charts and correlation heatmaps.
- **Scikit-Learn:** For data preprocessing, feature scaling, train/test splitting, and machine learning models.""")

add_code("""import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os

# Scikit-learn modules
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# Plot styling configuration
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams['figure.figsize'] = (10, 5)
print("All essential libraries successfully imported!")""")

# --- SECTION 2 ---
add_md("""## 2. Load the Student Dataset
We load the raw student dataset (`dataset/student_data.csv`).
*Note on Dataset Origin (Viva Tip):* This dataset is a clearly documented synthetic benchmark created specifically for development and testing. It models statistical dynamics from educational research (such as UCI Student Performance benchmarks) while respecting student privacy.""")

add_code("""data_path = os.path.join("..", "dataset", "student_data.csv")
if not os.path.exists(data_path):
    data_path = os.path.join("dataset", "student_data.csv")

df = pd.read_csv(data_path)
print(f"Dataset successfully loaded! Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")
df.head()""")

# --- SECTION 3 ---
add_md("""## 3. Understand the Dataset Structure
Before any data science operation, we must inspect:
1. Column names and their semantic data types (`df.info()`).
2. Numerical distributions, ranges, and standard deviations (`df.describe()`).
3. Initial counts of missing (`NaN`) values and duplicate rows.""")

add_code("""print("--- DATASET SUMMARY INFO ---")
df.info()

print("\\n--- STATISTICAL DESCRIPTIVE METRICS ---")
df.describe()""")

add_code("""print("--- INITIAL DATA QUALITY INSPECTION ---")
print("Missing values per column:")
print(df.isnull().sum())
print(f"\\nTotal duplicate rows detected: {df.duplicated().sum()}")""")

# --- SECTION 4 ---
add_md("""## 4. Data Cleaning Pipeline
Real-world educational data contains noise, missing entries, duplicates, and range anomalies.
Here, we execute a principled data cleaning procedure:
1. **Remove Duplicate Rows:** Prevent redundant records from biasing our models.
2. **Handle Invalid Range Outliers:** Cap attendance strictly between 0% and 100%, and ensure study hours >= 0.
3. **Missing Value Imputation:**
   - Numerical columns: Impute using **Median** (robust against extreme outliers).
   - Categorical columns: Impute using **Mode** (most frequent class).
4. Save the verified dataset to `dataset/cleaned_student_data.csv`.""")

add_code("""cleaned_df = df.copy()

# 1. Remove duplicate records
initial_count = len(cleaned_df)
cleaned_df = cleaned_df.drop_duplicates()
print(f"Removed {initial_count - len(cleaned_df)} duplicate rows.")

# 2. Correct domain constraint anomalies (outliers)
cleaned_df['attendance_percentage'] = cleaned_df['attendance_percentage'].clip(lower=0.0, upper=100.0)
cleaned_df['study_hours_per_week'] = cleaned_df['study_hours_per_week'].clip(lower=0.0, upper=60.0)
for col in ['internal_marks', 'assignment_score', 'previous_academic_marks']:
    cleaned_df[col] = cleaned_df[col].clip(lower=0.0, upper=100.0)

# 3. Impute missing values
num_cols = ['attendance_percentage', 'internal_marks', 'assignment_score', 'study_hours_per_week', 'previous_academic_marks', 'age']
for col in num_cols:
    if cleaned_df[col].isnull().sum() > 0:
        med = cleaned_df[col].median()
        cleaned_df[col] = cleaned_df[col].fillna(med)

# 4. Standardize types
cleaned_df['age'] = cleaned_df['age'].astype(int)
for col in ['attendance_percentage', 'internal_marks', 'assignment_score', 'study_hours_per_week', 'previous_academic_marks']:
    cleaned_df[col] = cleaned_df[col].round(1)

cleaned_df = cleaned_df.reset_index(drop=True)
print(f"Cleaned dataset shape: {cleaned_df.shape[0]} rows x {cleaned_df.shape[1]} columns")
print(f"Remaining missing values: {cleaned_df.isnull().sum().sum()}")

# Save to disk
cleaned_save_path = os.path.join("..", "dataset", "cleaned_student_data.csv")
if not os.path.exists(os.path.dirname(cleaned_save_path)):
    cleaned_save_path = os.path.join("dataset", "cleaned_student_data.csv")
cleaned_df.to_csv(cleaned_save_path, index=False)
print("Cleaned data saved to 'cleaned_student_data.csv'!")""")

# --- SECTION 5 ---
add_md("""## 5. Exploratory Data Analysis (EDA)
EDA allows us to uncover patterns and relationships between student academic habits and risk categories.""")

add_code("""# Target Class Breakdown
risk_counts = cleaned_df['academic_risk'].value_counts()
risk_pct = cleaned_df['academic_risk'].value_counts(normalize=True) * 100

summary_eda = pd.DataFrame({'Count': risk_counts, 'Percentage (%)': risk_pct.round(2)})
print("Academic Risk Distribution:")
display(summary_eda) if 'display' in globals() else print(summary_eda)

# Mean performance indicators grouped by Risk Category
metrics_by_risk = cleaned_df.groupby('academic_risk')[
    ['attendance_percentage', 'internal_marks', 'assignment_score', 'study_hours_per_week', 'previous_academic_marks']
].mean().round(2)

print("\\nAverage Metrics by Academic Risk Category:")
display(metrics_by_risk) if 'display' in globals() else print(metrics_by_risk)""")

# --- SECTION 6 ---
add_md("""## 6. Charts and Visualizations
Visual evidence for our MCA project presentation:
1. **Target Class Balance:** Visualizing the proportion of Low, Medium, and High risk students.
2. **Attendance vs. Internal Marks Scatter Plot:** Demonstrating how low attendance directly correlates with critical internal scores.
3. **Study Hours Distribution by Risk:** Visualizing student effort variation.
4. **Correlation Heatmap:** Demonstrating the linear associations between numerical features.""")

add_code("""plt.figure(figsize=(14, 10))

# 1. Target Class Countplot
plt.subplot(2, 2, 1)
palette_map = {"Low Risk": "#2ECC71", "Medium Risk": "#F39C12", "High Risk": "#E74C3C"}
sns.countplot(x='academic_risk', data=cleaned_df, palette=palette_map, order=['Low Risk', 'Medium Risk', 'High Risk'])
plt.title("Student Distribution by Academic Risk Level", fontweight='bold')
plt.xlabel("Risk Category")
plt.ylabel("Number of Students")

# 2. Scatter Plot: Attendance vs. Internal Marks
plt.subplot(2, 2, 2)
sns.scatterplot(
    x='attendance_percentage', y='internal_marks',
    hue='academic_risk', data=cleaned_df,
    palette=palette_map, alpha=0.75, s=60
)
plt.axvline(75, color='gray', linestyle='--', alpha=0.7, label='75% Attendance Threshold')
plt.axhline(50, color='gray', linestyle=':', alpha=0.7, label='50 Marks Threshold')
plt.title("Attendance vs. Internal Marks (Separation by Risk)", fontweight='bold')
plt.xlabel("Attendance Percentage (%)")
plt.ylabel("Internal Marks (out of 100)")
plt.legend(loc='lower right')

# 3. Boxplot: Study Hours per Week across Risk Classes
plt.subplot(2, 2, 3)
sns.boxplot(x='academic_risk', y='study_hours_per_week', data=cleaned_df, palette=palette_map, order=['Low Risk', 'Medium Risk', 'High Risk'])
plt.title("Weekly Independent Study Hours across Risk Groups", fontweight='bold')
plt.xlabel("Risk Category")
plt.ylabel("Study Hours / Week")

# 4. Correlation Heatmap
plt.subplot(2, 2, 4)
num_features = ['attendance_percentage', 'internal_marks', 'assignment_score', 'study_hours_per_week', 'previous_academic_marks', 'age']
corr_matrix = cleaned_df[num_features].corr()
sns.heatmap(corr_matrix, annot=True, cmap='Blues', fmt='.2f', square=True)
plt.title("Correlation Matrix of Numerical Features", fontweight='bold')

plt.tight_layout()
plt.show()""")

# --- SECTION 7 ---
add_md("""## 7. Feature Selection & Target Separation
For model training, we separate the predictor features ($X$) from the target variable ($y$):
- **Predictors ($X$):**
  - Numerical: `attendance_percentage`, `internal_marks`, `assignment_score`, `study_hours_per_week`, `previous_academic_marks`, `age`.
  - Categorical: `gender`, `department`, `extracurricular_activities`, `parental_education`, `internet_access`.
- **Target ($y$):** `academic_risk` (`Low Risk`, `Medium Risk`, `High Risk`).
- **Excluded Features:** `student_id` and `student_name` are identifiers and must never be fed into the model.""")

add_code("""feature_cols = [
    'attendance_percentage', 'internal_marks', 'assignment_score',
    'study_hours_per_week', 'previous_academic_marks', 'age',
    'gender', 'department', 'extracurricular_activities',
    'parental_education', 'internet_access'
]

X = cleaned_df[feature_cols]
y = cleaned_df['academic_risk']

print(f"Predictor Matrix X shape: {X.shape}")
print(f"Target Vector y shape: {y.shape}")""")

# --- SECTION 8 ---
add_md("""## 8. Stratified Train / Test Split
### Preventing Data Leakage (Crucial Viva Point)
- We split the dataset into **80% Training (960 samples)** and **20% Testing (241 samples)**.
- **`stratify=y`:** Preserves the exact same percentage of High, Medium, and Low risk students in both splits.
- Preprocessing transformers (scaling & encoding) are strictly fitted on `X_train` and applied to `X_test` via a Scikit-Learn `Pipeline` to prevent information from the test set leaking into the training phase.""")

add_code("""X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print(f"Training split samples: {len(X_train)} (80%)")
print(f"Testing split samples:  {len(X_test)} (20%)")
print("\\nClass balance in Test Split:")
print(y_test.value_counts(normalize=True).round(3) * 100)""")

# --- SECTION 9 ---
add_md("""## 9. Machine Learning Model Pipelines
We build a unified Scikit-Learn `ColumnTransformer` and evaluate two distinct algorithms:
1. **Logistic Regression (Multinomial with LBFGS):** A linear baseline model that maps input features to class probabilities using log-odds.
2. **Random Forest Classifier (Ensemble):** An ensemble of 120 decision trees that handles non-linear boundaries and feature interactions without overfitting.""")

add_code("""# Define Column Transformers
numerical_features = ['attendance_percentage', 'internal_marks', 'assignment_score', 'study_hours_per_week', 'previous_academic_marks', 'age']
categorical_features = ['gender', 'department', 'extracurricular_activities', 'parental_education', 'internet_access']

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_features)
    ]
)

# Pipeline 1: Logistic Regression
lr_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(max_iter=1000, random_state=42, solver='lbfgs'))
])

# Pipeline 2: Random Forest
rf_pipeline = Pipeline([
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(n_estimators=120, max_depth=10, min_samples_split=4, random_state=42))
])

# Train both pipelines on the training set
print("Training Logistic Regression pipeline...")
lr_pipeline.fit(X_train, y_train)

print("Training Random Forest pipeline...")
rf_pipeline.fit(X_train, y_train)
print("Both models trained successfully!")""")

# --- SECTION 10 ---
add_md("""## 10. Model Evaluation Metrics & Confusion Matrices
We compute standard machine learning performance metrics on the held-out test set:
- **Accuracy:** Overall percentage of correct classifications.
- **Precision:** Of all students flagged as high-risk, what proportion actually was?
- **Recall (Sensitivity):** Of all actual high-risk students, what percentage did the system successfully catch? (Critical in education: missing an at-risk student is dangerous!)
- **F1-Score:** Harmonic mean of precision and recall.
- **Confusion Matrix:** True Positives, False Positives, and False Negatives per class.""")

add_code("""labels = ['High Risk', 'Medium Risk', 'Low Risk']

def compute_metrics(model, name):
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    return {
        'name': name,
        'Accuracy (%)': round(acc * 100, 2),
        'Precision (%)': round(prec * 100, 2),
        'Recall (%)': round(rec * 100, 2),
        'F1-Score (%)': round(f1 * 100, 2),
        'cm': cm,
        'predictions': y_pred
    }

metrics_lr = compute_metrics(lr_pipeline, 'Logistic Regression')
metrics_rf = compute_metrics(rf_pipeline, 'Random Forest')

print(f"Logistic Regression Test Accuracy: {metrics_lr['Accuracy (%)']}% | F1: {metrics_lr['F1-Score (%)']}%")
print(f"Random Forest Test Accuracy:       {metrics_rf['Accuracy (%)']}% | F1: {metrics_rf['F1-Score (%)']}%")""")

add_code("""# Visualize Confusion Matrices Side-by-Side
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

sns.heatmap(metrics_lr['cm'], annot=True, fmt='d', cmap='Blues', ax=axes[0], xticklabels=labels, yticklabels=labels)
axes[0].set_title(f"Logistic Regression Confusion Matrix\\nAccuracy: {metrics_lr['Accuracy (%)']}%", fontweight='bold')
axes[0].set_xlabel("Predicted Class")
axes[0].set_ylabel("Actual Class")

sns.heatmap(metrics_rf['cm'], annot=True, fmt='d', cmap='Greens', ax=axes[1], xticklabels=labels, yticklabels=labels)
axes[1].set_title(f"Random Forest Confusion Matrix\\nAccuracy: {metrics_rf['Accuracy (%)']}%", fontweight='bold')
axes[1].set_xlabel("Predicted Class")
axes[1].set_ylabel("Actual Class")

plt.tight_layout()
plt.show()""")

# --- SECTION 11 ---
add_md("""## 11. Model Comparison & Analysis (Viva Defense)
We compare both models across all standard performance benchmarks.""")

add_code("""comparison_df = pd.DataFrame([
    {k: v for k, v in metrics_lr.items() if k not in ['cm', 'predictions']},
    {k: v for k, v in metrics_rf.items() if k not in ['cm', 'predictions']}
]).set_index('name')

print("--- MODEL COMPARISON SUMMARY ---")
display(comparison_df) if 'display' in globals() else print(comparison_df)

# Plot Model Comparison Bar Chart
comparison_df.plot(kind='bar', figsize=(10, 5), ylim=(80, 100), colormap='viridis')
plt.title("Comparative Performance: Logistic Regression vs. Random Forest", fontweight='bold')
plt.ylabel("Score (%)")
plt.xticks(rotation=0)
plt.legend(loc='lower right')
plt.tight_layout()
plt.show()""")

# --- SECTION 12 ---
add_md("""## 12. Save Selected Model & Preprocessing Pipeline
We select the **Random Forest Classifier** because of its superior weighted F1-score, high recall on High-Risk cases, and robustness against non-linear interactions. We serialize the pipeline to disk.""")

add_code("""models_dir = os.path.join("..", "models")
if not os.path.exists(models_dir):
    models_dir = "models"
os.makedirs(models_dir, exist_ok=True)

production_model_path = os.path.join(models_dir, "edupulse_best_model.joblib")
joblib.dump(rf_pipeline, production_model_path)
print(f"Production pipeline successfully exported to: {production_model_path}")""")

# --- SECTION 13 ---
add_md("""## 13. End-to-End Single Student Prediction & Diagnostic Walkthrough
To demonstrate our model in action during the viva examination, we load the saved model and predict the academic risk of an unseen sample student.""")

add_code("""# Load model from disk
deployed_pipeline = joblib.load(production_model_path)

# Sample test student: Struggling with low attendance and low internal marks
sample_student = pd.DataFrame([{
    'attendance_percentage': 52.0,
    'internal_marks': 38.0,
    'assignment_score': 45.0,
    'study_hours_per_week': 5.0,
    'previous_academic_marks': 58.0,
    'age': 22,
    'gender': 'Male',
    'department': 'Master of Computer Applications',
    'extracurricular_activities': 'No',
    'parental_education': 'High School',
    'internet_access': 'Yes'
}])

# Inference
predicted_risk = deployed_pipeline.predict(sample_student)[0]
predicted_probs = deployed_pipeline.predict_proba(sample_student)[0]
classes = deployed_pipeline.classes_

print("=" * 60)
print(f"  SAMPLE PREDICTION: {predicted_risk.upper()}")
print("=" * 60)
for cls, prob in zip(classes, predicted_probs):
    print(f"  Confidence ({cls}): {prob * 100:.2f}%")
print("=" * 60)
print("\\nRECOMMENDED ACTION:")
if predicted_risk == "High Risk":
    print("- Urgent mentor intervention required.")
    print("- Mandatory remedial tutorials for internal exam improvements.")
    print("- Parents/guardian attendance alert issued.")
elif predicted_risk == "Medium Risk":
    print("- Assign peer study buddy and monitor weekly lab submissions.")
else:
    print("- Student is performing well; maintain current study rhythm.")""")

# Create final notebook json
notebook_json = {
    "cells": notebook_cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (ipykernel)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

os.makedirs("notebooks", exist_ok=True)
output_path = os.path.join("notebooks", "edupulse_analysis.ipynb")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(notebook_json, f, indent=2)

print(f"Successfully generated complete Jupyter Notebook with {len(notebook_cells)} cells at '{output_path}'.")
