import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/axios';
import UploadForm from '../components/UploadForm';
import AnalysisResult from '../components/AnalysisResult';

export default function Dashboard() {
  const [prescriptions, setPrescriptions] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [analyzingId, setAnalyzingId] = useState(null); // track which one is loading
  const [showUpload, setShowUpload] = useState(false);
  const navigate = useNavigate();

  const fetchPrescriptions = async () => {
    try {
      const res = await api.get('/prescriptions/');
      setPrescriptions(res.data);
    } catch {
      navigate('/login');
    }
  };

  useEffect(() => { fetchPrescriptions(); }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleAnalyze = async (prescriptionId) => {
    setAnalyzingId(prescriptionId);
    setSelectedAnalysis(null);
    try {
      const res = await api.post(`/analysis/${prescriptionId}`);
      setSelectedAnalysis(res.data);
    } catch (err) {
      alert(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setAnalyzingId(null);
    }
  };

  const handleUploadSuccess = () => {
    setShowUpload(false);
    fetchPrescriptions();
  };

  return (
    <div className="dashboard">
      <header className="dash-header">
        <h1>💊 Health Companion</h1>
        <div>
          <button className="btn-secondary" onClick={() => setShowUpload(!showUpload)}>
            {showUpload ? 'Cancel' : '+ New Prescription'}
          </button>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      {showUpload && (
        <UploadForm onSuccess={handleUploadSuccess} />
      )}

      <div className="dash-body">
        <div className="prescriptions-list">
          <h2>Your Prescriptions</h2>
          {prescriptions.length === 0 && (
            <p className="empty-state">No prescriptions yet. Upload one to get started.</p>
          )}
          {prescriptions.map(p => (
            <div key={p.id} className="prescription-card">
              <div>
                <span className="badge">{p.file_type || 'text only'}</span>
                <p>{p.symptom_notes || 'No symptom notes'}</p>
                <small>{new Date(p.created_at).toLocaleDateString()}</small>
              </div>
              <button
                className="btn-analyze"
                onClick={() => handleAnalyze(p.id)}
                disabled={analyzingId !== null}
              >
                {analyzingId === p.id ? 'Analyzing...' : 'Analyze'}
              </button>
            </div>
          ))}
        </div>

        <div className="analysis-panel">
          {analyzingId !== null && (
            <div className="loading-state">
              <div className="spinner" />
              <p>AI is analyzing your prescription...</p>
            </div>
          )}
          {selectedAnalysis && analyzingId === null && (
            <AnalysisResult analysis={selectedAnalysis} />
          )}
        </div>
      </div>
    </div>
  );
}