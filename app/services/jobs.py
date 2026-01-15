from __future__ import annotations

import json
from redis import Redis
from rq import Queue

from app.core.config import settings

def get_queue() -> Queue:
    redis_conn = Redis.from_url(settings.redis_url)
    return Queue(settings.rq_queue_name, connection=redis_conn)

def enqueue_training(run_id: str) -> str:
    """Train job'ını queue'ya atar, job_id döner."""
    q = get_queue()
    job = q.enqueue("app.services.train_job.execute_train_job", run_id)
    return job.id
