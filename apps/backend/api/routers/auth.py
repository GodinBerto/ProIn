from ninja import Router
from django.http import HttpResponse
import requests
from django.conf import settings
from ..schemas import AuthPayload

router = Router()

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
import requests
from django.conf import settings
from django.http import HttpResponse
from ninja import Router
from ..schemas import AuthPayload

router = Router()

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
