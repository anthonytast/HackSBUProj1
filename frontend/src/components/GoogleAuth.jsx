import { useState } from 'react';
import { Calendar as CalendarIcon, LogIn } from 'lucide-react';
import { calendarAPI } from '../services/api';
import '../styles/AuthModal.css';

function GoogleAuth({ onAuthSuccess, isAuthenticated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGoogleAuth = async () => {
    setLoading(true);
    setError(null);

    try {
      // Note: In a real implementation, you'd use Google OAuth 2.0 flow
      // This is a simplified version
      alert(
        'Google OAuth flow would be implemented here. ' +
        'In production, this would redirect to Google\'s OAuth consent screen.'
      );
      
      // Simulate successful auth for demo
      const mockCredentials = { token: 'mock_google_token' };
      localStorage.setItem('google_auth', JSON.stringify(mockCredentials));
      onAuthSuccess(mockCredentials);
    } catch (err) {
      setError(err.response?.data?.detail || 'Google Calendar authentication failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('google_auth');
    onAuthSuccess(null);
  };

  if (isAuthenticated) {
    return (
      <div className="auth-status authenticated">
        <div className="auth-info">
          <div className="status-indicator success"></div>
          <span>Google Calendar Connected</span>
        </div>
        <button onClick={handleLogout} className="btn btn-outline btn-sm">
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <button
        onClick={handleGoogleAuth}
        className="btn btn-primary"
        disabled={loading}
      >
        <CalendarIcon size={18} />
        {loading ? 'Connecting...' : 'Connect Google Calendar'}
      </button>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}
    </div>
  );
}

export default GoogleAuth;
