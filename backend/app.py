"""
EduPulse AI - RESTful Backend API (app.py)
==========================================
Author: MCA Student Capstone Team
Project: EduPulse AI - Early Warning System for Student Academic Risk Prediction

Key Capabilities:
  - SQLite Database integration for Student Records and Prediction History
  - Real-time ML Inference with Scikit-learn Pipeline
  - Batch CSV Inference & Automated Risk Diagnostics
  - Dashboard Analytics & Risk Distribution Metrics
  - CSV Exporting for Academic Faculty Reports
  - Built-in CORS support
"""

import os
import sys
import json
import sqlite3
import io
import csv
from datetime import datetime
from flask import Flask, request, jsonify, send_file, Response

# Add current directory to path so predict.py is discoverable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from predict import predict_single, predict_batch, identify_risk_factors, generate_recommendations

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
DB_PATH = os.path.join(BASE_DIR, "edupulse.db")
METRICS_PATH = os.path.join(PROJECT_ROOT, "models", "model_metrics.json")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")


# --- CORS Middleware ---
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# --- Database Initialization & Utilities ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """
    Initializes SQLite tables for students and prediction logs,
    and seeds sample records from cleaned_student_data.csv if empty.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table 1: Students
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT UNIQUE NOT NULL,
        student_name TEXT NOT NULL,
        gender TEXT,
        age INTEGER,
        department TEXT,
        attendance_percentage REAL,
        internal_marks REAL,
        assignment_score REAL,
        study_hours_per_week REAL,
        previous_academic_marks REAL,
        extracurricular_activities TEXT,
        parental_education TEXT,
        internet_access TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # Table 2: Prediction History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT NOT NULL,
        student_name TEXT NOT NULL,
        predicted_risk TEXT NOT NULL,
        confidence_percentage REAL NOT NULL,
        prob_high REAL,
        prob_medium REAL,
        prob_low REAL,
        risk_factors_json TEXT,
        recommendations_json TEXT,
        features_json TEXT,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()

    # Seed initial records if empty
    cursor.execute("SELECT COUNT(*) FROM students;")
    count = cursor.fetchone()[0]
    if count == 0:
        cleaned_csv_path = os.path.join(PROJECT_ROOT, "dataset", "cleaned_student_data.csv")
        if os.path.exists(cleaned_csv_path):
            print("[DB] Seeding initial student records from cleaned_student_data.csv...")
            try:
                import pandas as pd
                df = pd.read_csv(cleaned_csv_path).head(60)
                now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for _, row in df.iterrows():
                    cursor.execute("""
                    INSERT OR IGNORE INTO students (
                        student_id, student_name, gender, age, department,
                        attendance_percentage, internal_marks, assignment_score,
                        study_hours_per_week, previous_academic_marks,
                        extracurricular_activities, parental_education, internet_access, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row["student_id"]), str(row["student_name"]), str(row["gender"]),
                        int(row["age"]), str(row["department"]), float(row["attendance_percentage"]),
                        float(row["internal_marks"]), float(row["assignment_score"]),
                        float(row["study_hours_per_week"]), float(row["previous_academic_marks"]),
                        str(row["extracurricular_activities"]), str(row["parental_education"]),
                        str(row["internet_access"]), now_str
                    ))
                    # Also log the initial baseline prediction
                    features_dict = row.to_dict()
                    factors = identify_risk_factors(features_dict)
                    recs = generate_recommendations(str(row["academic_risk"]), factors)
                    cursor.execute("""
                    INSERT INTO predictions (
                        student_id, student_name, predicted_risk, confidence_percentage,
                        prob_high, prob_medium, prob_low,
                        risk_factors_json, recommendations_json, features_json, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        str(row["student_id"]), str(row["student_name"]), str(row["academic_risk"]),
                        92.5, 0.0, 0.0, 0.0,
                        json.dumps(factors), json.dumps(recs), json.dumps(features_dict), now_str
                    ))
                conn.commit()
                print(f"[DB] Successfully seeded {len(df)} initial student and prediction records.")
            except Exception as e:
                print(f"[DB] Seeding note: {e}")

    conn.close()


