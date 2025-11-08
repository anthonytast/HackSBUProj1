from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from fastapi.responses import RedirectResponse
import urllib.parse
import base64
import json

from canvas_service import CanvasService
from gemini_service import GeminiService
from calendar_service import CalendarService
from schemas import (
    Assignment,
    StudyPlan,
    StudyTask,
    UserPreferences,
    CalendarEventResponse,
    CanvasAuthRequest,
    GoogleAuthRequest
)

app = FastAPI(
    title="Study Planner API",
    description="Automated study planner with Canvas, Gemini AI, and Google Calendar integration",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service instances (in production, use dependency injection properly)
canvas_service = CanvasService()
gemini_service = GeminiService()
calendar_service = CalendarService()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Study Planner API",
        "status": "active",
        "version": "1.0.0"
    }


@app.post("/canvas/authenticate")
async def authenticate_canvas(auth_request: CanvasAuthRequest):
    """
    Authenticate with Canvas using access token
    """
    try:
        is_valid = await canvas_service.authenticate(
            auth_request.canvas_url,
            auth_request.access_token
        )
        if is_valid:
            return {"message": "Canvas authentication successful", "authenticated": True}
        else:
            raise HTTPException(status_code=401, detail="Invalid Canvas credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/canvas/assignments")
async def get_canvas_assignments():
    """
    Fetch upcoming assignments from Canvas and classify them
    """
    try:
        assignments = await canvas_service.fetch_assignments()
        
        # Classify assignments using Gemini
        if assignments:
            try:
                classifications = await gemini_service.classify_assignments(assignments)
                # Create a lookup for classifications
                classification_lookup = {
                    c['assignment_id']: c for c in classifications
                }
                
                # Update assignments with classification data
                for assignment in assignments:
                    if assignment.id in classification_lookup:
                        classification = classification_lookup[assignment.id]
                        assignment.category = classification.get('category')
                        assignment.estimated_time = classification.get('estimated_time_minutes')
            except Exception as e:
                print(f"Warning: Classification failed, using defaults: {e}")
                # Continue without classification if it fails
        
        return {"assignments": assignments, "count": len(assignments)}
    except Exception as e:
        error_msg = str(e)
        if "not authenticated" in error_msg.lower():
            raise HTTPException(status_code=401, detail=error_msg)
        raise HTTPException(status_code=500, detail=f"Failed to fetch assignments: {error_msg}")


@app.get("/canvas/assignments/{course_id}")
async def get_course_assignments(course_id: int):
    """
    Fetch assignments for a specific course
    """
    try:
        assignments = await canvas_service.fetch_course_assignments(course_id)
        return {"assignments": assignments, "count": len(assignments)}
    except Exception as e:
        error_msg = str(e)
        if "not authenticated" in error_msg.lower():
            raise HTTPException(status_code=401, detail=error_msg)
        raise HTTPException(status_code=500, detail=f"Failed to fetch course assignments: {error_msg}")


@app.get("/canvas/courses")
async def get_canvas_courses():
    """
    Fetch list of active Canvas courses
    """
    try:
        courses = await canvas_service.get_courses()
        return {"courses": courses, "count": len(courses)}
    except Exception as e:
        error_msg = str(e)
        if "not authenticated" in error_msg.lower():
            raise HTTPException(status_code=401, detail=error_msg)
        raise HTTPException(status_code=500, detail=f"Failed to fetch courses: {error_msg}")


