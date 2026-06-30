import { useNavigate, useLocation } from 'react-router-dom';
import './Sidebar.css';

interface SidebarProps {
  children?: React.ReactNode;
}

export default function Sidebar({ children }: SidebarProps) {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="left-sidebar">
      <div className="sidebar-header">
        <span className="brand-name">Candidate Transformer</span>
      </div>

      <div className="sidebar-section">
        <div className="section-subtitle">NAVIGATION</div>
        <div className="nav-menu">
          <button 
            className={`nav-item ${location.pathname === '/' ? 'active' : ''}`} 
            onClick={() => navigate('/')}
          >
            <span className="nav-icon">🏠</span>
            <span className="nav-text">Home</span>
          </button>
          
          <button 
            className={`nav-item ${location.pathname.startsWith('/upload') ? 'active' : ''}`} 
            onClick={() => navigate('/upload/single')}
          >
            <span className="nav-icon">📁</span>
            <span className="nav-text">Files Upload</span>
          </button>
          
          <button 
            className={`nav-item ${location.pathname.startsWith('/builder') ? 'active' : ''}`}
            onClick={() => navigate('/builder')}
          >
            <span className="nav-icon">🛠️</span>
            <span className="nav-text">Builder</span>
          </button>
        </div>
      </div>
      
      {children}
    </div>
  );
}
