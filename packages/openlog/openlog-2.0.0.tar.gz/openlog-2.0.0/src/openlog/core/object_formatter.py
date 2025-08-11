from typing import Any, Union, List, Dict, Tuple

from rich.console import Console
from rich.pretty import Pretty


class ObjectFormatter:
    """Handles formatting of complex objects for logging."""

    def __init__(self, console: Console):
        """
        Initialize object formatter.

        Parameters:
            console (Console): Rich console instance for rendering.
        """
        self.console = console

    def should_format_as_object(self, obj: Any, available_width: int) -> bool:
        """
        Determine if an object should be formatted vertically.

        Parameters:
            obj: Object to check.
            available_width (int): Available width for display after service part.

        Returns:
            bool: True if object should be formatted vertically.
        """
        # Check if it's a complex object type
        if isinstance(obj, (list, dict, tuple, set)):
            # Convert to string representation to check length
            str_repr = str(obj)
            # Use 50% of available width as threshold
            threshold = available_width * 0.5
            return len(str_repr) > threshold

        return False

    def _should_format_nested_inline(self, obj: Any, available_width: int) -> bool:
        """
        Determine if a nested object should be formatted inline.

        Parameters:
            obj: Object to check.
            available_width (int): Available width for display.

        Returns:
            bool: True if object should be formatted inline.
        """
        if isinstance(obj, (list, dict, tuple, set)):
            str_repr = str(obj)
            # Use 20% of available width as threshold for nested objects
            threshold = available_width * 0.2
            return len(str_repr) <= threshold
        return True

    def format_object(self, obj: Any) -> str:
        """
        Format an object for vertical display using Rich.

        Parameters:
            obj: Object to format.

        Returns:
            str: Formatted string representation with 2-space indentation.
        """
        if isinstance(obj, (list, tuple)):
            return self._format_sequence(obj)
        elif isinstance(obj, dict):
            return self._format_dict(obj)
        elif isinstance(obj, set):
            return self._format_set(obj)
        else:
            # For other objects, use Rich's pretty printing
            with self.console.capture() as capture:
                self.console.print(Pretty(obj, expand_all=True))
            result = capture.get().strip()
            # Replace tabs with 2 spaces
            return result.replace('\t', '  ')

    def _format_sequence(self, seq: Union[List, Tuple], available_width: int = 80) -> str:
        """Format list or tuple with 2-space indentation."""
        opening = "[" if isinstance(seq, list) else "("
        closing = "]" if isinstance(seq, list) else ")"

        if not seq:
            return f"{opening}{closing}"

        lines = [opening]

        for i, item in enumerate(seq):
            is_last = i == len(seq) - 1
            comma = "" if is_last else ","

            if isinstance(item, (list, dict, tuple, set)):
                # Check if nested object should be inline
                if self._should_format_nested_inline(item, available_width):
                    # Format inline
                    formatted_item = str(item)
                    lines.append(f"  {formatted_item}{comma}")
                else:
                    # Format vertically
                    nested_formatted = self.format_object(item)
                    # Use 2-space indentation
                    indented_nested = "\n".join(f"  {line}" for line in nested_formatted.split("\n"))
                    lines.append(f"  {indented_nested}{comma}")
            else:
                # Simple item
                formatted_item = repr(item) if isinstance(item, str) else str(item)
                lines.append(f"  {formatted_item}{comma}")

        lines.append(closing)
        return "\n".join(lines)

    def _format_dict(self, d: Dict, available_width: int = 80) -> str:
        """Format dictionary with 2-space indentation and smart nested formatting."""
        if not d:
            return "{}"

        lines = ["{"]

        items = list(d.items())
        for i, (key, value) in enumerate(items):
            is_last = i == len(items) - 1
            comma = "" if is_last else ","

            key_repr = repr(key) if isinstance(key, str) else str(key)

            if isinstance(value, (list, dict, tuple, set)):
                # Check if nested object should be inline
                if self._should_format_nested_inline(value, available_width):
                    # Format inline
                    value_str = str(value)
                    lines.append(f"  {key_repr}: {value_str}{comma}")
                else:
                    # Format vertically
                    nested_formatted = self.format_object(value)
                    nested_lines = nested_formatted.split("\n")

                    # First line goes right after the colon
                    lines.append(f"  {key_repr}: {nested_lines[0]}")

                    # Subsequent lines get proper indentation
                    for line in nested_lines[1:]:
                        lines.append(f"  {line}")

                    # Add comma to the last line if needed
                    if comma and lines:
                        lines[-1] += comma
            else:
                # Simple value
                value_repr = repr(value) if isinstance(value, str) else str(value)
                lines.append(f"  {key_repr}: {value_repr}{comma}")

        lines.append("}")
        return "\n".join(lines)

    def _format_set(self, s: set, available_width: int = 80) -> str:
        """Format set with 2-space indentation."""
        if not s:
            return "set()"

        lines = ["{"]

        items = list(s)
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            comma = "" if is_last else ","

            if isinstance(item, (list, dict, tuple, set)):
                # Check if nested object should be inline
                if self._should_format_nested_inline(item, available_width):
                    # Format inline
                    formatted_item = str(item)
                    lines.append(f"  {formatted_item}{comma}")
                else:
                    # Format vertically
                    nested_formatted = self.format_object(item)
                    # Use 2-space indentation
                    indented_nested = "\n".join(f"  {line}" for line in nested_formatted.split("\n"))
                    lines.append(f"  {indented_nested}{comma}")
            else:
                # Simple item
                formatted_item = repr(item) if isinstance(item, str) else str(item)
                lines.append(f"  {formatted_item}{comma}")

        lines.append("}")
        return "\n".join(lines)
