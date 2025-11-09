# 🎓 StudyFlow AI

**Canvas to calendar, carefully coordinated.**

An intelligent study planning platform that seamlessly integrates Canvas LMS with Google Calendar, powered by AI to help students optimize their study schedules and stay on top of assignments.

[![Made with React](https://img.shields.io/badge/Made%20with-React-61DAFB?logo=react)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![AI Powered](https://img.shields.io/badge/AI-Gemini%202.5-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)

---

## ✨ Features

### 🎯 Core Functionality
- **Canvas Integration**: Automatically fetch and sync your Canvas assignments
- **AI Study Planning**: Generate personalized study schedules using Google Gemini 2.5
- **Smart Scheduling**: AI breaks down assignments into manageable tasks with optimal time allocation
- **Calendar Sync**: One-click export to Google Calendar with automated event creation
- **Priority Management**: Visual indicators for urgent assignments and upcoming deadlines
- **Real-time Updates**: Refresh assignments and regenerate plans on demand

### 🧠 Intelligent Features
- **Task Breakdown**: AI automatically splits complex assignments into actionable subtasks
- **Time Estimation**: Smart duration prediction based on assignment type and complexity
- **Buffer Time**: Configurable buffer days before deadlines to reduce stress
- **Pomodoro Support**: Study sessions optimized for focus and productivity
- **Weekend Options**: Flexible scheduling including or excluding weekend study time
- **Deadline Prioritization**: Automatic sorting by urgency and importance

### 💫 User Experience
- **Modern Dark UI**: Sleek, eye-friendly interface optimized for long study sessions
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Loading States**: Clear feedback with "This may take a minute" indicators
- **Error Handling**: Graceful error recovery with helpful messages
- **Local Storage**: Secure credential storage for persistent sessions
- **Portal Modals**: Properly layered UI components for seamless interaction

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+** - Backend API server
- **Node.js 16+** - Frontend development
- **Canvas LMS** account with API access
- **OpenRouter API Key** - For AI study plan generation
- **Google Cloud** account (for Calendar integration)

### 1. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your API keys:
# - OPENROUTER_API_KEY (required for AI)
# - GOOGLE_CLIENT_ID (for calendar)
# - GOOGLE_CLIENT_SECRET (for calendar)
# - CANVAS_URL and CANVAS_ACCESS_TOKEN (optional, can be set via UI)

# Start the backend server
uvicorn main:app --reload
```

Backend will run on http://localhost:8000

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Create environment file
cp .env.example .env
# (Default settings should work for local development)

# Start the frontend
npm run dev
```

Frontend will run on http://localhost:5173

### 3. First Time Usage

1. **Open the app**: Navigate to http://localhost:5173

2. **Connect Canvas**:
   - Click "Connect Canvas"
   - Enter your institution's Canvas URL (e.g., `https://yourschool.instructure.com`)
   - Enter your Canvas API token ([How to get token](https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273))

3. **Connect Google Calendar** (Optional):
   - Follow [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md) to configure OAuth
   - Click "Connect Google Calendar"
   - Grant permissions in Google consent screen

4. **Generate Study Plan**:
   - Click "Refresh Assignments" to fetch from Canvas
   - Review your assignments
   - Click "Generate Study Plan" for AI-powered scheduling
   - Click "Complete Plan" to add events to Google Calendar

## 📁 Project Structure

```
SchoolAppProj/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── canvas_service.py       # Canvas LMS integration
│   ├── gemini_service.py       # Google Gemini AI
│   ├── calendar_service.py     # Google Calendar integration
│   ├── schemas.py              # Data models
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Python dependencies
│   └── .env                    # Environment variables (create this)
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── services/           # API client
│   │   ├── styles/             # CSS files
│   │   ├── App.jsx             # Main app
│   │   └── main.jsx            # Entry point
│   ├── package.json
│   └── .env                    # Frontend config (create this)
│
├── GOOGLE_OAUTH_SETUP.md       # Google Calendar setup guide
└── README.md                   # This file
```

## 🔑 Getting API Keys

### 1. OpenRouter API Key (Required)
**StudyFlow uses OpenRouter to access Google Gemini 2.5 models**

1. Go to [OpenRouter](https://openrouter.ai/)
2. Sign up or log in
3. Navigate to [Keys](https://openrouter.ai/keys)
4. Click "Create Key"
5. Copy your API key (starts with `sk-or-v1-`)
6. Add to `.env`: `OPENROUTER_API_KEY=sk-or-v1-your_key_here`

> 💡 **Why OpenRouter?** Provides reliable access to Gemini 2.5 with better token limits and error handling.

### 2. Canvas API Token (Required)
**Get your Canvas access token to fetch assignments**

1. Log into your Canvas LMS
2. Click your profile → **Account** → **Settings**
3. Scroll to "Approved Integrations"
4. Click **"+ New Access Token"**
5. Set purpose (e.g., "StudyFlow AI")
6. Optional: Set expiration date
7. Click **"Generate Token"**
8. **Copy immediately** (shown only once!)
9. Add to `.env` or enter in UI when connecting

📚 [Canvas Token Guide](https://community.canvaslms.com/t5/Student-Guide/How-do-I-manage-API-access-tokens-as-a-student/ta-p/273)

### 3. Google OAuth (Optional - For Calendar)
**Enable calendar sync to automatically add study sessions**

See detailed setup guide: [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)

**Quick steps:**
1. Create project in [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google Calendar API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URI: `http://localhost:8000/google/auth/callback`
5. Download credentials and add to `.env`

## � Screenshots & UI

### Dashboard
- Real-time assignment overview with statistics
- Color-coded priority indicators
- Due date countdown
- Study progress tracking

### Study Plan Generator
- AI-powered task breakdown
- Visual timeline
- Customizable preferences
- One-click calendar export

### Canvas Integration
- Secure authentication modal
- Real-time assignment sync
- Course filtering
- Assignment details view

---

## 🏗️ Technology Stack

### Frontend
- **React 18** - Modern UI library
- **Vite** - Lightning-fast build tool
- **Lucide React** - Beautiful icon system
- **CSS3** - Custom dark theme with animations

### Backend
- **FastAPI** - High-performance Python API
- **Uvicorn** - ASGI server
- **httpx** - Async HTTP client
- **Python 3.8+** - Backend language

### AI & APIs
- **OpenRouter** - AI model gateway
- **Google Gemini 2.5** - Study plan generation
- **Canvas LMS API** - Assignment fetching
- **Google Calendar API** - Event creation
- **Google OAuth 2.0** - Secure authentication

## ⚙️ Configuration

### Backend Environment Variables

Create `backend/.env` from `backend/.env.example`:

```bash
# Application Settings
APP_NAME=Study Planner API
APP_VERSION=1.0.0
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# Canvas LMS (Optional - can be set via UI)
CANVAS_URL=https://your-institution.instructure.com/
CANVAS_ACCESS_TOKEN=your_canvas_token_here

# Google Gemini AI (Legacy - now using OpenRouter)
GEMINI_API_KEY=your_gemini_key_here

# OpenRouter Configuration (Required)
OPENROUTER_API_KEY=sk-or-v1-your_key_here
OPENROUTER_MODEL=google/gemini-2.5-flash

# Google OAuth 2.0 (For Calendar Integration)
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-your_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/google/auth/callback

# Timezone
TIMEZONE=America/New_York

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend Environment Variables

Create `frontend/.env` from `frontend/.env.example`:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
```

---

## 📊 API Documentation

### Canvas Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/canvas/authenticate` | Authenticate with Canvas using URL and access token |
| `GET` | `/canvas/assignments` | Fetch assignments for authenticated user |
| `GET` | `/canvas/courses` | Get list of user's courses |

### Study Plan Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/study-plan/generate` | Generate AI study plan from assignments |
| `POST` | `/study-plan/complete` | Full pipeline: fetch + generate + add to calendar |

### Google Calendar Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/google/auth/url` | Get OAuth authorization URL |
| `GET` | `/google/auth/callback` | OAuth callback handler |
| `POST` | `/calendar/create-events` | Create calendar events from study tasks |

### Utility Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API health check |
| `GET` | `/models` | List available OpenRouter models |

**Full API Docs:** Visit `http://localhost:8000/docs` when server is running

---

## 🐛 Troubleshooting

### 🔴 Backend Issues

#### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8001
```

#### Missing dependencies
```bash
cd backend
pip install -r requirements.txt --upgrade
```

#### API Key errors
- Verify `OPENROUTER_API_KEY` is set correctly in `.env`
- Check key has credits remaining on OpenRouter dashboard
- Ensure no extra spaces or quotes around the key

### 🟡 Frontend Issues

#### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Try different port if 5173 is busy
npm run dev -- --port 3000
```

#### Build errors
```bash
# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### 🟢 Integration Issues

#### Canvas authentication fails
- ✅ Verify Canvas URL is correct (include `https://`)
- ✅ Check token hasn't expired
- ✅ Ensure token has appropriate permissions
- ✅ Try generating a new access token
- ✅ Check backend logs for specific error messages

#### Google Calendar not connecting
- ✅ Follow [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md) completely
- ✅ Verify OAuth credentials in backend `.env`
- ✅ Check redirect URI matches exactly: `http://localhost:8000/google/auth/callback`
- ✅ Add yourself as a test user in Google Cloud Console
- ✅ Enable Google Calendar API in Cloud Console

#### No assignments showing
- ✅ Verify Canvas authentication was successful (green indicator)
- ✅ Check you have assignments with due dates in Canvas
- ✅ Open browser console (F12) and check for errors
- ✅ Check backend terminal logs for API errors
- ✅ Try clicking "Refresh Assignments" button

#### Study plan generation fails
- ✅ Ensure OpenRouter API key is valid
- ✅ Check you have assignments loaded
- ✅ Look for "This may take a minute" - generation can take 30-60 seconds
- ✅ Check backend logs for JSON parsing errors
- ✅ Verify sufficient OpenRouter credits

#### Modal/Popup appears behind content
- ✅ Clear browser cache and reload (Cmd/Ctrl + Shift + R)
- ✅ Check browser console for React Portal errors
- ✅ Verify latest code is deployed

### 🔍 Debug Tips

```bash
# View backend logs in real-time
cd backend
uvicorn main:app --reload --log-level debug

# Check frontend build
cd frontend
npm run build

# Test API directly
curl http://localhost:8000/
curl http://localhost:8000/models
```

**Still stuck?** Open browser DevTools (F12) → Console tab for detailed error messages

## � Deployment

### Backend Deployment (Railway/Render/Heroku)

#### Railway (Recommended)
1. Connect your GitHub repository
2. Select `backend` folder as root
3. Set environment variables from `.env.example`
4. Update `GOOGLE_REDIRECT_URI` to your production URL
5. Deploy automatically on push

#### Render/Heroku
```bash
# Create Procfile in backend/
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

**Important Environment Variables:**
- Set all variables from `backend/.env.example`
- Update `GOOGLE_REDIRECT_URI` to production callback URL
- Set `CORS_ORIGINS` to include your frontend URL
- Set `DEBUG=False` for production

### Frontend Deployment (Vercel/Netlify)

#### Vercel (Recommended)
1. Connect GitHub repository
2. Select `frontend` as root directory
3. Framework: Vite
4. Build command: `npm run build`
5. Output directory: `dist`
6. Add environment variable: `VITE_API_URL=https://your-backend-url.com`

#### Netlify
```bash
# Build settings
Build command: npm run build
Publish directory: dist
```

**Environment Variables:**
```bash
VITE_API_URL=https://your-backend-api-url.com
```

### Post-Deployment Checklist
- [ ] Update Google OAuth redirect URIs in Cloud Console
- [ ] Update CORS origins in backend `.env`
- [ ] Test Canvas authentication
- [ ] Test Google Calendar integration
- [ ] Verify API endpoints are accessible
- [ ] Check HTTPS is working
- [ ] Monitor error logs

---

## �‍💻 Development

### Project Structure
```
StudyFlow/
├── backend/
│   ├── main.py                 # FastAPI app and routes
│   ├── canvas_service.py       # Canvas LMS API client
│   ├── gemini_service.py       # AI study plan generation
│   ├── calendar_service.py     # Google Calendar integration
│   ├── models_service.py       # OpenRouter model management
│   ├── schemas.py              # Pydantic data models
│   ├── config.py               # App configuration
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment variables (gitignored)
│   └── .env.example            # Environment template
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx              # App header with auth
│   │   │   ├── Dashboard.jsx           # Main dashboard
│   │   │   ├── CanvasAuth.jsx          # Canvas login modal
│   │   │   ├── GoogleAuth.jsx          # Google OAuth button
│   │   │   ├── AssignmentList.jsx      # Assignment display
│   │   │   └── StudyPlanView.jsx       # Study plan display
│   │   ├── services/
│   │   │   └── api.js                  # API client
│   │   ├── styles/                     # Component CSS files
│   │   ├── App.jsx                     # Root component
│   │   ├── App.css                     # Global styles
│   │   └── main.jsx                    # Entry point
│   ├── index.html              # HTML template
│   ├── package.json            # Node dependencies
│   └── vite.config.js          # Vite configuration
│
├── GOOGLE_OAUTH_SETUP.md       # OAuth setup guide
├── OAUTH_FLOW.md               # OAuth flow documentation
└── README.md                   # This file
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests (if configured)
npm run test:e2e
```

### Code Style
```bash
# Frontend linting
cd frontend
npm run lint

# Backend formatting (if using black)
cd backend
black .
flake8 .
```

### Adding New Features

#### Adding a new API endpoint:
1. Define route in `backend/main.py`
2. Add business logic in appropriate service file
3. Update schemas in `backend/schemas.py`
4. Add API client method in `frontend/src/services/api.js`
5. Update component to use new endpoint

#### Adding a new UI component:
1. Create component file in `frontend/src/components/`
2. Create corresponding CSS in `frontend/src/styles/`
3. Import and use in parent component
4. Update prop types and documentation

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Ways to Contribute
- 🐛 **Report bugs** - Open an issue with reproduction steps
- 💡 **Suggest features** - Share your ideas for improvements
- 📝 **Improve docs** - Help make setup and usage clearer
- 🎨 **Enhance UI** - Contribute design improvements
- 🧪 **Add tests** - Increase code coverage and reliability
- 🔧 **Fix issues** - Submit PRs for open issues

### Development Workflow
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly (backend and frontend)
5. Commit with clear messages: `git commit -m 'Add amazing feature'`
6. Push to your fork: `git push origin feature/amazing-feature`
7. Open a Pull Request with detailed description

### Code Standards
- Follow existing code style
- Add comments for complex logic
- Update documentation for new features
- Test your changes locally
- Keep commits focused and atomic

---

## 📄 License

**MIT License** - Free to use for educational and personal purposes

See [LICENSE](./LICENSE) file for details.

---

## 🙋 Support & Help

### Having Issues?

**Check in order:**
1. 📖 This README - Most common setup steps
2. 🔐 [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md) - Calendar integration
3. 🔍 [Troubleshooting section](#-troubleshooting) - Common problems
4. 🖥️ Backend logs in terminal running `uvicorn`
5. 🌐 Browser console (F12) for frontend errors
6. 🔗 Network tab to see API request/response details

### Additional Resources
- **Backend API Docs**: `http://localhost:8000/docs` (when running)
- **OpenRouter Dashboard**: Monitor usage and credits
- **Canvas API Docs**: https://canvas.instructure.com/doc/api/
- **Google Calendar API**: https://developers.google.com/calendar

### Found a Bug?
Open an issue on GitHub with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Browser/OS information
- Relevant log output

---

## 🎓 About StudyFlow

**Built for students, by developers who understand the struggle.**

StudyFlow was created to solve a real problem: the overwhelming task of managing multiple course assignments, deadlines, and study schedules. By combining Canvas LMS data with AI-powered planning and calendar integration, we've built a tool that helps students:

- 📚 **Never miss a deadline** - Automatic tracking and reminders
- 🧠 **Study smarter** - AI breaks down complex assignments
- ⏰ **Optimize time** - Intelligent scheduling based on priorities
- 📅 **Stay organized** - Seamless calendar integration
- 💪 **Reduce stress** - Buffer time and realistic planning

### Why StudyFlow?
- **Canvas-First**: Built specifically for Canvas LMS users
- **AI-Powered**: Leverages Google Gemini 2.5 for intelligent planning
- **Free & Open**: No subscriptions, no hidden costs
- **Privacy-Focused**: Your data stays with you (local storage)
- **Modern UX**: Beautiful, responsive, dark-mode interface

---

## 🌟 Acknowledgments

Built with amazing open-source technologies:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - UI library
- [Vite](https://vitejs.dev/) - Frontend build tool
- [OpenRouter](https://openrouter.ai/) - AI model access
- [Google Gemini](https://ai.google.dev/) - AI study planning
- [Lucide Icons](https://lucide.dev/) - Beautiful icon set

Special thanks to the Canvas API and Google Calendar API teams for excellent documentation.

---

## 📊 Project Stats

- **Languages**: Python, JavaScript, CSS
- **Framework**: React + FastAPI
- **AI Model**: Google Gemini 2.5 (via OpenRouter)
- **APIs**: Canvas LMS, Google Calendar
- **Status**: ✅ Active Development

---

<div align="center">

**Made with ❤️ and ☕ for students everywhere**

*Happy studying! 📚✨*

</div>
