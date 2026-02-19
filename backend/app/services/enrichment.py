"""
Educational Enrichment Engine
Provides historical context, cultural insights, and book recommendations for destinations

Features:
- Fetches related books from books.csv
- Ranks books by rating and educational value
- Generates AI-powered historical summaries
- Provides cultural insights and travel tips
- Student-friendly and educational focus
"""

import pandas as pd
import httpx
import os
from typing import List, Dict, Optional
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EnrichmentEngine:
    """
    Educational enrichment engine for travel destinations
    
    Provides:
    - Book recommendations ranked by rating
    - Historical summaries
    - Cultural insights
    - Travel tips
    - Educational context
    """
    
    def __init__(self, csv_path: Optional[str] = None):
        """Initialize enrichment engine with books dataset"""
        if csv_path is None:
            base_dir = Path(__file__).parent.parent.parent
            csv_path = os.path.join(base_dir, "data", "books.csv")
        
        self.csv_path = csv_path
        self.df = None
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-3.5-turbo"  # Can be upgraded to gpt-4
        self._load_books()
    
    def _load_books(self):
        """Load books dataset from CSV"""
        try:
            self.df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(self.df)} books from {self.csv_path}")
        except FileNotFoundError:
            logger.error(f"Books CSV not found at {self.csv_path}")
            self.df = pd.DataFrame()
        except Exception as e:
            logger.error(f"Error loading books: {e}")
            self.df = pd.DataFrame()
    
    def get_recommended_books(
        self,
        destination: str,
        country: Optional[str] = None,
        top_n: int = 5,
        student_friendly_only: bool = True
    ) -> List[Dict]:
        """
        Get recommended books for a destination, ranked by rating
        
        Args:
            destination: City name (e.g., "Paris", "Tokyo")
            country: Country name for better matching (optional)
            top_n: Number of books to return
            student_friendly_only: Filter for student-friendly books
            
        Returns:
            List of book dictionaries with metadata
        """
        if self.df.empty:
            return []
        
        # Filter by destination (case-insensitive)
        books = self.df[
            self.df['destination'].str.lower() == destination.lower()
        ].copy()
        
        # If no exact match, try country match
        if books.empty and country:
            books = self.df[
                self.df['country'].str.lower() == country.lower()
            ].copy()
        
        # Filter for student-friendly books if requested
        if student_friendly_only:
            books = books[books['student_friendly'] == True]
        
        # Sort by rating (descending), then educational value
        def educational_value_score(val):
            mapping = {'high': 3, 'medium': 2, 'low': 1}
            return mapping.get(val.lower() if isinstance(val, str) else 'low', 1)
        
        books['edu_score'] = books['educational_value'].apply(educational_value_score)
        books = books.sort_values(
            by=['rating', 'edu_score'],
            ascending=[False, False]
        )
        
        # Select top N books
        top_books = books.head(top_n)
        
        # Convert to list of dictionaries
        book_list = []
        for _, book in top_books.iterrows():
            book_list.append({
                'id': int(book['id']),
                'title': str(book['title']),
                'author': str(book['author']),
                'genre': str(book['genre']),
                'rating': float(book['rating']),
                'year_published': int(book['year_published']),
                'pages': int(book['pages']),
                'description': str(book['description']),
                'isbn': str(book['isbn']),
                'cover_url': str(book['cover_url']),
                'student_friendly': bool(book['student_friendly']),
                'educational_value': str(book['educational_value']),
                'why_recommended': self._explain_book_recommendation(
                    book['title'],
                    book['genre'],
                    book['educational_value']
                )
            })
        
        return book_list
    
    def _explain_book_recommendation(
        self,
        title: str,
        genre: str,
        educational_value: str
    ) -> str:
        """Generate explanation for why a book is recommended"""
        explanations = {
            'Travel Guide': "Perfect for planning your trip with practical tips and insider knowledge.",
            'Travel Memoir': "Offers personal perspective and emotional connection to the destination.",
            'Travel Literature': "Beautifully written journey that captures the essence of the place.",
            'Travel Humor': "Makes learning about the destination entertaining and memorable.",
            'History': "Provides deep historical context that enriches your visit.",
            'Cultural Commentary': "Helps understand local customs, values, and way of life.",
            'Fiction': "Story-based learning makes cultural immersion more engaging.",
            'Classic Fiction': "Literary masterpiece that shaped how we view this destination.",
            'Memoir': "Personal insights into daily life and authentic experiences.",
            'Mystery Fiction': "Engaging way to learn about local culture through storytelling.",
            'True Crime': "Real stories that reveal fascinating aspects of local society.",
            'Adventure': "Inspires exploration and highlights unique experiences.",
            'Fantasy': "Creative reimagining that deepens appreciation for the setting."
        }
        
        base = explanations.get(genre, "Enriches your understanding of the destination.")
        
        if educational_value == 'high':
            return f"{base} High educational value for students."
        elif educational_value == 'medium':
            return f"{base} Good balance of entertainment and education."
        else:
            return base
    
    async def generate_enrichment(
        self,
        destination: str,
        country: str,
        region: str,
        books: List[Dict]
    ) -> Dict:
        """
        Generate AI-powered educational enrichment content
        
        Args:
            destination: Destination name
            country: Country name
            region: Geographic region
            books: List of recommended books
            
        Returns:
            Dictionary with summary, cultural tips, and travel insights
        """
        # Build prompt for LLM
        book_titles = [f"'{book['title']}' by {book['author']}" for book in books[:3]]
        book_context = ", ".join(book_titles) if book_titles else "various travel literature"
        
        prompt = f"""As an educational travel expert, provide enriching context for students visiting {destination}, {country}.

Context: The student has selected books including {book_context}.

Please provide:

1. HISTORICAL SUMMARY (2-3 sentences): Brief, engaging overview of the destination's historical significance. Focus on key events or periods that shaped it into what it is today.

2. CULTURAL INSIGHTS (3-4 bullet points): Essential cultural knowledge that helps students appreciate and respect local customs. Include:
   - Social etiquette and behavior norms
   - Cultural values or traditions
   - Common misconceptions to avoid
   - Best ways to engage with locals

3. MUST-KNOW TRAVEL TIPS (3-4 bullet points): Practical, student-friendly advice:
   - Budget-saving strategies
   - Safety considerations
   - Transportation tips
   - Best times to visit key sites

4. WHY THESE BOOKS ENHANCE THE EXPERIENCE (2-3 sentences): Explain how reading about the destination beforehand enriches the travel experience. Connect literature to deeper understanding of place.

Keep tone: Educational, engaging, student-friendly, concise.
Focus: Practical knowledge + cultural appreciation + intellectual growth."""

        try:
            # Call OpenAI API (or compatible service)
            enrichment = await self._call_llm(prompt)
            
            # Parse the response into structured format
            parsed = self._parse_enrichment_response(enrichment)
            
            return parsed
            
        except Exception as e:
            logger.error(f"Error generating enrichment: {e}")
            # Return fallback content
            return self._generate_fallback_enrichment(destination, country, books)
    
    async def _call_llm(self, prompt: str) -> str:
        """
        Call OpenAI API (or compatible LLM service)
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated text response
        """
        if not self.api_key or self.api_key.strip() == "":
            raise ValueError("OpenAI API key not configured")
        
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert educational travel advisor specializing in enriching student travel experiences through literature and cultural context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                result = response.json()
                
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise ValueError("No response from LLM")
                    
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid API key")
            elif e.response.status_code == 429:
                raise ValueError("Rate limit exceeded")
            else:
                raise ValueError(f"API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"LLM call error: {e}")
            raise
    
    def _parse_enrichment_response(self, response: str) -> Dict:
        """
        Parse LLM response into structured format
        
        Args:
            response: Raw LLM response text
            
        Returns:
            Structured dictionary with summary, cultural_tips, travel_tips, book_value
        """
        # Initialize result structure
        result = {
            "historical_summary": "",
            "cultural_insights": [],
            "travel_tips": [],
            "book_enhancement": ""
        }
        
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Detect section headers
            if 'HISTORICAL SUMMARY' in line.upper():
                current_section = 'historical_summary'
                continue
            elif 'CULTURAL INSIGHT' in line.upper():
                current_section = 'cultural_insights'
                continue
            elif 'TRAVEL TIP' in line.upper():
                current_section = 'travel_tips'
                continue
            elif 'WHY THESE BOOKS' in line.upper() or 'BOOK' in line.upper() and 'ENHANCE' in line.upper():
                current_section = 'book_enhancement'
                continue
            
            # Skip empty lines and section headers
            if not line or line.startswith('#') or line.endswith(':'):
                continue
            
            # Add content to appropriate section
            if current_section == 'historical_summary':
                result['historical_summary'] += line + ' '
            elif current_section == 'cultural_insights':
                # Remove bullet points and numbering
                clean_line = line.lstrip('•-*123456789.)')
                if clean_line:
                    result['cultural_insights'].append(clean_line.strip())
            elif current_section == 'travel_tips':
                clean_line = line.lstrip('•-*123456789.)')
                if clean_line:
                    result['travel_tips'].append(clean_line.strip())
            elif current_section == 'book_enhancement':
                result['book_enhancement'] += line + ' '
        
        # Clean up text
        result['historical_summary'] = result['historical_summary'].strip()
        result['book_enhancement'] = result['book_enhancement'].strip()
        
        return result
    
    def _generate_fallback_enrichment(
        self,
        destination: str,
        country: str,
        books: List[Dict]
    ) -> Dict:
        """
        Generate fallback enrichment when LLM is unavailable
        
        Args:
            destination: Destination name
            country: Country name
            books: List of books
            
        Returns:
            Basic enrichment content
        """
        return {
            "historical_summary": f"{destination} in {country} is a destination rich in history and culture, offering travelers a unique blend of traditional heritage and modern experiences.",
            "cultural_insights": [
                "Research local customs and etiquette before your visit",
                "Learn a few key phrases in the local language",
                "Respect religious and cultural sites with appropriate dress and behavior",
                "Engage with locals respectfully to gain authentic insights"
            ],
            "travel_tips": [
                "Book accommodations in advance, especially during peak season",
                "Use public transportation to save money and experience local life",
                "Visit popular attractions early morning or late afternoon to avoid crowds",
                "Keep copies of important documents and emergency contact numbers"
            ],
            "book_enhancement": f"Reading about {destination} before your trip helps you appreciate the historical context, understand cultural nuances, and discover hidden gems that typical tourists might miss. Literature transforms travel from mere sightseeing into a deeper educational journey."
        }


# Global singleton instance
_enrichment_engine = None


def get_enrichment_engine() -> EnrichmentEngine:
    """Get singleton enrichment engine instance"""
    global _enrichment_engine
    if _enrichment_engine is None:
        _enrichment_engine = EnrichmentEngine()
    return _enrichment_engine


# Convenience function
async def get_destination_enrichment(
    destination: str,
    country: str,
    region: str,
    top_books: int = 5,
    student_friendly: bool = True
) -> Dict:
    """
    Get complete enrichment package for a destination
    
    Args:
        destination: Destination name
        country: Country name
        region: Geographic region
        top_books: Number of books to recommend
        student_friendly: Filter for student-friendly books
        
    Returns:
        Complete enrichment package with books and AI-generated content
    """
    engine = get_enrichment_engine()
    
    # Get recommended books
    books = engine.get_recommended_books(
        destination=destination,
        country=country,
        top_n=top_books,
        student_friendly_only=student_friendly
    )
    
    # Generate enrichment content
    enrichment = await engine.generate_enrichment(
        destination=destination,
        country=country,
        region=region,
        books=books
    )
    
    # Combine results
    return {
        "destination": destination,
        "country": country,
        "region": region,
        "summary": enrichment.get("historical_summary", ""),
        "cultural_tips": enrichment.get("cultural_insights", []),
        "travel_tips": enrichment.get("travel_tips", []),
        "book_enhancement_explanation": enrichment.get("book_enhancement", ""),
        "recommended_books": books,
        "total_books_found": len(books)
    }