@app.post("/assignments/classify")
async def classify_assignments(assignments: List[Assignment]):
    """
    Classify assignments into categories based on their descriptions
    """
    try:
        classifications = await gemini_service.classify_assignments(assignments)
        
        # Update assignments with classification data
        classification_lookup = {
            c['assignment_id']: c for c in classifications
        }
        
        for assignment in assignments:
            if assignment.id in classification_lookup:
                classification = classification_lookup[assignment.id]
                assignment.category = classification.get('category')
                assignment.estimated_time = classification.get('estimated_time_minutes')
        
        return {
            "assignments": assignments,
            "classifications": classifications,
            "count": len(assignments)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to classify assignments: {str(e)}")


@app.post("/study-plan/generate")
async def generate_study_plan(
    assignments: List[Assignment],
    preferences: Optional[UserPreferences] = None
):
    """
    Generate AI-powered study plan using Google Gemini
    """
    try:
        # Set default preferences if none provided
        if preferences is None:
            preferences = UserPreferences()
        
        study_plan = await gemini_service.generate_study_plan(
            assignments=assignments,
            preferences=preferences
        )
        
        return {"study_plan": study_plan, "task_count": len(study_plan.tasks)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate study plan: {str(e)}")


@app.post("/study-plan/complete")
async def complete_study_plan():
    """
    Full pipeline: Fetch assignments → Generate plan → Create calendar events
    """
    try:
        # Step 1: Fetch assignments from Canvas
        try:
            assignments = await canvas_service.fetch_assignments()
        except Exception as e:
            error_msg = str(e)
            if "not authenticated" in error_msg.lower():
                raise HTTPException(status_code=401, detail="Canvas not authenticated. Please authenticate first.")
            raise HTTPException(status_code=500, detail=f"Failed to fetch assignments: {error_msg}")
        
        if not assignments:
            return {"message": "No upcoming assignments found", "events_created": 0}
        
        # Step 2: Generate study plan with Gemini
        preferences = UserPreferences()  # Use defaults or get from request
        study_plan = await gemini_service.generate_study_plan(
            assignments=assignments,
            preferences=preferences
        )
        
        # Step 3: Create calendar events
        events = await calendar_service.create_study_events(study_plan.tasks)
        
        return {
            "message": "Study plan created successfully",
            "assignments_processed": len(assignments),
            "tasks_generated": len(study_plan.tasks),
            "events_created": len(events),
            "calendar_events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to complete study plan: {str(e)}")


@app.get("/google/auth/url")
async def get_google_auth_url():
    """
    Get Google OAuth authorization URL
    """
    try:
        auth_url = await calendar_service.get_authorization_url()
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")


@app.get("/google/auth/callback")
async def google_auth_callback(code: str, state: Optional[str] = None):
    """
    Handle Google OAuth callback
    """
    try:
        # Exchange code for credentials
        credentials = await calendar_service.handle_oauth_callback(code, state)

        # Serialize credentials to a URL-safe base64 string and redirect to frontend
        # Use FRONTEND_URL env var if provided, otherwise default to Vite dev URL
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        creds_json = json.dumps(credentials)
        token = base64.urlsafe_b64encode(creds_json.encode()).decode()
        # Put token in fragment to avoid it being sent to backend in future requests
        redirect_url = f"{frontend_url}/#google_auth={urllib.parse.quote(token)}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")


@app.post("/google/authenticate")
async def authenticate_google(auth_request: GoogleAuthRequest):
    """
    Authenticate with Google Calendar using OAuth 2.0 credentials
    """
    try:
        is_valid = await calendar_service.authenticate(auth_request.credentials)
        if is_valid:
            return {"message": "Google Calendar authentication successful", "authenticated": True}
        else:
            raise HTTPException(status_code=401, detail="Invalid Google credentials")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/calendar/create-events")
async def create_calendar_events(tasks: List[StudyTask]):
    """
    Create Google Calendar events for study tasks
    """
    try:
        events = await calendar_service.create_study_events(tasks)
        return {
            "message": "Calendar events created successfully",
            "events_created": len(events),
            "events": events
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create calendar events: {str(e)}")


@app.get("/calendar/free-slots")
async def get_free_slots(start_date: str, end_date: str):
    """
    Get available time slots in the calendar
    """
    try:
        free_slots = await calendar_service.get_free_slots(start_date, end_date)
        return {"free_slots": free_slots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch free slots: {str(e)}")


@app.delete("/calendar/event/{event_id}")
async def delete_calendar_event(event_id: str):
    """
    Delete a specific calendar event
    """
    try:
        success = await calendar_service.delete_event(event_id)
        if success:
            return {"message": "Event deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Event not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
