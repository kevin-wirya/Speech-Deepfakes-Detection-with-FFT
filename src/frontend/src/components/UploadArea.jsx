import { useEffect, useRef, useState } from 'react';
import { apiUrl, isProductionApiMissing } from '../lib/api';

function UploadArea({ onFileSelect, onValidationError, hasFile }) {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('');
  const [isLoadingDataset, setIsLoadingDataset] = useState(false);
  const [datasetError, setDatasetError] = useState(
    isProductionApiMissing ? 'Set VITE_API_BASE_URL in Vercel to connect the backend.' : ''
  );

  useEffect(() => {
    let isMounted = true;
    fetch(apiUrl('/test-datasets'))
      .then((response) => {
        if (!response.ok) throw new Error('Dataset catalog is unavailable.');
        return response.json();
      })
      .then((data) => {
        if (isMounted) {
          setDatasets(data.datasets || []);
          setDatasetError(data.datasets?.length ? '' : 'No test samples were found on the backend.');
        }
      })
      .catch((error) => {
        if (isMounted) {
          setDatasets([]);
          setDatasetError(error.message || 'Dataset catalog is unavailable.');
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const isValidAudioFile = (file) => {
    const validTypes = ['audio/wav', 'audio/mpeg', 'audio/mp3', 'audio/x-wav', 'audio/wave'];
    const ext = file.name.split('.').pop().toLowerCase();
    return validTypes.includes(file.type) || ext === 'wav' || ext === 'mp3';
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && isValidAudioFile(file)) {
      onFileSelect(file);
    } else if (file) {
      onValidationError('Please upload a WAV or MP3 audio file.');
    }
  };

  const handleDatasetChange = async (e) => {
    const datasetPath = e.target.value;
    setSelectedDataset(datasetPath);
    if (!datasetPath) return;

    setIsLoadingDataset(true);
    try {
      const encodedPath = datasetPath.split('/').map(encodeURIComponent).join('/');
      const response = await fetch(apiUrl(`/test-datasets/${encodedPath}`));
      if (!response.ok) throw new Error('The selected dataset could not be loaded.');

      const dataset = datasets.find((item) => item.path === datasetPath);
      const blob = await response.blob();
      const file = new File([blob], dataset?.name || datasetPath.split('/').pop(), {
        type: blob.type || 'audio/mpeg'
      });
      onFileSelect(file);
    } catch (error) {
      onValidationError(error.message);
    } finally {
      setIsLoadingDataset(false);
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
    } else if (file) {
      onValidationError('Please upload a WAV or MP3 audio file.');
    }
  };

  return (
    <>
      <div className="dataset-picker" onClick={(e) => e.stopPropagation()}>
        <div className="dataset-picker-label">Choose a test dataset</div>
        <select
          value={selectedDataset}
          onChange={handleDatasetChange}
          disabled={isLoadingDataset || datasets.length === 0}
          aria-label="Choose an audio sample from the test dataset"
        >
          <option value="">
            {datasets.length === 0 ? 'Dataset catalog unavailable' : 'Select a sample to analyze'}
          </option>
          {datasets.map((dataset) => (
            <option key={dataset.path} value={dataset.path}>
              {dataset.category} / {dataset.name} ({dataset.label})
            </option>
          ))}
        </select>
        {isLoadingDataset && <div className="dataset-picker-status">Loading sample...</div>}
        {datasetError && <div className="dataset-picker-error">{datasetError}</div>}
      </div>

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
    </>
  );
}

export default UploadArea;
