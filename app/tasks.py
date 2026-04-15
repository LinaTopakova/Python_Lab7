import asyncio
import time
import httpx
from app.logger import logger
from app.storage import update_task, get_task

async def send_callback(callback_url: str, result: dict, max_retries: int = 3):
    async with httpx.AsyncClient() as client:
        for attempt in range(1, max_retries + 1):
            try:
                response = await client.post(callback_url, json=result, timeout=5.0)
                if response.status_code == 200:
                    logger.info(f"Callback successful to {callback_url}")
                    return
                else:
                    logger.warning(f"Callback attempt {attempt} failed with status {response.status_code}")
            except Exception as e:
                logger.error(f"Callback attempt {attempt} error: {e}")
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
    logger.error(f"Callback ultimately failed after {max_retries} attempts to {callback_url}")

async def long_running_task(task_id: str, input_data: dict):
    logger.info(f"Starting long running task {task_id} with input {input_data}")
    try:
        total_steps = 10
        for step in range(1, total_steps + 1):
            await asyncio.sleep(1)
            update_task(task_id, "running", {"progress": step, "total": total_steps})
            logger.debug(f"Task {task_id} progress: {step}/{total_steps}")

        result = {"output": f"Processed {input_data.get('name', 'unknown')}"}
        update_task(task_id, "completed", result)
        task_info = get_task(task_id)
        logger.info(f"Task {task_id} completed with result: {result}")

        if task_info and task_info.get("callback_url"):
            await send_callback(task_info["callback_url"], result)

    except Exception as e:
        logger.exception(f"Task {task_id} failed with error")
        update_task(task_id, "error", {"error": str(e)})

def sync_cpu_bound(data: dict) -> dict:
    time.sleep(3)
    return {"computed": data.get("value", 0) * 2}