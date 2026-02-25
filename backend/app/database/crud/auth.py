"""CRUD operations for authentication and user profiles."""
from typing import Optional
from datetime import datetime, timezone

from app.database.config import supabase, SUPABASE_ENABLED
from app.database.models import RegisterUserCreate, LoginUserRequest


class AuthCRUD:
    """Authentication operations backed by Supabase Auth and profile table."""

    TABLE_NAME = "user_profiles"

    @staticmethod
    def _build_auth_metadata(username: str, phone_number: str) -> dict:
        """Build structured metadata stored in Supabase Auth user_metadata."""
        return {
            "profile": {
                "username": username,
                "display_name": username,
            },
            "contact": {
                "phone_number": phone_number,
            },
            "auth": {
                "source": "travelgenie",
                "schema_version": 1,
            },
            "name": username,
            "full_name": username,
            "display_name": username,
            "username": username,
            "phone_number": phone_number,
        }

    @staticmethod
    def _extract_profile_from_metadata(user_meta: Optional[dict]) -> dict:
        """Extract normalized profile fields from nested or legacy metadata."""
        user_meta = user_meta or {}
        nested_profile = user_meta.get("profile") if isinstance(user_meta, dict) else {}
        nested_profile = nested_profile or {}
        nested_contact = user_meta.get("contact") if isinstance(user_meta, dict) else {}
        nested_contact = nested_contact or {}

        username = (
            nested_profile.get("username")
            or user_meta.get("username")
            or user_meta.get("display_name")
            or user_meta.get("name")
            or user_meta.get("full_name")
        )
        display_name = (
            nested_profile.get("display_name")
            or user_meta.get("display_name")
            or user_meta.get("name")
            or user_meta.get("full_name")
            or username
        )
        phone_number = (
            nested_contact.get("phone_number")
            or nested_profile.get("phone_number")
            or user_meta.get("phone_number")
        )

        return {
            "username": username,
            "display_name": display_name,
            "phone_number": phone_number,
        }

    @staticmethod
    def _sync_auth_metadata(user_id: str, email: str, username: str, phone_number: Optional[str]) -> None:
        """Upsert structured metadata on Supabase Auth user for consistency."""
        admin_client = AuthCRUD._get_admin_client()
        if admin_client is None:
            return

        metadata = AuthCRUD._build_auth_metadata(username=username, phone_number=phone_number or "")

        update_payload = {
            "email": email,
            "user_metadata": metadata,
        }

        admin_client.auth.admin.update_user_by_id(user_id, update_payload)

    @staticmethod
    def _get_admin_client():
        """Create a Supabase admin client using service role key when available."""
        try:
            from supabase import create_client
            from app.database.config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY

            if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
                return None
            return create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        except Exception:
            return None

    @staticmethod
    def _is_missing_table_error(error: Exception) -> bool:
        """Check if an exception indicates missing user_profiles table."""
        text = str(error)
        return "PGRST205" in text or "Could not find the table" in text

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
        try:
            response = (
                supabase.table(AuthCRUD.TABLE_NAME)
                .select("*")
                .eq("username", username)
                .limit(1)
                .execute()
            )
            if response.data:
                return response.data[0]
        except Exception:
            return None
        return None

    @staticmethod
    def _get_auth_user_by_username(username: str) -> Optional[dict]:
        """Lookup Supabase Auth user by username in user metadata."""
        admin_client = AuthCRUD._get_admin_client()
        if admin_client is None:
            return None

        try:
            page = 1
            per_page = 200
            max_pages = 25

            while page <= max_pages:
                users_response = admin_client.auth.admin.list_users(page=page, per_page=per_page)
                if isinstance(users_response, list):
                    users = users_response
                else:
                    users = getattr(users_response, "users", None)
                    if users is None and isinstance(users_response, dict):
                        users = users_response.get("users")
                users = users or []

                if not users:
                    break

                for user in users:
                    user_meta = getattr(user, "user_metadata", None)
                    if user_meta is None and isinstance(user, dict):
                        user_meta = user.get("user_metadata")
                    user_meta = user_meta or {}
                    profile = AuthCRUD._extract_profile_from_metadata(user_meta)

                    if profile.get("username") == username:
                        user_id = getattr(user, "id", None)
                        email = getattr(user, "email", None)
                        if isinstance(user, dict):
                            user_id = user_id or user.get("id")
                            email = email or user.get("email")

                        return {
                            "user_id": str(user_id or ""),
                            "username": profile.get("username") or username,
                            "display_name": profile.get("display_name") or profile.get("username") or username,
                            "email": email,
                            "phone_number": profile.get("phone_number"),
                        }

                page += 1
        except Exception:
            return None

        return None

    @staticmethod
    def _get_auth_user_by_email(email: str) -> Optional[dict]:
        """Lookup Supabase Auth user by email."""
        admin_client = AuthCRUD._get_admin_client()
        if admin_client is None:
            return None

        normalized_email = (email or "").strip().lower()
        if not normalized_email:
            return None

        try:
            page = 1
            per_page = 200
            max_pages = 25

            while page <= max_pages:
                users_response = admin_client.auth.admin.list_users(page=page, per_page=per_page)
                if isinstance(users_response, list):
                    users = users_response
                else:
                    users = getattr(users_response, "users", None)
                    if users is None and isinstance(users_response, dict):
                        users = users_response.get("users")
                users = users or []

                if not users:
                    break

                for user in users:
                    user_email = getattr(user, "email", None)
                    user_id = getattr(user, "id", None)
                    user_meta = getattr(user, "user_metadata", None)

                    if isinstance(user, dict):
                        user_email = user_email or user.get("email")
                        user_id = user_id or user.get("id")
                        user_meta = user_meta or user.get("user_metadata")

                    if (user_email or "").strip().lower() == normalized_email:
                        user_meta = user_meta or {}
                        profile = AuthCRUD._extract_profile_from_metadata(user_meta)
                        return {
                            "user_id": str(user_id or ""),
                            "username": profile.get("username"),
                            "display_name": profile.get("display_name") or profile.get("username"),
                            "email": user_email,
                            "phone_number": profile.get("phone_number"),
                        }

                page += 1
        except Exception:
            return None

        return None

    @staticmethod
    def register(payload: RegisterUserCreate) -> dict:
        """Register user with Supabase email auth + local profile table."""
        if error := AuthCRUD._check_db_available():
            return error

        try:
            existing = AuthCRUD._get_profile_by_username(payload.username)
            if not existing:
                existing = AuthCRUD._get_auth_user_by_username(payload.username)
            if existing:
                return {
                    "success": False,
                    "message": "Username is already taken",
                    "data": None,
                }

            existing_email = AuthCRUD._get_auth_user_by_email(payload.email)
            if existing_email:
                return {
                    "success": False,
                    "message": "Email is already registered. Please verify your email or login.",
                    "data": None,
                }

            signup = supabase.auth.sign_up(
                {
                    "email": payload.email,
                    "password": payload.password,
                    "options": {
                        "data": AuthCRUD._build_auth_metadata(
                            payload.username,
                            payload.phone_number,
                        )
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

            try:
                AuthCRUD._sync_auth_metadata(
                    user_id=str(user.id),
                    email=payload.email,
                    username=payload.username,
                    phone_number=payload.phone_number,
                )
            except Exception:
                pass

            try:
                supabase.table(AuthCRUD.TABLE_NAME).upsert(profile_payload).execute()
            except Exception as exc:
                if not AuthCRUD._is_missing_table_error(exc):
                    raise

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
            error_text = str(exc)
            if "rate limit" in error_text.lower() or "too many requests" in error_text.lower():
                return {
                    "success": False,
                    "message": "Email sending is temporarily rate-limited. Please wait a few minutes before trying again.",
                    "data": None,
                }
            return {
                "success": False,
                "message": error_text,
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
                profile = AuthCRUD._get_auth_user_by_username(payload.username)
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

            user_meta = getattr(user, "user_metadata", None) or {}
            metadata_profile = AuthCRUD._extract_profile_from_metadata(user_meta)

            try:
                AuthCRUD._sync_auth_metadata(
                    user_id=str(user.id),
                    email=profile["email"],
                    username=metadata_profile.get("username") or profile.get("username") or payload.username,
                    phone_number=metadata_profile.get("phone_number") or profile.get("phone_number"),
                )
            except Exception:
                pass

            if not getattr(user, "email_confirmed_at", None):
                return {
                    "success": False,
                    "message": "Please verify your email before logging in.",
                    "data": {"email_verified": False},
                }

            try:
                supabase.table(AuthCRUD.TABLE_NAME).update(
                    {
                        "is_email_verified": True,
                        "last_login_at": datetime.now(timezone.utc).isoformat(),
                    }
                ).eq("user_id", str(user.id)).execute()
            except Exception:
                pass

            return {
                "success": True,
                "message": "Login successful",
                "data": {
                    "user_id": str(user.id),
                    "username": metadata_profile.get("username") or profile.get("username") or payload.username,
                    "display_name": metadata_profile.get("display_name") or metadata_profile.get("username") or profile.get("username") or payload.username,
                    "email": profile["email"],
                    "phone_number": metadata_profile.get("phone_number") or profile.get("phone_number"),
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
