import { useState } from 'react';
import api from '../api/axios';

export default function UploadForm({ onSuccess }) {
  const [file, setFile] = useState(null);
  const [symptoms, setSymptoms] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file && !symptoms.trim()) {
      setError('Please upload a file or enter symptoms.');
      return;
    }
    setLoading(true);
    setError('');
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (symptoms) formData.append('symptom_notes', symptoms);

    try {
      await api.post('/prescriptions/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="upload-form">
      <h2>Upload Prescription</h2>
      {error && <div className="error-msg">{error}</div>}
      <form onSubmit={handleSubmit}>
        <label>Prescription File (JPG, PNG, or PDF)</label>
        <input
          type="file"
          accept=".jpg,.jpeg,.png,.pdf"
          onChange={e => setFile(e.target.files[0])}
        />
        <label>Describe your symptoms</label>
        <textarea
          placeholder="e.g. I have been having a fever and sore throat for 3 days..."
          value={symptoms}
          onChange={e => setSymptoms(e.target.value)}
          rows={4}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Uploading...' : 'Submit'}
        </button>
      </form>
    </div>
  );
}