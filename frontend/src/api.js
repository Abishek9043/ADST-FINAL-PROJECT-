/**
 * EduPulse AI - Frontend API Service Client
 * Connects React frontend components to the Flask backend endpoints.
 */

const BASE_URL = 'http://127.0.0.1:5000/api';

export async function fetchHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  return res.json();
}

export async function fetchDashboardStats() {
  const res = await fetch(`${BASE_URL}/dashboard/stats`);
  if (!res.ok) throw new Error('Failed to fetch dashboard statistics');
  return res.json();
}

export async function fetchStudents(searchQuery = '') {
  const url = searchQuery 
    ? `${BASE_URL}/students?q=${encodeURIComponent(searchQuery)}`
    : `${BASE_URL}/students`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch students');
  return res.json();
}

export async function registerStudent(studentData) {
  const res = await fetch(`${BASE_URL}/students`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(studentData),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Failed to register student');
  return data;
}

export async function fetchStudentDetails(studentId) {
  const res = await fetch(`${BASE_URL}/students/${studentId}`);
  if (!res.ok) throw new Error('Failed to fetch student details');
  return res.json();
}

export async function deleteStudent(studentId) {
  const res = await fetch(`${BASE_URL}/students/${studentId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error('Failed to delete student');
  return res.json();
}

export async function predictSingle(studentData) {
  const res = await fetch(`${BASE_URL}/predict/single`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(studentData),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Prediction calculation failed');
  return data;
}

export async function predictBatch(file) {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${BASE_URL}/predict/batch`, {
    method: 'POST',
    body: formData,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Batch prediction failed');
  return data;
}

export async function fetchPredictionHistory(riskFilter = '', limit = 100) {
  let url = `${BASE_URL}/predictions/history?limit=${limit}`;
  if (riskFilter) {
    url += `&risk=${encodeURIComponent(riskFilter)}`;
  }
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch prediction history');
  return res.json();
}

export function getExportCsvUrl() {
  return `${BASE_URL}/predictions/export`;
}

export async function fetchModelMetrics() {
  const res = await fetch(`${BASE_URL}/model/metrics`);
  if (!res.ok) throw new Error('Failed to fetch model metrics');
  return res.json();
}

export function getReportChartUrl(filename) {
  return `${BASE_URL}/reports/charts/${filename}`;
}
