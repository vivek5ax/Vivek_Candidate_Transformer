import { useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import './Home.css';

export default function Home() {
  const navigate = useNavigate();

  return (
    <>
      <Sidebar />
      <div className="container flex flex-col items-center justify-center home-container page-with-sidebar">
        
        <h1 className="title">Candidate Transformer</h1>
        <p className="subtitle">Select an extraction mode to begin.</p>
        <p className="description">
          Candidate Transformer is an AI-powered resume intelligence platform.<br/>
          It seamlessly extracts, normalizes, and enriches candidate data into a beautifully structured format.
        </p>
        
        <div className="flex gap-8 cards-wrapper mt-12">
          {/* Card A */}
          <div 
            className="glass-panel flex-col mode-card float-effect"
            onClick={() => navigate('/upload/single')}
          >
            <div className="card-icon">📄</div>
            <h2>Resume Only</h2>
            <p>Upload a single resume to instantly extract structured profile data using our hybrid AI engine.</p>
            <div className="formats">
              <span>Supported: .pdf, .docx, .txt</span>
            </div>
          </div>

          {/* Card B */}
          <div 
            className="glass-panel flex-col mode-card float-effect"
            onClick={() => navigate('/upload/multi')}
          >
            <div className="card-icon">🔄</div>
            <h2>Resume + CSV</h2>
            <p>Upload a resume alongside recruiter CSV data for enhanced projection and confidence scoring.</p>
            <div className="formats">
              <span>Supported: Resume + .csv</span>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
