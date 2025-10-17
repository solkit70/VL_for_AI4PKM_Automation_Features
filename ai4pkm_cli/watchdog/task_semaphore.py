"""Global semaphores for task management concurrency control."""

import threading

# Separate semaphores for generation vs execution/evaluation
_generation_semaphore = None
_execution_semaphore = None
_semaphore_lock = threading.Lock()


def get_generation_semaphore(config, logger):
    """
    Get or create the global task generation semaphore.

    Task generation (KTG) operates independently from execution to prevent
    long-running tasks from blocking new task creation.

    Args:
        config: Config instance
        logger: Logger instance

    Returns:
        threading.Semaphore instance
    """
    global _generation_semaphore, _semaphore_lock

    with _semaphore_lock:
        if _generation_semaphore is None:
            max_concurrent = config.get_max_concurrent_tasks()
            _generation_semaphore = threading.Semaphore(max_concurrent)
            logger.info(f"🎛️  Task Generation: max concurrent operations = {max_concurrent}")

    return _generation_semaphore


def get_execution_semaphore(config, logger):
    """
    Get or create the global task execution semaphore.

    Task execution (KTP) and evaluation share this semaphore to control
    overall processing load.

    Args:
        config: Config instance
        logger: Logger instance

    Returns:
        threading.Semaphore instance
    """
    global _execution_semaphore, _semaphore_lock

    with _semaphore_lock:
        if _execution_semaphore is None:
            max_concurrent = config.get_max_concurrent_tasks()
            _execution_semaphore = threading.Semaphore(max_concurrent)
            logger.info(f"🎛️  Task Execution: max concurrent operations = {max_concurrent}")

    return _execution_semaphore


def get_task_semaphore(config, logger):
    """
    Deprecated: Get execution semaphore for backward compatibility.

    New code should use get_generation_semaphore() or get_execution_semaphore()
    explicitly.

    Args:
        config: Config instance
        logger: Logger instance

    Returns:
        threading.Semaphore instance
    """
    return get_execution_semaphore(config, logger)

