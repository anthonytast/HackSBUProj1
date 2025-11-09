from typing import List
from datetime import datetime, timedelta
import json
import re
import os
import httpx
import pytz
from schemas import Assignment, StudyPlan, StudyTask, UserPreferences


class GeminiService:
    """Service for generating AI-powered study plans using OpenRouter's Gemini access"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.api_base = "https://openrouter.ai/api/v1"
        # Allow model override via env var. If not set, we'll attempt a sensible fallback.
        # Many OpenRouter installations expose different model IDs — prefer explicit config.
        # Will be set by find_available_model()
        self.model = None
        self.fallback_model = None
        # Create HTTP client first so model discovery can call the API
        self.http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000",  # Replace with your domain in production
                "Content-Type": "application/json"
            }
        )
        # Initialize model choices after HTTP client is ready
        self._initialize_models()
    
    async def generate_study_plan(
        self,
        assignments: List[Assignment],
        preferences: UserPreferences,
        free_slots: List[dict] | None = None
    ) -> StudyPlan:
        try:
            # Build the prompt and payload. If free_slots were provided (from the user's calendar),
            # include them so the model schedules only during available times.
            prompt = self._build_prompt(assignments, preferences, free_slots)
            payload = {
                "messages": [
                    {"role": "user", "content": [{"type": "text", "text": prompt}]}
                ],
                "temperature": 0.7,
                "max_tokens": 2048,
                "stream": False,
                "model": self.model  # Ensure model is in the payload
            }

            # Use helper to POST with configured model, and retry with a fallback if OpenRouter says model is invalid
            try:
                response = await self._post_with_model("/chat/completions", payload, timeout=30.0)
            except httpx.HTTPStatusError as e:
                # Already logged inside _post_with_model; fall back to creating a safe plan
                print(f"OpenRouter API error when generating study plan: {e}")
                return self._create_fallback_plan(assignments)

            # Extract the response text robustly (OpenRouter may return content as list)
            response_data = response.json()
            response_text = ""
            try:
                print("\n=== OpenRouter Response Debug ===")
                print("Raw response data:")
                print(json.dumps(response_data, indent=2))
                
                choice = response_data.get("choices", [])[0]
                message = choice.get("message", {})
                content = message.get("content")
                if isinstance(content, list):
                    parts = [c.get("text", "") for c in content if isinstance(c, dict)]
                    response_text = "".join(parts)
                elif isinstance(content, str):
                    response_text = content
                else:
                    response_text = response_data.get("output", "") or response_data.get("text", "") or json.dumps(response_data)
                
                print("\nExtracted response text:")
                print(response_text[:800] + "..." if len(response_text) > 800 else response_text)
                # If the model stopped due to token limits, proactively ask it to continue
                finish_reason = choice.get("finish_reason", "")
                native_finish = choice.get("native_finish_reason", "")
                try:
                    if ((isinstance(finish_reason, str) and finish_reason.lower() == "length")
                        or (isinstance(native_finish, str) and "max_tokens" in native_finish.lower())
                        or (isinstance(finish_reason, str) and "max_tokens" in finish_reason.lower())):
                        print(f"Model finish_reason='{finish_reason}', native_finish_reason='{native_finish}' -> attempting automatic continuation to complete JSON")
                        try:
                            # Attempt to get the missing remainder from the model and use the combined text
                            combined_text = await self._attempt_complete_json(response_text, prompt, attempts=3)
                            response_text = combined_text
                            print("Automatic continuation succeeded; using combined text for parsing")
                        except Exception as cont_err:
                            print(f"Automatic continuation failed: {cont_err}; will attempt parsing original response")
                except Exception:
                    # Defensive: don't allow continuation logic to crash the pipeline
                    pass

                print("=== End Debug ===\n")
            except Exception as e:
                print(f"Error extracting response text: {e}")
                response_text = json.dumps(response_data)

            # Parse the response. If parsing fails due to truncated JSON, attempt to
            # recover by asking the model to finish the JSON and re-parse the result.
            try:
                study_plan = self._parse_response(response_text, assignments)
                return study_plan
            except json.JSONDecodeError as e:
                print(f"Initial JSON parse failed: {e}. Attempting to recover by asking model to complete the JSON...")
                try:
                    # Ask the model to continue the partial JSON and return only the JSON
                    combined_text = await self._attempt_complete_json(response_text, prompt)
                    # Re-parse the combined text
                    study_plan = self._parse_response(combined_text, assignments)
                    return study_plan
                except Exception as e2:
                    print(f"Failed to recover JSON after continuation attempts: {e2}")
                    return self._create_fallback_plan(assignments)

        except httpx.HTTPError as api_error:
            print(f"OpenRouter API error: {api_error}")
            return self._create_fallback_plan(assignments)
        except Exception as e:
            print(f"Error in study plan generation: {e}")
            return self._create_fallback_plan(assignments)
    
    def _build_prompt(self, assignments: List[Assignment], preferences: UserPreferences, free_slots: List[dict] | None = None) -> str:
        """
        Build a detailed prompt for Gemini to generate study plan. If free_slots is provided,
        include the calendar availability so the model avoids scheduling during busy times.
        """

        # Use timezone from preferences or default to configured timezone
        timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))
        current_date = datetime.now(timezone)

        # Format assignments for the prompt
        assignments_text = ""
        for idx, assignment in enumerate(assignments, 1):
            # Ensure due date is timezone-aware
            if assignment.due_date:
                if assignment.due_date.tzinfo is None:
                    due_date = timezone.localize(assignment.due_date)
                else:
                    due_date = assignment.due_date
                due_date_str = due_date.strftime("%Y-%m-%d %H:%M %Z")
            else:
                due_date_str = "No due date"
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

CALENDAR AVAILABILITY:
"""

        if free_slots:
            # free_slots is expected to be a list of {start, end, duration_minutes}
            prompt += "The user has the following free time slots available in their calendar (ISO datetimes):\n"
            for slot in free_slots:
                start = slot.get('start')
                end = slot.get('end')
                dur = slot.get('duration_minutes')
                prompt += f"- Free slot: {start} to {end} ({dur} minutes)\n"
            prompt += "Only schedule study tasks inside these free slots. Do not schedule during busy events.\n\n"
        else:
            prompt += "No calendar availability was provided; schedule tasks according to preferred study times.\n\n"

        prompt += f"""
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
            
            # Parse JSON (use robust helper to handle malformed JSON from model)
            # NOTE: Let JSONDecodeError propagate so callers may attempt recovery
            data = self._safe_parse_json(cleaned_text)
            
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
            
        except json.JSONDecodeError:
            # Propagate JSON parsing errors up so the caller (generate_study_plan)
            # can attempt to recover by requesting the model to finish the output.
            raise
        except Exception as e:
            print(f"Error parsing Gemini response: {e}")
            return self._create_fallback_plan(assignments)

    async def _attempt_complete_json(self, partial_text: str, original_prompt: str, attempts: int = 2) -> str:
        """
        When the model output appears truncated (unterminated strings/braces), ask the model
        to continue the JSON. Try a couple of times and return the combined text if successful.

        Args:
            partial_text: The text the model returned that looks truncated
            original_prompt: The original prompt given to the model (for context if needed)
            attempts: Number of continuation attempts

        Returns:
            The combined text (original partial + continuation) expected to be valid JSON

        Raises:
            RuntimeError if unable to recover a valid JSON after attempts
        """
        # Normalize partial (strip fences)
        normalized = partial_text
        if normalized.startswith('```json'):
            normalized = normalized[7:]
        if normalized.startswith('```'):
            normalized = normalized[3:]
        if normalized.endswith('```'):
            normalized = normalized[:-3]
        normalized = normalized.strip()

        for i in range(attempts):
            cont_prompt = (
                "The previous response appears to have been cut off. Continue and return ONLY the complete JSON object, "
                "with no explanation, commentary, or markdown. Do not wrap in code fences. If the partial JSON is repeated, "
                "only include the missing remainder so that concatenating the partial and this continuation yields a valid JSON.\n\n"
                "Partial output:\n" + normalized
            )

            payload = {
                "messages": [
                    {"role": "system", "content": [{"type": "text", "text": "You are a helpful assistant that must reply with valid JSON only."}]},
                    {"role": "user", "content": [{"type": "text", "text": cont_prompt}]}
                ],
                "temperature": 0.0,
                "max_tokens": 1024,
                "stream": False,
            }

            try:
                resp = await self._post_with_model("/chat/completions", payload, timeout=20.0)
                resp_data = resp.json()
                choice = resp_data.get("choices", [])[0]
                message = choice.get("message", {})
                content = message.get("content")
                if isinstance(content, list):
                    parts = [c.get("text", "") for c in content if isinstance(c, dict)]
                    continuation = "".join(parts)
                else:
                    continuation = content or ""

                # Combine partial + continuation and try parsing
                combined = normalized + continuation
                # Clean obvious fences
                combined = combined.replace('```json', '').replace('```', '').strip()

                try:
                    # If _safe_parse_json succeeds, return the combined string
                    self._safe_parse_json(combined)
                    return combined
                except Exception as e:
                    print(f"_attempt_complete_json: parse after continuation attempt {i} failed: {e}")
                    # Expand normalized to include continuation and try again in next iteration
                    normalized = combined
                    continue
            except Exception as e:
                print(f"_attempt_complete_json: request attempt {i} failed: {e}")
                continue

        raise RuntimeError("Failed to recover truncated JSON after continuation attempts")
    
    async def classify_assignments(self, assignments: List[Assignment]) -> List[dict]:
        """
        Classify assignments into categories based on their descriptions and estimate time
        
        Args:
            assignments: List of assignments to classify
            
        Returns:
            List of dictionaries with classification data: {id, category, estimated_time_minutes}
        """
        try:
            # Build classification prompt
            prompt = self._build_classification_prompt(assignments)
            
            try:
                # Make request to OpenRouter API using helper (handles model/fallback)
                payload = {"messages": [{"role": "user", "content": [{"type": "text", "text": prompt}] }]}
                try:
                    response = await self._post_with_model("/chat/completions", payload)
                except httpx.HTTPStatusError as e:
                    print(f"OpenRouter API returned error when classifying: {e}")
                    raise

                response_data = response.json()
                # Extract text similarly to generation endpoint
                choice = response_data.get("choices", [])[0]
                message = choice.get("message", {})
                content = message.get("content")
                if isinstance(content, list):
                    parts = [c.get("text", "") for c in content if isinstance(c, dict)]
                    response_text = "".join(parts)
                elif isinstance(content, str):
                    response_text = content
                else:
                    response_text = json.dumps(response_data)
                
                # Parse the response
                classifications = self._parse_classification_response(response_text, assignments)
                return classifications
                
            except httpx.HTTPError as api_error:
                print(f"OpenRouter API error: {api_error}")
                return self._create_fallback_classifications(assignments)
            
        except Exception as e:
            print(f"Error in assignment classification: {e}")
            return self._create_fallback_classifications(assignments)
    
    def _build_classification_prompt(self, assignments: List[Assignment]) -> str:
        """
        Build prompt for classifying assignments
        
        Args:
            assignments: List of assignments
            
        Returns:
            Formatted prompt string
        """
        assignments_text = ""
        for idx, assignment in enumerate(assignments, 1):
            due_date_str = assignment.due_date.strftime("%Y-%m-%d %H:%M") if assignment.due_date else "No due date"
            description = assignment.description[:500] if assignment.description else "No description"
            assignments_text += f"""
