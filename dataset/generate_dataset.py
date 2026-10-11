"""
EduPulse AI - Dataset Generation Script
---------------------------------------
Generates a realistic, statistically sound synthetic student academic performance
dataset for development, benchmarking, and machine learning model training.

NOTE: This dataset is SYNTHETIC and generated specifically for development and
academic evaluation. It simulates realistic student behavior patterns based on
higher education academic early-warning research.
"""

import numpy as np
import pandas as pd
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

NUM_STUDENTS = 1200

first_names = [
    "Aarav", "Aditi", "Akash", "Ananya", "Arjun", "Deepak", "Divya", "Gaurav",
    "Ishaan", "Kavya", "Manish", "Meera", "Neha", "Nikhil", "Pooja", "Pranav",
    "Priya", "Rahul", "Rhea", "Rohan", "Sakshi", "Sanjay", "Shreya", "Siddharth",
    "Sneha", "Suraj", "Tanvi", "Varun", "Vikram", "Zara", "Abhishek", "Aishwarya",
    "Aniket", "Bhavna", "Chetan", "Devika", "Harsh", "Karan", "Komal", "Mayank"
]

last_names = [
    "Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Reddy", "Nair",
    "Iyer", "Rao", "Joshi", "Chopra", "Mehta", "Bose", "Das", "Menon",
    "Pandey", "Mishra", "Trivedi", "Deshmukh", "Kulkarni", "Pillai", "Bhat", "Saxena"
]

departments = [
    "Master of Computer Applications",
    "Computer Science and Engineering",
    "Information Technology",
    "Data Science and AI"
]

parental_education_levels = [
    "High School", "Diploma", "Bachelor", "Master", "Doctorate"
]

records = []

for i in range(1, NUM_STUDENTS + 1):
    student_id = f"STU{1000 + i}"
    name = f"{random.choice(first_names)} {random.choice(last_names)}"
    gender = random.choice(["Male", "Female", "Other"])
    age = int(np.random.choice([21, 22, 23, 24, 25], p=[0.25, 0.40, 0.20, 0.10, 0.05]))
    dept = random.choice(departments)
    parent_edu = random.choice(parental_education_levels)
    internet_access = np.random.choice(["Yes", "No"], p=[0.90, 0.10])
    extracurricular = np.random.choice(["Yes", "No"], p=[0.45, 0.55])
    
    # Latent student commitment factor (standard normal distribution)
    latent_ability = np.random.normal(0, 1)
    
    # Study hours per week (mean 16 hours, std 7 hours, bounded between 2 and 40)
    study_hours = np.clip(16 + (latent_ability * 5.5) + np.random.normal(0, 2.5), 2.0, 38.0)
    study_hours = round(float(study_hours), 1)
    
    # Attendance percentage (mean 76%, dependent on commitment)
    attendance = np.clip(76 + (latent_ability * 11) + np.random.normal(0, 7), 35.0, 99.5)
    attendance = round(float(attendance), 1)
    
    # Previous academic marks (percentage in previous degree / semester)
    prev_marks = np.clip(70 + (latent_ability * 10) + np.random.normal(0, 6), 40.0, 98.0)
    prev_marks = round(float(prev_marks), 1)
    
    # Internal assessment marks (0 to 100)
    internal_marks = np.clip(
        (0.40 * prev_marks) + (0.35 * (attendance * 0.9)) + (study_hours * 1.1) + np.random.normal(0, 5),
        20.0, 99.0
    )
    internal_marks = round(float(internal_marks), 1)
    
    # Assignment score (0 to 100)
    assignment_score = np.clip(
        (0.35 * internal_marks) + (0.35 * attendance) + (study_hours * 0.9) + np.random.normal(0, 6),
        25.0, 100.0
    )
    assignment_score = round(float(assignment_score), 1)
    
    # Early Academic Composite Score (EACS) calculated before final semester exams
    # Formula uses only early indicators available mid-semester
    composite_score = (
        (0.35 * internal_marks) +
        (0.25 * attendance) +
        (0.20 * assignment_score) +
        (0.15 * prev_marks) +
        (0.05 * min(study_hours * 3.5, 100.0))
    )
    
    # Realistic noise for academic risk (accounting for unobserved factors)
    noise = np.random.normal(0, 3.5)
    effective_score = composite_score + noise
    
    # Classification rule
    if effective_score < 52.0 or attendance < 60.0 or internal_marks < 40.0:
        risk = "High Risk"
    elif effective_score < 72.0:
        risk = "Medium Risk"
    else:
        risk = "Low Risk"
        
    records.append({
        "student_id": student_id,
        "student_name": name,
        "gender": gender,
        "age": age,
        "department": dept,
        "attendance_percentage": attendance,
        "internal_marks": internal_marks,
        "assignment_score": assignment_score,
        "study_hours_per_week": study_hours,
        "previous_academic_marks": prev_marks,
        "extracurricular_activities": extracurricular,
        "parental_education": parent_edu,
        "internet_access": internet_access,
        "academic_risk": risk
    })

df = pd.DataFrame(records)

# Introduce realistic imperfections for Step 2 (Data Cleaning demonstration)
# 1. Duplicate rows (12 duplicates)
duplicates = df.sample(n=12, random_state=101)
df_with_issues = pd.concat([df, duplicates], ignore_index=True)

# 2. A few missing values (NaN) in numerical features (~20 entries)
np.random.seed(99)
missing_indices_att = np.random.choice(df_with_issues.index, size=8, replace=False)
missing_indices_int = np.random.choice(df_with_issues.index, size=7, replace=False)
missing_indices_study = np.random.choice(df_with_issues.index, size=6, replace=False)

df_with_issues.loc[missing_indices_att, "attendance_percentage"] = np.nan
df_with_issues.loc[missing_indices_int, "internal_marks"] = np.nan
df_with_issues.loc[missing_indices_study, "study_hours_per_week"] = np.nan

# 3. Two outlier / invalid entries to demonstrate range validation
df_with_issues.loc[45, "attendance_percentage"] = 105.0  # Invalid > 100%
df_with_issues.loc[88, "study_hours_per_week"] = -4.0   # Invalid negative value

# Save to dataset/student_data.csv
df_with_issues.to_csv("dataset/student_data.csv", index=False)
print(f"Successfully generated dataset/student_data.csv with {len(df_with_issues)} records.")
