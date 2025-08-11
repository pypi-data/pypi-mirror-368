import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import dramatiq

from .progress import TaskProgressNotifier


class QueuedTaskHandler(ABC):
    """Base class for handling queued tasks."""

    _task_worker: Any

    def __init__(self, task_type: str):
        self.task_type = task_type
        self.progress_notifier = TaskProgressNotifier()

    @abstractmethod
    async def handle_task(self, task_id: str, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Handle the specific queued task.

        Args:
            task_id: Task ID
            user_id: User ID
            **kwargs: Task parameters

        Returns:
            Task result dict
        """
        pass

    async def notify_task_progress(
        self,
        task_id: str,
        progress_percent: int,
        message: str,
        user_id: str,
        database_id: Optional[str] = None,
        **extra_data,
    ):
        """Send notification about task progress."""
        await self.progress_notifier.notify(
            task_id=task_id,
            progress_percent=progress_percent,
            message=message,
            user_id=user_id,
            database_id=database_id,
            **extra_data,
        )


def queued_task(
    *,
    queue_name: str = "default",
    max_retries: int = 3,
    min_backoff: int = 15000,
    max_backoff: int = 300000,
    **dramatiq_options,
):
    """
    Decorator to create a queued task.

    Args:
        queue_name: Task queue name
        max_retries: Maximum number of retries
        min_backoff: Minimum backoff time (milliseconds)
        max_backoff: Maximum backoff time (milliseconds)
        **dramatiq_options: Other options for Dramatiq actor
    """

    def decorator(handler_class: type[QueuedTaskHandler]):
        handler = handler_class(task_type=handler_class.__name__)

        @dramatiq.actor(
            queue_name=queue_name,
            max_retries=max_retries,
            min_backoff=min_backoff,
            max_backoff=max_backoff,
            actor_name=f"{handler.task_type}_worker",
            store_results=True,  # Enable result storage
            **dramatiq_options,
        )
        async def task_worker(
            task_id: Optional[str] = None, user_id: Optional[str] = None, **kwargs
        ):
            """Dramatiq task worker"""
            if task_id is None:
                task_id = str(uuid.uuid4())

            if not user_id:
                user_id = "anonymous"

            try:
                await handler.notify_task_progress(
                    task_id, 0, f"Task {handler.task_type} started", user_id
                )

                result = await handler.handle_task(task_id, user_id, **kwargs)

                await handler.notify_task_progress(
                    task_id, 100, f"Task {handler.task_type} completed", user_id
                )

                return result

            except Exception as e:
                await handler.notify_task_progress(
                    task_id, -1, f"Task {handler.task_type} failed: {str(e)}", user_id
                )
                raise

        # Use the task type as the function name to avoid conflicts
        task_worker.__name__ = f"{handler.task_type}_worker"

        # Attach the task worker to the handler class
        handler_class._task_worker = task_worker
        return handler_class

    return decorator
