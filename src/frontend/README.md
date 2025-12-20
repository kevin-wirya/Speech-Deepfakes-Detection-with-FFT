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

Open http://localhost:5173 in your browser.

## Building for Production

```bash
npm run build
npm run preview
```

## Styling

All styles are written in vanilla CSS with animations, gradients, and responsive design.
