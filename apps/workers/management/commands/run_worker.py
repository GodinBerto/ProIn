import time
import requests
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

class Command(BaseCommand):
    help = 'Runs the background worker'

    def handle(self, *args, **options):
        worker_name = "queue-worker"
        interval = 15
        
        self.stdout.write(self.style.SUCCESS(f"Worker {worker_name} started. Will heartbeat every {interval}s."))
        
        while True:
            try:
                # HTTP ping the local API to emulate previous C# worker behavior
                resp = requests.get(f"{settings.BACKEND_URL}/api/health", timeout=5)
                if resp.status_code == 200:
                    health_status = resp.json().get("status", "unknown")
                    
                    # Send heartbeat
                    requests.post(
                        f"{settings.BACKEND_URL}/api/workers/heartbeat", 
                        json={"WorkerName": worker_name},
                        timeout=5
                    )
                    
                    self.stdout.write(f"Heartbeat acknowledged by backend at {timezone.now()}. Backend status: {health_status}")
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Heartbeat failed: {e}"))
            
            time.sleep(interval)
