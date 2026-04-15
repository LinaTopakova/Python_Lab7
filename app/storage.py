from typing import Any, Dict, Optional
from app.logger import logger

tasks_storage: Dict[str, Dict[str, Any]] = {}

def create_task(callback_url: Optional[str] = None) -> str:
    from uuid import uuid4
    task_id = str(uuid4())
    tasks_storage[task_id] = {
        "status": "pending",
        "result": None,
        "callback_url": callback_url
    }
    return task_id

def update_task(task_id: str, status: str, result: Any = None):
    if task_id in tasks_storage:
        old_status = tasks_storage[task_id]["status"]
        tasks_storage[task_id]["status"] = status
        if result is not None:
            tasks_storage[task_id]["result"] = result
        logger.info(f"Task {task_id} status changed: {old_status} -> {status}")

def get_task(task_id: str):
    return tasks_storage.get(task_id)