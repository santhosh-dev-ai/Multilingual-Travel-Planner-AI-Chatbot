"""CRUD operations for authentication and user profiles."""
from typing import Optional
from datetime import datetime, timezone

from app.database.config import supabase, SUPABASE_ENABLED
from app.database.models import RegisterUserCreate, LoginUserRequest


class AuthCRUD:
    """Authentication operations backed by Supabase Auth and profile table."""

    TABLE_NAME = "user_profiles"

    @staticmethod
    def _check_db_available() -> Optional[dict]:
        """Check if database is available."""
        if not SUPABASE_ENABLED or supabase is None:
            return {
                "success": False,
                "message": "Database not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env file.",
                "data": None,
            }
        return None

    @staticmethod
    def _get_profile_by_username(username: str) -> Optional[dict]:
        """Get user profile by username."""
        response = (
            supabase.table(AuthCRUD.TABLE_NAME)
            .select("*")
            .eq("username", username)
            .limit(1)
            .execute()
        )
        if response.data:
            return response.data[0]
        return None

    @staticmethod
    def register(payload: RegisterUserCreate) -> dict:
        """Register user with Supabase email auth + local profile table."""
        if error := AuthCRUD._check_db_available():
            return error

        try:
            existing = AuthCRUD._get_profile_by_username(payload.username)
            if existing:
                return {
                    "success": False,
                    "message": "Username is already taken",
                    "data": None,
                }

            signup = supabase.auth.sign_up(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "options": {
                        "data": {
                            "username": payload.username,
                            "phone_number": payload.phone_number,
                        }
                    },
                }
            )

            user = getattr(signup, "user", None)
            if user is None:
                return {
                    "success": False,
                    "message": "Failed to create user in Supabase Auth",
                    "data": None,
                }

            profile_payload = {
                "user_id": str(user.id),
                "username": payload.username,
                "email": payload.email,
                "phone_number": payload.phone_number,
                "is_email_verified": False,
            }

            supabase.table(AuthCRUD.TABLE_NAME).upsert(profile_payload).execute()

            return {
                "success": True,
                "message": "Registration successful. Please verify your email before logging in.",
                "data": {
                    "user_id": str(user.id),
                    "email": payload.email,
                    "username": payload.username,
                    "requires_email_verification": True,
                },
            }
        except Exception as exc:
            return {
                "success": False,
                "message": str(exc),
                "data": None,
            }

    @staticmethod
    def login(payload: LoginUserRequest) -> dict:
        """Login with username/password, mapping username -> email."""
        if error := AuthCRUD._check_db_available():
            return error

        try:
            profile = AuthCRUD._get_profile_by_username(payload.username)
            if not profile:
                return {
                    "success": False,
                    "message": "Invalid username or password",
                    "data": None,
                }

            login_response = supabase.auth.sign_in_with_password(
                {
                    "email": profile["email"],
                    "password": payload.password,
                }
            )

            user = getattr(login_response, "user", None)
            session = getattr(login_response, "session", None)

            if user is None:
                return {
                    "success": False,
                    "message": "Invalid username or password",
                    "data": None,
                }

            if not getattr(user, "email_confirmed_at", None):
                return {
                    "success": False,
                    "message": "Please verify your email before logging in.",
                    "data": {"email_verified": False},
                }

            supabase.table(AuthCRUD.TABLE_NAME).update(
                {
                    "is_email_verified": True,
                    "last_login_at": datetime.now(timezone.utc).isoformat(),
                }
            ).eq("user_id", str(user.id)).execute()

            return {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user_id": str(user.id),
                    "username": profile["username"],
                    "email": profile["email"],
                    "phone_number": profile.get("phone_number"),
                    "access_token": getattr(session, "access_token", None),
                    "refresh_token": getattr(session, "refresh_token", None),
                },
            }
        except Exception as exc:
            error_text = str(exc)
            if "Email not confirmed" in error_text:
                return {
                    "success": False,
                    "message": "Please verify your email before logging in.",
                    "data": {"email_verified": False},
                }
            return {
                "success": False,
                "message": error_text,
                "data": None,
            }
