"""
EduPulse AI - Comprehensive Automated Test Suite (test_edupulse.py)
===================================================================
Tests data cleaning, model training artifacts, inference engine,
and Flask REST API endpoints.
"""

import os
import sys
import json
import unittest
import pandas as pd
import numpy as np

# Ensure backend modules can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

from clean_data import clean_student_data
from predict import predict_single, predict_batch, get_model
from app import app, init_database


class TestEduPulsePipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize test client and database
        init_database()
        cls.client = app.test_client()

    def test_01_dataset_files_exist(self):
        """Check raw and cleaned dataset files exist."""
        raw_path = os.path.join(PROJECT_ROOT, "dataset", "student_data.csv")
        clean_path = os.path.join(PROJECT_ROOT, "dataset", "cleaned_student_data.csv")

        self.assertTrue(os.path.exists(raw_path), "student_data.csv should exist")
        self.assertTrue(os.path.exists(clean_path), "cleaned_student_data.csv should exist")

        df = pd.read_csv(clean_path)
        self.assertGreater(len(df), 1000, "Cleaned dataset should have > 1,000 records")
        self.assertEqual(df.isnull().sum().sum(), 0, "Cleaned dataset should have 0 missing values")

    def test_02_data_cleaning_logic(self):
        """Test that data cleaning function handles missing values, duplicates, and range anomalies."""
        dirty_data = pd.DataFrame([
            {"student_id": "T1", "attendance_percentage": 110.0, "internal_marks": 40.0, "study_hours_per_week": -5.0, "age": 22},
            {"student_id": "T1", "attendance_percentage": 110.0, "internal_marks": 40.0, "study_hours_per_week": -5.0, "age": 22}, # Duplicate
            {"student_id": "T2", "attendance_percentage": np.nan, "internal_marks": np.nan, "study_hours_per_week": 15.0, "age": 23} # Nulls
        ])
        cleaned, stats = clean_student_data(dirty_data)

        self.assertEqual(stats["duplicates_removed"], 1)
        self.assertLessEqual(cleaned["attendance_percentage"].max(), 100.0)
        self.assertGreaterEqual(cleaned["study_hours_per_week"].min(), 0.0)
        self.assertEqual(cleaned["attendance_percentage"].isnull().sum(), 0)

    def test_03_model_artifacts_and_metrics(self):
        """Verify saved machine learning pipeline and metrics JSON."""
        model_path = os.path.join(PROJECT_ROOT, "models", "edupulse_best_model.joblib")
        metrics_path = os.path.join(PROJECT_ROOT, "models", "model_metrics.json")

        self.assertTrue(os.path.exists(model_path), "Model pipeline joblib file should exist")
        self.assertTrue(os.path.exists(metrics_path), "Model metrics JSON should exist")

        with open(metrics_path, "r") as f:
            metrics = json.load(f)

        self.assertIn("best_model", metrics)
        self.assertIn("logistic_regression", metrics["models"])
        self.assertIn("random_forest", metrics["models"])

        rf_acc = metrics["models"]["random_forest"]["test_accuracy"]
        lr_acc = metrics["models"]["logistic_regression"]["test_accuracy"]

        self.assertGreater(rf_acc, 0.85, "Random Forest test accuracy should exceed 85%")
        self.assertGreater(lr_acc, 0.85, "Logistic Regression test accuracy should exceed 85%")

    def test_04_single_prediction_engine(self):
        """Test real-time prediction and diagnostic recommendations."""
        # Test 1: Vulnerable student -> Expected High Risk
        high_risk_input = {
            "student_id": "TEST_H1",
            "student_name": "Test Student High",
            "attendance_percentage": 45.0,
            "internal_marks": 30.0,
            "assignment_score": 38.0,
            "study_hours_per_week": 3.0,
            "previous_academic_marks": 50.0
        }
        res_high = predict_single(high_risk_input)
        self.assertEqual(res_high["predicted_risk"], "High Risk")
        self.assertGreater(res_high["confidence_percentage"], 60.0)
        self.assertGreater(len(res_high["risk_factors"]), 0)
        self.assertGreater(len(res_high["recommendations"]), 0)

        # Test 2: Distinction student -> Expected Low Risk
        low_risk_input = {
            "student_id": "TEST_L1",
            "student_name": "Test Student Low",
            "attendance_percentage": 95.0,
            "internal_marks": 90.0,
            "assignment_score": 92.0,
            "study_hours_per_week": 25.0,
            "previous_academic_marks": 88.0
        }
        res_low = predict_single(low_risk_input)
        self.assertEqual(res_low["predicted_risk"], "Low Risk")
        self.assertGreater(res_low["confidence_percentage"], 60.0)

    def test_05_batch_prediction_engine(self):
        """Test vectorized batch prediction across a DataFrame."""
        batch_df = pd.DataFrame([
            {"student_id": "B1", "student_name": "B One", "attendance_percentage": 50.0, "internal_marks": 35.0},
            {"student_id": "B2", "student_name": "B Two", "attendance_percentage": 92.0, "internal_marks": 89.0},
            {"student_id": "B3", "student_name": "B Three", "attendance_percentage": 72.0, "internal_marks": 65.0}
        ])
        results = predict_batch(batch_df)
        self.assertEqual(len(results), 3)
        valid_classes = {"High Risk", "Medium Risk", "Low Risk"}
        for r in results:
            self.assertIn(r["predicted_risk"], valid_classes)
            self.assertIn("class_probabilities", r)

    def test_06_flask_health_and_stats_api(self):
        """Test Flask health check and dashboard endpoints."""
        res_health = self.client.get("/api/health")
        self.assertEqual(res_health.status_code, 200)
        self.assertEqual(res_health.get_json()["status"], "online")

        res_stats = self.client.get("/api/dashboard/stats")
        self.assertEqual(res_stats.status_code, 200)
        data = res_stats.get_json()
        self.assertIn("total_students", data)
        self.assertIn("risk_distribution", data)
        self.assertIn("averages", data)

    def test_07_flask_prediction_and_history_api(self):
        """Test Flask predict single, history, and export API endpoints."""
        payload = {
            "student_id": "TEST_API_01",
            "student_name": "API Student",
            "attendance_percentage": 55.0,
            "internal_marks": 38.0,
            "assignment_score": 45.0,
            "study_hours_per_week": 5.0,
            "previous_academic_marks": 52.0
        }
        res_predict = self.client.post("/api/predict/single", json=payload)
        self.assertEqual(res_predict.status_code, 200)
        pred_data = res_predict.get_json()
        self.assertIn("predicted_risk", pred_data)

        # Check that it appears in history
        res_hist = self.client.get("/api/predictions/history")
        self.assertEqual(res_hist.status_code, 200)
        hist_data = res_hist.get_json()
        self.assertGreater(len(hist_data), 0)

        # Test CSV export
        res_export = self.client.get("/api/predictions/export")
        self.assertEqual(res_export.status_code, 200)
        self.assertIn("text/csv", res_export.content_type)


if __name__ == "__main__":
    unittest.main()
