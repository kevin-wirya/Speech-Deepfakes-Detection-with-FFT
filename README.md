# 🕵🏻 Audio Deepfake Detection System

![Conan](doc/img/conan.jpeg)

Speech Deepfakes Detection Website with FFT using Complex Linear Algebra

## Project Structure

```

doc/
├── main.tex      # Main LaTeX document (root file)
├── chapters/     # Chapter content files
├── img/          # Images and figures
└── main.pdf      # Compiled paper in pdf format

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
├── human/      # Human speech training datasets
└── nonhuman/   # AI-generated training datasets

test/
├── human/            # Human speech test cases
├── nonhuman-sim/     # AI-generated test cases (speed)
├── nonhuman-stab/    # AI-generated test cases (stability)
└── nonhuman-sim/     # AI-generated test cases (similarity)
```

## Quick Start

### Docker Compose (recommended)

Requirements: Docker Desktop with Compose enabled.

From the project root:

```bash
docker compose up --build
```

Open http://localhost:5173. The stack contains the Flask API, detector initialization, production frontend build, and Nginx API proxy. Stop it with `Ctrl+C`; remove the containers with:

```bash
docker compose down
```

### Local development

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

### Deploy to Vercel

Frontend sekarang menjalankan decoding audio, FFT, feature extraction, dan geometric scoring langsung di browser. Karena itu demo utama tidak membutuhkan backend Flask, Railway, atau Docker.

1. Push repository ini ke GitHub.
2. Di Vercel pilih **Add New Project** -> **Import Git Repository**.
3. Pilih repository GitHub ini dan set **Root Directory** ke `src/frontend`.
4. Pastikan Framework Preset adalah **Vite**.
5. Set `VITE_DATASET_BASE_URL` ke `https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/test`.
6. Deploy. Push berikutnya ke branch production akan memicu deployment otomatis.

Konfigurasi Vercel tersedia di `src/frontend/vercel.json`, template variable tersedia di `src/frontend/.env.example`, dan manifest dataset tersedia di `src/frontend/public/test-datasets.json`.

## Technology Stack

- **Backend**: Flask, NumPy, SciPy, Librosa
- **Frontend**: React 18, Vite, CSS
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
