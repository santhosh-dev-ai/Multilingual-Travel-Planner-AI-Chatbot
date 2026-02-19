"""
Utility Functions - Helper functions for common operations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import re
import unicodedata
import hashlib


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug
    
    Example:
        "Paris, France" -> "paris-france"
    """
    # Normalize unicode
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase, remove non-alphanumeric
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '-', text)
    
    return text.strip('-')


def generate_id(prefix: str = "", length: int = 16) -> str:
    """
    Generate unique ID
    
    Args:
        prefix: Optional prefix (e.g., "user_", "dest_")
        length: Length of random part
        
    Returns:
        Unique ID string
    """
    import secrets
    random_part = secrets.token_urlsafe(length)[:length]
    return f"{prefix}{random_part}" if prefix else random_part


def calculate_pagination(
    page: int,
    page_size: int,
    total_items: int
) -> Dict[str, Any]:
    """
    Calculate pagination metadata
    
    Args:
        page: Current page (1-indexed)
        page_size: Items per page
        total_items: Total items in dataset
        
    Returns:
        Pagination metadata dict
    """
    total_pages = (total_items + page_size - 1) // page_size
    
    return {
        'page': page,
        'page_size': page_size,
        'total_items': total_items,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_previous': page > 1
    }


def parse_budget_string(budget_str: str) -> Optional[Dict[str, int]]:
    """
    Parse budget string into min/max values
    
    Example:
        "$500-$1500" -> {"min": 500, "max": 1500}
        "$1000+" -> {"min": 1000, "max": None}
    """
    if not budget_str:
        return None
    
    # Remove currency symbols and whitespace
    budget_str = re.sub(r'[\$€£,\s]', '', budget_str)
    
    # Handle ranges
    if '-' in budget_str:
        parts = budget_str.split('-')
        try:
            return {
                'min': int(parts[0]),
                'max': int(parts[1])
            }
        except:
            return None
    
    # Handle "1000+" format
    if '+' in budget_str:
        try:
            return {
                'min': int(budget_str.replace('+', '')),
                'max': None
            }
        except:
            return None
    
    # Single value
    try:
        value = int(budget_str)
        return {'min': value, 'max': value}
    except:
        return None


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string
    
    Args:
        amount: Numeric amount
        currency: Currency code
        
    Returns:
        Formatted string (e.g., "$1,234.56")
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥'
    }
    
    symbol = symbols.get(currency, '$')
    
    # Format with commas
    formatted = f"{amount:,.2f}"
    
    # Remove decimals for whole numbers
    if amount == int(amount):
        formatted = f"{int(amount):,}"
    
    return f"{symbol}{formatted}"


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two coordinates (Haversine formula)
    
    Args:
        lat1, lon1: First coordinate
        lat2, lon2: Second coordinate
        
    Returns:
        Distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in km
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c


def time_ago(dt: datetime) -> str:
    """
    Convert datetime to human-readable "time ago" format
    
    Example:
        "2 hours ago", "3 days ago"
    """
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        months = int(seconds / 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"


def validate_email(email: str) -> bool:
    """Simple email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input
    
    Args:
        text: Input text
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C')
    
    # Trim to max length
    text = text[:max_length]
    
    # Strip whitespace
    text = text.strip()
    
    return text


def batch_items(items: List[Any], batch_size: int = 100) -> List[List[Any]]:
    """
    Split list into batches
    
    Args:
        items: List to batch
        batch_size: Size of each batch
        
    Returns:
        List of batches
    """
    return [
        items[i:i + batch_size]
        for i in range(0, len(items), batch_size)
    ]


def deep_merge(dict1: dict, dict2: dict) -> dict:
    """
    Deep merge two dictionaries
    dict2 values override dict1
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 100.0 if new_value > 0 else 0.0
    
    return ((new_value - old_value) / old_value) * 100


def get_season(month: int) -> str:
    """
    Get season name from month number
    
    Args:
        month: Month number (1-12)
        
    Returns:
        Season name (spring, summer, fall, winter)
    """
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "fall"
    else:
        return "winter"
