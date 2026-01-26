import httpx
import asyncio
from typing import Optional, List, Dict
from app.core.config import settings

class GroqService:
    """Service for interacting with Groq API."""
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-70b-versatile"
        self.system_prompt = "You are TravelGenie, an expert AI travel assistant powered by advanced AI. You have comprehensive knowledge about travel, destinations, planning, and tips."

    def _build_messages(self, messages: List[Dict], language: str = "en-US") -> List[Dict]:
        groq_messages = [
            {
                "role": "system",
                "content": self.system_prompt
            }
        ]
        for msg in messages:
            groq_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return groq_messages

    async def generate_response(
        self,
        messages: List[Dict],
        language: str = "en-US",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        if not self.api_key:
            return "Groq API key is not configured. Please add GROQ_API_KEY to your .env file."
        groq_messages = self._build_messages(messages, language)
        payload = {
            "model": self.model,
            "messages": groq_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.api_url, json=payload, headers=headers)
                response.raise_for_status()
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return "I apologize, but I couldn't generate a response. Please try again."
            except Exception as e:
                print(f"Groq API Error: {e}")
                return "Sorry, I encountered an error. Please try again later."

# Create singleton instance
groq_service = GroqService()
