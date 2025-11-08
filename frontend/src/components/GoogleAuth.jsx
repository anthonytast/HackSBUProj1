import { useState, useEffect } from 'react';
import { Calendar as CalendarIcon, LogIn, ExternalLink } from 'lucide-react';
import axios from 'axios';
import '../styles/AuthModal.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function GoogleAuth({ onAuthSuccess, isAuthenticated }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Check for OAuth callback on component mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const errorParam = urlParams.get('error');

    if (errorParam) {
      setError(`Authentication failed: ${errorParam}`);
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
      return;
    }

    if (code) {
      handleOAuthCallback(code, state);
    }
  }, []);

  const handleOAuthCallback = async (code, state) => {
    setLoading(true);
    setError(null);

    try {
      // Exchange code for credentials
      const response = await axios.get(`${API_BASE_URL}/google/auth/callback`, {
        params: { code, state }
      });

      const credentials = response.data.credentials;
      
      // Store credentials
      localStorage.setItem('google_auth', JSON.stringify(credentials));
      onAuthSuccess(credentials);

      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);

    } catch (err) {
      console.error('OAuth callback error:', err);
      setError(err.response?.data?.detail || 'Failed to complete authentication');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleAuth = async () => {
    setLoading(true);
    setError(null);

    try {
      // Get authorization URL from backend
      const response = await axios.get(`${API_BASE_URL}/google/auth/url`);
      const authUrl = response.data.auth_url;

      // Redirect to Google OAuth consent screen
      window.location.href = authUrl;

    } catch (err) {
      console.error('OAuth initiation error:', err);
      setError(err.response?.data?.detail || 'Failed to start authentication');
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
        {loading ? 'Redirecting...' : 'Connect Google Calendar'}
      </button>

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {loading && (
        <p className="auth-hint">
          You'll be redirected to Google to grant calendar permissions...
        </p>
      )}
    </div>
  );
}

export default GoogleAuth;
