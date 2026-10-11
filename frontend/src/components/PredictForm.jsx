import React, { useState } from 'react';
import { predictSingle } from '../api';

const PRESETS = {
  highRisk: {
    student_id: 'VIVA_DEMO_01',
    student_name: 'Rahul Deshmukh',
    gender: 'Male',
    age: 22,
    department: 'Master of Computer Applications',
    attendance_percentage: 52.0,
    internal_marks: 35.0,
    assignment_score: 42.0,
    study_hours_per_week: 5.0,
    previous_academic_marks: 54.0,
    extracurricular_activities: 'No',
    parental_education: 'High School',
    internet_access: 'Yes'
  },
  mediumRisk: {
    student_id: 'VIVA_DEMO_02',
    student_name: 'Priya Sharma',
    gender: 'Female',
    age: 23,
    department: 'Master of Computer Applications',
    attendance_percentage: 72.0,
    internal_marks: 61.0,
    assignment_score: 64.0,
    study_hours_per_week: 12.0,
    previous_academic_marks: 66.0,
    extracurricular_activities: 'Yes',
    parental_education: 'Bachelor',
    internet_access: 'Yes'
  },
  lowRisk: {
    student_id: 'VIVA_DEMO_03',
    student_name: 'Aditi Nair',
    gender: 'Female',
    age: 21,
    department: 'Master of Computer Applications',
    attendance_percentage: 94.0,
    internal_marks: 88.0,
    assignment_score: 91.0,
    study_hours_per_week: 22.0,
    previous_academic_marks: 86.0,
    extracurricular_activities: 'Yes',
    parental_education: 'Master',
    internet_access: 'Yes'
  }
};

