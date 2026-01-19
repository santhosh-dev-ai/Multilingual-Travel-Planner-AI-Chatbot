from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.groq_service import GroqService

router = APIRouter()
ai_service = GroqService()

class ConversationMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    language: str = "en-US"
    conversation_history: Optional[List[ConversationMessage]] = []

class ChatResponse(BaseModel):
    message: str
    created_at: datetime

@router.post("/message", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    try:
        # Build messages array from conversation history + current message
        messages = []
        
        # Add conversation history
        if request.conversation_history:
            for msg in request.conversation_history:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })
        
        response = await ai_service.generate_response(
            messages=messages,
            language=request.language
        )
        
        return ChatResponse(
            message=response,
            created_at=datetime.now()
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


