"""
Models package for Study Planner
Contains Pydantic schemas for request/response validation
"""

from .schemas import (
    Assignment,
    StudyPlan,
    StudyTask,
    UserPreferences,
    CalendarEventResponse,
    CanvasAuthRequest,
    GoogleAuthRequest,
    ErrorResponse
)

__all__ = [
    'Assignment',
    'StudyPlan',
    'StudyTask',
    'UserPreferences',
    'CalendarEventResponse',
    'CanvasAuthRequest',
    'GoogleAuthRequest',
    'ErrorResponse'
]
