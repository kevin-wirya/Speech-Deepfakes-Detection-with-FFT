"""
Flask Web API for Deepfake Detection
Audio deepfake detection using FFT Phase Geometry & Complex Linear Algebra
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import tempfile
from pathlib import Path
import json

from detector import DeepfakeDetector
from reference_stats import compute_and_save_reference_stats

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
REFERENCE_STATS_FILE = 'reference_stats.json'

# Global detector instance
detector = None

def allowed_file(filename):
    """Validate file extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def initialize_detector():
    """Initialize detector with reference statistics."""
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
    """Check API status and reference statistics."""
    if detector is None:
        return jsonify({
            'status': 'not_ready',
            'message': 'Detector not initialized'
        }), 503
    
    stats = detector.get_reference_statistics()
    return jsonify({
        'status': 'ready',
        'reference_statistics': {
            'human_phase_coherence_mean': stats['human']['mean'],
            'ai_phase_coherence_mean': stats['ai']['mean'],
            'decision_threshold': stats['threshold']
        }
    })


@app.route('/predict', methods=['POST'])
def predict():
    """Predict if uploaded audio is human or AI-generated."""
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
    
    try:
        # Save uploaded file to temporary location
        filename = file.filename
        temp_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_path)
        
        # Run prediction
        result = detector.predict(temp_path, verbose=False)

        # Clean up
        os.remove(temp_path)
        
        # Format response
        return jsonify({
            'success': True,
            'prediction': result['prediction'],
            'confidence': result['confidence'],
            'details': {
                'phase_coherence': result['phase_coherence'],
                'threshold': result['threshold'],
                'distance_to_human': result['distance_to_human'],
                'distance_to_ai': result['distance_to_ai'],
                'phase_velocity': result['phase_velocity'],
                'spectral_entropy': result['spectral_entropy'],
                'spectral_l2_norm': result['spectral_l2_norm']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        }), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get reference statistics."""
    if detector is None:
        return jsonify({
            'error': 'Detector not initialized'
        }), 503
    
    stats = detector.get_reference_statistics()
    return jsonify(stats)


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'error': 'Internal server error'
    }), 500


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
        
        app.run(debug=True, host='localhost', port=5000)
    else:
        print("\n[FATAL] Failed to initialize detector.")
        print("Make sure the dataset folders exist:")
        print("  - ../data/human/")
        print("  - ../data/nonhuman/")
