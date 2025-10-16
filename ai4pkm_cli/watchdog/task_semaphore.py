"""Global semaphore for task management concurrency control."""

import threading

# Global semaphore for all task operations (generation, processing, evaluation)
_task_semaphore = None
_semaphore_lock = threading.Lock()


def get_task_semaphore(config, logger):
    """
    Get or create the global task semaphore.
    
    Args:
        config: Config instance
        logger: Logger instance
        
    Returns:
        threading.Semaphore instance
    """
    global _task_semaphore, _semaphore_lock
    
    with _semaphore_lock:
        if _task_semaphore is None:
            max_concurrent = config.get_max_concurrent_tasks()
            _task_semaphore = threading.Semaphore(max_concurrent)
            logger.info(f"🎛️  Task Management: max concurrent operations = {max_concurrent}")
    
    return _task_semaphore

