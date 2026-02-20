from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, destinations, weather, itinerary, intelligence, ranking, recommendation, enrichment, budget, intelligent_itinerary, auth
from app.database import api as database_api
from app.core.config import settings
from app.middleware.production import (
    RequestLoggingMiddleware,
    ErrorHandlerMiddleware,
    RateLimitMiddleware,
    CacheControlMiddleware
)

app = FastAPI(
    title="TravelGenie AI Intelligence System",
    description="Production-grade AI-powered travel intelligence platform with ML recommendations, analytics, itinerary optimization, and unified intelligent itinerary generation",
    version="4.0.0"
)

# Production Middleware Stack (order matters: first added = innermost layer)
app.add_middleware(CacheControlMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RequestLoggingMiddleware)

# CORS Middleware
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

# API Routers
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(destinations.router, prefix="/api/destinations", tags=["Destinations"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(itinerary.router, prefix="/api/itinerary", tags=["Itinerary"])
app.include_router(intelligence.router, prefix="/api/intelligence", tags=["Intelligence"])
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(ranking.router, prefix="/api/recommend", tags=["Ranking"])
app.include_router(recommendation.router, prefix="/api/recommend", tags=["Recommendations"])
app.include_router(enrichment.router, prefix="/api/destination", tags=["Educational Enrichment"])
app.include_router(budget.router, prefix="/api/optimize", tags=["Budget Optimization"])
app.include_router(intelligent_itinerary.router, prefix="/api/generate", tags=["Intelligent Itinerary"])
app.include_router(database_api.router, tags=["Database"])

@app.get("/")
async def root():
    return {"status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
