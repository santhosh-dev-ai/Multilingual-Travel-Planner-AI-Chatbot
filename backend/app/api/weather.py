from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import os
from typing import Optional, List

router = APIRouter()

# OpenWeatherMap API - Free tier
WEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"

class WeatherResponse(BaseModel):
    location: str
    country: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str
    wind_speed: float
    visibility: int
    pressure: int
    clouds: int
    sunrise: int
    sunset: int

class ForecastDay(BaseModel):
    date: str
    temp_min: float
    temp_max: float
    description: str
    icon: str
    humidity: int
    wind_speed: float

class ForecastResponse(BaseModel):
    location: str
    country: str
    forecast: List[ForecastDay]


@router.get("/current")
async def get_current_weather(lat: float, lon: float):
    """Get current weather for a location by coordinates."""
    
    if not WEATHER_API_KEY:
        # Return mock data if no API key
        return {
            "location": "Location",
            "country": "",
            "temperature": 25,
            "feels_like": 26,
            "humidity": 65,
            "description": "Partly cloudy",
            "icon": "02d",
            "wind_speed": 3.5,
            "visibility": 10000,
            "pressure": 1015,
            "clouds": 40,
            "sunrise": 1609459200,
            "sunset": 1609498800,
            "note": "Demo data - Add OPENWEATHER_API_KEY for real weather"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{WEATHER_BASE_URL}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": WEATHER_API_KEY,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "location": data.get("name", "Unknown"),
                "country": data.get("sys", {}).get("country", ""),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"].title(),
                "icon": data["weather"][0]["icon"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0),
                "pressure": data["main"]["pressure"],
                "clouds": data["clouds"]["all"],
                "sunrise": data["sys"]["sunrise"],
                "sunset": data["sys"]["sunset"],
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@router.get("/forecast")
async def get_weather_forecast(lat: float, lon: float, days: int = 5):
    """Get weather forecast for a location."""
    
    if not WEATHER_API_KEY:
        # Return mock forecast data
        from datetime import datetime, timedelta
        mock_forecast = []
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            mock_forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "temp_min": 20 + (i % 5),
                "temp_max": 28 + (i % 5),
                "description": ["Sunny", "Partly Cloudy", "Clear", "Light Rain", "Cloudy"][i % 5],
                "icon": ["01d", "02d", "01d", "10d", "03d"][i % 5],
                "humidity": 60 + (i * 3) % 30,
                "wind_speed": 2 + (i % 4)
            })
        
        return {
            "location": "Location",
            "country": "",
            "forecast": mock_forecast,
            "note": "Demo data - Add OPENWEATHER_API_KEY for real weather"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{WEATHER_BASE_URL}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": WEATHER_API_KEY,
                    "units": "metric",
                    "cnt": days * 8  # API returns 3-hour intervals
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Group by day and get daily min/max
            daily_data = {}
            for item in data["list"]:
                date = item["dt_txt"].split(" ")[0]
                if date not in daily_data:
                    daily_data[date] = {
                        "temps": [],
                        "descriptions": [],
                        "icons": [],
                        "humidity": [],
                        "wind": []
                    }
                daily_data[date]["temps"].append(item["main"]["temp"])
                daily_data[date]["descriptions"].append(item["weather"][0]["description"])
                daily_data[date]["icons"].append(item["weather"][0]["icon"])
                daily_data[date]["humidity"].append(item["main"]["humidity"])
                daily_data[date]["wind"].append(item["wind"]["speed"])
            
            forecast = []
            for date, values in list(daily_data.items())[:days]:
                forecast.append({
                    "date": date,
                    "temp_min": round(min(values["temps"]), 1),
                    "temp_max": round(max(values["temps"]), 1),
                    "description": max(set(values["descriptions"]), key=values["descriptions"].count).title(),
                    "icon": max(set(values["icons"]), key=values["icons"].count),
                    "humidity": round(sum(values["humidity"]) / len(values["humidity"])),
                    "wind_speed": round(sum(values["wind"]) / len(values["wind"]), 1)
                })
            
            return {
                "location": data["city"]["name"],
                "country": data["city"]["country"],
                "forecast": forecast
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@router.get("/by-city")
async def get_weather_by_city(city: str, country: Optional[str] = None):
    """Get current weather for a city by name."""
    
    query = f"{city},{country}" if country else city
    
    if not WEATHER_API_KEY:
        return {
            "location": city,
            "country": country or "",
            "temperature": 24,
            "feels_like": 25,
            "humidity": 60,
            "description": "Pleasant weather",
            "icon": "02d",
            "wind_speed": 3.0,
            "visibility": 10000,
            "pressure": 1013,
            "clouds": 30,
            "note": "Demo data - Add OPENWEATHER_API_KEY for real weather"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{WEATHER_BASE_URL}/weather",
                params={
                    "q": query,
                    "appid": WEATHER_API_KEY,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "location": data.get("name", city),
                "country": data.get("sys", {}).get("country", ""),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"].title(),
                "icon": data["weather"][0]["icon"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0),
                "pressure": data["main"]["pressure"],
                "clouds": data["clouds"]["all"],
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")
