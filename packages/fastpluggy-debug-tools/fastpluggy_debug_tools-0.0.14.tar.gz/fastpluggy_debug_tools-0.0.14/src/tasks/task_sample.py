import time
from typing import Annotated

from loguru import logger

from fastpluggy.core.tools.inspect_tools import InjectDependency

from fastpluggy_plugin.tasks_worker.schema.context import TaskContext


def some_task_function(context: Annotated[TaskContext, InjectDependency], task_input: dict = None):
    logger.info("Starting some_task_function execution.")
    context.log_context({"input": task_input})

    # Simulate task steps
    for i in range(1, 6):
        time.sleep(1)  # Simulate work
        logger.info(f"Processing step {i}")
        context.log_context({"step": i, "progress": f"{i * 20}%"})

    logger.info("Task execution completed.")
    context.log_context({"result": "success"})
    return "Task completed!"


def some_task_exception():
    logger.info("Starting some_task_exception execution.")

    raise Exception("Some Exception")


def some_task_function_loguru(task_input: dict = None):
    """
    Execute a task and log progress using loguru.

    Args:
        task_input (dict): Input data for the task.

    Returns:
        str: Task result message.
    """
    logger.info("Starting some_task_function_loguru execution.")
    logger.debug(f"Task input: {task_input}")

    # Simulate task steps
    for i in range(1, 6):
        time.sleep(1)  # Simulate work
        logger.info(f"Processing step {i}")
        logger.debug(f"Step {i}: Progress: {i * 20}%")

    logger.info("Task execution completed.")
    logger.debug("Result: success")
    return "Task completed!"
