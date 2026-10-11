"""
EduPulse AI - Machine Learning Model Training Pipeline (train_model.py)
========================================================================
Author: MCA Student Capstone Team
Project: EduPulse AI - Early Warning System for Student Academic Risk Prediction

Purpose:
--------
Trains and benchmarks multiple machine learning algorithms (Logistic Regression
and Random Forest) to forecast student academic risk (Low Risk, Medium Risk, High Risk).
Strictly prevents data leakage by encapsulating feature scaling and encoding
inside a Scikit-Learn Pipeline fitted exclusively on the training split.

Outputs:
--------
- models/edupulse_best_model.joblib (Production Pipeline)
- models/logistic_regression_pipeline.joblib
- models/random_forest_pipeline.joblib
- models/model_metrics.json (Accuracy, Precision, Recall, F1, Confusion Matrix)
- models/feature_metadata.json (Feature definitions for inference API)
- reports/confusion_matrix.png
- reports/feature_importance.png
- reports/model_comparison.png
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend for server/CLI environments
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

# Ensure output directories exist
os.makedirs("models", exist_ok=True)
os.makedirs("reports", exist_ok=True)

DATA_PATH = os.path.join("dataset", "cleaned_student_data.csv")
TARGET_COLUMN = "academic_risk"

# Define predictor features available BEFORE final semester exams
NUMERICAL_FEATURES = [
    "attendance_percentage",
    "internal_marks",
    "assignment_score",
    "study_hours_per_week",
    "previous_academic_marks",
    "age"
]

CATEGORICAL_FEATURES = [
    "gender",
    "department",
    "extracurricular_activities",
    "parental_education",
    "internet_access"
]

ALL_FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
CLASS_LABELS = ["High Risk", "Medium Risk", "Low Risk"]


def load_dataset(filepath: str) -> pd.DataFrame:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Cleaned dataset not found at {filepath}. Run clean_data.py first.")
    df = pd.read_csv(filepath)
    print(f"[DATA] Loaded {len(df)} records from '{filepath}'.")
    return df


def build_preprocessor() -> ColumnTransformer:
    """
    Constructs a column transformer for numerical scaling and categorical one-hot encoding.
    Ensures zero data leakage as it is fit strictly on training splits.
    """
    numeric_transformer = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    return preprocessor


def evaluate_pipeline(name: str, pipeline: Pipeline, X_train, y_train, X_test, y_test) -> dict:
    """
    Evaluates a trained model pipeline on both training and held-out test splits.
    """
    pipeline.fit(X_train, y_train)

    # Predictions
    y_pred_train = pipeline.predict(X_train)
    y_pred_test = pipeline.predict(X_test)
    y_prob_test = pipeline.predict_proba(X_test)

    # Metrics
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)

    precision_macro = precision_score(y_test, y_pred_test, average="macro", zero_division=0)
    precision_weighted = precision_score(y_test, y_pred_test, average="weighted", zero_division=0)

    recall_macro = recall_score(y_test, y_pred_test, average="macro", zero_division=0)
    recall_weighted = recall_score(y_test, y_pred_test, average="weighted", zero_division=0)

    f1_macro = f1_score(y_test, y_pred_test, average="macro", zero_division=0)
    f1_weighted = f1_score(y_test, y_pred_test, average="weighted", zero_division=0)

    cm = confusion_matrix(y_test, y_pred_test, labels=CLASS_LABELS)
    report_dict = classification_report(y_test, y_pred_test, target_names=CLASS_LABELS, output_dict=True, zero_division=0)

    print(f"\n==================== {name.upper()} RESULTS ====================")
    print(f" Train Accuracy:     {train_acc * 100:.2f}%")
    print(f" Test Accuracy:      {test_acc * 100:.2f}%")
    print(f" Precision (Weighted): {precision_weighted * 100:.2f}%")
    print(f" Recall (Weighted):    {recall_weighted * 100:.2f}%")
    print(f" F1-Score (Weighted):  {f1_weighted * 100:.2f}%")
    print(f" Precision (Macro):    {precision_macro * 100:.2f}%")
    print(f" Recall (Macro):       {recall_macro * 100:.2f}%")
    print(f" F1-Score (Macro):     {f1_macro * 100:.2f}%")
    print("\nConfusion Matrix (Rows: Actual, Columns: Predicted):")
    print(f"Labels: {CLASS_LABELS}")
    print(cm)
    print("==================================================================")

    return {
        "model_name": name,
        "train_accuracy": round(float(train_acc), 4),
        "test_accuracy": round(float(test_acc), 4),
        "precision_macro": round(float(precision_macro), 4),
        "precision_weighted": round(float(precision_weighted), 4),
        "recall_macro": round(float(recall_macro), 4),
        "recall_weighted": round(float(recall_weighted), 4),
        "f1_macro": round(float(f1_macro), 4),
        "f1_weighted": round(float(f1_weighted), 4),
        "confusion_matrix": cm.tolist(),
        "classification_report": report_dict,
        "classes": CLASS_LABELS
    }


def generate_evaluation_plots(metrics_lr, metrics_rf, rf_pipeline, preprocessor):
    """
    Generates academic publication-grade visual evaluation charts:
      1. Confusion matrices for both models
      2. Feature importance bar chart for Random Forest
      3. Side-by-side performance comparison
    """
    sns.set_theme(style="whitegrid")

    # 1. Confusion Matrix Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    cm_rf = np.array(metrics_rf["confusion_matrix"])
    cm_lr = np.array(metrics_lr["confusion_matrix"])

    sns.heatmap(cm_lr, annot=True, fmt="d", cmap="Blues", ax=axes[0],
                xticklabels=CLASS_LABELS, yticklabels=CLASS_LABELS)
    axes[0].set_title(f"Logistic Regression (Accuracy: {metrics_lr['test_accuracy']*100:.1f}%)", fontsize=12, fontweight="bold")
    axes[0].set_xlabel("Predicted Label")
    axes[0].set_ylabel("Actual Label")

    sns.heatmap(cm_rf, annot=True, fmt="d", cmap="Greens", ax=axes[1],
                xticklabels=CLASS_LABELS, yticklabels=CLASS_LABELS)
    axes[1].set_title(f"Random Forest (Accuracy: {metrics_rf['test_accuracy']*100:.1f}%)", fontsize=12, fontweight="bold")
    axes[1].set_xlabel("Predicted Label")
    axes[1].set_ylabel("Actual Label")

    plt.tight_layout()
    cm_path = os.path.join("reports", "confusion_matrix.png")
    plt.savefig(cm_path, dpi=200)
    plt.close()
    print(f"[REPORTS] Saved confusion matrix chart to '{cm_path}'.")

    # 2. Model Comparison Bar Chart
    fig, ax = plt.subplots(figsize=(10, 5))
    metrics_names = ["Accuracy", "Precision", "Recall", "F1-Score"]
    lr_vals = [metrics_lr["test_accuracy"] * 100, metrics_lr["precision_weighted"] * 100,
               metrics_lr["recall_weighted"] * 100, metrics_lr["f1_weighted"] * 100]
    rf_vals = [metrics_rf["test_accuracy"] * 100, metrics_rf["precision_weighted"] * 100,
               metrics_rf["recall_weighted"] * 100, metrics_rf["f1_weighted"] * 100]

    x = np.arange(len(metrics_names))
    width = 0.35

    rects1 = ax.bar(x - width/2, lr_vals, width, label='Logistic Regression', color='#4A90E2')
    rects2 = ax.bar(x + width/2, rf_vals, width, label='Random Forest', color='#2ECC71')

    ax.set_ylabel('Score (%)', fontsize=12)
    ax.set_title('Model Performance Benchmark: Logistic Regression vs Random Forest', fontsize=13, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(metrics_names, fontsize=11)
    ax.set_ylim(0, 105)
    ax.legend(loc='lower right')

    for rect in rects1 + rects2:
        height = rect.get_height()
        ax.annotate(f'{height:.1f}%',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    comp_path = os.path.join("reports", "model_comparison.png")
    plt.savefig(comp_path, dpi=200)
    plt.close()
    print(f"[REPORTS] Saved model comparison chart to '{comp_path}'.")

    # 3. Random Forest Feature Importance Chart
    try:
        classifier = rf_pipeline.named_steps["classifier"]
        feature_encoder = rf_pipeline.named_steps["preprocessor"].named_transformers_["cat"].named_steps["encoder"]
        cat_encoded_names = list(feature_encoder.get_feature_names_out(CATEGORICAL_FEATURES))
        all_feature_names = NUMERICAL_FEATURES + cat_encoded_names

        importances = classifier.feature_importances_
        feature_imp_df = pd.DataFrame({
            "feature": all_feature_names,
            "importance": importances
        }).sort_values("importance", ascending=False).head(10)

        plt.figure(figsize=(10, 5))
        sns.barplot(x="importance", y="feature", data=feature_imp_df, palette="viridis")
        plt.title("Top 10 Most Influential Risk Factors (Random Forest)", fontsize=13, fontweight='bold')
        plt.xlabel("Gini Feature Importance")
        plt.ylabel("Academic & Demographic Feature")
        plt.tight_layout()
        imp_path = os.path.join("reports", "feature_importance.png")
        plt.savefig(imp_path, dpi=200)
        plt.close()
        print(f"[REPORTS] Saved feature importance chart to '{imp_path}'.")
        return feature_imp_df.to_dict(orient="records")
    except Exception as e:
        print(f"[WARNING] Feature importance extraction note: {e}")
        return []


def main():
    print("=" * 70)
    print("      EDUPULSE AI: MACHINE LEARNING MODEL TRAINING PIPELINE")
    print("=" * 70)

    # 1. Load Cleaned Dataset
    df = load_dataset(DATA_PATH)

    # 2. Features and Target
    X = df[ALL_FEATURES]
    y = df[TARGET_COLUMN]

    # Verify class distribution
    print("\n[TARGET DISTRIBUTION]")
    print(y.value_counts())

    # 3. Train-Test Split (Stratified to maintain class ratios)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.20,
        random_state=42,
        stratify=y
    )
    print(f"\n[SPLIT] Training Set: {len(X_train)} samples | Test Set: {len(X_test)} samples")

    # 4. Pipeline Definition - Model 1: Logistic Regression
    preprocessor_lr = build_preprocessor()
    lr_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor_lr),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42, solver="lbfgs"))
    ])

    # 5. Pipeline Definition - Model 2: Random Forest
    preprocessor_rf = build_preprocessor()
    rf_pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor_rf),
        ("classifier", RandomForestClassifier(n_estimators=120, max_depth=10, min_samples_split=4, random_state=42))
    ])

    # 6. Model Training & Evaluation
    metrics_lr = evaluate_pipeline("Logistic Regression", lr_pipeline, X_train, y_train, X_test, y_test)
    metrics_rf = evaluate_pipeline("Random Forest", rf_pipeline, X_train, y_train, X_test, y_test)

    # 7. Model Selection (Compare based on Weighted F1-score & Test Accuracy)
    if metrics_rf["f1_weighted"] >= metrics_lr["f1_weighted"]:
        best_model_name = "Random Forest"
        best_pipeline = rf_pipeline
        best_metrics = metrics_rf
    else:
        best_model_name = "Logistic Regression"
        best_pipeline = lr_pipeline
        best_metrics = metrics_lr

    print(f"\n[CHOSEN MODEL] >>> {best_model_name} selected as best production model! <<<")

    # 8. Save Models and Pipelines
    best_model_path = os.path.join("models", "edupulse_best_model.joblib")
    lr_model_path = os.path.join("models", "logistic_regression_pipeline.joblib")
    rf_model_path = os.path.join("models", "random_forest_pipeline.joblib")

    joblib.dump(best_pipeline, best_model_path)
    joblib.dump(lr_pipeline, lr_model_path)
    joblib.dump(rf_pipeline, rf_model_path)
    print(f"[SAVED] Production model pipeline saved to '{best_model_path}'.")

    # 9. Generate and Save Reports & Visualizations
    top_features = generate_evaluation_plots(metrics_lr, metrics_rf, rf_pipeline, preprocessor_rf)

    # 10. Save Metrics & Metadata JSON
    metrics_payload = {
        "best_model": best_model_name,
        "models": {
            "logistic_regression": metrics_lr,
            "random_forest": metrics_rf
        },
        "top_features": top_features,
        "class_labels": CLASS_LABELS
    }
    with open(os.path.join("models", "model_metrics.json"), "w") as f:
        json.dump(metrics_payload, f, indent=4)

    metadata_payload = {
        "features": ALL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "class_labels": CLASS_LABELS,
        "model_file": "models/edupulse_best_model.joblib"
    }
    with open(os.path.join("models", "feature_metadata.json"), "w") as f:
        json.dump(metadata_payload, f, indent=4)

    print(f"[SAVED] Model metrics saved to 'models/model_metrics.json'.")
    print(f"[SAVED] Feature metadata saved to 'models/feature_metadata.json'.")
    print("\nTraining completed successfully! Ready for inference and web API integration.")


if __name__ == "__main__":
    main()
