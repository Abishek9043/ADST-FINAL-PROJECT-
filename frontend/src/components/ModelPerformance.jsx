import React, { useState, useEffect } from 'react';
import { fetchModelMetrics, getReportChartUrl } from '../api';

export default function ModelPerformance() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMetrics();
  }, []);

  const loadMetrics = async () => {
    try {
      setLoading(true);
      const data = await fetchModelMetrics();
      setMetrics(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '4rem', color: '#64748b' }}>
        Loading machine learning evaluation metrics...
      </div>
    );
  }

  const lr = metrics?.models?.logistic_regression;
  const rf = metrics?.models?.random_forest;

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Machine Learning Model Performance & Viva Benchmark</h2>
        <p style={{ color: '#64748b', fontSize: '0.88rem' }}>
          Comparative evaluation of Logistic Regression vs. Random Forest algorithms for MCA capstone defense.
        </p>
      </div>

      {/* Production Model Highlight Card */}
      <div
        className="card"
        style={{
          borderLeft: '5px solid #22c55e',
          background: 'linear-gradient(135deg, #f0fdf4 0%, #ffffff 100%)',
          marginBottom: '1.5rem'
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <span style={{ fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', color: '#15803d' }}>
              Selected Production Pipeline
            </span>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#166534', marginTop: '0.2rem' }}>
              {metrics?.best_model || 'Random Forest Classifier'}
            </h3>
            <p style={{ fontSize: '0.88rem', color: '#334155', marginTop: '0.35rem' }}>
              Selected based on superior weighted F1-score (<strong>{((rf?.f1_weighted || 0) * 100).toFixed(2)}%</strong>) and robust recall across minority High-Risk student classifications.
            </p>
          </div>

          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '2.5rem', fontWeight: 800, color: '#166534' }}>
              {((rf?.test_accuracy || 0) * 100).toFixed(1)}%
            </div>
            <div style={{ fontSize: '0.8rem', color: '#15803d', fontWeight: 600 }}>Test Accuracy</div>
          </div>
        </div>
      </div>

      {/* Side-by-Side Model Comparison Table */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div className="card-title">Comparative Performance Metrics (Held-out 20% Test Split)</div>
        <div className="table-responsive">
          <table>
            <thead>
              <tr>
                <th>Evaluation Metric</th>
                <th>Logistic Regression</th>
                <th>Random Forest (Best)</th>
                <th>Performance Delta</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td style={{ fontWeight: 600 }}>Test Accuracy</td>
                <td>{((lr?.test_accuracy || 0) * 100).toFixed(2)}%</td>
                <td style={{ fontWeight: 700, color: '#15803d' }}>{((rf?.test_accuracy || 0) * 100).toFixed(2)}%</td>
                <td style={{ color: '#15803d', fontWeight: 600 }}>
                  +{(((rf?.test_accuracy || 0) - (lr?.test_accuracy || 0)) * 100).toFixed(2)}%
                </td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Training Accuracy</td>
                <td>{((lr?.train_accuracy || 0) * 100).toFixed(2)}%</td>
                <td>{((rf?.train_accuracy || 0) * 100).toFixed(2)}%</td>
                <td style={{ color: '#64748b' }}>—</td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Weighted Precision</td>
                <td>{((lr?.precision_weighted || 0) * 100).toFixed(2)}%</td>
                <td style={{ fontWeight: 700, color: '#15803d' }}>{((rf?.precision_weighted || 0) * 100).toFixed(2)}%</td>
                <td style={{ color: '#15803d', fontWeight: 600 }}>
                  +{(((rf?.precision_weighted || 0) - (lr?.precision_weighted || 0)) * 100).toFixed(2)}%
                </td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Weighted Recall (Sensitivity)</td>
                <td>{((lr?.recall_weighted || 0) * 100).toFixed(2)}%</td>
                <td style={{ fontWeight: 700, color: '#15803d' }}>{((rf?.recall_weighted || 0) * 100).toFixed(2)}%</td>
                <td style={{ color: '#15803d', fontWeight: 600 }}>
                  +{(((rf?.recall_weighted || 0) - (lr?.recall_weighted || 0)) * 100).toFixed(2)}%
                </td>
              </tr>
              <tr>
                <td style={{ fontWeight: 600 }}>Weighted F1-Score</td>
                <td>{((lr?.f1_weighted || 0) * 100).toFixed(2)}%</td>
                <td style={{ fontWeight: 700, color: '#15803d' }}>{((rf?.f1_weighted || 0) * 100).toFixed(2)}%</td>
                <td style={{ color: '#15803d', fontWeight: 600 }}>
                  +{(((rf?.f1_weighted || 0) - (lr?.f1_weighted || 0)) * 100).toFixed(2)}%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Visual Reports Section */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1.25rem', marginBottom: '1.5rem' }}>
        {/* Confusion Matrix Chart */}
        <div className="card">
          <div className="card-title">Confusion Matrices (Held-out Test Set)</div>
          <img
            src={getReportChartUrl('confusion_matrix.png')}
            alt="Confusion Matrix Chart"
            style={{ width: '100%', borderRadius: '6px', border: '1px solid #e2e8f0' }}
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
          <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.5rem' }}>
            Displays True Positives, False Positives, and True Negatives for High, Medium, and Low risk classes.
          </p>
        </div>

        {/* Feature Importance Chart */}
        <div className="card">
          <div className="card-title">Top Influential Risk Factors</div>
          <img
            src={getReportChartUrl('feature_importance.png')}
            alt="Feature Importance Chart"
            style={{ width: '100%', borderRadius: '6px', border: '1px solid #e2e8f0' }}
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
          <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.5rem' }}>
            Gini importance shows internal marks and class attendance as the strongest early predictors of semester risk.
          </p>
        </div>
      </div>

      {/* MCA Viva Defense Notes Card */}
      <div className="card" style={{ backgroundColor: '#eff6ff', borderColor: '#bfdbfe' }}>
        <h4 style={{ color: '#1e40af', fontWeight: 700, fontSize: '1rem', marginBottom: '0.5rem' }}>
          🎓 Key Discussion Points for MCA Viva Defense
        </h4>
        <ul style={{ paddingLeft: '1.2rem', color: '#1e3a8a', fontSize: '0.88rem', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
          <li>
            <strong>Why Not Final Exam Marks?</strong> In an Early Warning System (EWS), using final examination marks would constitute data leakage and defeat the early intervention purpose of the model.
          </li>
          <li>
            <strong>Why Prevent Data Leakage via Pipeline?</strong> Scikit-learn Pipelines ensure standard scaling and one-hot encoding are strictly fitted on the 80% training set and transformed on the 20% test split.
          </li>
          <li>
            <strong>Why Random Forest over Logistic Regression?</strong> While Logistic Regression yields an interpretable linear baseline, Random Forest handles non-linear boundaries and interaction effects between attendance and internal marks without overfitting.
          </li>
        </ul>
      </div>
    </div>
  );
}
