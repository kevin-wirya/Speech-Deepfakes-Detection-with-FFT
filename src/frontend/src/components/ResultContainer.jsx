import { useEffect, useState } from 'react';

function ResultContainer({ result }) {
  const [confidenceWidth, setConfidenceWidth] = useState(0);
  const {
    prediction,
    confidence,
    decision,
    uncertainty,
    details,
    quality,
    processing_ms: processingMs,
    model_version: modelVersion
  } = result;
  const confidencePercent = (confidence * 100).toFixed(1);
  const isUncertain = decision === 'uncertain';
  const isHuman = !isUncertain && (decision === 'human_likely' || prediction === 'human');
  const decisionLabel = isUncertain ? 'UNCERTAIN' : isHuman ? 'HUMAN-LIKELY' : 'AI-LIKELY';
  const closestFeature = details.feature_evidence?.reduce((closest, evidence) => {
    const distance = evidence.closer_to === 'ai' ? evidence.ai_distance : evidence.human_distance;
    return !closest || distance < closest.distance ? { ...evidence, distance } : closest;
  }, null);

  useEffect(() => {
    const timer = setTimeout(() => setConfidenceWidth(confidencePercent), 100);
    return () => clearTimeout(timer);
  }, [confidencePercent]);

  return (
    <div className="result-container visible">
      <div className="result-header">
        <div className="result-icon">{isUncertain ? '◌' : isHuman ? '✓' : '!'}</div>
        <div className="result-info">
          <h2>Detection Result</h2>
          <div className={`prediction ${isUncertain ? 'uncertain' : isHuman ? 'human' : 'ai'}`}>
            {decisionLabel}
          </div>
          <div className="confidence">
            Detection score: <span className="confidence-value">{confidencePercent}%</span>
          </div>
          <div className="confidence-bar">
            <div
              className={`confidence-fill ${isUncertain ? 'uncertain' : isHuman ? 'human' : 'ai'}`}
              style={{ width: `${confidenceWidth}%` }}
            ></div>
          </div>
        </div>
      </div>

      <div className={`explanation ${isUncertain ? 'explanation-uncertain' : ''}`}>
        <div className="explanation-title">Why this result?</div>
        <p>
          {isUncertain
            ? 'The two reference distances are too close for a reliable automated decision. Human review is recommended.'
            : `${closestFeature ? closestFeature.feature.replaceAll('_', ' ') : 'The measured features'} ${isHuman ? 'is more consistent with the human' : 'is more consistent with the synthetic'} reference distribution.`}
        </p>
        <span className="score-note">
          Relative distance score, not a calibrated probability. Uncertainty: {(uncertainty * 100).toFixed(1)}%
        </span>
      </div>

      <div className="distance-group">
        <div className="distance-group-title">Geometric distances</div>
        <div className="distance-cards">
          <div className="distance-card human-card">
            <div className="distance-card-label">Distance to Human</div>
            <div className="distance-card-value">{details.distance_to_human.toFixed(6)}</div>
          </div>
          <div className="distance-card ai-card">
            <div className="distance-card-label">Distance to AI</div>
            <div className="distance-card-value">{details.distance_to_ai.toFixed(6)}</div>
          </div>
        </div>
      </div>

      <div className="details">
        <div className="details-title">Feature metrics</div>
        <DetailRow label="Phase Coherence" value={details.phase_coherence.toFixed(6)} />
        <DetailRow label="Phase Velocity" value={details.phase_velocity.toFixed(6)} />
        <DetailRow label="Spectral Entropy" value={details.spectral_entropy.toFixed(6)} />
        {details.feature_evidence?.map((evidence) => (
          <DetailRow
            key={evidence.feature}
            label={`${evidence.feature.replaceAll('_', ' ')} evidence`}
            value={`closer to ${evidence.closer_to}`}
          />
        ))}
      </div>

      <div className="analysis-meta">
        <span>{quality?.duration_seconds ?? 'n/a'}s · {quality?.sample_rate ?? 'n/a'} Hz</span>
        <span>{processingMs ?? 'n/a'} ms · {modelVersion ?? 'unknown model'}</span>
      </div>
      {quality?.warnings?.length > 0 && (
        <div className="quality-warning">Audio quality warning: {quality.warnings.join(', ')}</div>
      )}
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
