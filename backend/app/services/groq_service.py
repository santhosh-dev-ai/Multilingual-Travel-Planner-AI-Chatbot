import httpx
import asyncio
from typing import Optional
from app.core.config import settings


class GroqService:
    """Service for interacting with Groq API."""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"  # Current supported model
        
        # System prompt for the travel assistant
        self.system_prompt = """You are TravelGenie, an expert AI travel assistant powered by advanced AI. You have comprehensive knowledge about:

🌍 TRAVEL EXPERTISE:
- Destinations worldwide (cities, countries, hidden gems, popular spots)
- Flight booking tips, best airlines, layover strategies
- Accommodation (hotels, hostels, Airbnb, boutique stays)
- Local transportation (metro, buses, taxis, rentals)
- Visa requirements, travel documents, entry restrictions
- Travel insurance, safety tips, health precautions
- Currency, budgeting, money-saving hacks
- Packing tips, what to wear, essentials
- Best seasons, weather, avoiding crowds
- Local cuisine, restaurants, street food, dietary needs
- Cultural etiquette, customs, language basics
- Activities, tours, experiences, adventure sports
- Family travel, solo travel, couple getaways, group trips

🎯 YOUR CAPABILITIES:
1. CREATE personalized itineraries (day-by-day plans)
2. RECOMMEND destinations based on preferences, budget, time
3. COMPARE options (hotels, flights, destinations)
4. PROVIDE real-time tips and insider knowledge
5. ANSWER any travel-related question
6. SUGGEST alternatives when asked
7. HELP with trip planning from start to finish
8. GIVE honest opinions and warnings when needed

💬 RESPONSE STYLE:
- Be conversational and friendly, like a knowledgeable travel buddy
- Keep responses concise but complete (3-5 sentences for quick questions)
- For detailed requests (itineraries, comparisons), provide structured info
- Use bullet points only when listing multiple items
- Add 1-2 relevant emojis for warmth
- Be honest if something isn't worth the hype
- Share insider tips that only experienced travelers would know

📋 FORMAT BASED ON REQUEST:
- Quick question → Short, direct answer (2-4 sentences)
- Destination info → Key highlights + best time + one insider tip
- Itinerary request → Day-by-day format with times and activities
- Comparison → Pros/cons in brief bullets
- Recommendations → Top 2-3 picks with why each is good for them

⚠️ CRITICAL FORMATTING RULE:
ALWAYS separate your main answer from any follow-up question with a blank line.
Put the follow-up question on its own paragraph.

CORRECT FORMAT:
"A luxurious resort stay in the Maldives sounds amazing 🌟. You can expect lavish villas, fine dining, and exceptional service. Some top resorts include Soneva Fushi and Cheval Blanc Randheli.

Would you like me to recommend a specific resort based on your preferences?"

WRONG FORMAT (no separation):
"A luxurious resort stay in the Maldives sounds amazing. Some top resorts include Soneva Fushi. Would you like me to recommend one?"

Always put a line break before questions like "Would you like...", "What type of...", "Are you looking for...", etc.

Remember: You're having a conversation, not writing an article. Be helpful, be real, be brief."""

    def _build_messages(self, messages: list[dict], language: str = "en-US") -> list[dict]:
        """Build the messages array for Groq API."""
        
        language_instructions = {
            "en-US": "Respond in English.",
            "es-ES": "Responde en español de forma natural y amigable.",
            "fr-FR": "Réponds en français de manière naturelle et amicale.",
            "de-DE": "Antworte auf Deutsch in einem natürlichen und freundlichen Ton.",
            "hi-IN": "हिंदी में स्वाभाविक और मैत्रीपूर्ण तरीके से जवाब दें।",
            "ja-JP": "自然でフレンドリーな日本語で返答してください。",
            "zh-CN": "请用自然友好的中文回复。",
            "pt-BR": "Responda em português de forma natural e amigável.",
            "ar-SA": "الرجاء الرد باللغة العربية بشكل طبيعي وودي.",
        }
        
        lang_instruction = language_instructions.get(language, "Respond in the user's language naturally and friendly.")
        
        # Build messages format
        groq_messages = [
            {
                "role": "system",
                "content": f"{self.system_prompt}\n\nLANGUAGE: {lang_instruction}"
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
        messages: list[dict], 
        language: str = "en-US",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from Groq."""
        
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
        
        max_retries = 3
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            for attempt in range(max_retries):
                try:
                    response = await client.post(
                        self.api_url,
                        json=payload,
                        headers=headers
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # Extract text from Groq response
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    
                    return "I apologize, but I couldn't generate a response. Please try again."
                    
                except httpx.HTTPStatusError as e:
                    error_detail = e.response.text
                    print(f"Groq API Error: {e.response.status_code} - {error_detail}")
                    
                    if e.response.status_code == 429:
                        # Rate limited - wait and retry
                        if attempt < max_retries - 1:
                            wait_time = 2 * (2 ** attempt)
                            print(f"Rate limited, waiting {wait_time}s...")
                            await asyncio.sleep(wait_time)
                            continue
                        return "The service is busy. Please wait a moment and try again."
                    elif e.response.status_code == 401:
                        return "Invalid API key. Please check your Groq API key."
                    elif e.response.status_code == 400:
                        return "I couldn't process that request. Please try rephrasing your question."
                    else:
                        return f"Sorry, I encountered an error. Please try again later."
                        
                except Exception as e:
                    print(f"Error: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(1)
                        continue
                    return "I encountered an error while processing your request. Please try again."
        
        return "Unable to get a response. Please try again."


# Create singleton instance
groq_service = GroqService()