Assignment {idx} (ID: {assignment.id}):
- Title: {assignment.title}
- Course: {assignment.course_name}
- Type: {assignment.assignment_type}
- Due Date: {due_date_str}
- Points: {assignment.points if assignment.points else 'N/A'}
- Description: {description}
"""
        
        prompt = f"""Analyze the following assignments and classify each one into a category based on estimated time to complete. Consider the title, description, type, points, and due date.

ASSIGNMENTS:
{assignments_text}

CATEGORIES (based on estimated time):
- "quick_task": 15-60 minutes (simple quizzes, short responses, quick readings)
- "medium_effort": 1-3 hours (homework problems, short essays, medium projects)
- "long_project": 3-8 hours (research papers, large projects, comprehensive exams)
- "major_project": 8+ hours (thesis work, major research, complex multi-part projects)

INSTRUCTIONS:
1. Analyze each assignment's description, title, type, and point value
2. Estimate realistic time to complete (in minutes)
3. Classify into the appropriate category
4. Consider: complexity, length, research needed, writing required, problem-solving difficulty

OUTPUT FORMAT:
Return ONLY a valid JSON array with this exact structure:
[
  {{
    "assignment_id": 12345,
    "category": "medium_effort",
    "estimated_time_minutes": 120,
    "reasoning": "Brief explanation of classification"
  }}
]

