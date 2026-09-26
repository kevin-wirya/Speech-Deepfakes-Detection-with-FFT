const referenceStats = {
  human: {
    phase_coherence: { mean: 0.3739498555660248, std: 0.08684681355953217 },
    phase_velocity: { mean: 1.578946828842163, std: 0.24255967140197754 },
    spectral_entropy: { mean: 10.832244873046875, std: 0.8368511199951172 }
  },
  ai: {
    phase_coherence: { mean: 0.39510607719421387, std: 0.10052265971899033 },
    phase_velocity: { mean: 1.5598325729370117, std: 0.2486287656406197 },
    spectral_entropy: { mean: 11.283088684082031, std: 0.7735753059387207 }
  }
};

const weights = {
  spectral_entropy: 0.8,
  phase_coherence: 0.1,
  phase_velocity: 0.1
};

function nextPowerOfTwo(value) {
  let size = 1;
  while (size < value) size *= 2;
  return size;
}

function fft(signal) {
  const size = nextPowerOfTwo(signal.length);
  const real = new Float64Array(size);
  const imaginary = new Float64Array(size);
  real.set(signal);

  for (let index = 1, reverse = 0; index < size; index += 1) {
    let bit = size >> 1;
    for (; reverse & bit; bit >>= 1) reverse ^= bit;
    reverse ^= bit;
    if (index < reverse) {
      [real[index], real[reverse]] = [real[reverse], real[index]];
    }
  }

  for (let length = 2; length <= size; length <<= 1) {
    const angle = -2 * Math.PI / length;
    const half = length >> 1;
    for (let start = 0; start < size; start += length) {
      for (let offset = 0; offset < half; offset += 1) {
        const phase = angle * offset;
        const cosine = Math.cos(phase);
        const sine = Math.sin(phase);
        const even = start + offset;
        const odd = even + half;
        const oddReal = real[odd] * cosine - imaginary[odd] * sine;
        const oddImaginary = real[odd] * sine + imaginary[odd] * cosine;
        real[odd] = real[even] - oddReal;
        imaginary[odd] = imaginary[even] - oddImaginary;
        real[even] += oddReal;
        imaginary[even] += oddImaginary;
      }
    }
  }

  return { real, imaginary, size };
}

function resample(signal, sourceRate, targetRate) {
  if (sourceRate === targetRate) return signal;
  const outputLength = Math.max(1, Math.round(signal.length * targetRate / sourceRate));
  const output = new Float32Array(outputLength);
  const ratio = sourceRate / targetRate;
  for (let index = 0; index < outputLength; index += 1) {
    const sourceIndex = index * ratio;
    const lower = Math.floor(sourceIndex);
    const upper = Math.min(lower + 1, signal.length - 1);
    const fraction = sourceIndex - lower;
    output[index] = signal[lower] * (1 - fraction) + signal[upper] * fraction;
  }
  return output;
}

function extractFeatures(signal) {
  const { real, imaginary, size } = fft(signal);
  const halfSize = Math.floor(size / 2);
  const magnitude = new Float64Array(halfSize);
  const phase = new Float64Array(halfSize);
  for (let index = 0; index < halfSize; index += 1) {
    magnitude[index] = Math.hypot(real[index], imaginary[index]);
    phase[index] = Math.atan2(imaginary[index], real[index]);
  }

  const coherenceValues = [];
  for (let index = 0; index < phase.length - 5; index += 1) {
    let realSum = 0;
    let imaginarySum = 0;
    for (let offset = 0; offset < 5; offset += 1) {
      realSum += Math.cos(phase[index + offset]);
      imaginarySum += Math.sin(phase[index + offset]);
    }
    coherenceValues.push(Math.hypot(realSum, imaginarySum) / 5);
  }
  const phaseCoherence = coherenceValues.reduce((sum, value) => sum + value, 0) / Math.max(1, coherenceValues.length);

  let phaseVelocity = 0;
  for (let index = 1; index < phase.length; index += 1) {
    let difference = phase[index] - phase[index - 1];
    difference = Math.atan2(Math.sin(difference), Math.cos(difference));
    phaseVelocity += Math.abs(difference);
  }
  phaseVelocity /= Math.max(1, phase.length - 1);

  const totalMagnitude = magnitude.reduce((sum, value) => sum + value, 0);
  const spectralEntropy = magnitude.reduce((sum, value) => {
    const probability = (value + 1e-10) / (totalMagnitude + 1e-10);
    return sum - probability * Math.log(probability);
  }, 0);
  let spectralL2Norm = 0;
  for (let index = 0; index < magnitude.length; index += 1) {
    spectralL2Norm += magnitude[index] ** 2;
  }
  spectralL2Norm = Math.sqrt(spectralL2Norm);

  return { phaseCoherence, phaseVelocity, spectralEntropy, spectralL2Norm };
}

