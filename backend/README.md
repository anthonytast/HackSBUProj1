# Study Planner Backend

A FastAPI backend service that integrates Canvas LMS, Google Gemini AI, and Google Calendar to automatically generate and schedule study plans.

## Features

- 📚 **Canvas Integration**: Fetch assignments from Canvas LMS
- 🤖 **AI Study Plans**: Generate personalized study plans using Google Gemini
- 📅 **Calendar Automation**: Automatically create Google Calendar events
- ⚡ **FastAPI**: High-performance, async REST API
- 🔒 **OAuth Support**: Secure authentication for Canvas and Google services

## Architecture

```
User Input → Canvas API → Fetch Assignments
                ↓
        Format Data for AI
                ↓
    Google Gemini API → Generate Study Plan
                ↓
        Parse AI Response
                ↓
   Google Calendar API → Create Events
                ↓
    Confirmation to User
```

## Prerequisites

- Python 3.9+
- Canvas LMS access token
- Google Gemini API key
- Google Cloud Project with Calendar API enabled

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd study_planner_backend
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
CANVAS_URL=https://your-institution.instructure.com
CANVAS_ACCESS_TOKEN=your_canvas_token
GEMINI_API_KEY=your_gemini_api_key
```

### 5. Set up Google Calendar OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` and place it in project root

## Getting API Keys

### Canvas Access Token

1. Log into Canvas
2. Go to Account → Settings
3. Scroll to "Approved Integrations"
4. Click "+ New Access Token"
5. Give it a purpose and generate
6. Copy the token (you won't see it again!)

### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key and add to `.env`

## Running the Server

### Development mode

```bash
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

```http
GET /
```

Returns API status and version.

### Canvas Endpoints

#### Authenticate with Canvas

```http
POST /canvas/authenticate
Content-Type: application/json

{
  "canvas_url": "https://institution.instructure.com",
  "access_token": "your_token"
}
```

#### Fetch All Assignments

```http
GET /canvas/assignments
```

Returns all upcoming assignments from your Canvas to-do list.

#### Fetch Course Assignments

```http
GET /canvas/assignments/{course_id}
```

Returns assignments for a specific course.

### Study Plan Endpoints

#### Generate Study Plan

```http
POST /study-plan/generate
Content-Type: application/json

{
  "assignments": [
    {
      "id": 12345,
      "title": "Math Problem Set 3",
      "due_date": "2025-11-15T23:59:00",
      "course_name": "Calculus II",
      "course_id": 101,
      "assignment_type": "problem_set",
      "points": 100
    }
  ],
  "preferences": {
    "study_session_length": 90,
    "break_frequency": 25,
    "daily_study_hours": 4,
    "preferred_study_times": ["09:00-12:00", "14:00-17:00"],
    "buffer_days": 1,
    "weekend_study": true
  }
}
```

#### Complete Study Plan (Full Pipeline)

```http
POST /study-plan/complete
```

Executes the complete workflow:
1. Fetches Canvas assignments
2. Generates AI study plan
3. Creates Google Calendar events

### Google Calendar Endpoints

#### Authenticate with Google

```http
POST /google/authenticate
Content-Type: application/json

{
  "credentials": {
    "token": "...",
    "refresh_token": "...",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_id": "...",
    "client_secret": "...",
    "scopes": ["https://www.googleapis.com/auth/calendar"]
  }
}
```

#### Create Calendar Events

```http
POST /calendar/create-events
Content-Type: application/json

{
  "tasks": [
    {
      "task_name": "Review Chapter 4",
      "assignment_title": "Math Problem Set 3",
      "course_name": "Calculus II",
      "duration_minutes": 60,
      "suggested_date": "2025-11-10",
      "suggested_start_time": "14:00",
      "priority": "high"
    }
  ]
}
```

#### Get Free Time Slots

```http
GET /calendar/free-slots?start_date=2025-11-08T00:00:00&end_date=2025-11-15T23:59:59
```

#### Delete Calendar Event

```http
DELETE /calendar/event/{event_id}
```

## Project Structure

```
study_planner_backend/
├── main.py                 # FastAPI application entry point
├── models/
│   └── schemas.py         # Pydantic models for request/response
├── services/
│   ├── canvas_service.py  # Canvas API integration
│   ├── gemini_service.py  # Google Gemini AI integration
│   └── calendar_service.py # Google Calendar integration
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Data Models

### Assignment

```python
{
  "id": int,
  "title": str,
  "description": str | None,
  "due_date": datetime | None,
  "course_name": str,
  "course_id": int,
  "assignment_type": str,
  "points": float | None,
  "estimated_time": int | None
}
```

### StudyTask

```python
{
  "task_name": str,
  "assignment_title": str,
  "course_name": str,
  "duration_minutes": int,
  "suggested_date": str,  # YYYY-MM-DD
  "suggested_start_time": str,  # HH:MM
  "priority": "high" | "medium" | "low",
  "description": str | None
}
```

### UserPreferences

```python
{
  "study_session_length": int = 90,
  "break_frequency": int = 25,
  "daily_study_hours": int = 4,
  "preferred_study_times": List[str] = ["09:00-12:00", "14:00-17:00"],
  "buffer_days": int = 1,
  "weekend_study": bool = True
}
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## Deployment

### Docker Deployment (Optional)

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t study-planner .
docker run -p 8000:8000 --env-file .env study-planner
```

### Production Considerations

1. **Security**:
   - Use environment variables for all secrets
   - Enable HTTPS
   - Restrict CORS origins
   - Implement rate limiting

2. **Performance**:
   - Use Redis for caching
   - Implement request queuing for AI calls
   - Add database for persistent storage

3. **Monitoring**:
   - Add logging (structured logging with JSON)
   - Implement health checks
   - Set up error tracking (e.g., Sentry)

## Troubleshooting

### Canvas API Issues

- **401 Unauthorized**: Check your access token and Canvas URL
- **Rate Limiting**: Canvas has API rate limits; implement exponential backoff

### Gemini API Issues

- **API Key Invalid**: Verify your Gemini API key
- **JSON Parsing Errors**: The AI sometimes returns markdown; the service handles this

### Google Calendar Issues

- **Authentication Failed**: Re-run OAuth flow and update credentials
- **Permission Denied**: Ensure Calendar API is enabled in Google Cloud Console

## Future Enhancements

- [ ] Database integration (PostgreSQL)
- [ ] User authentication and multi-user support
- [ ] WebSocket support for real-time updates
- [ ] Mobile push notifications
- [ ] Historical data tracking and analytics
- [ ] Smart rescheduling when falling behind
- [ ] Integration with more LMS platforms (Blackboard, Moodle)
- [ ] Spaced repetition for exam preparation
- [ ] Study group coordination features

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - feel free to use this project for your own purposes.

## Support

For issues or questions, please open an issue on GitHub.
