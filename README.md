# EduPulse AI: Early Warning System for Student Academic Risk Prediction

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-orange.svg)](https://scikit-learn.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-lightgrey.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Database](https://img.shields.io/badge/SQLite-3-003B57.svg)](https://www.sqlite.org/)

**A Complete MCA Capstone Project in Educational Data Mining & Machine Learning**

---

## 📌 1. Project Abstract & Pedagogical Concept

In higher education, academic detention or course failure is typically discovered only after final semester examination marks are declared—when it is too late to intervene. 

**EduPulse AI** is an intelligent **Early Warning System (EWS)** designed to identify students who are academically at risk during the formative mid-semester period. By analyzing early warning signals (such as class attendance rates, continuous internal assessment scores, assignment submissions, and weekly independent study habits), the system classifies students into:
- 🔴 **High Risk:** Severe risk of course debarment or semester detention (immediate counseling and remedial action plan triggered).
- 🟡 **Medium Risk:** Borderline academic trajectory (peer mentoring and study plan realignment required).
- 🟢 **Low Risk:** Satisfactory progress on track for university distinction.

> **💡 Golden Rule of Early Warning Systems (MCA Viva Concept):**  
> **Final examination marks are strictly excluded as inputs.** Early warning systems must predict risk **before** final examinations occur so that faculty mentors have time to stage proactive interventions.

---

## 📂 2. Project Directory Structure

```text
c:\Users\Abishek\Desktop\DS Final Projcets\
│
├── dataset/
│   ├── student_data.csv               # Raw dataset with realistic imperfections (1,212 records)
│   ├── cleaned_student_data.csv       # Preprocessed, imputed & validated dataset (1,201 records)
│   ├── generate_dataset.py            # Reproducible benchmark dataset generator
│   └── README.md                      # Dataset documentation, column schema & target formula
│
├── notebooks/
│   └── edupulse_analysis.ipynb        # Complete 13-section viva-ready Jupyter Notebook
│
├── backend/
│   ├── app.py                         # RESTful Flask API with SQLite integration & CORS
│   ├── clean_data.py                  # Step 2 data cleaning & quality assurance pipeline
│   ├── train_model.py                 # ML training script (Logistic Regression vs. Random Forest)
│   ├── predict.py                     # Real-time single & batch prediction + diagnostic engine
│   ├── edupulse.db                    # SQLite database storing students & prediction history
│   └── requirements.txt               # Backend Python library dependencies
│
├── frontend/
│   ├── package.json                   # React 19 + Vite dependencies
│   ├── vite.config.js                 # Vite development configuration & API proxy
│   ├── index.html                     # Web entry point
│   └── src/
│       ├── main.jsx                   # React root mount
│       ├── App.jsx                    # Primary application shell & tab navigation
│       ├── api.js                     # Centralized API service client
│       ├── index.css                  # Modern UI design system
│       └── components/
│           ├── Dashboard.jsx          # Institutional analytics, KPIs & risk breakdown
│           ├── PredictForm.jsx        # Individual student diagnostic form with Viva Presets
│           ├── StudentDirectory.jsx   # Student cohort management & profile inspector
│           ├── BatchPredict.jsx       # CSV roster upload & bulk evaluation
│           ├── HistoryAudit.jsx       # Chronological prediction log & CSV export
│           └── ModelPerformance.jsx   # Model comparison table, confusion matrices & viva notes
│
├── models/
│   ├── edupulse_best_model.joblib     # Production Random Forest pipeline (preprocessor + model)
│   ├── logistic_regression_pipeline.joblib
│   ├── random_forest_pipeline.joblib
│   ├── model_metrics.json             # Exact accuracy, precision, recall & F1 scores
│   └── feature_metadata.json          # Feature definitions & data contracts
│
├── reports/
│   ├── confusion_matrix.png           # Visual evaluation: Confusion matrix heatmap
│   ├── model_comparison.png           # Comparative bar chart: LR vs Random Forest
│   └── feature_importance.png         # Gini importance: Top influential academic risk factors
│
├── tests/
│   └── test_edupulse.py               # Unit & integration automated test suite (7 tests)
│
├── .gitignore                         # Git exclusion rules
├── .env.example                       # Environment variables template
└── README.md                          # Comprehensive setup & defense guide
```

---

## 🛠️ 3. Windows Installation & Setup Guide

### Prerequisites
- **Python:** 3.10 or higher (Anaconda3 / Miniforge / Python 3.12+).
- **Node.js:** v18 or higher (Node v24 is installed on your machine).

### Option A: Using Your Existing Anaconda Python (Recommended)
On your computer, Python is located at `C:\Users\Abishek\anaconda3\python.exe`.

#### Step 1: Open PowerShell or Command Prompt
Navigate to the project directory:
```powershell
cd "c:\Users\Abishek\Desktop\DS Final Projcets"
```

#### Step 2: Install Backend Dependencies (If not already present)
```powershell
& "C:\Users\Abishek\anaconda3\python.exe" -m pip install -r backend/requirements.txt
```

#### Step 3: Install Frontend Dependencies
On Windows PowerShell, use `npm.cmd` to bypass execution policy restrictions:
```powershell
cd frontend
npm.cmd install
cd ..
```

---

## 🚀 4. How to Run Each Stage of the Project

### Stage 1: Data Cleaning (Step 2)
Run the data cleaning script to inspect raw data, remove duplicates, impute missing values, and produce `dataset/cleaned_student_data.csv`:
```powershell
& "C:\Users\Abishek\anaconda3\python.exe" backend/clean_data.py
```

### Stage 2: Train Machine Learning Models (Steps 4 & 5)
Train Logistic Regression and Random Forest models with zero data leakage, generate evaluation plots, and save production pipelines to `models/`:
```powershell
& "C:\Users\Abishek\anaconda3\python.exe" backend/train_model.py
```

### Stage 3: Test Real-Time Prediction Engine
Verify single student diagnostic inference from the command line:
```powershell
& "C:\Users\Abishek\anaconda3\python.exe" backend/predict.py
```

### Stage 4: Launch Jupyter Notebook (Step 3)
To explore the analysis, data visualizations, and viva markdown explanations interactively:
```powershell
& "C:\Users\Abishek\anaconda3\python.exe" -m notebook notebooks/edupulse_analysis.ipynb
```

### Stage 5: Run Automated Test Suite (Step 8)
Run all 7 unit and integration tests:
```powershell
& "C:\Users\Abishek\anaconda3\python.exe" -m unittest tests/test_edupulse.py
```
*(All 7 tests pass with 100% success).*

---

## 🌐 5. Running the Full Web Application (Step 6)

The web application runs using two terminals simultaneously:

### Terminal 1: Start Flask Backend Server (Port 5000)
```powershell
cd "c:\Users\Abishek\Desktop\DS Final Projcets"
& "C:\Users\Abishek\anaconda3\python.exe" backend/app.py
```
> The backend boots on **`http://127.0.0.1:5000`** and initializes SQLite database `backend/edupulse.db`.

### Terminal 2: Start React Frontend Application (Port 3000)
```powershell
cd "c:\Users\Abishek\Desktop\DS Final Projcets\frontend"
npm.cmd run dev
```
> Open your browser at **`http://localhost:3000`** to access the EduPulse AI portal.

---

## 📊 6. Machine Learning Evaluation & Results (Held-out Test Split)

| Algorithm | Test Accuracy | Weighted Precision | Weighted Recall | Weighted F1-Score |
| :--- | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 90.46% | 90.68% | 90.46% | 90.49% |
| **Random Forest Classifier (Selected)** | **90.87%** | **91.14%** | **90.87%** | **90.90%** |

### Why Random Forest Was Selected:
1. **Handling Non-Linear Interactions:** Academic failure is non-linear; a student with 90% internal marks might still fail if attendance drops below 60% due to university debarment rules. Decision tree ensembles naturally capture this interaction.
2. **Superior Minority Recall:** Successfully caught 33 out of 36 actual high-risk students (91.7% class recall).
3. **Robustness to Collinearity:** Tree bagging mitigates multicollinearity between continuous assessment marks and internal marks.

---

## 🎓 7. MCA Capstone Viva Questions & Model Answers

### Q1: What makes this an "Early Warning System" rather than a final grade predictor?
**Answer:** A grade predictor estimates final scores at semester end when nothing can be done. An Early Warning System operates **mid-semester** using formative assessments (attendance %, first internal marks, weekly study hours) to detect declining trajectories early enough to assign remedial tutorials and mentor interventions.

### Q2: How did you prevent Data Leakage between training and testing data?
**Answer:** We encapsulated all feature preprocessing (`StandardScaler` for numerical metrics and `OneHotEncoder` for demographics) inside a Scikit-Learn `Pipeline`. The preprocessor was strictly fitted **only** on `X_train` (80%) and used to transform `X_test` (20%), preventing test distribution information from leaking into model weights.

### Q3: Why is Recall more important than Precision for the "High Risk" class?
**Answer:** In educational risk detection, a **False Negative** (classifying an actually failing student as safe) means a student receives no help and fails or gets detained. A **False Positive** (offering counseling to a student who might have passed) causes minimal harm. Therefore, maximizing High-Risk Recall is crucial.

### Q4: How is Explainability (XAI) implemented in the prediction engine?
**Answer:** Rather than acting as a black box, `backend/predict.py` executes a diagnostic rule engine alongside model inference. It surfaces exact contributing factors (e.g. *"Severe Attendance Deficit: 52% attendance &lt; 75% threshold"*) and pairs them with targeted pedagogical recommendations (e.g. *"Mandatory Academic Counseling"*).

---

## 📜 8. License & Ethical Disclaimer
This project is developed solely for educational and academic evaluation purposes. In adherence to privacy standards (FERPA / DPDP), no identifiable real student data is exposed.
