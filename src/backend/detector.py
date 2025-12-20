"""
Deepfake Detection Classifier
Based on Geometric Distance and Threshold Decision Rules
Output: Class label + confidence score based on geometric distance
"""

import json
import numpy as np
from pathlib import Path
from signal_processor import AudioSignalProcessor


class DeepfakeDetector:
    def __init__(self, reference_stats_file='reference_stats.json'):
        self.processor = AudioSignalProcessor()
        self.stats = self._load_stats(reference_stats_file)
        self.threshold = self.stats['decision_threshold']
        # Extract statistics for distance computation
        self.human_stats = self.stats['human']['phase_coherence']
        self.ai_stats = self.stats['nonhuman']['phase_coherence']
    
    def _load_stats(self, filepath):
        if not Path(filepath).exists():
            raise FileNotFoundError(
                f"Reference statistics file not found: {filepath}\n"
                "Run: python reference_stats.py to generate statistics."
            )
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _compute_geometric_distance(self, phase_coherence):
        mu_h = self.human_stats['mean']
        sigma_h = self.human_stats['std'] + 1e-6  # Avoid division by zero
        
        mu_ai = self.ai_stats['mean']
        sigma_ai = self.ai_stats['std'] + 1e-6
        
        # Standardized distances
        d_human = np.abs(phase_coherence - mu_h) / sigma_h
        d_ai = np.abs(phase_coherence - mu_ai) / sigma_ai
        
        # Confidence computing
        min_dist = min(d_human, d_ai)
        max_dist = max(d_human, d_ai)
        confidence = 1.0 - (min_dist / (max_dist + 1e-6))
        
        return d_human, d_ai, confidence
    
    def predict(self, audio_filepath, verbose=False):
        # Extract features
        features = self.processor.extract_all_features(audio_filepath)
        phase_coherence = features['phase_coherence']
        
        # Decision using threshold
        if phase_coherence > self.threshold:
            primary_prediction = 'human'
        else:
            primary_prediction = 'ai'
        
        # Compute geometric distances
        d_h, d_ai, confidence = self._compute_geometric_distance(phase_coherence)
        
        result = {
            'prediction': primary_prediction,
            'confidence': float(confidence),
            'phase_coherence': float(phase_coherence),
            'threshold': float(self.threshold),
            'distance_to_human': float(d_h),
            'distance_to_ai': float(d_ai),
            'phase_velocity': float(features['phase_velocity']),
            'spectral_entropy': float(features['spectral_entropy']),
            'spectral_l2_norm': float(features['spectral_l2_norm'])
        }
        
        return result
    
    def predict_batch(self, audio_files_list, verbose=False):
        predictions = []
        for filepath in audio_files_list:
            try:
                result = self.predict(filepath, verbose=verbose)
                result['filepath'] = str(filepath)
                predictions.append(result)
            except Exception as e:
                predictions.append({
                    'filepath': str(filepath),
                    'error': str(e),
                    'prediction': None,
                    'confidence': None
                })
        
        return predictions
    
    def get_reference_statistics(self):
        return {
            'human': self.human_stats,
            'ai': self.ai_stats,
            'threshold': self.threshold
        }


def create_detector(reference_stats_file='reference_stats.json'):
    return DeepfakeDetector(reference_stats_file)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python detector.py <audio_file.wav>")
        sys.exit(1)
    
    detector = DeepfakeDetector()
    result = detector.predict(sys.argv[1])
    print(f"\nPrediction: {result['prediction']} (confidence: {result['confidence']:.1%})")
