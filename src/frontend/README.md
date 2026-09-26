# Audio Deepfake Detection System - React Frontend

Modern React-based web interface for the Audio Deepfake Detection System using mathematical analysis (FFT Phase Geometry & Complex Linear Algebra).

## Features

- **Modern React Framework**: Built with React 18 and Vite for optimal performance
- **Component-Based Architecture**: Clean separation of concerns with reusable components
- **Real-time Audio Analysis**: Upload WAV/MP3 files and get instant deepfake detection results
- **Beautiful UI**: Gradient animations, smooth transitions, and responsive design
- **Audio Preview**: Listen to uploaded audio before analysis
- **Detailed Metrics**: View technical metrics including phase coherence, distances, and spectral properties
- **Drag & Drop Upload**: Intuitive file upload with drag-and-drop support
- **Test Dataset Picker**: Select labeled WAV/MP3 samples directly from the repository `test/` folder

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Header.jsx           # Application header with title and badges
│   │   ├── UploadArea.jsx       # File upload with drag & drop
│   │   ├── AudioPlayer.jsx      # Audio playback controls
│   │   ├── StatusMessage.jsx    # Status notifications
│   │   ├── ButtonGroup.jsx      # Predict and Clear buttons
│   │   ├── ResultContainer.jsx  # Results display with metrics
│   │   ├── Disclaimer.jsx       # Legal disclaimer
│   │   └── ParticleBackground.jsx # Animated background
│   ├── App.jsx                   # Main application component
│   ├── App.css                   # Application styles
│   ├── index.css                 # Global styles
│   └── main.jsx                  # Entry point
├── vite.config.js                # Vite configuration with API proxy
├── package.json                  # Dependencies
├── index.html                    # HTML template
└── README.md
```

## Components Overview

### Header

- Displays application title with gradient effect
- Shows badges for "No Neural Networks" and "Pure Mathematics"
- Subtitle explaining the mathematical foundation

### UploadArea

- Drag-and-drop file upload
- Click to browse files
- Validates file format (WAV/MP3 only)
- Visual feedback for drag states

### AudioPlayer

- Embedded audio player for uploaded files
- Allows users to listen before analysis
- Standard HTML5 controls

### StatusMessage

- Displays loading, success, and error messages
- Animated appearance with appropriate color coding
- Auto-hides after 3 seconds for success messages

### ResultContainer

- Shows prediction result (HUMAN or AI-GENERATED)
- Animated confidence bar with gradient colors
- Technical details panel with 6 key metrics

## State Management

The application uses React hooks for state management with useState and useEffect.

## API Integration

The frontend communicates with the Flask backend via API endpoints with Vite proxy configuration.

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

From the `src/frontend` directory, `npm run dev` starts both the Flask backend and the Vite frontend concurrently. The application is available at http://localhost:5173. The test dataset picker is populated by the backend endpoint and uses the same preview and analysis flow as uploaded files.

The combined command uses the existing backend quick-start flow with `--no-install`. Install backend dependencies once before running it:

```bash
cd ../backend
python -m pip install -r requirements.txt
cd ../frontend
npm install
npm run dev
```

To run only one service when debugging, use `npm run dev:frontend` or `npm run dev:backend`.

## Docker Compose

The recommended showcase command is from the project root:

```bash
docker compose up --build
```

Then open http://localhost:5173. Docker runs the Flask API and the production frontend together, with Nginx forwarding API requests to the backend container.

## Vercel Deployment

Push the repository to GitHub, then import it from Vercel. Set the Vercel project **Root Directory** to `src/frontend` and set:

```text
VITE_API_BASE_URL=https://your-public-backend.example.com
```

The Flask backend can be deployed separately on Railway using the repository `railway.json`. Set its `ALLOWED_ORIGINS` environment variable to the Vercel domain. The backend must also include `test/` if the test dataset picker is needed in the deployed demo.

## Building for Production

```bash
npm run build
npm run preview
```

## Styling

All styles are written in vanilla CSS with animations, gradients, and responsive design.
