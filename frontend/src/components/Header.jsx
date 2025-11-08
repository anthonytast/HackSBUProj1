import { GraduationCap, Settings } from 'lucide-react';
import CanvasAuth from './CanvasAuth';
import GoogleAuth from './GoogleAuth';
import '../styles/Header.css';

function Header({ canvasAuth, googleAuth, onCanvasAuth, onGoogleAuth }) {
  return (
    <header className="app-header">
      <div className="header-content">
        <div className="brand">
          <GraduationCap size={32} />
          <h1>Study Planner AI</h1>
        </div>

        <div className="auth-section">
          <CanvasAuth
            onAuthSuccess={onCanvasAuth}
            isAuthenticated={!!canvasAuth}
          />
          <GoogleAuth
            onAuthSuccess={onGoogleAuth}
            isAuthenticated={!!googleAuth}
          />
        </div>
      </div>
    </header>
  );
}

export default Header;
