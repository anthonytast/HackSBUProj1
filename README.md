# Study Planner AI - Quick Start Guide

An AI-powered study planner that integrates Canvas LMS, Google Gemini, and Google Calendar to help students manage assignments and create optimal study schedules.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Canvas LMS account with API access
- Google Cloud account (for Calendar integration)
- Google Gemini API key

### 1. Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env and add your API keys:
# - GEMINI_API_KEY (required)
# - GOOGLE_CLIENT_ID (for calendar)
# - GOOGLE_CLIENT_SECRET (for calendar)

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

### Canvas API Token
1. Log into Canvas
2. Go to Account → Settings
3. Scroll to "Approved Integrations"
4. Click "+ New Access Token"
5. Give it a name and generate
6. Copy and save the token immediately

### Google Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new project or select existing
4. Copy your API key

### Google OAuth (for Calendar)
See detailed guide in [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)

## 🎯 Features

### Core Features
- ✅ Fetch assignments from Canvas LMS
- ✅ AI-powered study plan generation
- ✅ Google Calendar event creation
- ✅ Assignment priority indicators
- ✅ Due date tracking
- ✅ Study session scheduling

### Study Plan Features
- Task breakdown for each assignment
- Time allocation recommendations
- Priority-based scheduling
- Buffer time before due dates
- Considers assignment difficulty
- Customizable study preferences

## 🛠️ Configuration

### Backend (.env)
```bash
GEMINI_API_KEY=your_key_here
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/google/auth/callback
```

### Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000
```

## 📊 API Endpoints

### Canvas
- `POST /canvas/authenticate` - Authenticate with Canvas
- `GET /canvas/assignments` - Fetch assignments

### Study Plans
- `POST /study-plan/generate` - Generate AI study plan
- `POST /study-plan/complete` - Full pipeline (fetch + generate + calendar)

### Google Calendar
- `GET /google/auth/url` - Get OAuth URL
- `GET /google/auth/callback` - OAuth callback
- `POST /calendar/create-events` - Create calendar events

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Kill the process if needed
kill -9 <PID>

# Or use a different port
uvicorn main:app --reload --port 8001
```

### Frontend issues
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 5173 is available
npm run dev -- --port 3000
```

### Canvas authentication fails
- Verify your Canvas URL is correct (include https://)
- Check token hasn't expired
- Ensure token has appropriate permissions
- Try generating a new token

### Google Calendar not connecting
- Follow [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md) completely
- Verify OAuth credentials in `.env`
- Check redirect URI matches exactly
- Add yourself as a test user in Google Cloud Console

### No assignments showing
- Verify Canvas authentication was successful
- Check you have upcoming assignments in Canvas
- Look at browser console for errors
- Check backend logs for API errors

## 🚢 Deployment

### Backend (Heroku/Railway/Render)
```bash
# Add Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT

# Set environment variables in platform dashboard
# Update GOOGLE_REDIRECT_URI to production URL
```

### Frontend (Vercel/Netlify)
```bash
# Build command
npm run build

# Output directory
dist

# Environment variables
VITE_API_URL=https://your-backend-url.com
```

## 📝 Development

### Running tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code style
```bash
# Frontend linting
npm run lint
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - Free to use for educational purposes

## 🙋 Support

Having issues? Check:
1. This README
2. [GOOGLE_OAUTH_SETUP.md](./GOOGLE_OAUTH_SETUP.md)
3. Backend logs (`uvicorn` terminal)
4. Browser console (F12)
5. Network tab for API errors

## 🎓 Built For Students

This project was created to help students better manage their academic workload using AI and automation. Happy studying! 📚✨
