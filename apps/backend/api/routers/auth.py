from django.http import JsonResponse
from ninja import Router, HttpError

from ..auth import AuthBearer
from ..models import Profile
from ..schemas import (
    AuthPayload,
    GoogleAuthPayload,
    MagicLinkPayload,
    ProfileSchema,
    SessionPayload,
)
from ..services.email_auth import (
    login_user,
    register_user,
    send_magic_link,
    sync_session,
)
from ..services.google_auth import GoogleAuthError, authenticate_google_user

router = Router()
auth_bearer = AuthBearer()


@router.post("/register")
def auth_register(request, payload: AuthPayload):
    try:
        return register_user(email=payload.email, password=payload.password)
    except GoogleAuthError as exc:
        return JsonResponse({"detail": str(exc)}, status=exc.status_code)


@router.post("/login")
def auth_login(request, payload: AuthPayload):
    try:
        return login_user(email=payload.email, password=payload.password)
    except GoogleAuthError as exc:
        return JsonResponse({"detail": str(exc)}, status=exc.status_code)


@router.post("/magic-link")
def auth_magic_link(request, payload: MagicLinkPayload):
    try:
        return send_magic_link(email=payload.email, redirect_to=payload.redirect_to)
    except GoogleAuthError as exc:
        return JsonResponse({"detail": str(exc)}, status=exc.status_code)


@router.post("/session")
def auth_session(request, payload: SessionPayload):
    try:
        return sync_session(access_token=payload.access_token)
    except GoogleAuthError as exc:
        return JsonResponse({"detail": str(exc)}, status=exc.status_code)


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
