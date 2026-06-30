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
        <p className="subtitle">Transforming unstructured resumes into verified, actionable intelligence.</p>
        <div className="infographic-flow">
          <div className="flow-step">
            <div className="step-icon step-1">📥</div>
            <span>Ingestion & Parsing</span>
          </div>
          <div className="flow-arrow">→</div>
          <div className="flow-step">
            <div className="step-icon step-2">⚙️</div>
            <span>Extraction</span>
          </div>
          <div className="flow-arrow">→</div>
          <div className="flow-step">
            <div className="step-icon step-3">✨</div>
            <span>Normalization</span>
          </div>
          <div className="flow-arrow">→</div>
          <div className="flow-step">
            <div className="step-icon step-4">🔗</div>
            <span>Merge & Resolve</span>
          </div>
          <div className="flow-arrow">→</div>
          <div className="flow-step">
            <div className="step-icon step-5">🎯</div>
            <span>Dynamic Projection</span>
          </div>
          <div className="flow-arrow">→</div>
          <div className="flow-step">
            <div className="step-icon step-6">✅</div>
            <span>Validation</span>
          </div>
        </div>
        
        <div className="flex gap-8 justify-center cards-wrapper mt-12">
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
