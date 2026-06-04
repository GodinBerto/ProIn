from datetime import timedelta

import requests
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import DataError, DatabaseError, IntegrityError
from django.utils import timezone
from django.shortcuts import get_object_or_404
from ninja import NinjaAPI, Router, Schema
from ninja.errors import HttpError
from django.http import HttpResponse
from packages.database import DatabaseTableDefinition, DatabaseTables
from .auth import AuthBearer
from .models import (
    Profile, Organization, OrganizationMember, OrganizationInvite,
    Document, DocumentShare, Message
)
from .schemas import (
    ProfileSchema, OrganizationSchema, OrganizationMemberSchema, OrganizationInviteSchema,
    DocumentSchema, DocumentShareSchema, MessageSchema, WorkerHeartbeatPayload,
    WorkerStatusResponse, HealthResponse, DatabaseHealthResponse
)

api = NinjaAPI()
auth_bearer = AuthBearer()
worker_heartbeats = {}
WORKER_HEALTH_WINDOW = timedelta(seconds=45)

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
def worker_heartbeat(request, payload: WorkerHeartbeatPayload):
    worker_name = payload.WorkerName or payload.workerName
    if not worker_name:
        raise HttpError(400, "WorkerName is required.")

    now = timezone.now()
    current = worker_heartbeats.get(worker_name)
    worker_heartbeats[worker_name] = {
        "workerName": worker_name,
        "lastSeenUtc": now,
        "heartbeatCount": (current["heartbeatCount"] if current else 0) + 1,
    }

    return HttpResponse(status=202)

@api.get("/workers/status", response=WorkerStatusResponse)
def worker_status(request):
    now = timezone.now()
    workers = []

    for worker in worker_heartbeats.values():
        last_seen = worker["lastSeenUtc"]
        workers.append({
            **worker,
            "isHealthy": now - last_seen <= WORKER_HEALTH_WINDOW,
        })

    return {
        "generatedAtUtc": now,
        "workers": sorted(workers, key=lambda worker: worker["workerName"]),
    }

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
def create_crud_router(model, schema, table: DatabaseTableDefinition):
    router = Router()

    @router.get("", response=list[schema])
    def list_items(request, limit: int = 100, offset: int = 0):
        limit = max(1, min(limit, 500))
        offset = max(0, offset)
        return model.objects.all().order_by(f'-{table.order_by_column}')[offset:offset+limit]

    @router.get("/{id}", response=schema)
    def get_item(request, id: str):
        return get_object_or_404(model, id=id)

    @router.post("", response=schema)
    def create_item(request, payload: dict):
        clean_payload = clean_payload_for_table(table, payload, mode="create")
        try:
            return model.objects.create(**clean_payload)
        except (DataError, IntegrityError, ValidationError) as exc:
            raise HttpError(400, str(exc)) from exc
        except DatabaseError as exc:
            raise HttpError(503, str(exc)) from exc

    @router.put("/{id}", response=schema)
    def update_item(request, id: str, payload: dict):
        obj = get_object_or_404(model, id=id)
        clean_payload = clean_payload_for_table(table, payload, mode="update")
        try:
            for attr, value in clean_payload.items():
                setattr(obj, attr, value)
            obj.save()
            return obj
        except (DataError, IntegrityError, ValidationError) as exc:
            raise HttpError(400, str(exc)) from exc
        except DatabaseError as exc:
            raise HttpError(503, str(exc)) from exc

    @router.delete("/{id}")
    def delete_item(request, id: str):
        obj = get_object_or_404(model, id=id)
        obj.delete()
        return {"success": True}

    return router

def clean_payload_for_table(
    table: DatabaseTableDefinition,
    payload: dict,
    *,
    mode: str,
) -> dict:
    allowed_columns = (
        table.create_column_names if mode == "create" else table.update_column_names
    )
    payload_columns = set(payload)
    unknown_columns = sorted(payload_columns - table.column_names)
    blocked_columns = sorted((payload_columns & table.column_names) - allowed_columns)

    if unknown_columns:
        raise HttpError(
            400,
            f"Unknown columns for {table.table_name}: {', '.join(unknown_columns)}",
        )

    if blocked_columns:
        raise HttpError(
            400,
            f"Columns cannot be {mode}d for {table.table_name}: {', '.join(blocked_columns)}",
        )

    return {
        column: value
        for column, value in payload.items()
        if column in allowed_columns
    }

api.add_router("/profiles", create_crud_router(Profile, ProfileSchema, DatabaseTables.PROFILES), auth=auth_bearer)
api.add_router("/organizations", create_crud_router(Organization, OrganizationSchema, DatabaseTables.ORGANIZATIONS), auth=auth_bearer)
api.add_router("/organization_members", create_crud_router(OrganizationMember, OrganizationMemberSchema, DatabaseTables.ORGANIZATION_MEMBERS), auth=auth_bearer)
api.add_router("/organization_invites", create_crud_router(OrganizationInvite, OrganizationInviteSchema, DatabaseTables.ORGANIZATION_INVITES), auth=auth_bearer)
api.add_router("/documents", create_crud_router(Document, DocumentSchema, DatabaseTables.DOCUMENTS), auth=auth_bearer)
api.add_router("/document_shares", create_crud_router(DocumentShare, DocumentShareSchema, DatabaseTables.DOCUMENT_SHARES), auth=auth_bearer)
api.add_router("/messages", create_crud_router(Message, MessageSchema, DatabaseTables.MESSAGES), auth=auth_bearer)
