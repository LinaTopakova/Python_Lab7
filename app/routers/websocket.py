from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import asyncio
from app.logger import logger
from app.storage import get_task

router = APIRouter(tags=["websocket"])

@router.websocket("/ws/task/{task_id}")
async def websocket_task_status(websocket: WebSocket, task_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connection accepted for task {task_id}")
    try:
        while True:
            task = get_task(task_id)
            if not task:
                logger.warning(f"WebSocket: Task {task_id} not found")
                await websocket.send_json({"error": "Task not found"})
                break

            await websocket.send_json(task)
            if task["status"] in ("completed", "error"):
                logger.info(f"Task {task_id} finished with status {task['status']}, closing WebSocket")
                break

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        logger.info(f"WebSocket client disconnected for task {task_id}")
    except Exception as e:
        logger.exception(f"WebSocket error for task {task_id}")