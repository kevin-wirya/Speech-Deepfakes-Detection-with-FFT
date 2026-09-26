"""
Flask Web API for Deepfake Detection
Audio deepfake detection using FFT Phase Geometry & Complex Linear Algebra
"""

from flask import Flask, request, jsonify, g, send_file
from flask_cors import CORS
import os
import tempfile
import time
import uuid
import numpy as np
from pathlib import Path

from detector import DeepfakeDetector
from reference_stats import compute_and_save_reference_stats

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 25 * 1024 * 1024
allowed_origins = [origin.strip() for origin in os.getenv(
    'ALLOWED_ORIGINS',
    'http://localhost:5173,http://127.0.0.1:5173'
).split(',') if origin.strip()]
CORS(app, resources={r'/*': {'origins': allowed_origins}})

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
REFERENCE_STATS_FILE = 'reference_stats.json'
TEST_DATASET_DIR = Path(__file__).resolve().parents[2] / 'test'
MIN_DURATION_SECONDS = 1.0
MAX_DURATION_SECONDS = 30.0

# Global detector instance
detector = None


@app.before_request
def assign_request_id():
    g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))


@app.after_request
def add_request_id(response):
    response.headers['X-Request-ID'] = g.get('request_id', 'unknown')
    return response

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def resolve_test_dataset_path(relative_path):
    requested_path = (TEST_DATASET_DIR / relative_path).resolve()
    try:
        requested_path.relative_to(TEST_DATASET_DIR.resolve())
    except ValueError:
        raise ValueError('Invalid dataset path.')
    if not requested_path.is_file() or requested_path.suffix.lower() not in {'.wav', '.mp3'}:
        raise FileNotFoundError('Dataset audio file not found.')
    return requested_path


def inspect_audio(filepath):
    signal, sample_rate = detector.processor.load_wav(filepath)
    duration_seconds = len(signal) / sample_rate if sample_rate else 0

    if duration_seconds < MIN_DURATION_SECONDS:
        raise ValueError(f'Audio is too short. Minimum duration is {MIN_DURATION_SECONDS:g} seconds.')
    if duration_seconds > MAX_DURATION_SECONDS:
        raise ValueError(f'Audio is too long. Maximum duration is {MAX_DURATION_SECONDS:g} seconds.')
    if signal.size == 0 or not signal.any() or float(abs(signal).max()) < 1e-5:
        raise ValueError('Audio is silent or empty.')
    if not np.isfinite(signal).all():
        raise ValueError('Audio contains invalid numeric samples.')
    if not signal.dtype.kind == 'f' or not signal.size:
        raise ValueError('Audio signal could not be decoded.')

    return {
        'duration_seconds': round(float(duration_seconds), 3),
        'sample_rate': int(sample_rate),
        'channels': 1,
        'warnings': ['Audio contains clipping'] if float(abs(signal).max()) >= 0.999 else []
    }

def initialize_detector():
    global detector
    
    # Check if reference stats exist
    if not os.path.exists(REFERENCE_STATS_FILE):
        print("\nReference statistics not found.")
        print("Computing reference statistics from dataset...")
        print("This may take a few minutes...\n")
        
        try:
            compute_and_save_reference_stats(
                human_dir='../../data/human',
                nonhuman_dir='../../data/nonhuman',
                output_file=REFERENCE_STATS_FILE
            )
            print(f"\n[SUCCESS] Reference statistics saved to {REFERENCE_STATS_FILE}")
        except Exception as e:
            print(f"\n[ERROR] Failed to compute reference statistics: {str(e)}")
            return False
    
    try:
        detector = DeepfakeDetector(REFERENCE_STATS_FILE)
        print(f"[SUCCESS] Detector initialized with {REFERENCE_STATS_FILE}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to initialize detector: {str(e)}")
        return False


@app.route('/status', methods=['GET'])
def status():
    if detector is None:
        return jsonify({
            'status': 'not_ready',
            'message': 'Detector not initialized'
        }), 503
    
    stats = detector.get_reference_statistics()
    return jsonify({
        'status': 'ready',
        'model_version': 'fft-geometry-v1',
        'reference_statistics': {
            'human_phase_coherence_mean': stats['human']['phase_coherence']['mean'],
            'ai_phase_coherence_mean': stats['ai']['phase_coherence']['mean']
        }
    })


