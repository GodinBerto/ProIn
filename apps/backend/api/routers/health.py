from django.utils import timezone
from ninja import Router
from django.db import connection
from ..schemas import HealthResponse, DatabaseHealthResponse

router = Router()

@router.get("/health", response=HealthResponse)
def health(request):
    return {"status": "healthy", "timestampUtc": timezone.now()}


@router.get("/database/health", response=DatabaseHealthResponse)
def db_health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return {"status": "healthy", "timestampUtc": timezone.now(), "detail": "postgres.public"}
    except Exception as exc:
        return {"status": "unhealthy", "timestampUtc": timezone.now(), "detail": str(exc)}
