import httpx
import asyncio
from typing import Optional, List, Dict
from app.core.config import settings

class GroqService:
    """Service for interacting with Groq API."""
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        self.system_prompt = (
            "You are TravelGenie, a student-focused AI travel assistant. "
            "Always prioritize affordable, practical, and safe advice for students. "
            "Use clear and simple language. Give concise answers with actionable steps. "
            "When suggesting places or plans, include budget-conscious options first, then optional upgrades. "
            "Mention student discounts, public transport, hostels/budget stays, low-cost food, and free activities when relevant. "
            "If key trip details are missing (budget, dates, group size, interests), ask short follow-up questions before giving final recommendations. "
            "Avoid overly generic responses: provide concrete examples, estimated price ranges, and realistic daily plans when possible."
        )

    def _build_messages(self, messages: List[Dict], language: str = "en-US") -> List[Dict]:
        language_instruction = (
            f"Respond in {language}. "
            "If the user language is unclear, respond in clear English."
        )

        groq_messages = [
            {
                "role": "system",
                "content": f"{self.system_prompt} {language_instruction}"
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
        if not self.api_key or self.api_key.strip() == "":
            return "❌ Groq API key is not configured. Please add GROQ_API_KEY to your backend/.env file."
        
        try:
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
                response = await client.post(self.api_url, json=payload, headers=headers)
                
                if response.status_code == 401:
                    return "❌ Invalid Groq API key. Please check your GROQ_API_KEY in backend/.env file."
                elif response.status_code == 429:
                    return "⏳ Rate limit exceeded. Please wait a moment and try again."
                elif response.status_code == 500:
                    return "🔧 Groq service is temporarily unavailable. Please try again later."
                
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except httpx.TimeoutException:
            return "⏰ Request timed out. Please try again."
        except httpx.RequestError as e:
            print(f"Groq API Request Error: {e}")
            return "🌐 Network error occurred. Please check your internet connection and try again."
        except Exception as e:
            print(f"Groq API Error: {e}")
            return "❌ Sorry, I encountered an unexpected error. Please try again later."

# Create singleton instance
groq_service = GroqService()
