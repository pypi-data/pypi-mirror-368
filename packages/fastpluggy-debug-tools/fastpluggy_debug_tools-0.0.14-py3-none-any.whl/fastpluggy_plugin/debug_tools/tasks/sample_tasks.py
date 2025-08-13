import logging
import time

from loguru import logger

from fastpluggy_plugin.tasks_worker.task_registry import task_registry


@task_registry.register()
def sync_job(x, name=None):
    logging.info("Running sync job...")
    logger.info(f"Hello from loguru - {name}")
    return f"Sync result: {x} by {name}"


@task_registry.register()
async def async_job(x):
    import asyncio
    logger.info("Running async job...")
    await asyncio.sleep(1)
    return f"Async result: {x}"


@task_registry.register()
def failing_sync(x):
    logging.info("About to fail...")
    raise ValueError(f"Bad value: {x}")


@task_registry.register()
async def failing_async():
    logger.info("This will always fail")
    raise ValueError("Nope, still broken")


@task_registry.register(description='Flaky task')
def flaky_task(attempts_left=[2]):
    logging.info("Trying...")
    if attempts_left[0] > 0:
        attempts_left[0] -= 1
        raise RuntimeError("Temporary failure.")
    return "Succeeded!"


@task_registry.register()
async def sample_task(i: int, delay: float = 1.0):
    """
    Sample of task
    """
    logger.info("Starting sample task...")
    logger.info(f"Task {i}")
    logger.info(f"Delay {delay}")
    for x in range(5):
        logging.info(f"[Task {i}] Step {x + 1}")
        time.sleep(delay)
    return f"Task {i} complete"

@task_registry.register(
    description="Syncs data to remote",
    tags=["sync", "data"],
    schedule="*/5 * * * *",
    max_retries=3
)
def sync_data_task():
    """This task syncs data to the remote server."""
    ...
    print("Task sync_data_task running ...")