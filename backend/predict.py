"""
EduPulse AI - Prediction & Diagnostic Engine (predict.py)
=========================================================
Author: MCA Student Capstone Team
Project: EduPulse AI - Early Warning System for Student Academic Risk Prediction

Purpose:
--------
Loads the trained machine learning pipeline from 'models/edupulse_best_model.joblib'
and generates:
  1. Multiclass Academic Risk Prediction (Low Risk, Medium Risk, High Risk)
  2. Class Probability Distribution (% confidence)
  3. Identified Risk Factors (explainable diagnostic reasons)
  4. Tailored Mentorship & Pedagogical Recommendations

Can be imported as a module by backend/app.py or executed directly from the CLI.
"""

import os
import joblib
import pandas as pd
import numpy as np


MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "edupulse_best_model.joblib")
if not os.path.exists(MODEL_PATH):
    # Fallback to local directory if run from root
    MODEL_PATH = os.path.join("models", "edupulse_best_model.joblib")

# Cache model instance in memory
_CACHED_PIPELINE = None


def get_model(path: str = MODEL_PATH):
    """
    Loads and caches the trained Scikit-Learn Pipeline.
    """
    global _CACHED_PIPELINE
    if _CACHED_PIPELINE is None:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Trained model not found at {path}. Please run backend/train_model.py first.")
        _CACHED_PIPELINE = joblib.load(path)
        print(f"[PREDICT] Model successfully loaded into memory from: {path}")
    return _CACHED_PIPELINE


def identify_risk_factors(student_data: dict) -> list[dict]:
    """
    Diagnostic Rule Engine: Analyzes academic indicators to extract specific root causes.
    Provides explainability so faculty mentors understand WHY the student was flagged.
    """
    factors = []

    att = float(student_data.get("attendance_percentage", 100.0))
    if att < 65.0:
        factors.append({
            "factor": "Severe Attendance Deficit",
            "severity": "Critical",
            "detail": f"Attendance is {att:.1f}%, far below the mandatory 75% institutional threshold."
        })
    elif att < 75.0:
        factors.append({
            "factor": "Attendance Warning",
            "severity": "Moderate",
            "detail": f"Attendance is {att:.1f}%, borderline with the minimum requirement."
        })

    internal = float(student_data.get("internal_marks", 100.0))
    if internal < 40.0:
        factors.append({
            "factor": "Critical Internal Assessment Score",
            "severity": "Critical",
            "detail": f"Internal marks ({internal:.1f}/100) are below passing grade. High risk of course detention."
        })
    elif internal < 55.0:
        factors.append({
            "factor": "Below-Average Internal Performance",
            "severity": "Moderate",
            "detail": f"Internal score ({internal:.1f}/100) reflects conceptual difficulties in core syllabus."
        })

    assignments = float(student_data.get("assignment_score", 100.0))
    if assignments < 50.0:
        factors.append({
            "factor": "Low Continuous Assessment & Lab Submissions",
            "severity": "Moderate",
            "detail": f"Assignment score is {assignments:.1f}/100, indicating missed deadlines or incomplete lab work."
        })

    study_hours = float(student_data.get("study_hours_per_week", 15.0))
    if study_hours < 8.0:
        factors.append({
            "factor": "Insufficient Weekly Independent Study",
            "severity": "Moderate",
            "detail": f"Self-study hours ({study_hours:.1f} hrs/wk) are inadequate for MCA coursework."
        })

    prev_marks = float(student_data.get("previous_academic_marks", 75.0))
    if prev_marks < 55.0:
        factors.append({
            "factor": "Prior Foundation Deficits",
            "severity": "Low",
            "detail": f"Previous aggregate ({prev_marks:.1f}%) suggests foundational prerequisite gaps."
        })

    if not factors:
        factors.append({
            "factor": "Optimal Academic Trajectory",
            "severity": "Positive",
            "detail": "All key performance metrics meet or exceed institutional standards."
        })

    return factors


def generate_recommendations(risk_level: str, risk_factors: list[dict]) -> list[str]:
    """
    Provides pedagogical recommendations tailored to the student's risk category.
    """
    recs = []

    if risk_level == "High Risk":
        recs.append("Mandatory Academic Counseling: Schedule an urgent one-on-one session with the MCA Class Coordinator.")
        recs.append("Remedial Classes: Enroll student in weekend revision bootcamps for foundational subjects.")
        recs.append("Attendance Recovery Plan: Issue official institutional notification to student and parents; require daily sign-ins.")
        recs.append("Assignment Remediation: Provide a 1-week grace window to resubmit incomplete lab projects for partial credit.")
    elif risk_level == "Medium Risk":
        recs.append("Peer Mentoring: Assign an academic peer tutor from the distinction cohort for group study.")
        recs.append("Structured Timetable: Assist student in designing a minimum 15 hrs/week structured self-study timetable.")
        recs.append("Continuous Quizzes: Encourage taking weekly formative LMS self-assessment quizzes to monitor retention.")
        recs.append("Internal Marks Review: Target scoring at least 65+ in the upcoming second internal exam.")
    else:  # Low Risk
        recs.append("Advanced Enrichment: Encourage participating in national hackathons, research paper writing, or coding contests.")
        recs.append("Leadership Opportunities: Invite student to serve as peer mentor or technical club workshop lead.")
        recs.append("Sustained Momentum: Maintain current study rhythm and aim for university distinction/honors ranking.")

    return recs