IMPORTANT:
- Return ONLY the JSON array, no additional text or markdown
- Include ALL assignments in the response
- Use realistic time estimates based on typical student work
- Categories should reflect actual time needed, not just assignment type
"""
        return prompt
    
    def _parse_classification_response(self, response_text: str, assignments: List[Assignment]) -> List[dict]:
        """
        Parse classification response from Gemini
        
        Args:
            response_text: Raw response from Gemini
            assignments: Original assignments for reference
            
        Returns:
            List of classification dictionaries
        """
        try:
            # Clean up the response
            cleaned_text = response_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            cleaned_text = cleaned_text.strip()
            
            # Parse JSON (use robust helper to handle malformed JSON from model)
            classifications = self._safe_parse_json(cleaned_text)
            
            # Validate and format
            result = []
            assignment_ids = {a.id for a in assignments}
            
            for item in classifications:
                assignment_id = item.get('assignment_id')
                if assignment_id in assignment_ids:
                    result.append({
                        'assignment_id': assignment_id,
                        'category': item.get('category', 'medium_effort'),
                        'estimated_time_minutes': item.get('estimated_time_minutes', 120),
                        'reasoning': item.get('reasoning', '')
                    })
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error in classification: {e}")
            print(f"Response text: {response_text}")
            return self._create_fallback_classifications(assignments)
        except Exception as e:
            print(f"Error parsing classification response: {e}")
            return self._create_fallback_classifications(assignments)

    def _safe_parse_json(self, text: str):
        """
        Try several heuristics to robustly parse JSON-like text produced by models.
        Handles truncated arrays, malformed task lists, and various JSON format errors.
        """
        # Track best attempt for error reporting
        best_attempt = None
        last_error = None
        
        def clean_text(t):
            """Remove markdown and normalize whitespace"""
            t = t.strip()
            if t.startswith('```json'):
                t = t[7:]
            if t.startswith('```'):
                t = t[3:]
            if t.endswith('```'):
                t = t[:-3]
            return t.strip()
        
        def extract_json_object(t):
            """Extract largest {...} block, handling nested braces"""
            start = t.find('{')
            if start == -1:
                return None
            
            # Track brace depth to handle nesting
            depth = 0
            for i, c in enumerate(t[start:], start):
                if c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        # Found matching end brace
                        return t[start:i+1]
            return None
        
        def fix_common_json_errors(t):
            """Apply various JSON fixes and normalizations"""
            # Replace single quotes with double quotes (outside of existing double-quoted strings)
            t = re.sub(r'(?<!")(\'[^\']*\')(?!")', lambda m: m.group(0).replace("'", '"'), t)
            
            # Quote unquoted keys
            t = re.sub(r'([\{,]\s*)([A-Za-z0-9_\-]+)(\s*:)', r'\1"\2"\3', t)
            
            # Fix truncated arrays by adding missing closing elements
            if t.count('[') > t.count(']'):
                t = t + ']' * (t.count('[') - t.count(']'))
            if t.count('{') > t.count('}'):
                t = t + '}' * (t.count('{') - t.count('}'))
                
            # Ensure objects end with } even if truncated
            if not t.rstrip().endswith('}'):
                if t.rstrip().endswith(','):
                    t = t.rstrip()[:-1]  # remove trailing comma
                t = t + '}'
                
            return t
        
        def try_parse(t, attempt_name=""):
            """Try to parse JSON and track attempt"""
            nonlocal best_attempt, last_error
            try:
                result = json.loads(t)
                # If we got here, this attempt worked
                return result
            except json.JSONDecodeError as e:
                # Track this attempt if it's the first or if it got further in the input
                if not last_error or e.pos > last_error.pos:
                    best_attempt = t[:e.pos + 10]  # keep some context
                    last_error = e
                if attempt_name:
                    print(f"_safe_parse_json: {attempt_name} failed: {e}")
                return None
        
        # Clean up the input
        cleaned = clean_text(text)
        
        # 1. Try parsing the cleaned input directly
        if result := try_parse(cleaned, "initial json.loads"):
            return result
        
        # 2. Try extracting and parsing the largest {...} block
        if json_obj := extract_json_object(cleaned):
            if result := try_parse(json_obj, "extracted object"):
                return result
        
        # 3. Try fixing common JSON errors in the extracted object or full text
        if json_obj:
            if result := try_parse(fix_common_json_errors(json_obj), "fixed object"):
                return result
        
        if result := try_parse(fix_common_json_errors(cleaned), "fixed full text"):
            return result
        
        # 4. Try ast.literal_eval as a fallback for Python-style dict syntax
        try:
            import ast
            pyobj = ast.literal_eval(cleaned)
            return json.loads(json.dumps(pyobj))
        except Exception as e:
            print(f"_safe_parse_json: ast.literal_eval failed: {e}")
        
        # If we got here, all attempts failed
        print("\n=== JSON Parse Debug ===")
        print("Original text:")
        print(text[:800] + "..." if len(text) > 800 else text)
        print("\nBest attempt reached:")
        if best_attempt:
            print(best_attempt)
            # Show the position where parsing failed
            if last_error and last_error.pos < len(best_attempt):
                print(" " * last_error.pos + "^ Error occurred here")
        print(f"\nLast error: {last_error}")
        print("=== End Debug ===\n")
        
        # Let caller decide whether to use fallback plan
        raise json.JSONDecodeError(
            "Failed to parse response after multiple attempts",
            doc=best_attempt or cleaned,
            pos=(last_error.pos if last_error else 0)
        )
    
    def _initialize_models(self):
        """Initialize by checking which models are available"""
        # First try env vars
        self.model = os.getenv("OPENROUTER_MODEL")
        self.fallback_model = os.getenv("OPENROUTER_FALLBACK_MODEL")
        
        if not self.model:
            # Default model preferences in order
            # Prefer the Gemini 2.5 family (explicit IDs from your OpenRouter model list)
            model_preferences = [
                "google/gemini-2.5-pro",
                "google/gemini-2.5-pro-preview",
                "google/gemini-2.5-pro-preview-05-06",
                "google/gemini-2.5-flash",
                "google/gemini-2.5-flash-preview-09-2025",
                "google/gemini-2.5-flash-image",
                "google/gemini-2.5-flash-image-preview",
                "google/gemini-2.5-flash-image-preview-09-2025",
                "google/gemini-2.5-flash-lite",
                "google/gemini-2.5-flash-lite-preview-09-2025",
                "google/gemini-2.5-flash-lite-preview-06-17",
                # older/other Gemini variants
                "google/gemini-2.0-flash-001",
                "google/gemini-1.0-pro",
                # sensible non-Google fallbacks if necessary
                "anthropic/claude-opus-4.1",
                "anthropic/claude-3-opus",
                "openai/gpt-4-turbo"
            ]
            
            # Try a quick API check for the first available preferred model
            try:
                # Perform a synchronous request here because __init__ is synchronous.
                # Using the async client without awaiting would return a coroutine and fail.
                resp = httpx.get(f"{self.api_base}/models", headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }, timeout=10.0)
                resp.raise_for_status()
                models = resp.json().get("data", [])
                available = {m.get("id") for m in models if m.get("id")}

                # Choose first preferred model that exists in OpenRouter's list
                for model_id in model_preferences:
                    if model_id in available:
                        self.model = model_id
                        break

                # If we found a primary, pick a fallback from available models (prefer another gemini)
                if self.model:
                    gemini_alternatives = [m for m in available if m and 'gemini' in m and m != self.model]
                    if gemini_alternatives:
                        self.fallback_model = gemini_alternatives[0]
                    else:
                        others = [m for m in available if m and m != self.model]
                        if others:
                            self.fallback_model = others[0]
            except Exception as e:
                print(f"Warning: Failed to check available models synchronously: {e}")
        
        # If we still don't have models set, use safe defaults
        if not self.model:
            self.model = "google/gemini-1.0-pro"
        if not self.fallback_model:
            self.fallback_model = "anthropic/claude-2.1"
        
        print(f"Using AI models: primary={self.model}, fallback={self.fallback_model}")

    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()

    async def _post_with_model(self, endpoint: str, payload: dict, timeout: float | None = None) -> httpx.Response:
        """
        Helper to POST to OpenRouter using configured model and retry with a fallback model

        Args:
            endpoint: API endpoint path, e.g. '/chat/completions'
            payload: JSON-serializable payload (model will be injected)
            timeout: Optional timeout override

        Returns:
            httpx.Response on success

        Raises:
            httpx.HTTPStatusError when all attempts failed
        """
        models_to_try = []
        if self.model:
            models_to_try.append(self.model)
        # Always try fallback if different
        if self.fallback_model and (not self.model or self.fallback_model != self.model):
            models_to_try.append(self.fallback_model)

        if not models_to_try:
            raise RuntimeError("No OPENROUTER_MODEL or fallback configured; set OPENROUTER_MODEL in environment")

        last_exc = None
        for model in models_to_try:
            payload_with_model = {**payload, "model": model}
            resp = await self.http_client.post(f"{self.api_base}{endpoint}", json=payload_with_model, timeout=timeout)
            try:
                resp.raise_for_status()
                # success
                # If we tried fallback model, log that we fell back
                if model == self.fallback_model and self.model:
                    print(f"Note: used fallback model '{self.fallback_model}' after '{self.model}' was rejected by OpenRouter")
                return resp
            except httpx.HTTPStatusError as e:
                # Inspect response body to see if it's a model-id error
                body_text = resp.text or ""
                try:
                    body_json = resp.json()
                    msg = body_json.get("error", {}).get("message", "").lower()
                except Exception:
                    msg = body_text.lower()

                # If OpenRouter says the model ID is invalid or has no endpoints, try the next model
                if ((resp.status_code == 400 and ("not a valid model" in msg or "invalid model" in msg or "not a valid model id" in msg))
                    or (resp.status_code == 404 and ("no endpoints" in msg or "no endpoints found" in msg))):
                    print(f"OpenRouter rejected model '{model}': {msg}. Trying next model if available.")
                    last_exc = e
                    continue

                # For other errors, log full body and re-raise
                print(f"OpenRouter API returned {resp.status_code}: {body_text}")
                raise

        # If we exit loop without returning, raise last exception
        if last_exc:
            raise last_exc
        raise httpx.HTTPStatusError("OpenRouter request failed for unknown reasons", request=None, response=resp)
    
    def _create_fallback_classifications(self, assignments: List[Assignment]) -> List[dict]:
        """
        Create fallback classifications based on assignment type and points
        
        Args:
            assignments: List of assignments
            
        Returns:
            List of classification dictionaries
        """
        classifications = []
        
        for assignment in assignments:
            # Default estimates based on type
            category = "medium_effort"
            estimated_time = 120  # 2 hours default
            
            assignment_type = (assignment.assignment_type or "").lower()
            points = assignment.points or 0
            title = (assignment.title or "").lower()
            
            # Classify based on type and points
            if 'quiz' in title or 'test' in title or 'exam' in title:
                if points > 100:
                    category = "long_project"
                    estimated_time = 240  # 4 hours
                else:
                    category = "medium_effort"
                    estimated_time = 90  # 1.5 hours
            elif 'paper' in title or 'essay' in title or 'research' in title:
                if points > 50:
                    category = "long_project"
                    estimated_time = 360  # 6 hours
                else:
                    category = "medium_effort"
                    estimated_time = 180  # 3 hours
            elif 'project' in title:
                if points > 100:
                    category = "major_project"
                    estimated_time = 600  # 10 hours
                else:
                    category = "long_project"
                    estimated_time = 300  # 5 hours
            elif 'homework' in title or 'problem' in title:
                category = "medium_effort"
                estimated_time = 120  # 2 hours
            elif points < 20:
                category = "quick_task"
                estimated_time = 45  # 45 minutes
            elif points > 100:
                category = "long_project"
                estimated_time = 360  # 6 hours
            
            classifications.append({
                'assignment_id': assignment.id,
                'category': category,
                'estimated_time_minutes': estimated_time,
                'reasoning': f'Fallback classification based on type: {assignment_type}, points: {points}'
            })
        
        return classifications

    def _create_fallback_plan(self, assignments: List[Assignment]) -> StudyPlan:
        """
        Create a basic fallback study plan if AI generation fails
        
        Args:
            assignments: List of assignments
            
        Returns:
            Basic StudyPlan
        """
        tasks = []
        timezone = pytz.timezone(os.getenv('TIMEZONE', 'America/New_York'))
        current_date = datetime.now(timezone)
        
        for assignment in assignments:
            if not assignment.due_date:
                continue
            
            # Ensure due date is timezone-aware
            if assignment.due_date.tzinfo is None:
                due_date = timezone.localize(assignment.due_date)
            else:
                due_date = assignment.due_date
            
            # Calculate days until due date
            days_until_due = (due_date - current_date).days
            
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
