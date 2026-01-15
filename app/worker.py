"""RQ worker entrypoint.

Docker compose'ta `worker` servisi bu modülü çalıştırır.
"""
from redis import Redis
from rq import Worker, Queue, Connection
from app.core.config import settings

def main():
    redis_conn = Redis.from_url(settings.redis_url)
    with Connection(redis_conn):
        q = Queue(settings.rq_queue_name)
        w = Worker([q])
        w.work(with_scheduler=False)

if __name__ == "__main__":
    main()
