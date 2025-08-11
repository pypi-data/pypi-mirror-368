import threading
import time
from typing import Dict, Optional
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, BarColumn
from rich.console import Console


class TaskManager:
    """Manages long-running tasks with progress bars."""

    def __init__(self, console: Console):
        """
        Initialize task manager.

        Parameters:
            console (Console): Rich console instance for output.
        """
        self.console = console
        self.tasks: Dict[str, Dict] = {}
        self.progress: Optional[Progress] = None
        self.progress_thread: Optional[threading.Thread] = None
        self._task_counter = 0
        self._lock = threading.Lock()

    def _generate_task_id(self) -> str:
        """Generate unique task ID."""
        with self._lock:
            self._task_counter += 1
            return f"task_{self._task_counter}"

    def _create_progress_bar(self):
        """Create and start progress bar display."""
        if self.progress is None:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
                console=self.console,
                transient=False
            )
            self.progress.start()

    def _stop_progress_bar(self):
        """Stop and cleanup progress bar."""
        if self.progress is not None:
            self.progress.stop()
            self.progress = None

    def add_task(self, task_message: str) -> str:
        """
        Add a new task and start displaying its progress.

        Parameters:
            task_message (str): Description of the task.

        Returns:
            str: Unique task ID for later reference.
        """
        task_id = self._generate_task_id()

        with self._lock:
            # Create progress bar if this is the first task
            if not self.tasks:
                self._create_progress_bar()

            # Add progress task
            if self.progress:
                progress_task_id = self.progress.add_task(
                    description=task_message,
                    total=None  # Indeterminate progress
                )

                self.tasks[task_id] = {
                    'message': task_message,
                    'progress_task_id': progress_task_id,
                    'start_time': time.time()
                }

        return task_id

    def stop_task(self, task_id: str) -> Optional[str]:
        """
        Stop a task and remove its progress bar.

        Parameters:
            task_id (str): ID of the task to stop.

        Returns:
            Optional[str]: Task message if task was found, None otherwise.
        """
        with self._lock:
            if task_id not in self.tasks:
                return None

            task_info = self.tasks[task_id]
            task_message = task_info['message']

            # Remove from progress bar
            if self.progress:
                self.progress.remove_task(task_info['progress_task_id'])

            # Remove from tasks
            del self.tasks[task_id]

            # Stop progress bar if no more tasks
            if not self.tasks:
                self._stop_progress_bar()

        return task_message

    def get_active_tasks(self) -> Dict[str, str]:
        """
        Get all currently active tasks.

        Returns:
            Dict[str, str]: Mapping of task IDs to task messages.
        """
        with self._lock:
            return {task_id: info['message'] for task_id, info in self.tasks.items()}

    def stop_all_tasks(self):
        """Stop all active tasks and cleanup."""
        with self._lock:
            for task_id in list(self.tasks.keys()):
                self.stop_task(task_id)
            self.tasks.clear()
            self._stop_progress_bar()
