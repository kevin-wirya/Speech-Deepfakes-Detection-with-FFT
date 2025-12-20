import { useState } from 'react';
import Header from './components/Header';
import UploadArea from './components/UploadArea';
import AudioPlayer from './components/AudioPlayer';
import StatusMessage from './components/StatusMessage';
import ButtonGroup from './components/ButtonGroup';
import ResultContainer from './components/ResultContainer';
import ParticleBackground from './components/ParticleBackground';
import './App.css';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [status, setStatus] = useState({ message: '', type: '' });
  const [result, setResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    setResult(null);
    setStatus({ message: '✅ File loaded successfully! You can listen to it above.', type: 'success' });
    
    setTimeout(() => {
      if (status.type === 'success') setStatus({ message: '', type: '' });
    }, 3000);
  };

  const handlePredict = async () => {
    if (!selectedFile) return;

    setIsAnalyzing(true);
    setStatus({ message: '🔬 Analyzing audio with FFT Phase Geometry...', type: 'loading' });
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('/predict', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (data.success) {
        setResult(data);
        setStatus({ message: '✅ Analysis complete!', type: 'success' });
        setTimeout(() => {
          if (status.type === 'success') setStatus({ message: '', type: '' });
        }, 3000);
      } else {
        setStatus({ message: `❌ Error: ${data.error}`, type: 'error' });
      }
    } catch (error) {
      setStatus({ message: `❌ Network error: ${error.message}`, type: 'error' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setAudioUrl(null);
    setResult(null);
    setStatus({ message: '', type: '' });
    if (audioUrl) {
      URL.revokeObjectURL(audioUrl);
    }
  };

  return (
    <>
      <ParticleBackground />
      <div className="container">
        <Header />
        
        {audioUrl && <AudioPlayer audioUrl={audioUrl} />}
        
        <UploadArea 
          onFileSelect={handleFileSelect}
          hasFile={!!selectedFile}
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
        
        {result && <ResultContainer result={result} />}
      </div>
    </>
  );
}

export default App;
