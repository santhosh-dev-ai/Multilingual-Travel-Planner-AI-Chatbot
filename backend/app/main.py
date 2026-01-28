from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, destinations, weather, itinerary
from app.core.config import settings

app = FastAPI(
    title="TravelGenie API",
    description="AI-powered travel assistant API with dynamic destinations, weather, and itinerary planning",
    version="2.0.0"
)

app = FastAPI(
    title="TravelGenie API",
    description="AI-powered travel assistant API",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://multilingual-travel-planner-ai-chat.vercel.app",
        "https://multilingual-travel-planner-ai-chatbot-nhi1l8na6.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router, prefix="/api/chat")
app.include_router(destinations.router, prefix="/api/destinations")
app.include_router(weather.router, prefix="/api/weather")
app.include_router(itinerary.router, prefix="/api/itinerary")

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
