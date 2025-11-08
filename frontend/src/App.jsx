import { useState, useEffect } from 'react';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [canvasAuth, setCanvasAuth] = useState(null);
  const [googleAuth, setGoogleAuth] = useState(null);

  // Load saved auth from localStorage on mount
  useEffect(() => {
    const savedCanvasAuth = localStorage.getItem('canvas_auth');
    const savedGoogleAuth = localStorage.getItem('google_auth');

    if (savedCanvasAuth) {
      try {
        setCanvasAuth(JSON.parse(savedCanvasAuth));
      } catch (e) {
        console.error('Failed to parse saved Canvas auth', e);
      }
    }

    if (savedGoogleAuth) {
      try {
        setGoogleAuth(JSON.parse(savedGoogleAuth));
      } catch (e) {
        console.error('Failed to parse saved Google auth', e);
      }
    }
  }, []);

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
            <h2>Welcome to Study Planner AI</h2>
            <p>Connect your Canvas account to get started with AI-powered study planning</p>
            <div className="features">
              <div className="feature">
                <h3>📚 Fetch Assignments</h3>
                <p>Automatically pull your upcoming assignments from Canvas</p>
              </div>
              <div className="feature">
                <h3>🤖 AI Study Plans</h3>
                <p>Generate personalized study schedules with Google Gemini</p>
              </div>
              <div className="feature">
                <h3>📅 Calendar Integration</h3>
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
