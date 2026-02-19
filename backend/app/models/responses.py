"""
Standard API Response Models
Consistent response format across all endpoints
"""

from typing import Generic, TypeVar, Optional, List, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response wrapper"""
    success: bool = True
    message: str = Field(default="Operation successful")
    data: Optional[T] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Data retrieved successfully",
                "data": {"id": 1, "name": "Example"},
                "timestamp": "2026-02-18T12:00:00"
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="API endpoint path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "ValidationError",
                "message": "Invalid input parameters",
                "details": {"field": "price", "issue": "must be positive"},
                "timestamp": "2026-02-18T12:00:00",
                "path": "/api/destinations"
            }
        }


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., ge=1, description="Current page")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total items in database")
    total_pages: int = Field(..., ge=0, description="Total pages")
    has_next: bool = Field(..., description="Has next page")
    has_previous: bool = Field(..., description="Has previous page")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    success: bool = True
    message: str = "Data retrieved successfully"
    data: List[T] = Field(default_factory=list)
    pagination: PaginationMeta
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Destinations retrieved",
                "data": [{"id": 1, "name": "Paris"}, {"id": 2, "name": "Tokyo"}],
                "pagination": {
                    "page": 1,
                    "page_size": 10,
                    "total_items": 50,
                    "total_pages": 5,
                    "has_next": True,
                    "has_previous": False
                },
                "timestamp": "2026-02-18T12:00:00"
            }
        }


class HealthCheck(BaseModel):
    """System health check response"""
    status: str = Field(..., description="healthy or degraded")
    version: str = Field(..., description="API version")
    uptime_seconds: float = Field(..., ge=0)
    services: Dict[str, str] = Field(
        default_factory=dict,
        description="Service status (database, cache, ai_service)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class BulkOperationResponse(BaseModel):
    """Response for bulk operations"""
    success: bool = True
    message: str = "Bulk operation completed"
    total_processed: int = Field(..., ge=0)
    successful: int = Field(..., ge=0)
    failed: int = Field(..., ge=0)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
