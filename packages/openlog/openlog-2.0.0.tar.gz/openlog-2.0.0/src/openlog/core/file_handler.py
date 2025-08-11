import os
from typing import Optional

from .timestamp import TimestampManager


class FileHandler:
    """Handles file operations for logging."""

    def __init__(self, write_to_file: bool = False, in_dir: bool = False,
                 session: bool = False, timestamp_manager: Optional[TimestampManager] = None):
        """
        Initialize file handler.

        Parameters:
            write_to_file (bool): Enable file logging.
            in_dir (bool): Store logs in '/logs' directory.
            session (bool): Create unique log files with timestamps.
            timestamp_manager (TimestampManager): Timestamp manager instance.
        """
        self.write_to_file = write_to_file
        self.in_dir = in_dir
        self.session = session
        self.timestamp_manager = timestamp_manager or TimestampManager()

        self.path_prefix = ""
        if self.in_dir:
            self.path_prefix = "/logs"
            if not os.path.isdir(f"{os.getcwd()}/logs"):
                if self.write_to_file:
                    os.mkdir(f"{os.getcwd()}/logs")

        if self.session:
            self.log_file_path = (
                    os.getcwd()
                    + self.path_prefix
                    + "/log_"
                    + self.timestamp_manager.get_file_timestamp()
                    + ".txt"
            )
        else:
            self.log_file_path = os.getcwd() + self.path_prefix + "/log.txt"

        if self.write_to_file:
            self._initialize_log_file()

    def _initialize_log_file(self) -> None:
        """Initialize the log file with a header."""
        with open(self.log_file_path, "w+", encoding="utf-8") as file:
            file.write(
                f"-----------------------{self.timestamp_manager.get_timestamp()}-----------------------\n"
            )

    def write_to_file_if_enabled(self, content: str) -> None:
        """
        Write content to file if file logging is enabled.

        Parameters:
            content (str): Content to write to file.
        """
        if self.write_to_file:
            with open(self.log_file_path, "a+", encoding="utf-8") as file:
                file.write(content)
