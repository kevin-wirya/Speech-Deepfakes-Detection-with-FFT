import { useRef, useState } from 'react';

function UploadArea({ onFileSelect, hasFile }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);

  const isValidAudioFile = (file) => {
    const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/x-wav', 'audio/wave'];
    const ext = file.name.split('.').pop().toLowerCase();
    return validTypes.includes(file.type) || ext === 'wav' || ext === 'mp3';
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && isValidAudioFile(file)) {
      onFileSelect(file);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const file = e.dataTransfer.files[0];
    if (file && isValidAudioFile(file)) {
      onFileSelect(file);
    }
  };

  return (
    <div 
      className={`upload-area ${isDragging ? 'dragover' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current?.click()}
    >
      <div className="upload-icon">🎤</div>
      <div className="upload-text">Drop your audio file here</div>
      <div className="upload-subtext">Supports WAV & MP3 formats</div>
      <label className="file-input-label" onClick={(e) => e.stopPropagation()}>
        Browse Files
      </label>
      <input 
        ref={fileInputRef}
        type="file" 
        accept=".wav,.mp3" 
        onChange={handleFileChange}
        style={{ display: 'none' }}
      />
    </div>
  );
}

export default UploadArea;