# --- API Routes ---

@app.route("/api/health", methods=["GET"])
def health_check():
    """Health & system status check."""
    return jsonify({
        "status": "online",
        "service": "EduPulse AI Engine",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })


@app.route("/api/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    """
    Returns aggregated KPIs, risk breakdown, and performance averages for the faculty dashboard.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    total_students = cursor.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_predictions = cursor.execute("SELECT COUNT(*) FROM predictions").fetchone()[0]

    # Academic averages
    avg_row = cursor.execute("""
        SELECT 
            AVG(attendance_percentage), 
            AVG(internal_marks), 
            AVG(assignment_score),
            AVG(study_hours_per_week)
        FROM students
    """).fetchone()

    avg_att = round(float(avg_row[0] or 0), 1)
    avg_internal = round(float(avg_row[1] or 0), 1)
    avg_assignment = round(float(avg_row[2] or 0), 1)
    avg_study = round(float(avg_row[3] or 0), 1)

    # Risk distribution from latest prediction of each student
    cursor.execute("""
        SELECT p.predicted_risk, COUNT(p.id)
        FROM predictions p
        INNER JOIN (
            SELECT student_id, MAX(id) as max_id
            FROM predictions
            GROUP BY student_id
        ) latest ON p.id = latest.max_id
        GROUP BY p.predicted_risk
    """)
    risk_rows = cursor.fetchall()

    risk_counts = {"High Risk": 0, "Medium Risk": 0, "Low Risk": 0}
    for row in risk_rows:
        if row[0] in risk_counts:
            risk_counts[row[0]] = row[1]

    # Department breakdown
    cursor.execute("SELECT department, COUNT(*) FROM students GROUP BY department")
    dept_rows = cursor.fetchall()
    dept_breakdown = {row[0]: row[1] for row in dept_rows}

    # Recent 6 predictions
    cursor.execute("""
        SELECT id, student_id, student_name, predicted_risk, confidence_percentage, created_at
        FROM predictions
        ORDER BY id DESC LIMIT 6
    """)
    recent_preds = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        "total_students": total_students,
        "total_predictions": total_predictions,
        "averages": {
            "attendance": avg_att,
            "internal_marks": avg_internal,
            "assignment_score": avg_assignment,
            "study_hours": avg_study
        },
        "risk_distribution": risk_counts,
        "department_distribution": dept_breakdown,
        "recent_predictions": recent_preds
    })


