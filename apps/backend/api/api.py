import requests
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Router, Schema
from django.http import HttpResponse
from .auth import AuthBearer
from .models import (
    Profile, Organization, OrganizationMember, OrganizationInvite,
    Document, DocumentShare, Message
)
from .schemas import (
    ProfileSchema, OrganizationSchema, OrganizationMemberSchema, OrganizationInviteSchema,
    DocumentSchema, DocumentShareSchema, MessageSchema,
    HealthResponse, DatabaseHealthResponse
)

api = NinjaAPI()
auth_bearer = AuthBearer()

# Auth Payload Schemas
class AuthPayload(Schema):
    email: str
    password: str

@api.get("/health", response=HealthResponse)
def health(request):
    return {"status": "healthy", "timestampUtc": timezone.now()}

@api.get("/database/health", response=DatabaseHealthResponse)
def db_health(request):
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy", "timestampUtc": timezone.now(), "detail": "postgres.public"}
    except Exception as e:
        return {"status": "unhealthy", "timestampUtc": timezone.now(), "detail": str(e)}

@api.post("/workers/heartbeat")
def worker_heartbeat(request):
    return HttpResponse(status=202)

# Auth Proxy
@api.post("/auth/register")
def auth_register(request, payload: AuthPayload):
    resp = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/signup",
        json={"email": payload.email, "password": payload.password},
        headers={"apikey": settings.SUPABASE_ANON_KEY}
    )
    return HttpResponse(resp.content, status=resp.status_code, content_type="application/json")

@api.post("/auth/login")
def auth_login(request, payload: AuthPayload):
    resp = requests.post(
        f"{settings.SUPABASE_URL}/auth/v1/token?grant_type=password",
        json={"email": payload.email, "password": payload.password},
        headers={"apikey": settings.SUPABASE_ANON_KEY}
    )
    return HttpResponse(resp.content, status=resp.status_code, content_type="application/json")


# CRUD Factory
def create_crud_router(model, schema, name):
    router = Router()

    @router.get("", response=list[schema])
    def list_items(request, limit: int = 100, offset: int = 0):
        return model.objects.all().order_by('-id')[offset:offset+limit]

    @router.get("/{id}", response=schema)
    def get_item(request, id: str):
        return get_object_or_404(model, id=id)

    @router.post("", response=schema)
    def create_item(request, payload: dict):
        obj = model.objects.create(**payload)
        return obj

    @router.put("/{id}", response=schema)
    def update_item(request, id: str, payload: dict):
        obj = get_object_or_404(model, id=id)
        for attr, value in payload.items():
            if attr != "id":
                setattr(obj, attr, value)
        obj.save()
        return obj

    @router.delete("/{id}")
    def delete_item(request, id: str):
        obj = get_object_or_404(model, id=id)
        obj.delete()
        return {"success": True}

    return router

api.add_router("/profiles", create_crud_router(Profile, ProfileSchema, "profiles"), auth=auth_bearer)
api.add_router("/organizations", create_crud_router(Organization, OrganizationSchema, "organizations"), auth=auth_bearer)
api.add_router("/organization_members", create_crud_router(OrganizationMember, OrganizationMemberSchema, "organization_members"), auth=auth_bearer)
api.add_router("/organization_invites", create_crud_router(OrganizationInvite, OrganizationInviteSchema, "organization_invites"), auth=auth_bearer)
api.add_router("/documents", create_crud_router(Document, DocumentSchema, "documents"), auth=auth_bearer)
api.add_router("/document_shares", create_crud_router(DocumentShare, DocumentShareSchema, "document_shares"), auth=auth_bearer)
api.add_router("/messages", create_crud_router(Message, MessageSchema, "messages"), auth=auth_bearer)
