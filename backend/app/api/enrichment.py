"""
Educational Enrichment API
FastAPI endpoint for destination enrichment with book recommendations
"""

from fastapi import APIRouter, HTTPException, status, Body
from typing import Optional
import logging

from app.models.enrichment import (
    EnrichmentRequest,
    EnrichmentResponse,
    BookRecommendation
)
from app.services.enrichment import get_destination_enrichment, get_enrichment_engine

# Initialize router
router = APIRouter(tags=["Educational Enrichment"])

# Logging
logger = logging.getLogger(__name__)


# ============================================================================
# ENRICHMENT ENDPOINT
# ============================================================================

@router.post(
    "/enrichment",
    response_model=EnrichmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Get educational enrichment for a destination",
    description="""
    Educational Enrichment Engine for AI Travel Planner.
    
    **When a student confirms a destination, this endpoint provides:**
    
    1. **Book Recommendations**: Fetched from books.csv, ranked by rating and educational value
    2. **Historical Summary**: AI-generated overview of destination's history
    3. **Cultural Insights**: Essential cultural knowledge and etiquette tips
    4. **Travel Tips**: Student-friendly practical advice for budget, safety, and planning
    5. **Book Enhancement Explanation**: Why reading enriches the travel experience
    
    **Features**:
    - Student-friendly and educational focus
    - Books ranked by rating and educational value
    - AI-powered content generation (OpenAI compatible)
    - Structured, clean JSON response
    - Fallback content when LLM unavailable
    
    **Use Case**: Call this endpoint after user confirms destination to provide enriching pre-trip educational content.
    """,
    responses={
        200: {
            "description": "Enrichment content generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "message": "Enrichment generated successfully",
                        "destination": "Paris",
                        "country": "France",
                        "region": "europe",
                        "summary": "Paris has been a center of art and culture for centuries...",
                        "cultural_tips": [
                            "Greet shopkeepers with 'Bonjour' before requests",
                            "Tipping is appreciated but not mandatory (5-10%)"
                        ],
                        "travel_tips": [
                            "Buy a Paris Museum Pass for unlimited entry",
                            "Use the Metro - fast, cheap, covers entire city"
                        ],
                        "book_enhancement_explanation": "Reading about Paris helps understand historical context...",
                        "recommended_books": [
                            {
                                "title": "Rick Steves Paris",
                                "author": "Rick Steves",
                                "rating": 4.6,
                                "genre": "Travel Guide"
                            }
                        ],
                        "total_books_found": 3
                    }
                }
            }
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error or LLM unavailable"}
    }
)
async def get_destination_enrichment_endpoint(
    request: EnrichmentRequest = Body(
        ...,
        examples={
            "default": {
                "summary": "Sample destination enrichment request",
                "value": {
                    "destination": "Paris",
                    "country": "France",
                    "region": "europe",
                    "top_books": 5,
                    "student_friendly_only": True
                }
            }
        }
    )
):
    """
    Get educational enrichment for a confirmed destination
    
    Args:
        request: EnrichmentRequest with destination details
        
    Returns:
        EnrichmentResponse with books, summary, cultural tips, travel tips
        
    Example:
        ```python
        POST /api/destination/enrichment
        {
            "destination": "Tokyo",
            "country": "Japan",
            "region": "asia",
            "top_books": 5,
            "student_friendly_only": true
        }
        ```
    """
    try:
        logger.info(
            f"[Enrichment API] Request received - "
            f"destination={request.destination}, country={request.country}"
        )
        
        # Get enrichment from service
        enrichment = await get_destination_enrichment(
            destination=request.destination,
            country=request.country,
            region=request.region or "unknown",
            top_books=request.top_books,
            student_friendly=request.student_friendly_only
        )
        
        logger.info(
            f"[Enrichment API] Generated enrichment with "
            f"{enrichment['total_books_found']} books for {request.destination}"
        )
        
        # Build response
        response = EnrichmentResponse(
            success=True,
            message="Enrichment generated successfully",
            destination=enrichment["destination"],
            country=enrichment["country"],
            region=enrichment.get("region"),
            summary=enrichment["summary"],
            cultural_tips=enrichment["cultural_tips"],
            travel_tips=enrichment["travel_tips"],
            book_enhancement_explanation=enrichment["book_enhancement_explanation"],
            recommended_books=[
                BookRecommendation(**book) for book in enrichment["recommended_books"]
            ],
            total_books_found=enrichment["total_books_found"]
        )
        
        return response
        
    except FileNotFoundError as e:
        logger.error(f"[Enrichment API] Books dataset not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Books dataset not found. Please ensure books.csv exists."
        )
    except ValueError as e:
        error_msg = str(e)
        logger.warning(f"[Enrichment API] ValueError: {error_msg}")
        
        if "API key" in error_msg:
            # API key issue - still return data but with fallback content
            logger.info("[Enrichment API] Using fallback enrichment (no API key)")
            
            # Get books and fallback enrichment
            engine = get_enrichment_engine()
            books = engine.get_recommended_books(
                destination=request.destination,
                country=request.country,
                top_n=request.top_books,
                student_friendly_only=request.student_friendly_only
            )
            
            fallback = engine._generate_fallback_enrichment(
                destination=request.destination,
                country=request.country,
                books=books
            )
            
            return EnrichmentResponse(
                success=True,
                message="Enrichment generated with fallback content (LLM unavailable)",
                destination=request.destination,
                country=request.country,
                region=request.region,
                summary=fallback["historical_summary"],
                cultural_tips=fallback["cultural_insights"],
                travel_tips=fallback["travel_tips"],
                book_enhancement_explanation=fallback["book_enhancement"],
                recommended_books=[BookRecommendation(**book) for book in books],
                total_books_found=len(books)
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid request: {error_msg}"
            )
    except Exception as e:
        logger.error(f"[Enrichment API] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate enrichment. Please try again later."
        )


# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/books/{destination}",
    status_code=status.HTTP_200_OK,
    summary="Get book recommendations for a destination",
    description="Returns list of books for a specific destination, ranked by rating",
    response_model=dict
)
async def get_books_for_destination(
    destination: str,
    country: Optional[str] = None,
    top_n: int = 5,
    student_friendly: bool = True
):
    """Get book recommendations only (without AI enrichment)"""
    try:
        engine = get_enrichment_engine()
        books = engine.get_recommended_books(
            destination=destination,
            country=country,
            top_n=top_n,
            student_friendly_only=student_friendly
        )
        
        return {
            "success": True,
            "destination": destination,
            "country": country,
            "books": books,
            "total_found": len(books)
        }
    except Exception as e:
        logger.error(f"[Books API] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get(
    "/destinations-with-books",
    status_code=status.HTTP_200_OK,
    summary="Get list of destinations that have book recommendations",
    description="Returns all destinations for which books are available",
    response_model=dict
)
async def get_destinations_with_books():
    """Get list of destinations that have book recommendations"""
    try:
        engine = get_enrichment_engine()
        
        if engine.df.empty:
            return {
                "success": False,
                "message": "No books loaded",
                "destinations": []
            }
        
        # Get unique destinations
        destinations = engine.df[['destination', 'country', 'region']].drop_duplicates()
        
        destination_list = []
        for _, row in destinations.iterrows():
            # Count books for this destination
            book_count = len(engine.df[
                engine.df['destination'].str.lower() == row['destination'].lower()
            ])
            
            destination_list.append({
                "destination": row['destination'],
                "country": row['country'],
                "region": row['region'],
                "book_count": book_count
            })
        
        # Sort by book count (descending)
        destination_list.sort(key=lambda x: x['book_count'], reverse=True)
        
        return {
            "success": True,
            "destinations": destination_list,
            "total_destinations": len(destination_list),
            "total_books": len(engine.df)
        }
    except Exception as e:
        logger.error(f"[Destinations API] Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# HEALTH CHECK
# ============================================================================

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health check for enrichment service",
    response_model=dict
)
async def health_check():
    """Check if enrichment service is operational"""
    try:
        engine = get_enrichment_engine()
        
        # Check API key status
        api_key_status = "configured" if engine.api_key and engine.api_key.strip() else "not configured"
        
        return {
            "success": True,
            "status": "healthy",
            "service": "Educational Enrichment Engine",
            "books_loaded": len(engine.df),
            "destinations_available": len(engine.df['destination'].unique()) if not engine.df.empty else 0,
            "llm_api_key": api_key_status,
            "features": {
                "book_recommendations": True,
                "ai_generated_content": api_key_status == "configured",
                "fallback_content": True,
                "student_friendly_filter": True
            }
        }
    except Exception as e:
        logger.error(f"[Health Check] Service unhealthy: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Enrichment service unavailable: {str(e)}"
        )
