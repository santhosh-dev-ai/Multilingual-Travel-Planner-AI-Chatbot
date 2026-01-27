from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, destinations, weather, itinerary
from app.core.config import settings

app = FastAPI(
    title="TravelGenie API",
    description="AI-powered travel assistant API with dynamic destinations, weather, and itinerary planning",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://multilingual-travel-planner-ai-chat.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(destinations.router, prefix="/api/destinations", tags=["destinations"])
app.include_router(weather.router, prefix="/api/weather", tags=["weather"])
app.include_router(itinerary.router, prefix="/api/itinerary", tags=["itinerary"])

@app.get("/")
async def root():
    return {"message": "Welcome to TravelGenie API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


