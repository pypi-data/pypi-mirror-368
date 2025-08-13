import asyncio
from typing import Annotated

from fastpluggy.core.tools.inspect_tools import InjectDependency

from fastpluggy_plugin.tasks_worker.task_registry import task_registry
from fastpluggy_plugin.tasks_worker.schema.context import TaskContext
from fastpluggy_plugin.tasks_worker.services.notification_service import TaskNotificationService


@task_registry.register()
async def sample_progress_task(context: Annotated[TaskContext, InjectDependency], i: int, delay: float = 1.0, ):
    from loguru import logger
    logger.info("Starting sample task...")
    for step in range(5):
        logger.info(f"[Task {i}] Step {step + 1}")
        await asyncio.sleep(delay)

        if context:
            TaskNotificationService.notify_progress(
                context,
                message=f"Completed step {step + 1}/5",
                percent=(step + 1) * 20,
                step=f"Step-{step + 1}"
            )

    return f"Task {i} complete"
