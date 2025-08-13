import time
from typing import Annotated

from loguru import logger
from fastpluggy_plugin.tasks_worker.task_registry import task_registry
from fastpluggy_plugin.tasks_worker.schema.context import TaskContext

from fastpluggy.core.tools.inspect_tools import InjectDependency


@task_registry.register(
    description="Sample task with locking logic",
    allow_concurrent=False,  # This flag is used by TaskLockManager
)
def locked_sample_task(context: Annotated[TaskContext, InjectDependency] ):
    task_name = context.task_name

    logger.info(f"Task {task_name} is locked")

    try:
        for i in range(15):
            logger.info(f"[{task_name}] Running... {i+1}/15")
            time.sleep(1)
        return f"{task_name} finished work!"
    finally:
        logger.info(f"Releasing lock for {task_name}")
