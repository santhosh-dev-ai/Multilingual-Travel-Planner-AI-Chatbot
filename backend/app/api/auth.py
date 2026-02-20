"""Authentication API endpoints."""
from fastapi import APIRouter, HTTPException

from app.database.crud import AuthCRUD
from app.database.models import RegisterUserCreate, LoginUserRequest


router = APIRouter()


@router.post("/register")
def register_user(payload: RegisterUserCreate):
    """Register user with Supabase email verification."""
    result = AuthCRUD.register(payload)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Registration failed"))
    return result


@router.post("/login")
def login_user(payload: LoginUserRequest):
    """Login user with username/password after email verification."""
    result = AuthCRUD.login(payload)
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("message", "Login failed"))
    return result
