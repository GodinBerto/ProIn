from datetime import timedelta
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from django.http import HttpResponse
from ..schemas import WorkerHeartbeatPayload, WorkerStatusResponse

router = Router()
worker_heartbeats = {}
WORKER_HEALTH_WINDOW = timedelta(seconds=45)

@router.post("/heartbeat")
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


@router.get("/status", response=WorkerStatusResponse)
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