export default function PredictForm() {
  const [formData, setFormData] = useState(PRESETS.highRisk);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: ['age', 'attendance_percentage', 'internal_marks', 'assignment_score', 'study_hours_per_week', 'previous_academic_marks'].includes(name)
        ? parseFloat(value) || ''
        : value
    }));
  };

  const handlePreset = (type) => {
    setFormData(PRESETS[type]);
    setResult(null);
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await predictSingle(formData);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Student Academic Risk Predictor</h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
            Input mid-semester academic indicators to forecast academic risk before final examinations.
          </p>
        </div>

        {/* Quick Demo Presets */}
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={{ fontSize: '0.78rem', color: '#64748b', fontWeight: 600 }}>VIVA DEMO PRESETS:</span>
          <button type="button" className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }} onClick={() => handlePreset('highRisk')}>
            🔴 High Risk Case
          </button>
          <button type="button" className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }} onClick={() => handlePreset('mediumRisk')}>
            🟡 Medium Risk Case
          </button>
          <button type="button" className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.35rem 0.65rem' }} onClick={() => handlePreset('lowRisk')}>
            🟢 Low Risk Case
          </button>
        </div>
      </div>

      {error && (
        <div className="alert-box alert-info">
          <div>
            <strong>Prediction Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="card">
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {/* Student ID */}
            <div className="form-group">
              <label className="form-label">Student ID</label>
              <input
                type="text"
                name="student_id"
                className="form-input"
                required
                value={formData.student_id}
                onChange={handleChange}
                placeholder="e.g. STU1042"
              />
            </div>

            {/* Student Name */}
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="student_name"
                className="form-input"
                required
                value={formData.student_name}
                onChange={handleChange}
                placeholder="e.g. Rahul Sharma"
              />
            </div>

            {/* Department */}
            <div className="form-group">
              <label className="form-label">Academic Department</label>
              <select name="department" className="form-select" value={formData.department} onChange={handleChange}>
                <option value="Master of Computer Applications">Master of Computer Applications (MCA)</option>
                <option value="Computer Science and Engineering">Computer Science & Engineering</option>
                <option value="Information Technology">Information Technology</option>
                <option value="Data Science and AI">Data Science & AI</option>
              </select>
            </div>

            {/* Attendance Percentage */}
            <div className="form-group">
              <label className="form-label">
                Attendance Percentage (%) <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                name="attendance_percentage"
                className="form-input"
                required
                value={formData.attendance_percentage}
                onChange={handleChange}
              />
              <span className="form-hint">Institutional alert triggered if &lt; 75.0%</span>
            </div>

            {/* Internal Marks */}
            <div className="form-group">
              <label className="form-label">
                Internal Assessment Marks (0-100) <span style={{ color: '#ef4444' }}>*</span>
              </label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                name="internal_marks"
                className="form-input"
                required
                value={formData.internal_marks}
                onChange={handleChange}
              />
              <span className="form-hint">Mid-semester continuous test evaluation</span>
            </div>

            {/* Assignment Score */}
            <div className="form-group">
              <label className="form-label">Assignment & Lab Score (0-100)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                name="assignment_score"
                className="form-input"
                value={formData.assignment_score}
                onChange={handleChange}
              />
              <span className="form-hint">Continuous laboratory and problem set marks</span>
            </div>

            {/* Study Hours */}
            <div className="form-group">
              <label className="form-label">Weekly Self-Study Hours</label>
              <input
                type="number"
                step="0.5"
                min="0"
                max="50"
                name="study_hours_per_week"
                className="form-input"
                value={formData.study_hours_per_week}
                onChange={handleChange}
              />
              <span className="form-hint">Average independent practice outside lecture hours</span>
            </div>

            {/* Previous Academic Marks */}
            <div className="form-group">
              <label className="form-label">Previous Academic Marks (%)</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                name="previous_academic_marks"
                className="form-input"
                value={formData.previous_academic_marks}
                onChange={handleChange}
              />
              <span className="form-hint">Undergraduate aggregate percentage</span>
            </div>

            {/* Gender */}
            <div className="form-group">
              <label className="form-label">Gender</label>
              <select name="gender" className="form-select" value={formData.gender} onChange={handleChange}>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Parental Education */}
            <div className="form-group">
              <label className="form-label">Parental Education Level</label>
              <select name="parental_education" className="form-select" value={formData.parental_education} onChange={handleChange}>
                <option value="Doctorate">Doctorate</option>
                <option value="Master">Master</option>
                <option value="Bachelor">Bachelor</option>
                <option value="Diploma">Diploma</option>
                <option value="High School">High School</option>
              </select>
            </div>

            {/* Extracurricular Activities */}
            <div className="form-group">
              <label className="form-label">Extracurricular Activities</label>
              <select name="extracurricular_activities" className="form-select" value={formData.extracurricular_activities} onChange={handleChange}>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>

            {/* Internet Access */}
            <div className="form-group">
              <label className="form-label">Hostel / Home Internet Access</label>
              <select name="internet_access" className="form-select" value={formData.internet_access} onChange={handleChange}>
                <option value="Yes">Yes</option>
                <option value="No">No</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', borderTop: '1px solid #e2e8f0', paddingTop: '1.25rem' }}>
            <button
              type="submit"
              className="btn btn-primary"
              style={{ padding: '0.75rem 2rem', fontSize: '1rem' }}
              disabled={loading}
            >
              {loading ? 'Evaluating Model Pipeline...' : '⚡ Predict Academic Risk'}
            </button>
          </div>
        </form>
      </div>

      {/* Prediction Output & Diagnostic Report */}
      {result && (
        <div style={{ marginTop: '2rem' }}>
          {/* Banner */}
          <div
            className={`result-banner ${
              result.predicted_risk === 'High Risk' ? 'high' : result.predicted_risk === 'Medium Risk' ? 'medium' : 'low'
            }`}
          >
            <div>
              <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                Early Warning Diagnostic Result
              </div>
              <div style={{ fontSize: '1.85rem', fontWeight: 800, marginTop: '0.2rem' }}>
                {result.predicted_risk}
              </div>
              <div style={{ fontSize: '0.9rem', marginTop: '0.25rem', opacity: 0.9 }}>
                Evaluated for: <strong>{result.student_name}</strong> (ID: {result.student_id})
              </div>
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 600 }}>
                Model Confidence
              </div>
              <div style={{ fontSize: '2.2rem', fontWeight: 800 }}>
                {result.confidence_percentage}%
              </div>
              <div style={{ fontSize: '0.78rem' }}>Ensemble Random Forest</div>
            </div>
          </div>

          {/* Probability Breakdown Card */}
          <div className="card" style={{ marginTop: '1.25rem' }}>
            <div className="card-title">Class Probability Distribution</div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              {/* High */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600 }}>
                  <span style={{ color: 'var(--risk-high)' }}>High Risk</span>
                  <span>{result.class_probabilities?.['High Risk'] || 0}%</span>
                </div>
                <div className="prob-bar-track">
                  <div
                    className="prob-bar-fill"
                    style={{ width: `${result.class_probabilities?.['High Risk'] || 0}%`, backgroundColor: 'var(--risk-high)' }}
                  />
                </div>
              </div>

              {/* Medium */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600 }}>
                  <span style={{ color: '#d97706' }}>Medium Risk</span>
                  <span>{result.class_probabilities?.['Medium Risk'] || 0}%</span>
                </div>
                <div className="prob-bar-track">
                  <div
                    className="prob-bar-fill"
                    style={{ width: `${result.class_probabilities?.['Medium Risk'] || 0}%`, backgroundColor: '#f59e0b' }}
                  />
                </div>
              </div>

              {/* Low */}
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', fontWeight: 600 }}>
                  <span style={{ color: '#059669' }}>Low Risk</span>
                  <span>{result.class_probabilities?.['Low Risk'] || 0}%</span>
                </div>
                <div className="prob-bar-track">
                  <div
                    className="prob-bar-fill"
                    style={{ width: `${result.class_probabilities?.['Low Risk'] || 0}%`, backgroundColor: '#10b981' }}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Explainable Risk Factors & Recommendations Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 1fr', gap: '1.25rem', marginTop: '1.25rem' }}>
            {/* Risk Factors */}
            <div className="card">
              <div className="card-title">
                <span>🔍 Identified Risk Factors (Explainability)</span>
              </div>
              <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.75rem' }}>
                Pedagogical root causes contributing to the forecasted risk level:
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {result.risk_factors && result.risk_factors.map((f, i) => {
                  const borderCol = f.severity === 'Critical' ? '#f87171' : f.severity === 'Moderate' ? '#fcd34d' : '#86efac';
                  const bgCol = f.severity === 'Critical' ? '#fef2f2' : f.severity === 'Moderate' ? '#fffbeb' : '#f0fdf4';
                  return (
                    <div
                      key={i}
                      style={{
                        padding: '0.75rem 1rem',
                        borderLeft: `4px solid ${borderCol}`,
                        backgroundColor: bgCol,
                        borderRadius: '4px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <strong style={{ fontSize: '0.88rem' }}>{f.factor}</strong>
                        <span style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', color: '#475569' }}>
                          {f.severity}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#475569', marginTop: '0.2rem' }}>
                        {f.detail}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Pedagogical Action Plan */}
            <div className="card">
              <div className="card-title">
                <span>📋 Recommended Intervention Plan</span>
              </div>
              <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '0.75rem' }}>
                Faculty mentorship steps tailored to salvage or elevate academic standing:
              </p>
              <ul style={{ paddingLeft: '1.2rem', display: 'flex', flexDirection: 'column', gap: '0.65rem' }}>
                {result.recommendations && result.recommendations.map((rec, i) => (
                  <li key={i} style={{ fontSize: '0.88rem', color: '#334155' }}>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
