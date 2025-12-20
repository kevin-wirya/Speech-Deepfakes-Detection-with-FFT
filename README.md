# Audio Deepfake Detection System

![Conan](doc/img/conan.jpeg)

Speech Deepfakes Detection Website with FFT using Complex Linear Algebra

## Project Structure

```
src/
├── backend/           # Python Flask API
│   ├── app.py
│   ├── detector.py
│   ├── signal_processor.py
│   ├── reference_stats.py
│   ├── quickstart.py
│   └── requirements.txt
│
└── frontend/          # React + Vite web interface
    ├── src/
    ├── components/
    ├── package.json
    └── vite.config.js

data/
├── human/      # Human speech samples
└── nonhuman/   # AI-generated samples
```

## Quick Start

### Backend
```bash
cd src/backend
python quickstart.py
```

### Frontend
```bash
cd src/frontend
npm install
npm run dev
```
Opens on http://localhost:5173

## Technology Stack

- **Backend**: Flask, NumPy, SciPy, Librosa
- **Frontend**: React 18, Vite, CSS
- **Algorithm**: FFT Phase Geometry, Statistical Classification
- **Audio**: WAV, MP3 support

## Installation

```bash
cd src/backend
pip install -r requirements.txt
```

## Usage

### Web Interface
1. Open http://localhost:5173
2. Upload an audio file (WAV or MP3)
3. Click "Analyze Audio"
4. View prediction with confidence score

## Features

✅ No neural networks - pure mathematics

✅ Fast analysis using FFT

✅ No training needed - uses reference statistics

## Limitations

- Requires good quality audio
- Performance depends on dataset diversity
- Not ideal for heavily compressed audio
- Best for fresh recordings

## Supported Formats

- **Input**: WAV, MP3
- **Sample Rate**: 16kHz or higher recommended
- **Duration**: 2-30 seconds optimal

## License

Educational use - research and learning purposes
