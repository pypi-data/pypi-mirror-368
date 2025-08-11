from typing import List


class MessageBatch:
    """Handles message batching functionality."""

    def __init__(self):
        """Initialize message batch."""
        self.messages: List[str] = []

    def add_message(self, msg: str) -> None:
        """
        Add a message to the batch.

        Parameters:
            msg (str): Message to add to the batch.
        """
        self.messages.append(msg)

    def get_batched_message(self) -> str:
        """
        Get all messages as a single string with newlines between them.

        Returns:
            str: All batched messages joined with newlines.
        """
        return '\n'.join(self.messages)

    def clear(self) -> None:
        """Clear the batch."""
        self.messages = []

    def is_empty(self) -> bool:
        """
        Check if batch is empty.

        Returns:
            bool: True if batch is empty.
        """
        return len(self.messages) == 0

    def size(self) -> int:
        """
        Get the number of messages in the batch.

        Returns:
            int: Number of messages in the batch.
        """
        return len(self.messages)
