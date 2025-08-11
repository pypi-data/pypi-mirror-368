from typing import Dict

from .timestamp import TimestampManager


class MessageFormatter:
    """Handles message formatting for console and file output."""

    COLOR_CODES: Dict[str, str] = {
        "INFO": "blue bold",
        "ERROR": "red bold",
        "WARN": "yellow bold",
        "INIT": "purple bold"
    }

    def __init__(self, prefix: str = "", timestamp_manager: TimestampManager = None):
        """
        Initialize message formatter.

        Parameters:
            prefix (str): Prefix to add to messages.
            timestamp_manager (TimestampManager): Timestamp manager instance.
        """
        self.prefix = prefix
        self.timestamp_manager = timestamp_manager or TimestampManager()

    def format_for_file(self, msg: str, m_type: str) -> str:
        """
        Format message for file output.

        Parameters:
            msg (str): Message content.
            m_type (str): Message type.

        Returns:
            str: Formatted message for file.
        """
        timestamp = self.timestamp_manager.get_timestamp()
        if self.prefix:
            return f"[{timestamp}]::[{self.prefix}]::{m_type}::{msg}\n"
        else:
            return f"[{timestamp}]::{m_type}::{msg}\n"

    def format_for_console(self, m_type: str) -> tuple[str, str, int]:
        """
        Format prefix for console output.

        Parameters:
            m_type (str): Message type.

        Returns:
            tuple: (console_prefix_with_markup, plain_prefix, visual_length)
        """
        timestamp_str = self.timestamp_manager.get_timestamp()
        color_code = self.COLOR_CODES.get(m_type, "white bold")

        if self.prefix:
            # Format: [timestamp]::[prefix]::TYPE::
            plain_prefix = f"[{timestamp_str}]::[{self.prefix}]::{m_type}::"
            console_prefix = f"[steel_blue][{timestamp_str}][/][red bold]::[/][green bold][{self.prefix}][/][red bold]::[/][{color_code}]{m_type}[/][red bold]::[/]"
        else:
            # Format: [timestamp]::TYPE::
            plain_prefix = f"[{timestamp_str}]::{m_type}::"
            console_prefix = f"[steel_blue][{timestamp_str}][/][red bold]::[/][{color_code}]{m_type}[/][red bold]::[/]"

        return console_prefix, plain_prefix, len(plain_prefix)
