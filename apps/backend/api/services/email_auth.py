import uuid

import jwt
import requests
from django.conf import settings

from ..models import Profile
from .google_auth import GoogleAuthError, _ensure_profile


def _supabase_headers() -> dict[str, str]:
    return {
        "apikey": settings.SUPABASE_ANON_KEY,
        "Content-Type": "application/json",
    }


def _parse_supabase_error(response: requests.Response) -> str:
    try:
        body = response.json()
    except ValueError:
        return "Authentication request failed"

    return (
        body.get("error_description")
        or body.get("msg")
        or body.get("message")
        or "Authentication request failed"
    )


def _build_auth_response(
    *,
    access_token: str,
    refresh_token: str | None,
    user_id: uuid.UUID,
    email: str,
    profile: Profile,
    is_new_user: bool,
) -> dict:
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "is_new_user": is_new_user,
        "user": {
            "id": str(user_id),
            "email": email,
            "full_name": profile.full_name,
            "avatar_url": profile.avatar_url,
        },
    }


def register_user(*, email: str, password: str) -> dict:
    if not settings.SUPABASE_ANON_KEY:
        raise GoogleAuthError("SUPABASE_ANON_KEY is not configured", status_code=503)

    response = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/signup",
        json={"email": email, "password": password},
        headers=_supabase_headers(),
        timeout=15,
    )

    if response.status_code >= 400:
        raise GoogleAuthError(
            _parse_supabase_error(response),
            status_code=response.status_code,
        )

    data = response.json()
    user = data.get("user") or {}
    user_id = user.get("id")
    user_email = user.get("email") or email
    access_token = data.get("access_token")

    if not user_id or not access_token:
        raise GoogleAuthError(
            "Account created. Check your email to confirm before signing in.",
            status_code=400,
        )

    profile, is_new_user = _ensure_profile(
        user_id=uuid.UUID(user_id),
        email=user_email,
        full_name=None,
        avatar_url=None,
    )

    return _build_auth_response(
        access_token=access_token,
        refresh_token=data.get("refresh_token"),
        user_id=uuid.UUID(user_id),
        email=user_email,
        profile=profile,
        is_new_user=is_new_user,
    )


def login_user(*, email: str, password: str) -> dict:
    if not settings.SUPABASE_ANON_KEY:
        raise GoogleAuthError("SUPABASE_ANON_KEY is not configured", status_code=503)

    response = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password",
        json={"email": email, "password": password},
        headers=_supabase_headers(),
        timeout=15,
    )

    if response.status_code >= 400:
        raise GoogleAuthError(
            _parse_supabase_error(response),
            status_code=response.status_code,
        )

    data = response.json()
    user = data.get("user") or {}
    user_id = user.get("id")
    user_email = user.get("email") or email
    access_token = data.get("access_token")

    if not user_id or not access_token:
        raise GoogleAuthError("Invalid login response", status_code=500)

    profile, is_new_user = _ensure_profile(
        user_id=uuid.UUID(user_id),
        email=user_email,
        full_name=None,
        avatar_url=None,
    )

    return _build_auth_response(
        access_token=access_token,
        refresh_token=data.get("refresh_token"),
        user_id=uuid.UUID(user_id),
        email=user_email,
        profile=profile,
        is_new_user=is_new_user,
    )


def send_magic_link(*, email: str, redirect_to: str | None = None) -> dict:
    if not settings.SUPABASE_ANON_KEY:
        raise GoogleAuthError("SUPABASE_ANON_KEY is not configured", status_code=503)

    callback_url = redirect_to or f"{settings.WEB_APP_URL}/auth/callback"

    response = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/otp",
        json={
            "email": email,
            "options": {
                "email_redirect_to": callback_url,
                "should_create_user": True,
            },
        },
        headers=_supabase_headers(),
        timeout=15,
    )

    if response.status_code >= 400:
        raise GoogleAuthError(
            _parse_supabase_error(response),
            status_code=response.status_code,
        )

    return {"message": "Magic link sent. Check your email to continue."}


def sync_session(*, access_token: str) -> dict:
    if not settings.JWT_SECRET:
        raise GoogleAuthError("JWT_SECRET is not configured", status_code=503)

    try:
        decoded = jwt.decode(
            access_token,
            settings.JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
            issuer=settings.JWT_ISSUER,
        )
    except jwt.PyJWTError as exc:
        raise GoogleAuthError("Invalid or expired session", status_code=401) from exc

    user_id = decoded.get("sub")
    email = decoded.get("email")

    if not user_id or not email:
        raise GoogleAuthError("Invalid session token", status_code=401)

    profile, is_new_user = _ensure_profile(
        user_id=uuid.UUID(user_id),
        email=email,
        full_name=None,
        avatar_url=None,
    )

    return _build_auth_response(
        access_token=access_token,
        refresh_token=None,
        user_id=uuid.UUID(user_id),
        email=email,
        profile=profile,
        is_new_user=is_new_user,
    )
