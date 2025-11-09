import os
import httpx
from typing import List, Dict

class ModelsService:
    """Service for checking available OpenRouter models"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        self.api_base = "https://openrouter.ai/api/v1"
        self.http_client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "http://localhost:8000",
                "Content-Type": "application/json"
            }
        )
    
    async def get_available_models(self) -> List[Dict]:
        """
        Fetch list of available models from OpenRouter
        Returns: List of model info dictionaries
        """
        try:
            response = await self.http_client.get(f"{self.api_base}/models")
            response.raise_for_status()
            models = response.json().get("data", [])

            # Prefer to return the full model list but sort Gemini models first for convenience
            def score(m: Dict) -> int:
                mid = (m.get("id") or "").lower()
                if "gemini" in mid:
                    return 0
                if "claude" in mid:
                    return 1
                if "gpt-4" in mid or "gpt-4o" in mid or "gpt-4o" in mid:
                    return 2
                return 10

            models_sorted = sorted(models, key=score)
            return models_sorted
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()