import httpx
from typing import List, Optional
from datetime import datetime
import os
from models.schemas import Assignment


class CanvasService:
    """Service for interacting with Canvas LMS API"""
    
    def __init__(self):
        self.canvas_url = os.getenv("CANVAS_URL", "")
        self.access_token = os.getenv("CANVAS_ACCESS_TOKEN", "")
        self.base_url = ""
        self.headers = {}
    
    async def authenticate(self, canvas_url: str, access_token: str) -> bool:
        """
        Authenticate with Canvas API and verify credentials
        
        Args:
            canvas_url: Canvas institution URL
            access_token: Canvas API access token
            
        Returns:
            bool: True if authentication successful
        """
        try:
            self.canvas_url = canvas_url.rstrip('/')
            self.access_token = access_token
            self.base_url = f"{self.canvas_url}/api/v1"
            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            # Test authentication by fetching user profile
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/self",
                    headers=self.headers,
                    timeout=10.0
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Canvas authentication error: {e}")
            return False
    
    async def fetch_assignments(self) -> List[Assignment]:
        """
        Fetch upcoming assignments from Canvas to-do list
        
        Returns:
            List of Assignment objects
        """
        try:
            assignments = []
            
            # Fetch from to-do list
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/self/todo",
                    headers=self.headers,
                    timeout=15.0
                )
                response.raise_for_status()
                todo_items = response.json()
                
                # Also fetch upcoming assignments
                response = await client.get(
                    f"{self.base_url}/users/self/upcoming_events",
                    headers=self.headers,
                    timeout=15.0
                )
                response.raise_for_status()
                upcoming = response.json()
                
                # Combine and deduplicate
                all_items = todo_items + upcoming
                seen_ids = set()
                
                for item in all_items:
                    # Handle both assignment and calendar event formats
                    if 'assignment' in item:
                        assignment_data = item['assignment']
                        assignment_id = assignment_data.get('id')
                    else:
                        assignment_data = item
                        assignment_id = item.get('id')
                    
                    if assignment_id and assignment_id not in seen_ids:
                        seen_ids.add(assignment_id)
                        
                        # Parse assignment data
                        assignment = self._parse_assignment(assignment_data, item)
                        if assignment:
                            assignments.append(assignment)
            
            # Sort by due date
            assignments.sort(key=lambda x: x.due_date or datetime.max)
            return assignments
            
        except Exception as e:
            print(f"Error fetching Canvas assignments: {e}")
            raise Exception(f"Failed to fetch assignments from Canvas: {str(e)}")
    
    async def fetch_course_assignments(self, course_id: int) -> List[Assignment]:
        """
        Fetch assignments for a specific course
        
        Args:
            course_id: Canvas course ID
            
        Returns:
            List of Assignment objects
        """
        try:
            assignments = []
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/courses/{course_id}/assignments",
                    headers=self.headers,
                    params={"order_by": "due_at"},
                    timeout=15.0
                )
                response.raise_for_status()
                assignment_list = response.json()
                
                # Get course info
                course_response = await client.get(
                    f"{self.base_url}/courses/{course_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                course_data = course_response.json()
                course_name = course_data.get('name', f'Course {course_id}')
                
                for item in assignment_list:
                    assignment = self._parse_assignment(item, {'context_name': course_name})
                    if assignment and assignment.due_date and assignment.due_date > datetime.now():
                        assignments.append(assignment)
            
            return assignments
            
        except Exception as e:
            print(f"Error fetching course assignments: {e}")
            raise Exception(f"Failed to fetch course assignments: {str(e)}")
    
    def _parse_assignment(self, assignment_data: dict, context: dict) -> Optional[Assignment]:
        """
        Parse Canvas API response into Assignment model
        
        Args:
            assignment_data: Raw assignment data from Canvas
            context: Additional context (course name, etc.)
            
        Returns:
            Assignment object or None if parsing fails
        """
        try:
            # Extract due date
            due_date_str = assignment_data.get('due_at')
            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                except:
                    pass
            
            # Determine assignment type
            assignment_type = "assignment"
            name = assignment_data.get('name', '').lower()
            if 'exam' in name or 'test' in name or 'quiz' in name:
                assignment_type = "exam"
            elif 'paper' in name or 'essay' in name:
                assignment_type = "paper"
            elif 'problem' in name or 'homework' in name:
                assignment_type = "problem_set"
            elif 'project' in name:
                assignment_type = "project"
            
            # Get course name from context
            course_name = context.get('context_name') or context.get('course', {}).get('name', 'Unknown Course')
            
            return Assignment(
                id=assignment_data.get('id'),
                title=assignment_data.get('name', 'Untitled Assignment'),
                description=assignment_data.get('description', ''),
                due_date=due_date,
                course_name=course_name,
                course_id=assignment_data.get('course_id', 0),
                assignment_type=assignment_type,
                points=assignment_data.get('points_possible'),
                submission_types=assignment_data.get('submission_types', []),
                html_url=assignment_data.get('html_url')
            )
            
        except Exception as e:
            print(f"Error parsing assignment: {e}")
            return None
    
    async def get_courses(self) -> List[dict]:
        """
        Fetch list of active courses
        
        Returns:
            List of course dictionaries
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/courses",
                    headers=self.headers,
                    params={
                        "enrollment_state": "active",
                        "per_page": 100
                    },
                    timeout=15.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Error fetching courses: {e}")
            return []
