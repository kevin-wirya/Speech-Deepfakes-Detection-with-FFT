"""
Reference Statistics Module
Computes baseline statistics from human and AI-generated speech datasets.
The classifier decision rule: if C(x) > θ -> Human else -> AI
"""

import os
import numpy as np
from pathlib import Path
from signal_processor import AudioSignalProcessor
import json

class ReferenceStatisticsComputer:
    def __init__(self, human_dir, nonhuman_dir):
        self.human_dir = Path(human_dir)
        self.nonhuman_dir = Path(nonhuman_dir)
        self.processor = AudioSignalProcessor()
    
    def get_wav_files(self, directory):
        audio_files = []
        if os.path.exists(directory):
            audio_files = list(Path(directory).glob('**/*.wav'))
            audio_files += list(Path(directory).glob('**/*.mp3'))
        return sorted(audio_files)
    
    def compute_statistics(self, verbose=True):
        stats = {
            'human': {'coherences': [], 'velocities': [], 'entropies': []},
            'nonhuman': {'coherences': [], 'velocities': [], 'entropies': []}
        }
        # Process human speech
        if verbose:
            print("=" * 70)
            print("PROCESSING HUMAN SPEECH DATASET")
            print("=" * 70)
        human_files = self.get_wav_files(self.human_dir)
        if verbose:
            print(f"Found {len(human_files)} human speech files\n")
        for filepath in human_files:
            try:
                if verbose:
                    print(f"Processing: {filepath.name}", end=" → ")
                features = self.processor.extract_all_features(str(filepath))
                stats['human']['coherences'].append(features['phase_coherence'])
                stats['human']['velocities'].append(features['phase_velocity'])
                stats['human']['entropies'].append(features['spectral_entropy'])
                if verbose:
                    print(f"Coherence: {features['phase_coherence']:.4f}")
            except Exception as e:
                if verbose:
                    print(f"ERROR: {str(e)}")
        
        # Process AI-generated speech
        if verbose:
            print("\n" + "=" * 70)
            print("PROCESSING AI-GENERATED SPEECH DATASET")
            print("=" * 70)
        nonhuman_files = self.get_wav_files(self.nonhuman_dir)
        if verbose:
            print(f"Found {len(nonhuman_files)} AI-generated speech files\n")
        for filepath in nonhuman_files:
            try:
                if verbose:
                    print(f"Processing: {filepath.name}", end=" → ")
                features = self.processor.extract_all_features(str(filepath))
                stats['nonhuman']['coherences'].append(features['phase_coherence'])
                stats['nonhuman']['velocities'].append(features['phase_velocity'])
                stats['nonhuman']['entropies'].append(features['spectral_entropy'])
                if verbose:
                    print(f"Coherence: {features['phase_coherence']:.4f}")
            except Exception as e:
                if verbose:
                    print(f"ERROR: {str(e)}")
        
        # Compute aggregate statistics
        if verbose:
            print("\n" + "=" * 70)
            print("COMPUTED STATISTICS")
            print("=" * 70)
        
        result = {}
        
        for label in ['human', 'nonhuman']:
            coherences = np.array(stats[label]['coherences'])
            velocities = np.array(stats[label]['velocities'])
            entropies = np.array(stats[label]['entropies'])
            
            result[label] = {
                'phase_coherence': {
                    'mean': float(np.mean(coherences)) if len(coherences) > 0 else 0.0,
                    'std': float(np.std(coherences)) if len(coherences) > 0 else 0.0,
                    'min': float(np.min(coherences)) if len(coherences) > 0 else 0.0,
                    'max': float(np.max(coherences)) if len(coherences) > 0 else 0.0,
                    'count': len(coherences)
                },
                'phase_velocity': {
                    'mean': float(np.mean(velocities)) if len(velocities) > 0 else 0.0,
                    'std': float(np.std(velocities)) if len(velocities) > 0 else 0.0,
                    'count': len(velocities)
                },
                'spectral_entropy': {
                    'mean': float(np.mean(entropies)) if len(entropies) > 0 else 0.0,
                    'std': float(np.std(entropies)) if len(entropies) > 0 else 0.0,
                    'count': len(entropies)
                }
            }
            
            if verbose:
                print(f"\n{label.upper()} SPEECH (N={len(coherences)})")
                print(f"  Phase Coherence:")
                print(f"    μ = {result[label]['phase_coherence']['mean']:.4f}")
                print(f"    σ = {result[label]['phase_coherence']['std']:.4f}")
                print(f"    range = [{result[label]['phase_coherence']['min']:.4f}, {result[label]['phase_coherence']['max']:.4f}]")
                print(f"  Phase Velocity:")
                print(f"    μ = {result[label]['phase_velocity']['mean']:.4f}")
                print(f"    σ = {result[label]['phase_velocity']['std']:.4f}")
                print(f"  Spectral Entropy:")
                print(f"    μ = {result[label]['spectral_entropy']['mean']:.4f}")
                print(f"    σ = {result[label]['spectral_entropy']['std']:.4f}")
        
        # Compute decision threshold
        mu_h = result['human']['phase_coherence']['mean']
        mu_ai = result['nonhuman']['phase_coherence']['mean']
        threshold = (mu_h + mu_ai) / 2.0
        
        result['decision_threshold'] = float(threshold)
        
        if verbose:
            print(f"\n" + "=" * 70)
            print(f"DECISION THRESHOLD (Midpoint Rule)")
            print(f"=" * 70)
            print(f"  μ(human) = {mu_h:.4f}")
            print(f"  μ(AI)    = {mu_ai:.4f}")
            print(f"  Threshold θ = {threshold:.4f}")
            print(f"\nDecision Rule:")
            print(f"  if C(x) > θ -> HUMAN")
            print(f"  if C(x) ≤ θ -> AI-GENERATED")
            print("=" * 70 + "\n")
        
        return result
    
    def save_statistics(self, stats, filepath='reference_stats.json'):
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        print(f"Statistics saved to {filepath}")
    
    def load_statistics(self, filepath='reference_stats.json'):
        with open(filepath, 'r') as f:
            return json.load(f)


def compute_and_save_reference_stats(human_dir='../../data/human', 
                                      nonhuman_dir='../../data/nonhuman',
                                      output_file='reference_stats.json'):
    computer = ReferenceStatisticsComputer(human_dir, nonhuman_dir)
    stats = computer.compute_statistics(verbose=True)
    computer.save_statistics(stats, output_file)
    return stats


if __name__ == '__main__':
    compute_and_save_reference_stats()
