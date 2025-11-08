# Quick Start Guide

Get your Study Planner backend running in 5 minutes!

## Prerequisites

- Python 3.9+ installed
- Canvas LMS account with API access
- Google account

## Setup Steps

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Get API Keys

#### Canvas Access Token
1. Log into Canvas
2. Account → Settings → "+ New Access Token"
3. Copy the token

#### Google Gemini API Key
1. Visit https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key

#### Google Calendar OAuth
1. Go to https://console.cloud.google.com/
2. Create project → Enable Calendar API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download as `credentials.json` in project root

### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
CANVAS_URL=https://your-school.instructure.com
CANVAS_ACCESS_TOKEN=your_token_here
GEMINI_API_KEY=your_gemini_key_here
```

### 4. Run the Server

```bash
python main.py
```

Or use the startup script:
```bash
chmod +x start.sh
./start.sh
```

### 5. Test the API

Open your browser to:
- **Interactive Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

Or run the test script:
```bash
python test_api.py
```

## First API Calls

### 1. Authenticate with Canvas

```bash
curl -X POST http://localhost:8000/canvas/authenticate \
  -H "Content-Type: application/json" \
  -d '{
    "canvas_url": "https://your-school.instructure.com",
    "access_token": "your_token"
  }'
```

### 2. Fetch Assignments

```bash
curl http://localhost:8000/canvas/assignments
```

### 3. Generate Study Plan

```bash
curl -X POST http://localhost:8000/study-plan/complete
```

This will:
1. ✅ Fetch your Canvas assignments
2. 🤖 Generate AI study plan
3. 📅 Create Google Calendar events

## What's Next?

- Customize user preferences in the API
- Build a frontend (React, React Native, or web)
- Add more features (analytics, progress tracking, etc.)
- Deploy to production

## Troubleshooting

**Canvas 401 Error**: Check your Canvas URL and token

**Gemini API Error**: Verify your API key is active

**Calendar Auth Failed**: 
1. Make sure `credentials.json` is in the project root
2. Run the OAuth flow when prompted
3. Check that Calendar API is enabled in Google Cloud Console

## Need Help?

- Check the full README.md for detailed documentation
- Visit http://localhost:8000/docs for API reference
- Open an issue on GitHub

---

🎓 Happy studying!
