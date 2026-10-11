import React, { useState } from 'react';
import { predictBatch, getExportCsvUrl } from '../api';

export default function BatchPredict() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [batchResult, setBatchResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a CSV file first.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await predictBatch(file);
      setBatchResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadSampleTemplate = () => {
    const csvContent =
      'student_id,student_name,gender,age,department,attendance_percentage,internal_marks,assignment_score,study_hours_per_week,previous_academic_marks,extracurricular_activities,parental_education,internet_access\n' +
      'STU9001,Amit Verma,Male,22,Master of Computer Applications,58.0,42.0,50.0,6.0,55.0,No,High School,Yes\n' +
      'STU9002,Sneha Roy,Female,21,Master of Computer Applications,91.0,85.0,88.0,20.0,82.0,Yes,Bachelor,Yes\n' +
      'STU9003,Karan Gill,Male,23,Master of Computer Applications,74.0,65.0,68.0,12.0,70.0,No,Diploma,Yes\n';

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'edupulse_sample_student_template.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Batch CSV Academic Risk Evaluation</h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
            Upload semester rosters or department CSV sheets to perform instantaneous institutional risk screening.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={downloadSampleTemplate}>
          📄 Download Sample CSV Template
        </button>
      </div>

      {error && (
        <div className="alert-box alert-info">
          <div>
            <strong>Processing Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Upload Zone */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <form onSubmit={handleUpload}>
          <div
            style={{
              border: '2px dashed #cbd5e1',
              borderRadius: '8px',
              padding: '2.5rem',
              textAlign: 'center',
              backgroundColor: '#f8fafc',
              cursor: 'pointer'
            }}
          >
            <div style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>📁</div>
            <div style={{ fontWeight: 600, fontSize: '1.05rem', color: '#1e293b' }}>
              {file ? file.name : 'Choose or Drag & Drop Student Dataset (.csv)'}
            </div>
            <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
              Supports UTF-8 CSV containing mid-semester attendance, internal marks, and study hours.
            </p>

            <input
              type="file"
              accept=".csv"
              style={{ marginTop: '1rem', display: 'inline-block' }}
              onChange={handleFileChange}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1.25rem' }}>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !file}
              style={{ padding: '0.75rem 2rem' }}
            >
              {loading ? 'Evaluating Cohort with Random Forest Pipeline...' : '⚡ Process Batch Prediction'}
            </button>
          </div>
        </form>
      </div>

      {/* Batch Results View */}
      {batchResult && (
        <div>
          {/* Summary Cards */}
          <div className="grid-cols-4">
            <div className="card stat-card">
              <div className="stat-label">Processed Students</div>
              <div className="stat-value">{batchResult.total_processed}</div>
              <div className="stat-subtext">Total records screened</div>
            </div>

            <div className="card stat-card" style={{ borderLeft: '4px solid var(--risk-high)' }}>
              <div className="stat-label" style={{ color: 'var(--risk-high)' }}>High Risk Flagged</div>
              <div className="stat-value" style={{ color: 'var(--risk-high)' }}>
                {batchResult.summary?.['High Risk'] || 0}
              </div>
              <div className="stat-subtext">Urgent counseling needed</div>
            </div>

            <div className="card stat-card" style={{ borderLeft: '4px solid #f59e0b' }}>
              <div className="stat-label" style={{ color: '#d97706' }}>Medium Risk</div>
              <div className="stat-value" style={{ color: '#d97706' }}>
                {batchResult.summary?.['Medium Risk'] || 0}
              </div>
              <div className="stat-subtext">Remedial support needed</div>
            </div>

            <div className="card stat-card" style={{ borderLeft: '4px solid #10b981' }}>
              <div className="stat-label" style={{ color: '#059669' }}>Low Risk</div>
              <div className="stat-value" style={{ color: '#059669' }}>
                {batchResult.summary?.['Low Risk'] || 0}
              </div>
              <div className="stat-subtext">Satisfactory progress</div>
            </div>
          </div>

          {/* Results Table */}
          <div className="card">
            <div className="card-title">
              <span>Cohort Risk Assessment Output ({batchResult.results?.length})</span>
              <button className="btn btn-secondary" style={{ fontSize: '0.8rem' }} onClick={() => window.open(getExportCsvUrl(), '_blank')}>
                📥 Download Full Report (CSV)
              </button>
            </div>

            <div className="table-responsive">
              <table>
                <thead>
                  <tr>
                    <th>Student ID</th>
                    <th>Name</th>
                    <th>Predicted Risk</th>
                    <th>Confidence</th>
                    <th>Primary Risk Factors</th>
                  </tr>
                </thead>
                <tbody>
                  {batchResult.results?.map((item, idx) => {
                    const badgeClass = item.predicted_risk === 'High Risk' ? 'high' : item.predicted_risk === 'Medium Risk' ? 'medium' : 'low';
                    const topFactors = item.risk_factors?.map((f) => f.factor).slice(0, 2).join('; ');
                    return (
                      <tr key={idx}>
                        <td style={{ fontWeight: 600, color: '#2563eb' }}>{item.student_id}</td>
                        <td style={{ fontWeight: 600 }}>{item.student_name}</td>
                        <td>
                          <span className={`badge-risk ${badgeClass}`}>{item.predicted_risk}</span>
                        </td>
                        <td>{item.confidence_percentage}%</td>
                        <td style={{ fontSize: '0.82rem', color: '#475569' }}>
                          {topFactors || 'None detected'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
