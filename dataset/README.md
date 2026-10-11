# EduPulse AI - Dataset Documentation

## 1. Dataset Overview & Source
- **Dataset File:** `dataset/student_data.csv`
- **Cleaned Dataset:** `dataset/cleaned_student_data.csv`
- **Data Source Nature:** **Synthetic Benchmark Dataset** designed specifically for research, development, and academic capstone evaluation.
  > **Important Ethical Disclosure:** In strict accordance with academic integrity and privacy regulations (FERPA, DPDP), this dataset contains simulated student records and is **never** presented as real identifiable student records. The statistical distributions, correlations, and feature dynamics are modeled directly on empirical patterns established in higher education learning analytics literature (e.g., UCI Machine Learning Student Performance benchmark and Cortez & Silva educational data modeling).

- **Number of Initial Records:** 1,212 records (1,200 unique students + 12 deliberate duplicate records for data cleaning demonstration).
- **Target Audience:** Master of Computer Applications (MCA) / Computer Science / Data Science students.

---

## 2. Feature Schema & Column Definitions

| Column Name | Data Type | Units / Range | Description & Pedagogical Relevance |
| :--- | :--- | :--- | :--- |
| `student_id` | String | `STU1001` - `STU2200` | Unique anonymized identifier for each student record. |
| `student_name` | String | Text | Student full name (used for user interface & student management). |
| `gender` | Categorical | `Male`, `Female`, `Other` | Self-reported gender identity. |
| `age` | Integer | 21 - 25 years | Age in years (standard postgraduate MCA/MTech cohort). |
| `department` | Categorical | 4 Programs | Academic department (MCA, CSE, IT, Data Science & AI). |
| `attendance_percentage`| Float | 0.0% - 100.0% | Class attendance rate up to mid-semester. Critical early indicator (attendance < 75% or < 60% flags institutional alerts). |
| `internal_marks` | Float | 0.0 - 100.0 | Mid-term internal assessment score. Primary predictor of semester trajectory. |
| `assignment_score` | Float | 0.0 - 100.0 | Cumulative laboratory and continuous assessment submissions score. |
| `study_hours_per_week` | Float | 2.0 - 40.0 hrs | Self-reported weekly independent study and practice hours. |
| `previous_academic_marks`| Float | 40.0 - 100.0% | Prior semester or Undergraduate aggregate percentage / scaled CGPA. |
| `extracurricular_activities`| Categorical| `Yes` / `No` | Active participation in technical clubs, sports, or hackathons. |
| `parental_education` | Categorical | 5 Levels | Highest parental education (`High School`, `Diploma`, `Bachelor`, `Master`, `Doctorate`). |
| `internet_access` | Categorical | `Yes` / `No` | Reliable home or hostel internet connectivity for coding labs. |
| `academic_risk` | Categorical | `Low`, `Medium`, `High` | **Target Label (Multiclass)** indicating intervention urgency. |

---

## 3. Target Label Formulation (Early Warning Principle)

### Why Final Examination Marks are EXCLUDED as Inputs
In an **Early Warning System (EWS)**, predicting academic failure *after* final exam marks are recorded is futile because the semester has already concluded. Therefore, all model input features reflect **formative, mid-semester indicators** recorded before final examinations.

### Early Academic Composite Score (EACS) Formula
$$\text{EACS} = 0.35 \times \text{Internal} + 0.25 \times \text{Attendance} + 0.20 \times \text{Assignment} + 0.15 \times \text{PreviousMarks} + 0.05 \times \min(3.5 \times \text{StudyHours}, 100)$$

### Decision Thresholds:
1. **High Risk (Immediate Academic Hazard):**
   - Condition: $\text{EACS} < 52.0$ OR $\text{Attendance} < 60\%$ OR $\text{Internal} < 40\%$.
   - Meaning: High probability of course detention, debarment from exams, or semester backlog. Requires immediate faculty mentor intervention.
2. **Medium Risk (Borderline / Vulnerable):**
   - Condition: $52.0 \le \text{EACS} < 72.0$.
   - Meaning: Vulnerable academic trajectory. In need of remedial tutorials and study habit realignment.
3. **Low Risk (Satisfactory / Distinction Track):**
   - Condition: $\text{EACS} \ge 72.0$.
   - Meaning: Consistent attendance, solid internal marks, self-sufficient learning pace.
