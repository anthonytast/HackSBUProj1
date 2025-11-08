import httpx
from typing import List, Optional
from datetime import datetime, timezone
import os
from schemas import Assignment


class CanvasService:
    """Service for interacting with Canvas LMS API"""
    
    def __init__(self):
        self.canvas_url = os.getenv("CANVAS_URL", "")
        self.access_token = os.getenv("CANVAS_ACCESS_TOKEN", "")
        self.base_url = ""
        self.headers = {}
        self.is_authenticated = False
    
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
                if response.status_code == 200:
                    self.is_authenticated = True
                    return True
                else:
                    self.is_authenticated = False
                    return False
        except Exception as e:
            print(f"Canvas authentication error: {e}")
            self.is_authenticated = False
            return False
    
    async def fetch_assignments(self) -> List[Assignment]:
        """
        Fetch upcoming assignments from Canvas - from to-do list, upcoming events, and all active courses
        
        Returns:
            List of Assignment objects
        """
        if not self.is_authenticated or not self.base_url or not self.headers:
            raise Exception("Canvas service not authenticated. Please authenticate first.")
        
        try:
            assignments = []
            seen_ids = set()
            # Use UTC for comparison since Canvas dates are in UTC
            now = datetime.now(timezone.utc)
            
            async with httpx.AsyncClient() as client:
                # Fetch from to-do list
                try:
                    response = await client.get(
                        f"{self.base_url}/users/self/todo",
                        headers=self.headers,
                        timeout=15.0
                    )
                    response.raise_for_status()
                    todo_items = response.json()
                except Exception as e:
                    print(f"Warning: Could not fetch todo items: {e}")
                    todo_items = []
                
                # Also fetch upcoming assignments
                try:
                    response = await client.get(
                        f"{self.base_url}/users/self/upcoming_events",
                        headers=self.headers,
                        timeout=15.0
                    )
                    response.raise_for_status()
                    upcoming = response.json()
                except Exception as e:
                    print(f"Warning: Could not fetch upcoming events: {e}")
                    upcoming = []
                
                # Combine and deduplicate from todo/upcoming
                all_items = todo_items + upcoming
                
                for item in all_items:
                    # Handle both assignment and calendar event formats
                    if 'assignment' in item:
                        assignment_data = item['assignment']
                        assignment_id = assignment_data.get('id')
                    else:
                        assignment_data = item
                        assignment_id = item.get('id')
                    
                    if assignment_id and assignment_id not in seen_ids:
                        # Check if assignment has a due date and it's today or in the future
                        due_date_str = assignment_data.get('due_at')
                        should_include = True
                        
                        if due_date_str:
                            try:
                                # Parse UTC date from Canvas - handle both 'Z' and '+00:00' formats
                                if due_date_str.endswith('Z'):
                                    due_date_str_parsed = due_date_str.replace('Z', '+00:00')
                                elif '+' in due_date_str or due_date_str.endswith('UTC'):
                                    due_date_str_parsed = due_date_str
                                else:
                                    # If no timezone info, assume UTC
                                    due_date_str_parsed = due_date_str + '+00:00'
                                
                                due_date = datetime.fromisoformat(due_date_str_parsed)
                                
                                # Ensure both datetimes are timezone-aware for comparison
                                if due_date.tzinfo is None:
                                    due_date = due_date.replace(tzinfo=timezone.utc)
                                
                                # Only include if due date is today or in the future
                                if due_date < now:
                                    should_include = False  # Skip past assignments
                            except Exception as e:
                                # If we can't parse the date, include it anyway (might be valid)
                                print(f"Warning: Could not parse due date '{due_date_str}': {e}")
                                should_include = True
                        
                        if should_include:
                            # Include assignments without due dates (they might be upcoming)
                            seen_ids.add(assignment_id)
                            
                            # Parse assignment data
                            assignment = self._parse_assignment(assignment_data, item)
                            if assignment:
                                assignments.append(assignment)
                
                # Also fetch assignments from all active courses for comprehensive coverage
                try:
                    courses_response = await client.get(
                        f"{self.base_url}/courses",
                        headers=self.headers,
                        params={
                            "enrollment_state": "active",
                            "per_page": 100
                        },
                        timeout=15.0
                    )
                    courses_response.raise_for_status()
                    courses = courses_response.json()
                    
                    # Fetch assignments from each course
                    for course in courses:
                        course_id = course.get('id')
                        if not course_id:
                            continue
                        
                        try:
                            assignments_response = await client.get(
                                f"{self.base_url}/courses/{course_id}/assignments",
                                headers=self.headers,
                                params={
                                    "order_by": "due_at",
                                    "per_page": 100
                                },
                                timeout=10.0
                            )
                            assignments_response.raise_for_status()
                            course_assignments = assignments_response.json()
                            
                            course_name = course.get('name', f'Course {course_id}')
                            
                            for assignment_data in course_assignments:
                                assignment_id = assignment_data.get('id')
                                
                                # Only add if not already seen and has a due date today or in the future
                                if assignment_id and assignment_id not in seen_ids:
                                    # Check if assignment has a due date and it's today or in the future
                                    due_date_str = assignment_data.get('due_at')
                                    should_include = True
                                    
                                    if due_date_str:
                                        try:
                                            # Parse UTC date from Canvas - handle both 'Z' and '+00:00' formats
                                            if due_date_str.endswith('Z'):
                                                due_date_str_parsed = due_date_str.replace('Z', '+00:00')
                                            elif '+' in due_date_str or due_date_str.endswith('UTC'):
                                                due_date_str_parsed = due_date_str
                                            else:
                                                # If no timezone info, assume UTC
                                                due_date_str_parsed = due_date_str + '+00:00'
                                            
                                            due_date = datetime.fromisoformat(due_date_str_parsed)
                                            
                                            # Ensure both datetimes are timezone-aware for comparison
                                            if due_date.tzinfo is None:
                                                due_date = due_date.replace(tzinfo=timezone.utc)
                                            
                                            # Only include if due date is today or in the future
                                            if due_date < now:
                                                should_include = False  # Skip past assignments
                                        except Exception as e:
                                            # If we can't parse the date, include it anyway (might be valid)
                                            print(f"Warning: Could not parse due date '{due_date_str}': {e}")
                                            should_include = True
                                    
                                    if should_include:
                                        # Include assignments without due dates (they might be upcoming)
                                        seen_ids.add(assignment_id)
                                        assignment = self._parse_assignment(
                                            assignment_data,
                                            {'context_name': course_name}
                                        )
                                        if assignment:
                                            assignments.append(assignment)
                        except Exception as e:
                            print(f"Warning: Could not fetch assignments for course {course_id}: {e}")
                            continue
                            
                except Exception as e:
                    print(f"Warning: Could not fetch courses: {e}")
                    # Continue with assignments we already have
            
            # Sort by due date (handle None values and timezone-aware datetimes)
            def get_sort_key(assignment):
                if assignment.due_date:
                    return assignment.due_date
                # Use a far future UTC datetime for assignments without due dates
                # datetime.max is timezone-naive, so create a far future UTC datetime instead
                return datetime(9999, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
            
            assignments.sort(key=get_sort_key)
            return assignments
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error fetching Canvas assignments: {e}")
            print(f"Traceback: {error_details}")
            raise Exception(f"Failed to fetch assignments from Canvas: {str(e)}")
    
    async def fetch_course_assignments(self, course_id: int) -> List[Assignment]:
        """
        Fetch assignments for a specific course
        
        Args:
            course_id: Canvas course ID
            
        Returns:
            List of Assignment objects
        """
        if not self.is_authenticated or not self.base_url or not self.headers:
            raise Exception("Canvas service not authenticated. Please authenticate first.")
        
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
                
                # Use UTC for comparison since Canvas dates are in UTC
                now = datetime.now(timezone.utc)
                for item in assignment_list:
                    assignment = self._parse_assignment(item, {'context_name': course_name})
                    # Only include assignments with due dates today or in the future, or no due date
                    if assignment:
                        if assignment.due_date:
                            # Only include if due date is today or in the future
                            if assignment.due_date >= now:
                                assignments.append(assignment)
                        else:
                            # Include assignments without due dates (they might be upcoming)
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
        if not self.is_authenticated or not self.base_url or not self.headers:
            raise Exception("Canvas service not authenticated. Please authenticate first.")
        
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
