import asyncio
from typing import Callable, Any, Dict
from app.redis_storage import storage   
from app.logger import logger

class TaskQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None

    async def worker(self):
        while True:
            task_func, task_id, input_data = await self.queue.get()
            logger.info(f"Processing task {task_id} from queue")
            try:
                await task_func(task_id, input_data)
            except Exception as e:
                await storage.update_task(task_id, "error", {"error": str(e)})
                logger.exception(f"Task {task_id} failed in worker")
            finally:
                self.queue.task_done()
                logger.info(f"Finished processing task {task_id}")

    async def start(self):
        self.worker_task = asyncio.create_task(self.worker())

    async def stop(self):
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

    def add_task(self, task_func: Callable, task_id: str, input_data: Dict[str, Any]):
        self.queue.put_nowait((task_func, task_id, input_data))

task_queue = TaskQueue()