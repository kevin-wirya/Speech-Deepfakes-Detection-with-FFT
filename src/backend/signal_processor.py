"""
Signal Processing Module for Audio Deepfake Detection
NOTE: Uses optimized scipy FFT for performance.
"""

import numpy as np
from scipy.io import wavfile
from scipy.fftpack import fft
import warnings
from pathlib import Path

warnings.filterwarnings('ignore')

# Importing librosa
try:
    import librosa
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False

# Importing pydub
try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False


class AudioSignalProcessor:
    def __init__(self, target_sr=16000):
        self.target_sr = target_sr
    
    def load_wav(self, filepath):
        try:
            filepath = Path(filepath)
            file_ext = filepath.suffix.lower()            
            # Load MP3 files with librosa
            if file_ext == '.mp3':
                if not HAS_LIBROSA:
                    raise ValueError("librosa not installed")
                signal, sr = librosa.load(str(filepath), sr=None, mono=True)
                return signal, sr
            # Load WAV files
            elif file_ext == '.wav':
                sr, signal = wavfile.read(filepath)
                # Convert stereo to mono if needed
                if len(signal.shape) > 1:
                    signal = np.mean(signal, axis=1)
                # Normalize to [-1, 1]
                if signal.dtype in [np.int16, np.int32]:
                    signal = signal.astype(np.float32) / np.max(np.abs(signal))
                else:
                    signal = signal.astype(np.float32)
                return signal, sr
            else:
                raise ValueError(f"Unsupported file format: {file_ext}. Use WAV or MP3.")
        except Exception as e:
            raise ValueError(f"Error loading audio file: {str(e)}")
    
    def compute_spectral_features(self, signal, sr=None):
        # Apply FFT
        X = fft(signal)
        # Keep only positive frequencies
        N = len(X)
        X = X[:N//2]
        # Compute magnitude and phase in polar form
        magnitude = np.abs(X) 
        phase = np.angle(X) 
        # Frequency bins (in Hz)
        if sr is None:
            sr = self.target_sr
        freq = np.fft.fftfreq(N, d=1/sr)[:N//2]
        return {
            'X': X,                         # Complex spectral vector
            'magnitude': magnitude,         # Energy spectrum
            'phase': phase,                 # Phase spectrum
            'freq': freq,                   # Frequency axis
            'N': N                          # Original signal length
        }
    
    def compute_phase_coherence(self, phase, window_size=5):
        try:
            # Remove NaN and infinite values
            phase = np.nan_to_num(phase, nan=0.0, posinf=0.0, neginf=0.0)
            # Ensure phase is valid
            if len(phase) < window_size:
                return 0.5, np.array([0.5])
            
            # Compute coherence in sliding windows
            coherence_bins = []
            for i in range(len(phase) - window_size):
                window_phase = phase[i:i+window_size]
                # Sum phase vectors: Σ exp(j*∠X(k))
                phase_sum = np.abs(np.sum(np.exp(1j * window_phase)))
                # Normalize by window size
                coherence = phase_sum / window_size
                coherence_bins.append(coherence)
            
            # Overall coherence: mean of window coherences
            overall_coherence = np.mean(coherence_bins) if coherence_bins else 0.5
            overall_coherence = np.clip(overall_coherence, 0.0, 1.0)
            
            return overall_coherence, np.array(coherence_bins)
        except Exception as e:
            return 0.5, np.array([0.5])
    
    def compute_phase_velocity(self, phase):
        # Phase difference between adjacent frequency bins
        phase_velocity = np.diff(phase)
        phase_velocity = np.angle(np.exp(1j * phase_velocity))
        # Mean absolute velocity / smoothness metric
        velocity_smoothness = np.mean(np.abs(phase_velocity))
        
        return velocity_smoothness
    
    def compute_spectral_inner_products(self, magnitude):
        # Euclidean norm of magnitude vector
        l2_norm = np.linalg.norm(magnitude, ord=2)
        # Normalized spectral shape (unit vector for cosine similarity)
        if l2_norm > 0:
            spectral_shape = magnitude / l2_norm
        else:
            spectral_shape = magnitude

        # Spectral entropy
        prob = (magnitude + 1e-10) / (np.sum(magnitude) + 1e-10)
        entropy = -np.sum(prob * np.log(prob))
        return {
            'l2_norm': l2_norm,
            'spectral_shape': spectral_shape,
            'entropy': entropy
        }
    
    def extract_all_features(self, filepath):
        # Load signal
        signal, sr = self.load_wav(filepath)
        
        # Spectral features
        spectral = self.compute_spectral_features(signal, sr)
        # Phase coherence, velocity + Spectral entropy
        phase_coherence, _ = self.compute_phase_coherence(spectral['phase'])
        phase_velocity = self.compute_phase_velocity(spectral['phase'])
        geom = self.compute_spectral_inner_products(spectral['magnitude'])
        
        return {
            'signal': signal,
            'sr': sr,
            'magnitude': spectral['magnitude'],
            'phase': spectral['phase'],
            'phase_coherence': phase_coherence,
            'phase_velocity': phase_velocity,
            'spectral_entropy': geom['entropy'],
            'spectral_l2_norm': geom['l2_norm'],
            'spectral_shape': geom['spectral_shape']
        }


def extract_features_from_file(filepath):
    processor = AudioSignalProcessor()
    return processor.extract_all_features(filepath)
