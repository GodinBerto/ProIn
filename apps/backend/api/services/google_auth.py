import time
import uuid

import jwt
import requests
from django.conf import settings
from django.db import transaction

from ..models import Profile


class GoogleAuthError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _supabase_headers(*, service: bool = False) -> dict[str, str]:
    api_key = (
        settings.SUPABASE_SERVICE_ROLE_KEY
        if service
        else settings.SUPABASE_ANON_KEY
    )
    return {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _exchange_google_id_token(id_token: str) -> dict:
    response = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=id_token",
        json={"provider": "google", "id_token": id_token},
        headers=_supabase_headers(),
        timeout=15,
    )

    if response.status_code >= 400:
        body = response.json()
        raise GoogleAuthError(
            body.get("error_description") or body.get("msg", "Google token exchange failed"),
            status_code=response.status_code,
        )

    return response.json()


def _find_supabase_user_by_email(email: str) -> dict | None:
    response = requests.get(
        f"{settings.SUPABASE_URL}/auth/v1/admin/users",
        params={"email": email},
        headers=_supabase_headers(service=True),
        timeout=15,
    )

    if response.status_code >= 400:
        body = response.json()
        raise GoogleAuthError(
            body.get("msg", "Failed to look up user"),
            status_code=response.status_code,
        )

    users = response.json().get("users", [])
    return users[0] if users else None


def _create_supabase_user(email: str, full_name: str | None, avatar_url: str | None) -> dict:
    payload: dict[str, object] = {
        "email": email,
        "email_confirm": True,
        "user_metadata": {
            "full_name": full_name,
            "avatar_url": avatar_url,
            "provider": "google",
        },
    }

    response = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/admin/users",
        json=payload,
        headers=_supabase_headers(service=True),
        timeout=15,
    )

    if response.status_code >= 400:
        body = response.json()
        raise GoogleAuthError(
            body.get("msg", "Failed to create user"),
            status_code=response.status_code,
        )

    return response.json()


def _create_access_token(user_id: str, email: str) -> str:
    now = int(time.time())
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "aud": "authenticated",
        "iss": settings.JWT_ISSUER,
        "iat": now,
        "exp": now + 3600,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def _ensure_profile(
    *,
    user_id: uuid.UUID,
    email: str,
    full_name: str | None,
    avatar_url: str | None,
) -> tuple[Profile, bool]:
    with transaction.atomic():
        profile = Profile.objects.filter(email=email).first()

        if profile is None:
            profile = Profile.objects.create(
                id=user_id,
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
            )
            return profile, True

        updates: dict[str, str] = {}
        if full_name and not profile.full_name:
            updates["full_name"] = full_name
        if avatar_url and not profile.avatar_url:
            updates["avatar_url"] = avatar_url

        if updates:
            for field, value in updates.items():
                setattr(profile, field, value)
            profile.save(update_fields=[*updates.keys(), "updated_at"])

        return profile, False


def _authenticate_with_supabase_admin(
    *,
    email: str,
    full_name: str | None,
    avatar_url: str | None,
) -> tuple[uuid.UUID, str, bool]:
    existing_user = _find_supabase_user_by_email(email)

    if existing_user:
        user_id = uuid.UUID(existing_user["id"])
        access_token = _create_access_token(str(user_id), email)
        return user_id, access_token, False

    created_user = _create_supabase_user(email, full_name, avatar_url)
    user_id = uuid.UUID(created_user["id"])
    access_token = _create_access_token(str(user_id), email)
    return user_id, access_token, True


def _authenticate_with_database_only(
    *,
    email: str,
    full_name: str | None,
    avatar_url: str | None,
) -> tuple[uuid.UUID, str, bool]:
    profile = Profile.objects.filter(email=email).first()

    if profile is None:
        user_id = uuid.uuid4()
        profile = Profile.objects.create(
            id=user_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
        )
        access_token = _create_access_token(str(user_id), email)
        return user_id, access_token, True

    updates: dict[str, str] = {}
    if full_name and not profile.full_name:
        updates["full_name"] = full_name
    if avatar_url and not profile.avatar_url:
        updates["avatar_url"] = avatar_url

    if updates:
        for field, value in updates.items():
            setattr(profile, field, value)
        profile.save(update_fields=[*updates.keys(), "updated_at"])

    access_token = _create_access_token(str(profile.id), email)
    return profile.id, access_token, False


def authenticate_google_user(
    *,
    email: str,
    full_name: str | None = None,
    avatar_url: str | None = None,
    id_token: str | None = None,
) -> dict:
    if not email:
        raise GoogleAuthError("Email is required", status_code=400)

    if not settings.JWT_SECRET:
        raise GoogleAuthError("JWT_SECRET is not configured", status_code=503)

    access_token: str | None = None
    refresh_token: str | None = None
    user_id: uuid.UUID | None = None
    is_new_user = False
    profile: Profile | None = None
    profile_created = False

    if id_token:
        try:
            token_data = _exchange_google_id_token(id_token)
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            user_id = uuid.UUID(token_data["user"]["id"])
        except GoogleAuthError:
            pass

    if user_id is None and settings.SUPABASE_SERVICE_ROLE_KEY:
        try:
            user_id, access_token, is_new_user = _authenticate_with_supabase_admin(
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
            )
        except GoogleAuthError:
            pass

    if user_id is None:
        user_id, access_token, is_new_user = _authenticate_with_database_only(
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
        )
        profile = Profile.objects.get(email=email)
        profile_created = is_new_user
    else:
        profile, profile_created = _ensure_profile(
            user_id=user_id,
            email=email,
            full_name=full_name,
            avatar_url=avatar_url,
        )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600,
        "is_new_user": is_new_user or profile_created,
        "user": {
            "id": str(user_id),
            "email": email,
            "full_name": profile.full_name,
            "avatar_url": profile.avatar_url,
        },
    }
