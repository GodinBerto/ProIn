from django.http import JsonResponse
from ninja import Router, HttpError

import requests
from django.conf import settings
from django.http import HttpResponse

from ..auth import AuthBearer
from ..models import Profile
from ..schemas import AuthPayload, GoogleAuthPayload, ProfileSchema
from ..services.google_auth import GoogleAuthError, authenticate_google_user

router = Router()
auth_bearer = AuthBearer()


@router.post("/register")
def auth_register(request, payload: AuthPayload):
    resp = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/signup",
        json={"email": payload.email, "password": payload.password},
        headers={"apikey": settings.SUPABASE_ANON_KEY},
    )
    return HttpResponse(resp.content, status=resp.status_code, content_type="application/json")


@router.post("/login")
def auth_login(request, payload: AuthPayload):
    resp = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password",
        json={"email": payload.email, "password": payload.password},
        headers={"apikey": settings.SUPABASE_ANON_KEY},
    )
    return HttpResponse(resp.content, status=resp.status_code, content_type="application/json")


@router.post("/google")
def auth_google(request, payload: GoogleAuthPayload):
    try:
        result = authenticate_google_user(
            email=payload.email,
            full_name=payload.full_name,
            avatar_url=payload.avatar_url,
            id_token=payload.id_token,
        )
        return result
    except GoogleAuthError as exc:
        return JsonResponse({"detail": str(exc)}, status=exc.status_code)


@router.get("/me", response=ProfileSchema, auth=auth_bearer)
def get_user(request):
    user_id = request.auth.get("sub")
    if not user_id:
        raise HttpError(401, "Invalid token")

    profile = Profile.objects.filter(id=user_id).first()
    if profile is None:
        raise HttpError(404, "User not found")

    return profile