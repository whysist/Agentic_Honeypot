import json
import os
import redis
from app.storage.models import SessionState

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)


async def get_session(session_id: str) -> SessionState:
    data = await redis_client.get(session_id)
    if not data:
        return SessionState(sessionId=session_id)
    return SessionState(**json.loads(data))


async def save_session(session: SessionState):
    await redis_client.set(
        session.sessionId,
        session.model_dump_json(),
        ex=3600  # 1 hour TTL
    )
