#!/usr/bin/env python3
"""
Quick-start script for the deepfake detection system.
"""

import os
import sys
import argparse
from pathlib import Path

def check_datasets():
    human_dir = Path('../../data/human')
    nonhuman_dir = Path('../../data/nonhuman')
    
    print("\n" + "="*70)
    print("CHECKING DATASETS")
    print("="*70)
    
    if not human_dir.exists():
        print(f"{human_dir}/ not found")
        return False
    
    human_wav = list(human_dir.glob('*.wav'))
    human_mp3 = list(human_dir.glob('*.mp3'))
    human_files = human_wav + human_mp3
    print(f"{human_dir}/: {len(human_wav)} WAV + {len(human_mp3)} MP3 = {len(human_files)} total files")
    
    if not nonhuman_dir.exists():
        print(f"✗ {nonhuman_dir}/ not found")
        return False
    
    nonhuman_wav = list(nonhuman_dir.glob('*.wav'))
    nonhuman_mp3 = list(nonhuman_dir.glob('*.mp3'))
    nonhuman_files = nonhuman_wav + nonhuman_mp3
    print(f"{nonhuman_dir}/: {len(nonhuman_wav)} WAV + {len(nonhuman_mp3)} MP3 = {len(nonhuman_files)} total files")
    
    if len(human_files) == 0 or len(nonhuman_files) == 0:
        print("\n⚠ At least one dataset is empty!")
        return False
    
    return True

def install_dependencies():
    print("\n" + "="*70)
    print("INSTALLING DEPENDENCIES")
    print("="*70)
    
    try:
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', '-r', 'requirements.txt'])
        print("Dependencies installed")
        return True
    except Exception as e:
        print(f"Failed to install dependencies: {str(e)}")
        return False

def compute_stats():
    print("\n" + "="*70)
    print("COMPUTING REFERENCE STATISTICS")
    print("="*70)
    try:
        from reference_stats import compute_and_save_reference_stats
        stats = compute_and_save_reference_stats()
        print("Statistics computed and saved")
        return True
    except Exception as e:
        print(f"Failed to compute statistics: {str(e)}")
        return False

def start_server():
    print("\n" + "="*70)
    print("STARTING WEB SERVER")
    print("="*70)
    try:
        from app import app, initialize_detector
        
        if not initialize_detector():
            print("Failed to initialize detector")
            return False
        
        print("\nServer starting on http://localhost:5000")
        print("Frontend: http://localhost:5173 (Vite dev server)")
        print("Open frontend URL in your browser\n")
        
        app.run(debug=False, host='localhost', port=5000, use_reloader=False)
        return True
    except Exception as e:
        print(f"Failed to start server: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Deepfake Detection System - Quick Start'
    )
    parser.add_argument('--no-install', action='store_true', 
                       help='Skip dependency installation')
    parser.add_argument('--recompute-stats', action='store_true',
                       help='Recompute reference statistics')
    parser.add_argument('--test-predict', metavar='FILE',
                       help='Test prediction on a file (no server)')
    
    args = parser.parse_args()
    
    print("\n" + "╔" + "="*68 + "╗")
    print("║" + " "*10 + "AUDIO DEEPFAKE DETECTION SYSTEM - BACKEND" + " "*17 + "║")
    print("╚" + "="*68 + "╝\n")
    
    # Test prediction mode
    if args.test_predict:
        try:
            from detector import DeepfakeDetector
            detector = DeepfakeDetector('reference_stats.json')
            result = detector.predict(args.test_predict)
            print(f"\nPrediction: {result['prediction'].upper()}")
            print(f"Confidence: {result['confidence']:.1%}")
            return
        except Exception as e:
            print(f"Error: {str(e)}")
            return
        
    # Normal startup sequence
    if not check_datasets():
        print("\n!!! Dataset check failed !!!")
        sys.exit(1)
    
    if not args.no_install:
        if not install_dependencies():
            print("\n!!! Dependency installation failed !!!")
            sys.exit(1)
    
    if args.recompute_stats or not Path('reference_stats.json').exists():
        if not compute_stats():
            print("\n!!! Statistics computation failed !!!")
            sys.exit(1)
    else:
        print("\n" + "="*70)
        print("REFERENCE STATISTICS")
        print("="*70)
        print("!!! Using existing reference_stats.json !!!")
        print("(Use --recompute-stats to regenerate)")
    
    if start_server():
        print("\n!!! System shutdown !!!")
    else:
        print("\n!!! Server startup failed !!!")
        sys.exit(1)

if __name__ == '__main__':
    main()