@app.route("/api/students", methods=["GET", "POST"])
def handle_students():
    """
    GET: List all students (supports search query '?q=')
    POST: Register a new student
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        data = request.get_json() or {}
        required = ["student_id", "student_name", "attendance_percentage", "internal_marks"]
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        try:
            cursor.execute("""
            INSERT INTO students (
                student_id, student_name, gender, age, department,
                attendance_percentage, internal_marks, assignment_score,
                study_hours_per_week, previous_academic_marks,
                extracurricular_activities, parental_education, internet_access, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["student_id"],
                data["student_name"],
                data.get("gender", "Male"),
                int(data.get("age", 22)),
                data.get("department", "Master of Computer Applications"),
                float(data["attendance_percentage"]),
                float(data["internal_marks"]),
                float(data.get("assignment_score", 70.0)),
                float(data.get("study_hours_per_week", 15.0)),
                float(data.get("previous_academic_marks", 70.0)),
                data.get("extracurricular_activities", "No"),
                data.get("parental_education", "Bachelor"),
                data.get("internet_access", "Yes"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            return jsonify({"message": "Student successfully registered", "id": new_id}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({"error": f"Student ID '{data['student_id']}' already exists."}), 409
        except Exception as e:
            conn.close()
            return jsonify({"error": str(e)}), 500

    else:
        # GET
        query = request.args.get("q", "").strip()
        if query:
            cursor.execute("""
                SELECT * FROM students 
                WHERE student_name LIKE ? OR student_id LIKE ? OR department LIKE ?
                ORDER BY id DESC
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
        else:
            cursor.execute("SELECT * FROM students ORDER BY id DESC")
        
        students = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify(students)


@app.route("/api/students/<student_id>", methods=["GET", "DELETE"])
def handle_single_student(student_id):
    """
    GET: Retrieve specific student profile and their past predictions
    DELETE: Remove student record
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == "DELETE":
        cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM predictions WHERE student_id = ?", (student_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": f"Student '{student_id}' deleted."})

    # GET
    student = cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    if not student:
        conn.close()
        return jsonify({"error": "Student not found"}), 404

    preds = cursor.execute("""
        SELECT * FROM predictions WHERE student_id = ? ORDER BY id DESC
    """, (student_id,)).fetchall()

    student_dict = dict(student)
    pred_list = []
    for p in preds:
        item = dict(p)
        item["risk_factors"] = json.loads(item["risk_factors_json"]) if item["risk_factors_json"] else []
        item["recommendations"] = json.loads(item["recommendations_json"]) if item["recommendations_json"] else []
        pred_list.append(item)

    conn.close()
    return jsonify({
        "student": student_dict,
        "predictions": pred_list
    })


@app.route("/api/predict/single", methods=["POST"])
def api_predict_single():
    """
    Receives student academic parameters, executes model inference,
    stores result in database, and returns diagnostic results.
    """
    data = request.get_json() or {}
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Inference using trained pipeline
        result = predict_single(data)

        # Store in SQLite prediction table
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        prob_high = result["class_probabilities"].get("High Risk", 0.0)
        prob_med = result["class_probabilities"].get("Medium Risk", 0.0)
        prob_low = result["class_probabilities"].get("Low Risk", 0.0)

        cursor.execute("""
        INSERT INTO predictions (
            student_id, student_name, predicted_risk, confidence_percentage,
            prob_high, prob_medium, prob_low,
            risk_factors_json, recommendations_json, features_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(result["student_id"]),
            str(result["student_name"]),
            result["predicted_risk"],
            result["confidence_percentage"],
            prob_high, prob_med, prob_low,
            json.dumps(result["risk_factors"]),
            json.dumps(result["recommendations"]),
            json.dumps(result["input_features"]),
            now_str
        ))

        # Also upsert into students table if student_id is provided
        if result["student_id"] and result["student_id"] != "N/A":
            features = result["input_features"]
            cursor.execute("""
            INSERT INTO students (
                student_id, student_name, gender, age, department,
                attendance_percentage, internal_marks, assignment_score,
                study_hours_per_week, previous_academic_marks,
                extracurricular_activities, parental_education, internet_access, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(student_id) DO UPDATE SET
                attendance_percentage=excluded.attendance_percentage,
                internal_marks=excluded.internal_marks,
                assignment_score=excluded.assignment_score,
                study_hours_per_week=excluded.study_hours_per_week,
                previous_academic_marks=excluded.previous_academic_marks
            """, (
                str(result["student_id"]),
                str(result["student_name"]),
                features.get("gender", "Male"),
                int(features.get("age", 22)),
                features.get("department", "Master of Computer Applications"),
                float(features.get("attendance_percentage", 75.0)),
                float(features.get("internal_marks", 65.0)),
                float(features.get("assignment_score", 70.0)),
                float(features.get("study_hours_per_week", 14.0)),
                float(features.get("previous_academic_marks", 68.0)),
                features.get("extracurricular_activities", "No"),
                features.get("parental_education", "Bachelor"),
                features.get("internet_access", "Yes"),
                now_str
            ))

        conn.commit()
        conn.close()

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/predict/batch", methods=["POST"])
def api_predict_batch():
    """
    Accepts CSV file upload, runs batch predictions, records them in the database,
    and returns a summary + detailed results array.
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded in form-data ('file' key expected)"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename provided"}), 400

    try:
        import pandas as pd
        df = pd.read_csv(file)
        if len(df) == 0:
            return jsonify({"error": "Uploaded CSV contains 0 rows"}), 400

        results = predict_batch(df)

        # Bulk save to DB
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        high_count, med_count, low_count = 0, 0, 0
        for r in results:
            risk = r["predicted_risk"]
            if risk == "High Risk": high_count += 1
            elif risk == "Medium Risk": med_count += 1
            else: low_count += 1

            prob_high = r["class_probabilities"].get("High Risk", 0.0)
            prob_med = r["class_probabilities"].get("Medium Risk", 0.0)
            prob_low = r["class_probabilities"].get("Low Risk", 0.0)

            cursor.execute("""
            INSERT INTO predictions (
                student_id, student_name, predicted_risk, confidence_percentage,
                prob_high, prob_medium, prob_low,
                risk_factors_json, recommendations_json, features_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(r["student_id"]), str(r["student_name"]), r["predicted_risk"],
                r["confidence_percentage"], prob_high, prob_med, prob_low,
                json.dumps(r["risk_factors"]), json.dumps(r["recommendations"]),
                json.dumps(r["input_features"]), now_str
            ))

        conn.commit()
        conn.close()

        return jsonify({
            "total_processed": len(results),
            "summary": {
                "High Risk": high_count,
                "Medium Risk": med_count,
                "Low Risk": low_count
            },
            "results": results
        })
    except Exception as e:
        return jsonify({"error": f"Failed to process CSV: {str(e)}"}), 500


@app.route("/api/predictions/history", methods=["GET"])
def get_prediction_history():
    """
    Retrieves logged prediction history with optional search and limit.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    limit = int(request.args.get("limit", 100))
    risk_filter = request.args.get("risk", "").strip()

    if risk_filter:
        cursor.execute("""
            SELECT * FROM predictions 
            WHERE predicted_risk = ?
            ORDER BY id DESC LIMIT ?
        """, (risk_filter, limit))
    else:
        cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,))

    rows = cursor.fetchall()
    results = []
    for r in rows:
        item = dict(r)
        item["risk_factors"] = json.loads(item["risk_factors_json"]) if item["risk_factors_json"] else []
        item["recommendations"] = json.loads(item["recommendations_json"]) if item["recommendations_json"] else []
        results.append(item)

    conn.close()
    return jsonify(results)


@app.route("/api/predictions/export", methods=["GET"])
def export_predictions_csv():
    """
    Generates and downloads a CSV export of all student prediction records for faculty audits.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT student_id, student_name, predicted_risk, confidence_percentage,
               prob_high, prob_medium, prob_low, created_at
        FROM predictions ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Student ID", "Student Name", "Predicted Risk Level", "Confidence (%)",
        "High Risk Probability (%)", "Medium Risk Probability (%)", "Low Risk Probability (%)", "Timestamp"
    ])

    for row in rows:
        writer.writerow(list(row))

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=edupulse_academic_predictions.csv"}
    )


@app.route("/api/model/metrics", methods=["GET"])
def get_model_metrics():
    """
    Returns live model benchmarks, accuracy, confusion matrix, and feature importances.
    """
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            data = json.load(f)
        return jsonify(data)
    else:
        return jsonify({"error": "Model metrics not found. Run backend/train_model.py first."}), 404


@app.route("/api/reports/charts/<path:filename>", methods=["GET"])
def serve_report_chart(filename):
    """
    Serves generated PNG evaluation charts.
    """
    file_path = os.path.join(REPORTS_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, mimetype="image/png")
    return jsonify({"error": "Chart not found"}), 404


# Initialize SQLite on server boot
init_database()

if __name__ == "__main__":
    print("=" * 70)
    print("       EDUPULSE AI BACKEND SERVER STARTING (PORT 5000)")
    print("=" * 70)
    app.run(host="127.0.0.1", port=5000, debug=True)
