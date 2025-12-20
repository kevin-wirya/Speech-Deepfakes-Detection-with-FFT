# Backend - Python Deepfake Detection API

Flask-based REST API for audio deepfake detection using FFT Phase Geometry and Complex Linear Algebra.

## Files

- **app.py** - Flask REST API server
- **detector.py** - Deepfake classification logic
- **signal_processor.py** - Audio signal processing (FFT, phase coherence)
- **reference_stats.py** - Reference statistics computation
- **quickstart.py** - Setup and initialization script
- **requirements.txt** - Python dependencies

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

```bash
python quickstart.py
```

This will:
1. Check datasets exist
2. Install dependencies
3. Compute reference statistics (if needed)
4. Start Flask API on http://localhost:5000

## API Endpoints

- `POST /predict` - Upload audio file for prediction
- `GET /status` - Check API readiness
- `GET /stats` - Get reference statistics

## With Frontend

Start this backend, then start the React frontend in another terminal:
```bash
cd ../src/frontend
npm run dev
```

Frontend will be on http://localhost:5173
