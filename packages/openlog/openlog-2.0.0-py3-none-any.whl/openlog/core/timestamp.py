from datetime import datetime


class TimestampManager:
    """Handles timestamp generation and formatting."""

    def __init__(self, short_format: bool = False):
        """
        Initialize timestamp manager.

        Parameters:
            short_format (bool): If True, uses short format (HH:MM), otherwise full format.
        """
        self.short_format = short_format

    def get_timestamp(self) -> str:
        """
        Creates a formatted timestamp string.

        Returns:
            str: Current timestamp as a string. Format depends on short_format setting:
                 - If short_format is True: 'HH:MM'
                 - If short_format is False: 'YYYY-MM-DD HH:MM:SS'
        """
        timestamp = str(datetime.now()).split(".")[0]
        if self.short_format:
            time_part = timestamp.split(" ")[1]  # Get the time part (HH:MM:SS)
            return ":".join(time_part.split(":")[:2])  # Return only HH:MM
        return timestamp

    def get_file_timestamp(self) -> str:
        """
        Creates a timestamp suitable for filenames.

        Returns:
            str: Timestamp formatted for use in filenames.
        """
        return str(datetime.now()).replace(" ", "_").replace(":", "-")
