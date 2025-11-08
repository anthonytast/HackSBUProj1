import { useState } from 'react';
import { LogIn, KeyRound, ExternalLink } from 'lucide-react';
import { canvasAPI } from '../services/api';
import '../styles/AuthModal.css';

function CanvasAuth({ onAuthSuccess, isAuthenticated }) {
  const [canvasUrl, setCanvasUrl] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const handleAuthenticate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await canvasAPI.authenticate(canvasUrl, accessToken);
      if (result.authenticated) {
        onAuthSuccess({ canvasUrl, accessToken });
        setShowModal(false);
        // Store in localStorage for persistence
        localStorage.setItem('canvas_auth', JSON.stringify({ canvasUrl, accessToken }));
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('canvas_auth');
    onAuthSuccess(null);
    setCanvasUrl('');
    setAccessToken('');
  };

  if (isAuthenticated) {
    return (
      <div className="auth-status authenticated">
        <div className="auth-info">
          <div className="status-indicator success"></div>
          <span>Canvas Connected</span>
        </div>
        <button onClick={handleLogout} className="btn btn-outline btn-sm">
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <button onClick={() => setShowModal(true)} className="btn btn-primary">
        <LogIn size={18} />
        Connect Canvas
      </button>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Connect to Canvas</h2>
              <button onClick={() => setShowModal(false)} className="modal-close">
                ×
              </button>
            </div>

            <form onSubmit={handleAuthenticate} className="auth-form">
              <div className="form-group">
                <label htmlFor="canvasUrl">
                  Canvas Institution URL
                  <span className="label-hint">
                    (e.g., https://yourschool.instructure.com)
                  </span>
                </label>
                <input
                  id="canvasUrl"
                  type="url"
                  value={canvasUrl}
                  onChange={(e) => setCanvasUrl(e.target.value)}
                  placeholder="https://institution.instructure.com"
                  required
                  className="form-input"
                />
              </div>

              <div className="form-group">
                <label htmlFor="accessToken">
                  Access Token
                  <a
                    href="https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="help-link"
                  >
                    <ExternalLink size={14} />
                    How to get your token
                  </a>
                </label>
                <input
                  id="accessToken"
                  type="password"
                  value={accessToken}
                  onChange={(e) => setAccessToken(e.target.value)}
                  placeholder="Enter your Canvas API token"
                  required
                  className="form-input"
                />
              </div>

              {error && (
                <div className="alert alert-error">
                  {error}
                </div>
              )}

              <div className="form-actions">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="btn btn-secondary"
                  disabled={loading}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? 'Connecting...' : 'Connect'}
                </button>
              </div>
            </form>

            <div className="auth-help">
              <KeyRound size={16} />
              <p>
                Your credentials are stored locally and used only to connect to Canvas.
                Never share your access token with anyone.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CanvasAuth;
