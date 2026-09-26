import { useEffect, useRef, useState } from 'react';
import Header from './components/Header';
import UploadArea from './components/UploadArea';
import AudioPlayer from './components/AudioPlayer';
import StatusMessage from './components/StatusMessage';
import ButtonGroup from './components/ButtonGroup';
import ResultContainer from './components/ResultContainer';
import { analyzeAudioFile } from './lib/browserDetector';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [status, setStatus] = useState({ message: '', type: '' });
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const statusTimerRef = useRef(null);

  useEffect(() => () => {
    if (audioUrl) URL.revokeObjectURL(audioUrl);
    if (statusTimerRef.current) clearTimeout(statusTimerRef.current);
  }, [audioUrl]);

  const showTemporaryStatus = (message, type) => {
    if (statusTimerRef.current) clearTimeout(statusTimerRef.current);
    setStatus({ message, type });
    statusTimerRef.current = setTimeout(() => setStatus({ message: '', type: '' }), 3000);
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setAudioUrl(URL.createObjectURL(file));
    setResult(null);
    showTemporaryStatus('Sample loaded. Ready for analysis.', 'success');
  };

  const handlePredict = async () => {
    if (!selectedFile) return;
    setIsAnalyzing(true);
    if (statusTimerRef.current) clearTimeout(statusTimerRef.current);
    setStatus({ message: 'Extracting spectral features in your browser...', type: 'loading' });
    setResult(null);

    try {
      const data = await analyzeAudioFile(selectedFile);
      setResult(data);
      showTemporaryStatus('Analysis complete.', 'success');
    } catch (error) {
      setStatus({ message: error.message || 'The audio could not be analyzed.', type: 'error' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setAudioUrl(null);
    setResult(null);
    setStatus({ message: '', type: '' });
    if (statusTimerRef.current) clearTimeout(statusTimerRef.current);
  };

  return (
    <div className="app-shell">
      <section className="workspace">
        <main className="dashboard">
          <Header />
          <div className={`dashboard-grid ${result ? 'has-result' : ''}`}>
            <section className="panel analysis-panel">
              <div className="panel-heading">
                <div>
                  <span className="eyebrow">New analysis</span>
                  <h2>Inspect an audio sample</h2>
                </div>
                <span className="panel-index">01</span>
              </div>

              {audioUrl && <AudioPlayer audioUrl={audioUrl} />}
              <UploadArea onFileSelect={handleFileSelect} hasFile={!!selectedFile} onValidationError={(message) => showTemporaryStatus(message, 'error')} />

              {selectedFile && (
                <div className="file-info visible">
                  <div className="file-name"><span className="file-type">WAV</span><strong>{selectedFile.name}</strong></div>
                  <div className="file-size">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</div>
                </div>
              )}

              {status.message && <StatusMessage status={status} />}
              <ButtonGroup onPredict={handlePredict} onClear={handleClear} isAnalyzing={isAnalyzing} hasFile={!!selectedFile} />
            </section>

            {result ? (
              <section className="panel result-panel"><ResultContainer result={result} /></section>
            ) : (
              <section className="panel briefing-panel">
                <div className="panel-heading">
                  <div><span className="eyebrow">How it works</span><h2>Signal-level screening</h2></div>
                  <span className="panel-index">02</span>
                </div>
                <div className="briefing-copy">
                  <p>A lightweight, explainable pass over the audio signal. No upload leaves this browser.</p>
                  <div className="method-row"><span>01</span><div><strong>Decode</strong><small>Normalize and resample to 16 kHz</small></div></div>
                  <div className="method-row"><span>02</span><div><strong>Measure</strong><small>Phase coherence, phase velocity, entropy</small></div></div>
                  <div className="method-row"><span>03</span><div><strong>Compare</strong><small>Distance to human and synthetic references</small></div></div>
                </div>
                <div className="privacy-note"><span>◉</span><div><strong>Local-first processing</strong><small>Audio is analyzed in memory and is not uploaded.</small></div></div>
              </section>
            )}
          </div>
        </main>
      </section>
    </div>
  );
}

export default App;
