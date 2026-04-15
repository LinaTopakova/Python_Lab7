import redis.asyncio as redis
import json
from typing import Optional, Dict, Any
from app.logger import logger

class RedisStorage:
    def __init__(self, redis_url: str = "redis://localhost:6379", ttl_seconds: int = 3600):
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.ttl = ttl_seconds  # 1 час по умолчанию

    async def create_task(self, callback_url: Optional[str] = None) -> str:
        from uuid import uuid4
        task_id = str(uuid4())
        task_data = {
            "status": "pending",
            "result": None,
            "callback_url": callback_url
        }
        key = f"task:{task_id}"
        await self.redis.setex(key, self.ttl, json.dumps(task_data))
        logger.info(f"Task {task_id} created in Redis with TTL {self.ttl}s")
        return task_id

    async def update_task(self, task_id: str, status: str, result: Any = None):
        key = f"task:{task_id}"
        data_raw = await self.redis.get(key)
        if data_raw:
            task_data = json.loads(data_raw)
            old_status = task_data["status"]
            task_data["status"] = status
            if result is not None:
                task_data["result"] = result
            await self.redis.setex(key, self.ttl, json.dumps(task_data))
            logger.info(f"Task {task_id} status changed: {old_status} -> {status}")
        else:
            logger.warning(f"Attempt to update non-existent task {task_id}")

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        key = f"task:{task_id}"
        data_raw = await self.redis.get(key)
        if data_raw:
            return json.loads(data_raw)
        return None

storage = RedisStorage()