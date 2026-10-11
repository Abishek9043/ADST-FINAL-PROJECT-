import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import PredictForm from './components/PredictForm';
import StudentDirectory from './components/StudentDirectory';
import BatchPredict from './components/BatchPredict';
import HistoryAudit from './components/HistoryAudit';
import ModelPerformance from './components/ModelPerformance';
import { fetchHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemOnline, setSystemOnline] = useState(false);
  const [prefilledStudent, setPrefilledStudent] = useState(null);

  useEffect(() => {
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  const checkBackendHealth = async () => {
    try {
      const data = await fetchHealth();
      if (data && data.status === 'online') {
        setSystemOnline(true);
      }
    } catch {
      setSystemOnline(false);
    }
  };

  const handleSelectStudentForPredict = (student) => {
    setPrefilledStudent(student);
    setActiveTab('predict');
  };

  return (
    <div className="app-container">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">EP</div>
          <div>
            <div className="brand-title">EduPulse AI</div>
            <div className="brand-subtitle">Early Warning System</div>
          </div>
        </div>

        <ul className="nav-menu">
          <li>
            <button
              className={`nav-item ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              📊 Dashboard
            </button>
          </li>
          <li>
            <button
              className={`nav-item ${activeTab === 'predict' ? 'active' : ''}`}
              onClick={() => setActiveTab('predict')}
            >
              ⚡ Risk Predictor
            </button>
          </li>
          <li>
            <button
              className={`nav-item ${activeTab === 'students' ? 'active' : ''}`}
              onClick={() => setActiveTab('students')}
            >
              👥 Student Directory
            </button>
          </li>
          <li>
            <button
              className={`nav-item ${activeTab === 'batch' ? 'active' : ''}`}
              onClick={() => setActiveTab('batch')}
            >
              📁 Batch CSV Predict
            </button>
          </li>
          <li>
            <button
              className={`nav-item ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => setActiveTab('history')}
            >
              📜 Prediction History
            </button>
          </li>
          <li>
            <button
              className={`nav-item ${activeTab === 'performance' ? 'active' : ''}`}
              onClick={() => setActiveTab('performance')}
            >
              🧠 Model Performance
            </button>
          </li>
        </ul>

        <div className="sidebar-footer">
          <div>MCA Capstone Project 2026</div>
          <div style={{ marginTop: '0.2rem', color: '#475569' }}>EduPulse ML Engine v1.0</div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Topbar */}
        <header className="topbar">
          <div>
            <h1 className="page-title">
              {activeTab === 'dashboard' && 'Academic Risk Dashboard'}
              {activeTab === 'predict' && 'Student Risk Predictor & Diagnostics'}
              {activeTab === 'students' && 'Institutional Student Directory'}
              {activeTab === 'batch' && 'Batch CSV Roster Evaluation'}
              {activeTab === 'history' && 'Prediction Audit Trail'}
              {activeTab === 'performance' && 'Model Benchmark & Viva Defense'}
            </h1>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div className="badge-live">
              <span
                className="badge-live-dot"
                style={{ backgroundColor: systemOnline ? '#10b981' : '#ef4444' }}
              />
              <span>{systemOnline ? 'Flask ML Engine: Connected' : 'Flask Engine: Offline'}</span>
            </div>
          </div>
        </header>

        {/* Content Body */}
        <main className="content-body">
          {activeTab === 'dashboard' && <Dashboard setActiveTab={setActiveTab} />}
          {activeTab === 'predict' && <PredictForm initialStudent={prefilledStudent} />}
          {activeTab === 'students' && (
            <StudentDirectory onSelectStudentForPredict={handleSelectStudentForPredict} />
          )}
          {activeTab === 'batch' && <BatchPredict />}
          {activeTab === 'history' && <HistoryAudit />}
          {activeTab === 'performance' && <ModelPerformance />}
        </main>
      </div>
    </div>
  );
}
