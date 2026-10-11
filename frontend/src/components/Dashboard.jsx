import React, { useState, useEffect } from 'react';
import { fetchDashboardStats, getExportCsvUrl } from '../api';

export default function Dashboard({ setActiveTab }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const data = await fetchDashboardStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem' }}>
        <div style={{ fontSize: '1.2rem', color: '#64748b' }}>Loading dashboard analytics...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="alert-box alert-info">
        <div>
          <strong>Backend Notice:</strong> {error}.
          <div style={{ marginTop: '0.5rem' }}>
            Ensure the Flask backend is running on <code>http://127.0.0.1:5000</code>.
          </div>
          <button className="btn btn-primary" style={{ marginTop: '0.75rem' }} onClick={loadData}>
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  const riskDist = stats?.risk_distribution || { 'High Risk': 0, 'Medium Risk': 0, 'Low Risk': 0 };
  const totalEvaluated = (riskDist['High Risk'] || 0) + (riskDist['Medium Risk'] || 0) + (riskDist['Low Risk'] || 0);

  const getPct = (val) => (totalEvaluated > 0 ? ((val / totalEvaluated) * 100).toFixed(1) : 0);

  return (
    <div>
      {/* Top Action Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Institutional Overview</h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
            Formative Academic Risk Monitoring & Early Warning Metrics (Pre-Final Examination)
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={() => window.open(getExportCsvUrl(), '_blank')}>
            📥 Export Report (CSV)
          </button>
          <button className="btn btn-primary" onClick={() => setActiveTab('predict')}>
            + Evaluate New Student
          </button>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid-cols-4">
        <div className="card stat-card">
          <div className="stat-label">Enrolled Students</div>
          <div className="stat-value">{stats?.total_students || 0}</div>
          <div className="stat-subtext">Active cohort records</div>
        </div>

        <div className="card stat-card">
          <div className="stat-label">Class Attendance Avg</div>
          <div className="stat-value" style={{ color: (stats?.averages?.attendance || 0) < 75 ? '#ef4444' : '#10b981' }}>
            {stats?.averages?.attendance || 0}%
          </div>
          <div className="stat-subtext">Minimum threshold: 75.0%</div>
        </div>

        <div className="card stat-card">
          <div className="stat-label">Internal Marks Avg</div>
          <div className="stat-value">
            {stats?.averages?.internal_marks || 0} <span style={{ fontSize: '1rem', color: '#64748b' }}>/ 100</span>
          </div>
          <div className="stat-subtext">Formative mid-term assessments</div>
        </div>

        <div className="card stat-card">
          <div className="stat-label">Total Predictions Run</div>
          <div className="stat-value">{stats?.total_predictions || 0}</div>
          <div className="stat-subtext">AI diagnostics completed</div>
        </div>
      </div>

      {/* Risk Distribution Visual Cards */}
      <div className="card" style={{ marginBottom: '1.75rem' }}>
        <div className="card-title">
          <span>Student Risk Distribution Breakdown</span>
          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>Total Assessed: {totalEvaluated}</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginTop: '0.5rem' }}>
          {/* High Risk Card */}
          <div style={{
            background: 'var(--risk-high-bg)', border: '1px solid var(--risk-high-border)',
            borderRadius: '10px', padding: '1.25rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge-risk high">High Risk</span>
              <span style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--risk-high)' }}>
                {riskDist['High Risk']}
              </span>
            </div>
            <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#991b1b' }}>
              <strong>{getPct(riskDist['High Risk'])}%</strong> of evaluated students
            </div>
            <p style={{ fontSize: '0.78rem', color: '#7f1d1d', marginTop: '0.35rem' }}>
              Immediate intervention required: Attendance &lt; 60% or Internals &lt; 40%.
            </p>
          </div>

          {/* Medium Risk Card */}
          <div style={{
            background: 'var(--risk-med-bg)', border: '1px solid var(--risk-med-border)',
            borderRadius: '10px', padding: '1.25rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge-risk medium">Medium Risk</span>
              <span style={{ fontSize: '1.5rem', fontWeight: 800, color: '#d97706' }}>
                {riskDist['Medium Risk']}
              </span>
            </div>
            <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#92400e' }}>
              <strong>{getPct(riskDist['Medium Risk'])}%</strong> of evaluated students
            </div>
            <p style={{ fontSize: '0.78rem', color: '#78350f', marginTop: '0.35rem' }}>
              Borderline trajectory: Needs peer tutoring & study plan realignment.
            </p>
          </div>

          {/* Low Risk Card */}
          <div style={{
            background: 'var(--risk-low-bg)', border: '1px solid var(--risk-low-border)',
            borderRadius: '10px', padding: '1.25rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span className="badge-risk low">Low Risk</span>
              <span style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--risk-low)' }}>
                {riskDist['Low Risk']}
              </span>
            </div>
            <div style={{ marginTop: '0.75rem', fontSize: '0.85rem', color: '#065f46' }}>
              <strong>{getPct(riskDist['Low Risk'])}%</strong> of evaluated students
            </div>
            <p style={{ fontSize: '0.78rem', color: '#064e3b', marginTop: '0.35rem' }}>
              On-track for good academic standing & university distinction.
            </p>
          </div>
        </div>
      </div>

      {/* Grid: Academic Averages & Recent Predictions */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: '1.5rem' }}>
        {/* Academic Indicators */}
        <div className="card">
          <div className="card-title">Key Academic Habits</div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                <span>Assignment & Lab Completion</span>
                <strong>{stats?.averages?.assignment_score || 0}%</strong>
              </div>
              <div className="prob-bar-track">
                <div className="prob-bar-fill" style={{ width: `${stats?.averages?.assignment_score || 0}%`, backgroundColor: '#3b82f6' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                <span>Weekly Self-Study Time</span>
                <strong>{stats?.averages?.study_hours || 0} hrs/wk</strong>
              </div>
              <div className="prob-bar-track">
                <div className="prob-bar-fill" style={{ width: `${Math.min(((stats?.averages?.study_hours || 0) / 30) * 100, 100)}%`, backgroundColor: '#8b5cf6' }} />
              </div>
            </div>

            <div style={{ marginTop: '1rem', borderTop: '1px solid #e2e8f0', paddingTop: '1rem' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 600, marginBottom: '0.5rem', color: '#475569' }}>
                Department Enrollment
              </div>
              {stats?.department_distribution && Object.entries(stats.department_distribution).map(([dept, count]) => (
                <div key={dept} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', padding: '0.3rem 0' }}>
                  <span style={{ color: '#334155' }}>{dept}</span>
                  <span style={{ fontWeight: 600 }}>{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Recent Predictions Table */}
        <div className="card">
          <div className="card-title">
            <span>Recent AI Predictions</span>
            <button className="btn btn-secondary" style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }} onClick={() => setActiveTab('history')}>
              View All
            </button>
          </div>

          <div className="table-responsive">
            <table>
              <thead>
                <tr>
                  <th>Student</th>
                  <th>ID</th>
                  <th>Predicted Risk</th>
                  <th>Confidence</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {stats?.recent_predictions && stats.recent_predictions.length > 0 ? (
                  stats.recent_predictions.map((p) => {
                    const badgeClass = p.predicted_risk === 'High Risk' ? 'high' : p.predicted_risk === 'Medium Risk' ? 'medium' : 'low';
                    return (
                      <tr key={p.id}>
                        <td style={{ fontWeight: 600 }}>{p.student_name}</td>
                        <td style={{ color: '#64748b' }}>{p.student_id}</td>
                        <td>
                          <span className={`badge-risk ${badgeClass}`}>{p.predicted_risk}</span>
                        </td>
                        <td>{p.confidence_percentage}%</td>
                        <td style={{ color: '#94a3b8', fontSize: '0.78rem' }}>
                          {p.created_at ? p.created_at.split(' ')[0] : 'Today'}
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan="5" style={{ textAlign: 'center', color: '#94a3b8', padding: '1.5rem' }}>
                      No recent predictions logged yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
