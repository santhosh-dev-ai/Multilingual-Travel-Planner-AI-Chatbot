"""
Educational Enrichment Models
Pydantic models for destination enrichment API
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BookRecommendation(BaseModel):
    """Single book recommendation with metadata"""
    
    id: int = Field(..., description="Book ID")
    title: str = Field(..., description="Book title")
    author: str = Field(..., description="Author name")
    genre: str = Field(..., description="Book genre")
    rating: float = Field(..., ge=0, le=5, description="Book rating (0-5)")
    year_published: int = Field(..., description="Year of publication")
    pages: int = Field(..., ge=1, description="Number of pages")
    description: str = Field(..., description="Book description")
    isbn: str = Field(..., description="ISBN number")
    cover_url: str = Field(..., description="Cover image URL")
    student_friendly: bool = Field(..., description="Suitable for students")
    educational_value: str = Field(..., description="Educational value: high, medium, low")
    why_recommended: str = Field(
        ...,
        description="Explanation of why this book enhances the travel experience"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 23,
                "title": "Rick Steves Paris",
                "author": "Rick Steves",
                "genre": "Travel Guide",
                "rating": 4.6,
                "year_published": 2024,
                "pages": 680,
                "description": "Student-friendly budget guide to Paris",
                "isbn": "1641714360",
                "cover_url": "https://example.com/rs-paris.jpg",
                "student_friendly": True,
                "educational_value": "high",
                "why_recommended": "Perfect for planning your trip with practical tips and insider knowledge. High educational value for students."
            }
        }


class EnrichmentRequest(BaseModel):
    """Request model for destination enrichment"""
    
    destination: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Destination city name (e.g., 'Paris', 'Tokyo')"
    )
    country: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Country name"
    )
    region: Optional[str] = Field(
        None,
        description="Geographic region (e.g., 'europe', 'asia')"
    )
    top_books: int = Field(
        5,
        ge=1,
        le=20,
        description="Number of book recommendations to return"
    )
    student_friendly_only: bool = Field(
        True,
        description="Filter for student-friendly books only"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Paris",
                "country": "France",
                "region": "europe",
                "top_books": 5,
                "student_friendly_only": True
            }
        }


class EnrichmentResponse(BaseModel):
    """Response model for destination enrichment"""
    
    success: bool = Field(True, description="Request success status")
    message: str = Field("Enrichment generated successfully")
    destination: str = Field(..., description="Destination name")
    country: str = Field(..., description="Country name")
    region: Optional[str] = Field(None, description="Geographic region")
    
    # Core enrichment content
    summary: str = Field(
        ...,
        description="Historical summary and overview of the destination"
    )
    cultural_tips: List[str] = Field(
        ...,
        description="Cultural insights and etiquette tips"
    )
    travel_tips: List[str] = Field(
        ...,
        description="Practical travel tips for students"
    )
    book_enhancement_explanation: str = Field(
        ...,
        description="Explanation of why reading enhances the travel experience"
    )
    
    # Book recommendations
    recommended_books: List[BookRecommendation] = Field(
        ...,
        description="List of recommended books ranked by rating"
    )
    total_books_found: int = Field(
        ...,
        ge=0,
        description="Total number of matching books"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Enrichment generated successfully",
                "destination": "Paris",
                "country": "France",
                "region": "europe",
                "summary": "Paris, the capital of France, has been a center of art, culture, and intellectual thought for centuries. From the French Revolution to the Belle Époque, its history shaped modern Western civilization.",
                "cultural_tips": [
                    "Greet shopkeepers with 'Bonjour' before making requests",
                    "Tipping is appreciated but not mandatory (5-10% for good service)",
                    "Dress more formally than typical American casual wear",
                    "Learn basic French phrases - locals appreciate the effort"
                ],
                "travel_tips": [
                    "Buy a Paris Museum Pass for unlimited entry to major attractions",
                    "Use the Metro - it's fast, cheap, and covers the entire city",
                    "Visit popular sites like the Louvre on Wednesday or Friday evenings",
                    "Stay in the Latin Quarter or Marais for budget-friendly student accommodations"
                ],
                "book_enhancement_explanation": "Reading about Paris before your trip helps you understand the historical context behind landmarks like Notre-Dame and the Eiffel Tower. Literature connects you emotionally to the city's artistic legacy and helps you discover hidden gems beyond typical tourist routes.",
                "recommended_books": [
                    {
                        "id": 23,
                        "title": "Rick Steves Paris",
                        "author": "Rick Steves",
                        "rating": 4.6,
                        "genre": "Travel Guide",
                        "why_recommended": "Perfect for planning your trip with practical tips and insider knowledge."
                    }
                ],
                "total_books_found": 3
            }
        }
