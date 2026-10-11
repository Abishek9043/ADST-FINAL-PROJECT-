"""
EduPulse AI - Data Cleaning Pipeline (clean_data.py)
===================================================
Author: MCA Student Capstone Team
Project: EduPulse AI - Early Warning System for Student Academic Risk Prediction

Purpose:
--------
This script implements Step 2 of the Machine Learning pipeline.
It performs thorough data quality checks, handles duplicate records,
imputes missing values, validates feature domain constraints, and produces
a verified clean dataset ready for Exploratory Data Analysis (EDA) and model training.

Input:  dataset/student_data.csv
Output: dataset/cleaned_student_data.csv
"""

import os
import pandas as pd
import numpy as np


def load_raw_dataset(filepath: str) -> pd.DataFrame:
    """
    Step 2.1: Loads the student dataset from a CSV file using Pandas.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Dataset file not found at: {filepath}")
    
    df = pd.read_csv(filepath)
    print("=" * 70)
    print(f" [LOAD] Successfully loaded dataset from '{filepath}'")
    print(f" [SHAPE] Initial Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print("=" * 70)
    return df


def inspect_raw_dataset(df: pd.DataFrame) -> dict:
    """
    Step 2.2: Displays preview, column names, data types, missing values, and duplicates.
    """
    print("\n--- 1. FIRST 5 ROWS ---")
    print(df.head())

    print("\n--- 2. COLUMN DATA TYPES ---")
    print(df.dtypes)

    print("\n--- 3. MISSING VALUES PER COLUMN ---")
    missing_series = df.isnull().sum()
    print(missing_series[missing_series > 0])
    total_missing = int(missing_series.sum())
    print(f"Total Missing Cells: {total_missing}")

    print("\n--- 4. DUPLICATE RECORDS ---")
    num_duplicates = int(df.duplicated().sum())
    print(f"Total Duplicate Rows Detected: {num_duplicates}")

    return {
        "initial_rows": len(df),
        "initial_missing": total_missing,
        "initial_duplicates": num_duplicates
    }


def clean_student_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Executes the comprehensive data cleaning workflow:
      1. Removes duplicate records
      2. Validates and rectifies invalid numerical ranges (outliers/erroneous entries)
      3. Imputes missing values using statistical medians/modes
      4. Standardizes data types
    """
    cleaned_df = df.copy()
    stats = {}

    # --- Step 2.3: Remove Duplicates ---
    initial_len = len(cleaned_df)
    cleaned_df = cleaned_df.drop_duplicates()
    duplicates_removed = initial_len - len(cleaned_df)
    stats["duplicates_removed"] = duplicates_removed
    print(f"\n[CLEANING] Removed {duplicates_removed} duplicate records.")

    # --- Step 2.4: Validate Invalid Values and Outliers ---
    # Attendance must logically be between 0.0% and 100.0%
    invalid_att_count = (cleaned_df["attendance_percentage"] > 100.0) | (cleaned_df["attendance_percentage"] < 0.0)
    att_invalids = invalid_att_count.sum()
    if att_invalids > 0:
        print(f"[VALIDATION] Found {att_invalids} out-of-range attendance records. Clipping to [0.0, 100.0].")
        cleaned_df["attendance_percentage"] = cleaned_df["attendance_percentage"].clip(lower=0.0, upper=100.0)

    # Study hours must logically be >= 0.0 and <= 60 hours/week
    invalid_study_count = (cleaned_df["study_hours_per_week"] < 0.0) | (cleaned_df["study_hours_per_week"] > 60.0)
    study_invalids = invalid_study_count.sum()
    if study_invalids > 0:
        print(f"[VALIDATION] Found {study_invalids} invalid study hours values. Correcting negative values.")
        cleaned_df["study_hours_per_week"] = cleaned_df["study_hours_per_week"].clip(lower=0.0, upper=60.0)

    # Marks columns must be within [0, 100]
    marks_cols = ["internal_marks", "assignment_score", "previous_academic_marks"]
    for col in marks_cols:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].clip(lower=0.0, upper=100.0)

    stats["invalid_values_adjusted"] = int(att_invalids + study_invalids)

    # --- Step 2.5: Handle Missing Values ---
    numerical_features = [
        "attendance_percentage",
        "internal_marks",
        "assignment_score",
        "study_hours_per_week",
        "previous_academic_marks",
        "age"
    ]

    for col in numerical_features:
        if col in cleaned_df.columns and cleaned_df[col].isnull().sum() > 0:
            median_val = cleaned_df[col].median()
            cleaned_df[col] = cleaned_df[col].fillna(round(median_val, 1))
            print(f"[IMPUTATION] Imputed missing values in '{col}' with median: {median_val:.1f}")

    categorical_features = [
        "gender", "department", "extracurricular_activities",
        "parental_education", "internet_access"
    ]

    for col in categorical_features:
        if col in cleaned_df.columns and cleaned_df[col].isnull().sum() > 0:
            mode_val = cleaned_df[col].mode()[0]
            cleaned_df[col] = cleaned_df[col].fillna(mode_val)
            print(f"[IMPUTATION] Imputed missing values in '{col}' with mode: {mode_val}")

    # --- Step 2.6: Convert / Standardize Data Types ---
    if "age" in cleaned_df.columns:
        cleaned_df["age"] = cleaned_df["age"].astype(int)
    for col in ["attendance_percentage", "internal_marks", "assignment_score", "study_hours_per_week", "previous_academic_marks"]:
        if col in cleaned_df.columns:
            cleaned_df[col] = cleaned_df[col].astype(float).round(1)

    # Ensure Student IDs are unique and clean
    cleaned_df = cleaned_df.reset_index(drop=True)

    stats["final_rows"] = len(cleaned_df)
    stats["final_missing"] = int(cleaned_df.isnull().sum().sum())

    return cleaned_df, stats


def print_summary(before_info: dict, after_stats: dict):
    """
    Prints a clear before-and-after comparison report.
    """
    print("\n" + "=" * 70)
    print("        EDUPULSE AI: DATA CLEANING SUMMARY REPORT (MCA VIVA)")
    print("=" * 70)
    print(f" Initial Total Records:        {before_info['initial_rows']}")
    print(f" Duplicate Records Removed:    {after_stats['duplicates_removed']}")
    print(f" Outliers / Invalid Corrected: {after_stats['invalid_values_adjusted']}")
    print(f" Missing Cells Imputed:        {before_info['initial_missing']}")
    print(f" Final Cleaned Records:        {after_stats['final_rows']}")
    print(f" Remaining Missing Values:     {after_stats['final_missing']}")
    print(" Status:                       READY FOR EDA & MACHINE LEARNING")
    print("=" * 70 + "\n")


def main():
    raw_path = os.path.join("dataset", "student_data.csv")
    cleaned_path = os.path.join("dataset", "cleaned_student_data.csv")

    # 1. Load data
    df = load_raw_dataset(raw_path)

    # 2. Inspect raw data
    before_info = inspect_raw_dataset(df)

    # 3. Clean dataset
    cleaned_df, after_stats = clean_student_data(df)

    # 4. Save cleaned dataset
    cleaned_df.to_csv(cleaned_path, index=False)
    print(f"[SAVED] Cleaned dataset successfully saved to '{cleaned_path}'")

    # 5. Print before-and-after summary
    print_summary(before_info, after_stats)


if __name__ == "__main__":
    main()