@app.route('/test-datasets', methods=['GET'])
def list_test_datasets():
    datasets = []
    if TEST_DATASET_DIR.exists():
        for filepath in sorted(TEST_DATASET_DIR.rglob('*')):
            if filepath.is_file() and filepath.suffix.lower() in {'.wav', '.mp3'}:
                relative_path = filepath.relative_to(TEST_DATASET_DIR).as_posix()
                category = relative_path.split('/', 1)[0]
                datasets.append({
                    'path': relative_path,
                    'name': filepath.name,
                    'category': category,
                    'label': 'human' if category.lower() == 'human' else 'ai',
                    'condition': category
                })
    return jsonify({'datasets': datasets})


@app.route('/test-datasets/<path:relative_path>', methods=['GET'])
def download_test_dataset(relative_path):
    try:
        dataset_path = resolve_test_dataset_path(relative_path)
    except (ValueError, FileNotFoundError) as error:
        return jsonify({'error': str(error)}), 404
    return send_file(dataset_path, conditional=True)


@app.route('/predict', methods=['POST'])
def predict():
    started_at = time.perf_counter()
    # Check if detector is initialized
    if detector is None:
        return jsonify({
            'success': False,
            'error': 'Detector not initialized. Please try again.'
        }), 503
    
    # Check if file is in request
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'No file part in the request'
        }), 400
    
    file = request.files['file']
    
    # Check if file was selected
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'No file selected'
        }), 400
    
    # Check file extension
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': 'Invalid file format. Please upload a WAV or MP3 file.'
        }), 400
    
    temp_path = None
    try:
        extension = os.path.splitext(file.filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=extension, dir=UPLOAD_FOLDER) as temp_file:
            temp_path = temp_file.name
        file.save(temp_path)

        quality = inspect_audio(temp_path)

        # Run prediction
        result = detector.predict(temp_path, verbose=False)

        # Format response
        return jsonify({
            'request_id': g.request_id,
            'success': True,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'decision': result['decision'],
            'score_type': result['score_type'],
            'uncertainty': result['uncertainty'],
            'processing_ms': round((time.perf_counter() - started_at) * 1000, 2),
            'details': {
                'phase_coherence': result['phase_coherence'],
                'distance_to_human': result['distance_to_human'],
                'distance_to_ai': result['distance_to_ai'],
                'phase_velocity': result['phase_velocity'],
                'spectral_entropy': result['spectral_entropy'],
                'spectral_l2_norm': result['spectral_l2_norm'],
                'feature_evidence': result['feature_evidence']
            },
            'quality': quality,
            'model_version': 'fft-geometry-v1'
        }), 200
    except ValueError as e:
        return jsonify({
            'request_id': g.request_id,
            'success': False,
            'error': str(e)
        }), 422
    
    except Exception as e:
        return jsonify({
            'request_id': g.request_id,
            'success': False,
            'error': 'The audio could not be analyzed. Please check the file and try again.'
        }), 500
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.route('/stats', methods=['GET'])
def get_stats():
    if detector is None:
        return jsonify({
            'error': 'Detector not initialized'
        }), 503
    
    stats = detector.get_reference_statistics()
    return jsonify(stats)


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500


@app.errorhandler(413)
def request_too_large(error):
    return jsonify({
        'success': False,
        'error': 'File is too large. Maximum upload size is 25 MB.'
    }), 413


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("DEEPFAKE DETECTION API - Initialization")
    print("=" * 70)
    print("\n[STEP 1] Initializing Detector...")
    
    success = initialize_detector()
    
    if success:
        print("\n[STEP 2] Starting Flask Server...")
        print("\n" + "=" * 70)
        print("API is running!")
        print("=" * 70)
        print("\nEndpoints:")
        print("  POST /predict             - Deepfake detection")
        print("  GET  /status              - Check API status")
        print("  GET  /stats               - Reference statistics")
        print("\nBackend: http://localhost:5000")
        print("Frontend: http://localhost:5173")
        print("=" * 70 + "\n")
        
        app.run(debug=False, host=os.getenv('HOST', '0.0.0.0'), port=int(os.getenv('PORT', '5000')))
    else:
        print("\n[FATAL] Failed to initialize detector.")
        print("Make sure the dataset folders exist:")
        print("  - ../data/human/")
        print("  - ../data/nonhuman/")


if os.getenv('INITIALIZE_DETECTOR_ON_IMPORT') == '1' and detector is None:
    initialize_detector()
