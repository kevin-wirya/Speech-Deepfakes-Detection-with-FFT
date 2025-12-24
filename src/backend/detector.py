"""
Deepfake Detection Classifier
Based on Geometric Distance
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
        # Extract statistics for all three metrics
        self.human_stats = {
            'phase_coherence': self.stats['human']['phase_coherence'],
            'phase_velocity': self.stats['human']['phase_velocity'],
            'spectral_entropy': self.stats['human']['spectral_entropy']
        }
        self.ai_stats = {
            'phase_coherence': self.stats['nonhuman']['phase_coherence'],
            'phase_velocity': self.stats['nonhuman']['phase_velocity'],
            'spectral_entropy': self.stats['nonhuman']['spectral_entropy']
        }
    
    def _load_stats(self, filepath):
        if not Path(filepath).exists():
            raise FileNotFoundError(
                f"Reference statistics file not found: {filepath}\n"
                "Run: python reference_stats.py to generate statistics."
            )
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def _compute_geometric_distance(self, features):
        # Weights based on discriminative power
        weights = {
            'spectral_entropy': 0.80,    # Highest weight
            'phase_coherence': 0.10,     # Medium weight
            'phase_velocity': 0.10       # Lower weight
        }
        
        distances_human = []
        distances_ai = []
        
        metrics = ['phase_coherence', 'phase_velocity', 'spectral_entropy']
        
        for metric in metrics:
            value = features[metric]
            
            mu_h = self.human_stats[metric]['mean']
            sigma_h = self.human_stats[metric]['std'] + 1e-6
            
            mu_ai = self.ai_stats[metric]['mean']
            sigma_ai = self.ai_stats[metric]['std'] + 1e-6
            
            # Standardized distances per metric
            d_h = np.abs(value - mu_h) / sigma_h
            d_ai = np.abs(value - mu_ai) / sigma_ai
            
            # Apply weights
            weight = weights[metric]
            distances_human.append(weight * d_h)
            distances_ai.append(weight * d_ai)
        
        # Weighted Euclidean distance
        d_human = np.sqrt(np.sum(np.array(distances_human)**2))
        d_ai = np.sqrt(np.sum(np.array(distances_ai)**2))
        
        # Confidence based on relative distances
        min_dist = min(d_human, d_ai)
        max_dist = max(d_human, d_ai)
        confidence = 1.0 - (min_dist / (max_dist + 1e-6))
        
        return d_human, d_ai, confidence
    
    def predict(self, audio_filepath, verbose=False):
        # Extract features
        features = self.processor.extract_all_features(audio_filepath)
        
        # Compute geometric distances
        d_h, d_ai, confidence = self._compute_geometric_distance(features)
        
        # Decision using geometric distance
        if d_ai < d_h:
            primary_prediction = 'ai'
        else:
            primary_prediction = 'human'
        
        result = {
            'prediction': primary_prediction,
            'confidence': float(confidence),
            'phase_coherence': float(features['phase_coherence']),
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
            'ai': self.ai_stats
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
