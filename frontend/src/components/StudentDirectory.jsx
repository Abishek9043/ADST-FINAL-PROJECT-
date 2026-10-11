import React, { useState, useEffect } from 'react';
import { fetchStudents, registerStudent, deleteStudent, fetchStudentDetails } from '../api';

export default function StudentDirectory({ onSelectStudentForPredict }) {
  const [students, setStudents] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);

  // New Student Form State
  const [formData, setFormData] = useState({
    student_id: '',
    student_name: '',
    gender: 'Male',
    age: 22,
    department: 'Master of Computer Applications',
    attendance_percentage: 75.0,
    internal_marks: 65.0,
    assignment_score: 70.0,
    study_hours_per_week: 14.0,
    previous_academic_marks: 68.0,
    extracurricular_activities: 'No',
    parental_education: 'Bachelor',
    internet_access: 'Yes'
  });
  const [formError, setFormError] = useState(null);

  useEffect(() => {
    loadStudents();
  }, [search]);

  const loadStudents = async () => {
    try {
      setLoading(true);
      const data = await fetchStudents(search);
      setStudents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete student record ${id}?`)) return;
    try {
      await deleteStudent(id);
      loadStudents();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleViewProfile = async (id) => {
    try {
      const details = await fetchStudentDetails(id);
      setSelectedStudent(details);
      setDetailModalOpen(true);
    } catch (err) {
      alert(err.message);
    }
  };

  const handleRegisterSubmit = async (e) => {
    e.preventDefault();
    setFormError(null);
    try {
      await registerStudent(formData);
      setShowAddModal(false);
      loadStudents();
      // Reset
      setFormData({
        student_id: '',
        student_name: '',
        gender: 'Male',
        age: 22,
        department: 'Master of Computer Applications',
        attendance_percentage: 75.0,
        internal_marks: 65.0,
        assignment_score: 70.0,
        study_hours_per_week: 14.0,
        previous_academic_marks: 68.0,
        extracurricular_activities: 'No',
        parental_education: 'Bachelor',
        internet_access: 'Yes'
      });
    } catch (err) {
      setFormError(err.message);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Student Management Directory</h2>
          <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
            Maintain institutional student profiles, academic metrics, and historical logs.
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          + Register New Student
        </button>
      </div>

      {/* Search Bar */}
      <div className="card" style={{ padding: '1rem', marginBottom: '1.5rem' }}>
        <input
          type="text"
          className="form-input"
          placeholder="🔍 Search students by Name, ID, or Department..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Students Table */}
      <div className="card">
        <div className="card-title">
          <span>Registered Cohort ({students.length})</span>
        </div>

        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Student Name</th>
                <th>Department</th>
                <th>Attendance</th>
                <th>Internals</th>
                <th>Study Hrs</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2rem' }}>
                    Loading student directory...
                  </td>
                </tr>
              ) : students.length > 0 ? (
                students.map((s) => (
                  <tr key={s.id}>
                    <td style={{ fontWeight: 600, color: '#2563eb' }}>{s.student_id}</td>
                    <td style={{ fontWeight: 600 }}>{s.student_name}</td>
                    <td style={{ color: '#475569' }}>{s.department}</td>
                    <td>
                      <span
                        style={{
                          fontWeight: 700,
                          color: s.attendance_percentage < 75 ? '#ef4444' : '#10b981'
                        }}
                      >
                        {s.attendance_percentage}%
                      </span>
                    </td>
                    <td>
                      <span
                        style={{
                          fontWeight: 700,
                          color: s.internal_marks < 50 ? '#ef4444' : '#334155'
                        }}
                      >
                        {s.internal_marks} / 100
                      </span>
                    </td>
                    <td>{s.study_hours_per_week} hrs/wk</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.4rem' }}>
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                          onClick={() => handleViewProfile(s.student_id)}
                        >
                          Profile
                        </button>
                        <button
                          className="btn btn-primary"
                          style={{ fontSize: '0.75rem', padding: '0.3rem 0.6rem' }}
                          onClick={() => onSelectStudentForPredict(s)}
                        >
                          Predict Risk
                        </button>
                        <button
                          className="btn btn-secondary"
                          style={{ fontSize: '0.75rem', padding: '0.3rem 0.5rem', color: '#ef4444' }}
                          onClick={() => handleDelete(s.student_id)}
                        >
                          ✕
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" style={{ textAlign: 'center', padding: '2rem', color: '#94a3b8' }}>
                    No students found matching "{search}".
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal 1: Register Student */}
      {showAddModal && (
        <div className="modal-backdrop">
          <div className="modal-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Register New Student</h3>
              <button
                style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}
                onClick={() => setShowAddModal(false)}
              >
                ✕
              </button>
            </div>

            {formError && <div className="alert-box alert-info" style={{ color: '#ef4444' }}>{formError}</div>}

            <form onSubmit={handleRegisterSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label className="form-label">Student ID *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={formData.student_id}
                    onChange={(e) => setFormData({ ...formData, student_id: e.target.value })}
                    placeholder="e.g. STU1301"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Student Name *</label>
                  <input
                    type="text"
                    required
                    className="form-input"
                    value={formData.student_name}
                    onChange={(e) => setFormData({ ...formData, student_name: e.target.value })}
                    placeholder="e.g. Tanvi Joshi"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Department</label>
                  <select
                    className="form-select"
                    value={formData.department}
                    onChange={(e) => setFormData({ ...formData, department: e.target.value })}
                  >
                    <option value="Master of Computer Applications">Master of Computer Applications</option>
                    <option value="Computer Science and Engineering">Computer Science & Engineering</option>
                    <option value="Information Technology">Information Technology</option>
                    <option value="Data Science and AI">Data Science & AI</option>
                  </select>
                </div>

                <div className="form-group">
                  <label className="form-label">Attendance (%) *</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    required
                    className="form-input"
                    value={formData.attendance_percentage}
                    onChange={(e) => setFormData({ ...formData, attendance_percentage: parseFloat(e.target.value) || 0 })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Internal Marks (0-100) *</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    required
                    className="form-input"
                    value={formData.internal_marks}
                    onChange={(e) => setFormData({ ...formData, internal_marks: parseFloat(e.target.value) || 0 })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Assignment Score (0-100)</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    className="form-input"
                    value={formData.assignment_score}
                    onChange={(e) => setFormData({ ...formData, assignment_score: parseFloat(e.target.value) || 0 })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Study Hours / Week</label>
                  <input
                    type="number"
                    step="0.5"
                    min="0"
                    className="form-input"
                    value={formData.study_hours_per_week}
                    onChange={(e) => setFormData({ ...formData, study_hours_per_week: parseFloat(e.target.value) || 0 })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Previous Marks (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    className="form-input"
                    value={formData.previous_academic_marks}
                    onChange={(e) => setFormData({ ...formData, previous_academic_marks: parseFloat(e.target.value) || 0 })}
                  />
                </div>
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Student
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal 2: View Profile & History */}
      {detailModalOpen && selectedStudent && (
        <div className="modal-backdrop">
          <div className="modal-content" style={{ maxWidth: '750px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <div>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700 }}>
                  {selectedStudent.student?.student_name}
                </h3>
                <span style={{ color: '#64748b', fontSize: '0.85rem' }}>
                  ID: {selectedStudent.student?.student_id} | {selectedStudent.student?.department}
                </span>
              </div>
              <button
                style={{ background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}
                onClick={() => setDetailModalOpen(false)}
              >
                ✕
              </button>
            </div>

            {/* Academic Snapshot */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '0.75rem', marginBottom: '1.5rem' }}>
              <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Attendance</div>
                <strong style={{ fontSize: '1.1rem' }}>{selectedStudent.student?.attendance_percentage}%</strong>
              </div>
              <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Internal Marks</div>
                <strong style={{ fontSize: '1.1rem' }}>{selectedStudent.student?.internal_marks}/100</strong>
              </div>
              <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Assignments</div>
                <strong style={{ fontSize: '1.1rem' }}>{selectedStudent.student?.assignment_score}/100</strong>
              </div>
              <div style={{ background: '#f8fafc', padding: '0.75rem', borderRadius: '6px' }}>
                <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Self-Study</div>
                <strong style={{ fontSize: '1.1rem' }}>{selectedStudent.student?.study_hours_per_week} hrs</strong>
              </div>
            </div>

            {/* Diagnostic History */}
            <h4 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>
              Diagnostic Evaluations Log ({selectedStudent.predictions?.length || 0})
            </h4>

            {selectedStudent.predictions && selectedStudent.predictions.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {selectedStudent.predictions.map((p) => {
                  const badgeClass = p.predicted_risk === 'High Risk' ? 'high' : p.predicted_risk === 'Medium Risk' ? 'medium' : 'low';
                  return (
                    <div key={p.id} style={{ border: '1px solid #e2e8f0', borderRadius: '8px', padding: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <span className={`badge-risk ${badgeClass}`}>{p.predicted_risk}</span>
                          <span style={{ marginLeft: '0.75rem', fontSize: '0.82rem', color: '#64748b' }}>
                            Confidence: {p.confidence_percentage}%
                          </span>
                        </div>
                        <span style={{ fontSize: '0.78rem', color: '#94a3b8' }}>{p.created_at}</span>
                      </div>

                      {p.risk_factors && p.risk_factors.length > 0 && (
                        <div style={{ marginTop: '0.5rem', fontSize: '0.8rem', color: '#475569' }}>
                          <strong>Flagged Factors:</strong> {p.risk_factors.map((f) => f.factor).join(', ')}
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.88rem' }}>No prediction logs recorded yet for this student.</p>
            )}

            <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
              <button className="btn btn-secondary" onClick={() => setDetailModalOpen(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
