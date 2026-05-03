export default function AnalysisResult({ analysis }) {
  let medicines = [];
  try {
    medicines = JSON.parse(analysis.medicines || '[]');
  } catch {
    medicines = [];
  }

  return (
    <div className="analysis-result">
      <div className="disclaimer">
        ⚠️ {analysis.disclaimer}
      </div>

      <h2>AI Analysis Result</h2>

      {medicines.length > 0 && (
        <section>
          <h3>💊 Medicines Prescribed</h3>
          <div className="medicines-grid">
            {medicines.map((med, i) => (
              <div key={i} className="medicine-card">
                <h4>{med.name}</h4>
                <p><strong>Dosage:</strong> {med.dosage}</p>
                <p><strong>Frequency:</strong> {med.frequency}</p>
                {med.duration && <p><strong>Duration:</strong> {med.duration}</p>}
              </div>
            ))}
          </div>
        </section>
      )}

      {analysis.doctor_advice && (
        <section>
          <h3>👨‍⚕️ Doctor's Advice</h3>
          <p>{analysis.doctor_advice}</p>
        </section>
      )}

      {analysis.lifestyle_changes && (
        <section>
          <h3>🏃 Lifestyle & Activities</h3>
          <p>{analysis.lifestyle_changes}</p>
        </section>
      )}
    </div>
  );
}