import google.generativeai as genai
from typing import List
from datetime import datetime, timedelta
import json
import os
from models.schemas import Assignment, StudyPlan, StudyTask, UserPreferences


class GeminiService:
    """Service for generating AI-powered study plans using Google Gemini"""
    
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_study_plan(
        self,
        assignments: List[Assignment],
        preferences: UserPreferences
    ) -> StudyPlan:
        """
        Generate a comprehensive study plan using Gemini AI
        
        Args:
            assignments: List of Canvas assignments
            preferences: User study preferences
            
        Returns:
            StudyPlan object with scheduled tasks
        """
        try:
            # Build the prompt
            prompt = self._build_prompt(assignments, preferences)
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the AI response
            study_plan = self._parse_response(response.text, assignments)
            
            return study_plan
            
        except Exception as e:
            print(f"Error generating study plan: {e}")
            raise Exception(f"Failed to generate study plan: {str(e)}")
    
    def _build_prompt(self, assignments: List[Assignment], preferences: UserPreferences) -> str:
        """
        Build a detailed prompt for Gemini to generate study plan
        
        Args:
            assignments: List of assignments
            preferences: User preferences
            
        Returns:
            Formatted prompt string
        """
        current_date = datetime.now()
        
        # Format assignments for the prompt
        assignments_text = ""
        for idx, assignment in enumerate(assignments, 1):
            due_date_str = assignment.due_date.strftime("%Y-%m-%d %H:%M") if assignment.due_date else "No due date"
            assignments_text += f"""
Assignment {idx}:
- Title: {assignment.title}
- Course: {assignment.course_name}
- Type: {assignment.assignment_type}
- Due Date: {due_date_str}
- Points: {assignment.points if assignment.points else 'N/A'}
- Description: {assignment.description[:200] if assignment.description else 'No description'}
"""
        
        prompt = f"""You are an expert study planner. Create a detailed, realistic study plan for the following assignments.

Current Date: {current_date.strftime("%Y-%m-%d")}
Current Time: {current_date.strftime("%H:%M")}

ASSIGNMENTS:
{assignments_text}

USER PREFERENCES:
- Study session length: {preferences.study_session_length} minutes
- Break frequency: {preferences.break_frequency} minutes (Pomodoro technique)
- Maximum daily study hours: {preferences.daily_study_hours} hours
- Preferred study times: {', '.join(preferences.preferred_study_times)}
- Buffer days before deadline: {preferences.buffer_days} days
- Study on weekends: {'Yes' if preferences.weekend_study else 'No'}

INSTRUCTIONS:
1. Break down EACH assignment into specific, actionable study tasks
2. Estimate realistic time needed for each task (in minutes)
3. Schedule tasks strategically:
   - Start earlier for harder/longer assignments
   - Finish at least {preferences.buffer_days} day(s) before due date
   - Distribute work evenly across available days
   - Consider assignment type (exams need more review, papers need drafting/editing, etc.)
4. Prioritize based on:
   - Due date proximity
   - Point value/weight
   - Assignment difficulty
5. Schedule tasks during preferred study times when possible
6. Keep sessions at or under {preferences.study_session_length} minutes

OUTPUT FORMAT:
Return ONLY a valid JSON object with this exact structure:
{{
  "tasks": [
    {{
      "task_name": "Specific task description",
      "assignment_title": "Assignment name",
      "course_name": "Course name",
      "duration_minutes": 60,
      "suggested_date": "2025-11-10",
      "suggested_start_time": "14:00",
      "priority": "high|medium|low",
      "description": "Detailed description of what to do"
    }}
  ],
  "plan_summary": "Brief overview of the study plan"
}}

IMPORTANT:
- Use 24-hour time format (HH:MM)
- Use ISO date format (YYYY-MM-DD)
- Ensure dates are realistic and in the future
- Return ONLY the JSON object, no additional text or markdown formatting
- Make sure all tasks have realistic time estimates
"""
        
        return prompt
    
    def _parse_response(self, response_text: str, assignments: List[Assignment]) -> StudyPlan:
        """
        Parse Gemini's JSON response into StudyPlan object
        
        Args:
            response_text: Raw response from Gemini
            assignments: Original assignments for reference
            
        Returns:
            StudyPlan object
        """
        try:
            # Clean up the response (remove markdown code blocks if present)
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON
            data = json.loads(cleaned_text)
            
            # Create StudyTask objects
            tasks = []
            total_time = 0
            
            # Create a lookup for assignment details
            assignment_lookup = {a.title: a for a in assignments}
            
            for task_data in data.get('tasks', []):
                # Find matching assignment
                assignment_title = task_data.get('assignment_title', '')
                matching_assignment = assignment_lookup.get(assignment_title)
                
                task = StudyTask(
                    task_name=task_data.get('task_name', ''),
                    assignment_title=assignment_title,
                    course_name=task_data.get('course_name', ''),
                    duration_minutes=task_data.get('duration_minutes', 60),
                    suggested_date=task_data.get('suggested_date', ''),
                    suggested_start_time=task_data.get('suggested_start_time', '09:00'),
                    priority=task_data.get('priority', 'medium'),
                    description=task_data.get('description', ''),
                    course_id=matching_assignment.course_id if matching_assignment else None,
                    assignment_id=matching_assignment.id if matching_assignment else None
                )
                tasks.append(task)
                total_time += task.duration_minutes
            
            # Create StudyPlan
            study_plan = StudyPlan(
                tasks=tasks,
                total_study_time=total_time,
                plan_summary=data.get('plan_summary', f'Study plan with {len(tasks)} tasks')
            )
            
            return study_plan
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")
            print(f"Response text: {response_text}")
            # Return a basic fallback plan
            return self._create_fallback_plan(assignments)
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._create_fallback_plan(assignments)
    
    def _create_fallback_plan(self, assignments: List[Assignment]) -> StudyPlan:
        """
        Create a basic fallback study plan if AI generation fails
        
        Args:
            assignments: List of assignments
            
        Returns:
            Basic StudyPlan
        """
        tasks = []
        current_date = datetime.now()
        
        for assignment in assignments:
            if not assignment.due_date:
                continue
            
            # Calculate days until due date
            days_until_due = (assignment.due_date - current_date).days
            
            # Create 2-3 tasks per assignment
            if days_until_due > 3:
                # Task 1: Review/Research
                tasks.append(StudyTask(
                    task_name=f"Review materials for {assignment.title}",
                    assignment_title=assignment.title,
                    course_name=assignment.course_name,
                    duration_minutes=90,
                    suggested_date=(current_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                    suggested_start_time="14:00",
                    priority="medium",
                    description=f"Review course materials and requirements for {assignment.title}",
                    course_id=assignment.course_id,
                    assignment_id=assignment.id
                ))
                
                # Task 2: Work session
                tasks.append(StudyTask(
                    task_name=f"Work on {assignment.title}",
                    assignment_title=assignment.title,
                    course_name=assignment.course_name,
                    duration_minutes=120,
                    suggested_date=(current_date + timedelta(days=max(2, days_until_due-2))).strftime("%Y-%m-%d"),
                    suggested_start_time="10:00",
                    priority="high" if days_until_due <= 5 else "medium",
                    description=f"Complete main work for {assignment.title}",
                    course_id=assignment.course_id,
                    assignment_id=assignment.id
                ))
                
                # Task 3: Review/Polish
                tasks.append(StudyTask(
                    task_name=f"Final review for {assignment.title}",
                    assignment_title=assignment.title,
                    course_name=assignment.course_name,
                    duration_minutes=60,
                    suggested_date=(assignment.due_date - timedelta(days=1)).strftime("%Y-%m-%d"),
                    suggested_start_time="15:00",
                    priority="high",
                    description=f"Review and polish {assignment.title} before submission",
                    course_id=assignment.course_id,
                    assignment_id=assignment.id
                ))
        
        total_time = sum(task.duration_minutes for task in tasks)
        
        return StudyPlan(
            tasks=tasks,
            total_study_time=total_time,
            plan_summary=f"Basic study plan with {len(tasks)} tasks for {len(assignments)} assignments"
        )