function classify(features) {
  const featureNames = ['phase_coherence', 'phase_velocity', 'spectral_entropy'];
  const featureValues = {
    phase_coherence: features.phaseCoherence,
    phase_velocity: features.phaseVelocity,
    spectral_entropy: features.spectralEntropy
  };
  const humanParts = [];
  const aiParts = [];
  const featureEvidence = [];

  featureNames.forEach((feature) => {
    const value = featureValues[feature];
    const humanDistance = Math.abs(value - referenceStats.human[feature].mean) / (referenceStats.human[feature].std + 1e-6);
    const aiDistance = Math.abs(value - referenceStats.ai[feature].mean) / (referenceStats.ai[feature].std + 1e-6);
    humanParts.push(weights[feature] * humanDistance);
    aiParts.push(weights[feature] * aiDistance);
    featureEvidence.push({
      feature,
      value,
      human_distance: humanDistance,
      ai_distance: aiDistance,
      weight: weights[feature],
      closer_to: aiDistance < humanDistance ? 'ai' : 'human'
    });
  });

  const distanceToHuman = Math.hypot(...humanParts);
  const distanceToAi = Math.hypot(...aiParts);
  const confidence = Math.max(0, Math.min(1, 1 - Math.min(distanceToHuman, distanceToAi) / (Math.max(distanceToHuman, distanceToAi) + 1e-6)));
  const prediction = distanceToAi < distanceToHuman ? 'ai' : 'human';
  const decision = confidence < 0.2 ? 'uncertain' : `${prediction}_likely`;

  return {
    prediction,
    confidence,
    decision,
    score_type: 'relative_distance_score',
    uncertainty: 1 - confidence,
    details: {
      phase_coherence: features.phaseCoherence,
      distance_to_human: distanceToHuman,
      distance_to_ai: distanceToAi,
      phase_velocity: features.phaseVelocity,
      spectral_entropy: features.spectralEntropy,
      spectral_l2_norm: features.spectralL2Norm,
      feature_evidence: featureEvidence
    }
  };
}

export async function analyzeAudioFile(file) {
  const audioContext = new (window.AudioContext || window.webkitAudioContext)();
  try {
    const audioBuffer = await audioContext.decodeAudioData(await file.arrayBuffer());
    const durationSeconds = audioBuffer.duration;
    if (durationSeconds < 1 || durationSeconds > 30) {
      throw new Error('Audio duration must be between 1 and 30 seconds.');
    }

    const channelData = Array.from({ length: audioBuffer.numberOfChannels }, (_, channel) => audioBuffer.getChannelData(channel));
    const monoSignal = new Float32Array(audioBuffer.length);
    for (let index = 0; index < audioBuffer.length; index += 1) {
      monoSignal[index] = channelData.reduce((sum, channel) => sum + channel[index], 0) / channelData.length;
    }
    let peak = 0;
    for (let index = 0; index < monoSignal.length; index += 1) {
      peak = Math.max(peak, Math.abs(monoSignal[index]));
    }
    if (!peak || peak < 1e-5) throw new Error('Audio is silent or empty.');
    const normalized = Float32Array.from(monoSignal, (value) => value / peak);
    const signal = resample(normalized, audioBuffer.sampleRate, 16000);
    const features = extractFeatures(signal);
    const result = classify(features);

    return {
      success: true,
      ...result,
      quality: {
        duration_seconds: Number(durationSeconds.toFixed(3)),
        sample_rate: 16000,
        channels: audioBuffer.numberOfChannels,
        warnings: peak >= 0.999 ? ['Audio contains clipping'] : []
      },
      processing_ms: 0,
      model_version: 'fft-geometry-browser-v1'
    };
  } finally {
    await audioContext.close();
  }
}
