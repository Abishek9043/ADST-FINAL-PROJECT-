import React, { useState, useEffect } from 'react';
import { fetchPredictionHistory, getExportCsvUrl } from '../api';

export default function HistoryAudit() {
  const [history, setHistory] = useState([]);
  const [filterRisk, setFilterRisk] = useState('');
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState(null);

  useEffect(() => {
    loadHistory();
  }, [filterRisk]);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await fetchPredictionHistory(filterRisk);
      setHistory(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Prediction History & Audit Logs</h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
            Complete audit trail of AI risk classifications generated for student records.
          </p>
        </div>
        <button className="btn btn-secondary" onClick={() => window.open(getExportCsvUrl(), '_blank')}>
          📥 Export Audit Trail (CSV)
        </button>
      </div>

      {/* Filter Tabs */}
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.25rem' }}>
        {[
          { label: 'All Records', value: '' },
          { label: '🔴 High Risk Only', value: 'High Risk' },
          { label: '🟡 Medium Risk Only', value: 'Medium Risk' },
          { label: '🟢 Low Risk Only', value: 'Low Risk' },
        ].map((tab) => (
          <button
            key={tab.value}
            className={`btn ${filterRisk === tab.value ? 'btn-primary' : 'btn-secondary'}`}
            style={{ fontSize: '0.82rem', padding: '0.45rem 0.85rem' }}
            onClick={() => setFilterRisk(tab.value)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Audit Table */}
      <div className="card">
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Student Name</th>
                <th>Predicted Risk</th>
                <th>Confidence</th>
                <th>High Prob</th>
                <th>Medium Prob</th>
                <th>Low Prob</th>
                <th>Timestamp</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem' }}>
                    Loading audit records...
                  </td>
                </tr>
              ) : history.length > 0 ? (
                history.map((r) => {
                  const badgeClass = r.predicted_risk === 'High Risk' ? 'high' : r.predicted_risk === 'Medium Risk' ? 'medium' : 'low';
                  return (
                    <tr key={r.id}>
                      <td style={{ fontWeight: 600, color: '#2563eb' }}>{r.student_id}</td>
                      <td style={{ fontWeight: 600 }}>{r.student_name}</td>
                      <td>
                        <span className={`badge-risk ${badgeClass}`}>{r.predicted_risk}</span>
                      </td>
                      <td><strong>{r.confidence_percentage}%</strong></td>
                      <td style={{ color: '#ef4444' }}>{r.prob_high || 0}%</td>
                      <td style={{ color: '#d97706' }}>{r.prob_medium || 0}%</td>
                      <td style={{ color: '#10b981' }}>{r.prob_low || 0}%</td>
                      <td style={{ fontSize: '0.78rem', color: '#64748b' }}>{r.created_at}</td>
                      <td>
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                          onClick={() => setSelectedRecord(r)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="9" style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
                    No prediction history found matching the selected filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Details Modal */}
      {selectedRecord && (
        <div className="modal-backdrop">
          <div className="modal-content" style={{ maxWidth: '600px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>
                  Diagnostic Report: {selectedRecord.student_name}
                </h3>
                <span style={{ fontSize: '0.82rem', color: '#64748b' }}>
                  Student ID: {selectedRecord.student_id} | Date: {selectedRecord.created_at}
                </span>
              </div>
              <button
                style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}
                onClick={() => setSelectedRecord(null)}
              >
                ✕
              </button>
            </div>

            <div style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.85rem', color: '#64748b' }}>Predicted Classification:</div>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, marginTop: '0.2rem' }}>
                {selectedRecord.predicted_risk} ({selectedRecord.confidence_percentage}% confidence)
              </div>
            </div>

            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Contributing Risk Factors:
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', marginBottom: '1.25rem' }}>
              {selectedRecord.risk_factors && selectedRecord.risk_factors.length > 0 ? (
                selectedRecord.risk_factors.map((f, i) => (
                  <div key={i} style={{ background: '#f8fafc', padding: '0.65rem', borderRadius: '6px', fontSize: '0.85rem' }}>
                    <strong>{f.factor}</strong> ({f.severity})
                    <div style={{ color: '#64748b', fontSize: '0.8rem', marginTop: '0.15rem' }}>{f.detail}</div>
                  </div>
                ))
              ) : (
                <div style={{ color: '#64748b', fontSize: '0.85rem' }}>No adverse risk factors flagged.</div>
              )}
            </div>

            <h4 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '0.5rem' }}>
              Faculty Mentorship Recommendations:
            </h4>
            <ul style={{ paddingLeft: '1.2rem', fontSize: '0.85rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
              {selectedRecord.recommendations?.map((rec, i) => (
                <li key={i}>{rec}</li>
              ))}
            </ul>

            <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
              <button className="btn btn-secondary" onClick={() => setSelectedRecord(null)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
