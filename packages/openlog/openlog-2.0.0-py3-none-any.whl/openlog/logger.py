from typing import Any

from rich.console import Console

from .core.batch import MessageBatch
from .core.file_handler import FileHandler
from .core.formatter import MessageFormatter
from .core.object_formatter import ObjectFormatter
from .core.text_wrapper import TextWrapper
from .core.timestamp import TimestampManager
from .core.task_manager import TaskManager


class Logger:
    """
     A versatile logging utility that provides console output with color formatting
     and optional file logging capabilities.

     This logger uses Rich for console output with color formatting and can
     simultaneously write logs to files. It supports different log levels
     (INFO, ERROR, WARN, INIT), batch logging, task management with progress bars,
     and can maintain logs in memory for later retrieval.

     Features:
     - Color-coded console output
     - File logging with session support
     - Batch message processing
     - Long-running task tracking with progress bars
     - In-memory log storage and retrieval
     - Thread-safe operations
     """

    def __init__(self, write_to_file: bool = False, in_dir: bool = False,
                 session: bool = False, prefix: str = "", short_timestamp: bool = False):
        """
        Initialize a new Logger instance.

        Parameters:
            write_to_file (bool, optional): If True, writes logs to file in addition to
                                           console output. Defaults to False.
            in_dir (bool, optional): If True, logs will be stored in a '/logs' directory.
                                    Only takes effect when write_to_file is True.
                                    Defaults to False.
            session (bool, optional): If True, creates a unique log file for each session
                                     with timestamp in the filename. If False, uses a single
                                     'log.txt' file. Only takes effect when write_to_file is True.
                                     Defaults to False.
            prefix (str, optional): A prefix to add before each log message. Defaults to "".
            short_timestamp (bool, optional): If True, uses short timestamp format (HH:MM).
                                             If False, uses full timestamp format (YYYY-MM-DD HH:MM:SS).
                                             Defaults to False.
        """
        self.cls = Console()

        # Initialize core components
        self.timestamp_manager = TimestampManager(short_format=short_timestamp)
        self.file_handler = FileHandler(
            write_to_file=write_to_file,
            in_dir=in_dir,
            session=session,
            timestamp_manager=self.timestamp_manager
        )
        self.formatter = MessageFormatter(
            prefix=prefix,
            timestamp_manager=self.timestamp_manager
        )
        self.object_formatter = ObjectFormatter(self.cls)

        # Log storage for flush functionality
        self.log_list = []
        self.log_list_to_send = []

        # Batch functionality
        self.batch = MessageBatch()

        # Task management
        self.task_manager = TaskManager(self.cls)

    def _process_message(self, msg: Any) -> str:
        """
        Process message, converting objects to appropriate string representation.

        Parameters:
            msg: Message to process (can be string or any object).

        Returns:
            str: Processed message string.
        """
        if isinstance(msg, str):
            return msg

        # Get console width and calculate available space for message
        console_width = self.cls.size.width

        # Calculate actual prefix length more accurately
        # Create a temporary prefix to measure its visual length
        temp_prefix, _, visual_prefix_length = self.formatter.format_for_console("INFO")

        # Calculate available width after service part
        available_width = console_width - visual_prefix_length

        # Ensure we have reasonable minimum width
        if available_width < 20:
            available_width = 80

        # Check if object should be formatted vertically (using 50% threshold)
        if self.object_formatter.should_format_as_object(msg, available_width):
            # Pass available width to formatter for smart nested formatting
            if isinstance(msg, (list, tuple)):
                formatted_result = self.object_formatter._format_sequence(msg, available_width)
            elif isinstance(msg, dict):
                formatted_result = self.object_formatter._format_dict(msg, available_width)
            elif isinstance(msg, set):
                formatted_result = self.object_formatter._format_set(msg, available_width)
            else:
                formatted_result = self.object_formatter.format_object(msg)

            # Replace any remaining tabs with 2 spaces
            return formatted_result.replace('\t', '  ')
        else:
            # Convert to string normally
            return str(msg)

    def _echo(self, msg: Any, m_type: str) -> None:
        """
        Internal method to process and display log messages.

        This method handles both console output with appropriate color formatting
        and file writing if enabled. Automatically wraps long lines while maintaining
        proper indentation.

        Parameters:
            msg: The message content to log (can be string or any object).
            m_type (str): The message type/level (INFO, ERROR, WARN, INIT).

        Returns:
            None
        """
        # Process the message (convert objects to strings if needed)
        processed_msg = self._process_message(msg)

        # Handle file logging
        if self.file_handler.write_to_file:
            file_content = self.formatter.format_for_file(processed_msg, m_type)
            self.file_handler.write_to_file_if_enabled(file_content)

            self.log_list.append(file_content)
            self.log_list_to_send.append(file_content)

        # Handle console output
        console_prefix, plain_prefix, visual_prefix_length = self.formatter.format_for_console(m_type)

        # Get console width and calculate available space for message
        console_width = self.cls.size.width
        available_width = console_width - visual_prefix_length

        # Ensure we have reasonable minimum width
        if available_width < 20:
            available_width = 50

        # Process message lines with wrapping
        all_wrapped_lines = TextWrapper.process_message_lines(processed_msg, available_width)

        # Print first line with full prefix
        if all_wrapped_lines:
            self.cls.print(f"{console_prefix}{all_wrapped_lines[0]}")

            # Print subsequent lines with proper indentation
            if len(all_wrapped_lines) > 1:
                indent = " " * visual_prefix_length
                for line in all_wrapped_lines[1:]:
                    self.cls.print(f"{indent}{line}")

    def log(self, msg: Any):
        """
        Logs an informational message.

        Parameters:
            msg: The message to log (can be string or any object).

        Returns:
            None
        """
        self._echo(msg, "INFO")

    def error(self, msg: Any):
        """
        Logs an error message.

        Parameters:
            msg: The error message to log (can be string or any object).

        Returns:
            None
        """
        self._echo(msg, "ERROR")

    def warn(self, msg: Any):
        """
        Logs a warning message.

        Parameters:
            msg: The warning message to log (can be string or any object).

        Returns:
            None
        """
        self._echo(msg, "WARN")

    def init(self, msg: Any):
        """
        Logs an initialization message.

        Parameters:
            msg: The initialization message to log (can be string or any object).

        Returns:
            None
        """
        self._echo(msg, "INIT")

    def add_to_batch(self, msg: str) -> None:
        """
        Add a message to the batch without immediately logging it.

        Parameters:
            msg (str): The message to add to the batch.

        Returns:
            None
        """
        self.batch.add_message(msg)

    def flush_batch(self, m_type: str = "INFO") -> None:
        """
        Flush all batched messages as a single log entry.

        Parameters:
            m_type (str, optional): The message type for the batched output.
                                   Defaults to "INFO".

        Returns:
            None
        """
        if not self.batch.is_empty():
            batched_message = self.batch.get_batched_message()
            self._echo(batched_message, m_type)
            self.batch.clear()

    def clear_batch(self) -> None:
        """
        Clear the batch without logging.

        Returns:
            None
        """
        self.batch.clear()

    def batch_size(self) -> int:
        """
        Get the number of messages currently in the batch.

        Returns:
            int: Number of messages in the batch.
        """
        return self.batch.size()

    def add_task(self, task_message: str) -> str:
        """
        Start a new long-running task with progress display.

        Logs a start message and displays a progress bar at the bottom of the terminal.

        Parameters:
            task_message (str): Description of the task being started.

        Returns:
            str: Unique task ID for later reference when stopping the task.
        """
        # Log the task start
        self.log(f"Started --> {task_message}")

        # Start progress bar
        task_id = self.task_manager.add_task(task_message)

        return task_id

    def stop_task(self, task_id: str) -> bool:
        """
        Stop a long-running task and remove its progress display.

        Logs a completion message and removes the progress bar.

        Parameters:
            task_id (str): ID of the task to stop (returned by add_task).

        Returns:
            bool: True if task was found and stopped, False otherwise.
        """
        # Stop the task and get its message
        task_message = self.task_manager.stop_task(task_id)

        if task_message is not None:
            # Log the task completion
            self.log(f"Completed --> {task_message}")
            return True

        return False

    def get_active_tasks(self) -> dict:
        """
        Get information about all currently active tasks.

        Returns:
            dict: Mapping of task IDs to task messages.
        """
        return self.task_manager.get_active_tasks()

    def stop_all_tasks(self) -> None:
        """
        Stop all active tasks and cleanup progress displays.

        This method is useful for cleanup when shutting down the logger.
        """
        active_tasks = self.task_manager.get_active_tasks()

        # Log completion for all active tasks
        for task_id, task_message in active_tasks.items():
            self.log(f"Completed --> {task_message}")

        # Stop all tasks
        self.task_manager.stop_all_tasks()

    def flush_logs(self, from_start: bool = False) -> list:
        """
        Retrieves and clears the pending log messages.

        Parameters:
            from_start (bool, optional): If True, returns all logs since logger
                                        initialization. If False, returns only logs
                                        since the last flush. Defaults to False.

        Returns:
            list: A list of log message strings.
        """
        if from_start:
            self.log_list_to_send = self.log_list.copy()
        log_list = self.log_list_to_send.copy()
        self.log_list_to_send = []
        return log_list
