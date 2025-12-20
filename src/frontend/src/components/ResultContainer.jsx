import { useEffect, useState } from 'react';

function ResultContainer({ result }) {
  const [confidenceWidth, setConfidenceWidth] = useState(0);
  const { prediction, confidence, details } = result;
  const confidencePercent = (confidence * 100).toFixed(1);

  useEffect(() => {
    setTimeout(() => {
      setConfidenceWidth(confidencePercent);
    }, 100);
  }, [confidencePercent]);

  const isHuman = prediction === 'human';

  return (
    <div className="result-container visible">
      <div className="result-header">
        <div className="result-icon">{isHuman ? '✅' : '⚠️'}</div>
        <div className="result-info">
          <h2>Detection Result</h2>
          <div className={`prediction ${isHuman ? 'human' : 'ai'}`}>
            {isHuman ? 'HUMAN SPEECH' : 'AI-GENERATED'}
          </div>
          <div className="confidence">
            Confidence: <span className="confidence-value">{confidencePercent}%</span>
          </div>
          <div className="confidence-bar">
            <div 
              className={`confidence-fill ${isHuman ? 'human' : 'ai'}`}
              style={{ width: `${confidenceWidth}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className="details">
        <div className="details-title">📊 Technical Details</div>
        <DetailRow label="Phase Coherence" value={details.phase_coherence.toFixed(6)} />
        <DetailRow label="Decision Threshold" value={details.threshold.toFixed(6)} />
        <DetailRow label="Distance to Human" value={details.distance_to_human.toFixed(6)} />
        <DetailRow label="Distance to AI" value={details.distance_to_ai.toFixed(6)} />
        <DetailRow label="Phase Velocity" value={details.phase_velocity.toFixed(6)} />
        <DetailRow label="Spectral Entropy" value={details.spectral_entropy.toFixed(6)} />
      </div>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="detail-row">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{value}</span>
    </div>
  );
}

export default ResultContainer;