def predict_single(student_dict: dict, model_path: str = MODEL_PATH) -> dict:
    """
    Predicts academic risk for a single student dictionary.
    """
    pipeline = get_model(model_path)

    # Required feature defaults
    default_record = {
        "attendance_percentage": 75.0,
        "internal_marks": 65.0,
        "assignment_score": 70.0,
        "study_hours_per_week": 14.0,
        "previous_academic_marks": 68.0,
        "age": 22,
        "gender": "Male",
        "department": "Master of Computer Applications",
        "extracurricular_activities": "No",
        "parental_education": "Bachelor",
        "internet_access": "Yes"
    }

    # Merge provided data with defaults
    merged_data = {**default_record, **student_dict}

    # Create 1-row DataFrame
    input_df = pd.DataFrame([merged_data])

    # Model inference
    prediction = pipeline.predict(input_df)[0]
    probabilities = pipeline.predict_proba(input_df)[0]
    classes = list(pipeline.classes_)

    # Map class probabilities
    prob_dict = {cls: round(float(prob) * 100, 2) for cls, prob in zip(classes, probabilities)}

    # Determine confidence score of predicted class
    pred_confidence = prob_dict.get(prediction, round(float(np.max(probabilities)) * 100, 2))

    # Explainability factors and recommendations
    risk_factors = identify_risk_factors(merged_data)
    recommendations = generate_recommendations(prediction, risk_factors)

    return {
        "student_id": student_dict.get("student_id", "N/A"),
        "student_name": student_dict.get("student_name", "Student"),
        "predicted_risk": prediction,
        "confidence_percentage": pred_confidence,
        "class_probabilities": prob_dict,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "input_features": merged_data
    }


def predict_batch(df: pd.DataFrame, model_path: str = MODEL_PATH) -> list[dict]:
    """
    Performs vector batch prediction on a pandas DataFrame.
    """
    pipeline = get_model(model_path)
    results = []

    # Iterate rows and generate diagnostic outputs
    for idx, row in df.iterrows():
        student_data = row.to_dict()
        pred_res = predict_single(student_data, model_path)
        results.append(pred_res)

    return results


def main():
    """
    CLI Demonstration: Test sample predictions for all three risk categories.
    """
    print("=" * 70)
    print("      EDUPULSE AI: REAL-TIME INFERENCE & DIAGNOSTIC DEMONSTRATION")
    print("=" * 70)

    # Test Sample 1: Vulnerable student (expected High Risk)
    sample_high = {
        "student_id": "TEST_001",
        "student_name": "Rohan Verma",
        "attendance_percentage": 48.0,
        "internal_marks": 32.0,
        "assignment_score": 40.0,
        "study_hours_per_week": 4.0,
        "previous_academic_marks": 52.0,
        "age": 23,
        "gender": "Male",
        "department": "Master of Computer Applications",
        "extracurricular_activities": "No",
        "parental_education": "High School",
        "internet_access": "Yes"
    }

    # Test Sample 2: Strong student (expected Low Risk)
    sample_low = {
        "student_id": "TEST_002",
        "student_name": "Ananya Sharma",
        "attendance_percentage": 94.0,
        "internal_marks": 88.0,
        "assignment_score": 92.0,
        "study_hours_per_week": 24.0,
        "previous_academic_marks": 85.0,
        "age": 22,
        "gender": "Female",
        "department": "Master of Computer Applications",
        "extracurricular_activities": "Yes",
        "parental_education": "Master",
        "internet_access": "Yes"
    }

    for sample in [sample_high, sample_low]:
        result = predict_single(sample)
        print(f"\nStudent: {result['student_name']} (ID: {result['student_id']})")
        print(f"Prediction: {result['predicted_risk']} (Confidence: {result['confidence_percentage']}%)")
        print(f"Probabilities: {result['class_probabilities']}")
        print(f"Identified Risk Factors ({len(result['risk_factors'])}):")
        for f in result['risk_factors']:
            print(f"  - [{f.get('severity', 'Note')}] {f['factor']}: {f['detail']}")
        print("Pedagogical Recommendations:")
        for r in result['recommendations']:
            print(f"  * {r}")
        print("-" * 70)


if __name__ == "__main__":
    main()
