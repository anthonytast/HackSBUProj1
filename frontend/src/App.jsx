import { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import { canvasAPI } from './services/api';
import './App.css';

function App() {
  const [canvasAuth, setCanvasAuth] = useState(null);
  const [googleAuth, setGoogleAuth] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  // Load saved auth from localStorage on mount and re-authenticate
  useEffect(() => {
    const loadSavedAuth = async () => {
      const savedCanvasAuth = localStorage.getItem('canvas_auth');
      const savedGoogleAuth = localStorage.getItem('google_auth');

      if (savedCanvasAuth) {
        try {
          const authData = JSON.parse(savedCanvasAuth);
          // Re-authenticate with backend
          try {
            await canvasAPI.authenticate(authData.canvasUrl, authData.accessToken);
            setCanvasAuth(authData);
          } catch (e) {
            console.error('Failed to re-authenticate Canvas', e);
            // Clear invalid auth
            localStorage.removeItem('canvas_auth');
          }
        } catch (e) {
          console.error('Failed to parse saved Canvas auth', e);
          localStorage.removeItem('canvas_auth');
        }
      }

      if (savedGoogleAuth) {
        try {
          setGoogleAuth(JSON.parse(savedGoogleAuth));
        } catch (e) {
          console.error('Failed to parse saved Google auth', e);
          localStorage.removeItem('google_auth');
        }
      }

      setLoadingAuth(false);
    };

    loadSavedAuth();
  }, []);

  if (loadingAuth) {
    return (
      <div className="app">
        <div className="loading-screen">
          <p>Loading...</p>
          <p className="loading-hint">This may take a minute</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <Header
        canvasAuth={canvasAuth}
        googleAuth={googleAuth}
        onCanvasAuth={setCanvasAuth}
        onGoogleAuth={setGoogleAuth}
      />
      
      <main className="app-main">
        {!canvasAuth ? (
          <div className="welcome-screen">
            <h2>Welcome to StudyFlow AI</h2>
            <h3>Canvas to calendar, carefully coordinated.</h3>
            <p>Connect your Canvas account to get started with AI-powered study planning!</p>
            <div className="features">
              <div className="feature">
                <h3>Fetch Assignments</h3>
                <p>Automatically pull your upcoming assignments from Canvas</p>
              </div>
              <div className="feature">
                <h3>AI Study Plans</h3>
                <p>Generate personalized study schedules with Google Gemini</p>
              </div>
              <div className="feature">
                <h3>
                  Calendar Integration</h3>
                <p>Automatically schedule study sessions in Google Calendar</p>
              </div>
            </div>
          </div>
        ) : (
          <Dashboard
            canvasAuth={canvasAuth}
            googleAuth={googleAuth}
          />
        )}
      </main>

      <footer className="app-footer">
        <p>Study Planner AI - Powered by Canvas, Google Gemini & Google Calendar</p>
      </footer>
    </div>
  );
}

export default App;
