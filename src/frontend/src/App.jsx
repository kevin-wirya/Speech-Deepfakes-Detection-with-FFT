import { useEffect, useRef, useState } from 'react';
import Header from './components/Header';
import UploadArea from './components/UploadArea';
import AudioPlayer from './components/AudioPlayer';
import StatusMessage from './components/StatusMessage';
import ButtonGroup from './components/ButtonGroup';
import ResultContainer from './components/ResultContainer';
import ParticleBackground from './components/ParticleBackground';
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
    statusTimerRef.current = setTimeout(() => {
      setStatus({ message: '', type: '' });
    }, 3000);
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    setResult(null);
    showTemporaryStatus('File loaded. Preview the audio before analysis.', 'success');
  };

  const handleInvalidFile = (message) => {
    showTemporaryStatus(message, 'error');
  };

  const handlePredict = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    if (statusTimerRef.current) clearTimeout(statusTimerRef.current);
    setStatus({ message: 'Analyzing audio with FFT Phase Geometry...', type: 'loading' });
    setResult(null);

    try {
      const data = await analyzeAudioFile(selectedFile);

      if (data.success) {
        setResult(data);
        showTemporaryStatus('Analysis complete.', 'success');
      } else {
        setStatus({ message: data.error || 'The audio could not be analyzed.', type: 'error' });
      }
    } catch (error) {
      setStatus({ message: `Network error: ${error.message}`, type: 'error' });
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
    <>
      <ParticleBackground />
      <div className={`app-wrapper ${result ? 'has-result' : ''}`}>
        <div className="container left-panel">
          <Header />
          
          {audioUrl && <AudioPlayer audioUrl={audioUrl} />}
          
          <UploadArea 
            onFileSelect={handleFileSelect}
            hasFile={!!selectedFile}
            onValidationError={handleInvalidFile}
          />
          
          {selectedFile && (
            <div className="file-info visible">
              <div className="file-name">
                📁 <strong>{selectedFile.name}</strong>
              </div>
              <div className="file-size">
                Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
              </div>
            </div>
          )}
          
          {status.message && <StatusMessage status={status} />}
          
          <ButtonGroup 
            onPredict={handlePredict}
            onClear={handleClear}
            isAnalyzing={isAnalyzing}
            hasFile={!!selectedFile}
          />
        </div>
        
        {result && (
          <div className="container right-panel">
            <ResultContainer result={result} />
          </div>
        )}
      </div>
    </>
  );
}

export default App;
