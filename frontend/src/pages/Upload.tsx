import { useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import './Upload.css';

export default function Upload() {
  const { mode } = useParams(); // 'single' or 'multi'
  const navigate = useNavigate();
  
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [csvFile, setCsvFile] = useState<File | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [dragActiveResume, setDragActiveResume] = useState(false);
  const [dragActiveCsv, setDragActiveCsv] = useState(false);

  const resumeInputRef = useRef<HTMLInputElement>(null);
  const csvInputRef = useRef<HTMLInputElement>(null);

  const MAX_SIZE_MB = 5;
  const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

  const handleFile = (file: File | undefined, type: 'resume' | 'csv') => {
    if (!file) return;

    if (file.size > MAX_SIZE_BYTES) {
      setError(`File ${file.name} exceeds the ${MAX_SIZE_MB}MB limit.`);
      return;
    }

    setError(null);
    if (type === 'resume') setResumeFile(file);
    else setCsvFile(file);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: 'resume' | 'csv') => {
    handleFile(e.target.files?.[0], type);
  };

  const handleDrag = (e: React.DragEvent, type: 'resume' | 'csv', isActive: boolean) => {
    e.preventDefault();
    e.stopPropagation();
    if (type === 'resume') setDragActiveResume(isActive);
    else setDragActiveCsv(isActive);
  };

  const handleDrop = (e: React.DragEvent, type: 'resume' | 'csv') => {
    e.preventDefault();
    e.stopPropagation();
    if (type === 'resume') setDragActiveResume(false);
    else setDragActiveCsv(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0], type);
    }
  };

  const handleExtract = async () => {
    if (!resumeFile) {
      setError("Please upload a resume first.");
      return;
    }
    if (mode === 'multi' && !csvFile) {
      setError("Please upload the supporting CSV file.");
      return;
    }

    setIsExtracting(true);
    setError(null);

    const formData = new FormData();
    formData.append('resume_file', resumeFile);
    if (mode === 'multi' && csvFile) {
      formData.append('csv_file', csvFile);
    }

    const endpoint = mode === 'multi' 
      ? 'http://127.0.0.1:8000/api/extract/multi-source'
      : 'http://127.0.0.1:8000/api/extract/resume';

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Extraction failed");
      }

      const data = await response.json();
      
      // Navigate to builder, passing the massive extracted JSON in state
      navigate('/builder', { state: { rawData: data } });

    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsExtracting(false);
    }
  };

  return (
    <>
      <Sidebar />
      <div className="container flex flex-col items-center upload-page page-with-sidebar">
        <button className="back-btn" onClick={() => navigate('/')}>← Back</button>
        
        <h1 className="title">
          {mode === 'multi' ? 'Multi-Source Extraction' : 'Resume Extraction'}
        </h1>
        <p className="subtitle">Upload your files below to begin processing.</p>

        {error && <div className="error-banner">{error}</div>}

        <div className={`upload-zones flex ${mode === 'multi' ? 'gap-6' : 'justify-center'}`}>
          
          {/* Resume Drop Zone */}
        <div 
          className={`glass-panel drop-zone ${resumeFile ? 'has-file' : ''} ${dragActiveResume ? 'drag-active' : ''}`}
          onClick={() => resumeInputRef.current?.click()}
          onDragEnter={(e) => handleDrag(e, 'resume', true)}
          onDragLeave={(e) => handleDrag(e, 'resume', false)}
          onDragOver={(e) => handleDrag(e, 'resume', true)}
          onDrop={(e) => handleDrop(e, 'resume')}
        >
          <div className="zone-icon">📄</div>
          <h3>{resumeFile ? resumeFile.name : 'Upload Resume'}</h3>
          <p>{resumeFile ? `${(resumeFile.size / 1024 / 1024).toFixed(2)} MB` : 'Drag & drop or click to browse'}</p>
          <span className="limit">Max size: {MAX_SIZE_MB}MB | .pdf, .docx, .txt</span>
          <input 
            type="file" 
            ref={resumeInputRef} 
            onChange={(e) => handleFileChange(e, 'resume')} 
            accept=".pdf,.docx,.txt"
            hidden 
          />
        </div>

        {/* CSV Drop Zone (Multi Mode Only) */}
        {mode === 'multi' && (
          <div 
            className={`glass-panel drop-zone ${csvFile ? 'has-file' : ''} ${dragActiveCsv ? 'drag-active' : ''}`}
            onClick={() => csvInputRef.current?.click()}
            onDragEnter={(e) => handleDrag(e, 'csv', true)}
            onDragLeave={(e) => handleDrag(e, 'csv', false)}
            onDragOver={(e) => handleDrag(e, 'csv', true)}
            onDrop={(e) => handleDrop(e, 'csv')}
          >
            <div className="zone-icon">📊</div>
            <h3>{csvFile ? csvFile.name : 'Upload CSV'}</h3>
            <p>{csvFile ? `${(csvFile.size / 1024 / 1024).toFixed(2)} MB` : 'Drag & drop or click to browse'}</p>
            <span className="limit">Max size: {MAX_SIZE_MB}MB | .csv</span>
            <input 
              type="file" 
              ref={csvInputRef} 
              onChange={(e) => handleFileChange(e, 'csv')} 
              accept=".csv"
              hidden 
            />
          </div>
        )}
      </div>

      <button 
        className="btn btn-primary extract-btn" 
        onClick={handleExtract}
        disabled={isExtracting}
      >
        {isExtracting ? 'Extracting...' : 'Extract Data'}
        </button>
      </div>
    </>
  );
}
