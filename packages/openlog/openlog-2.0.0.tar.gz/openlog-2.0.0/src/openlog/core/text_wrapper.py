from typing import List


class TextWrapper:
    """Handles text wrapping functionality."""

    @staticmethod
    def wrap_text(text: str, width: int) -> List[str]:
        """
        Wraps text to specified width, breaking on word boundaries when possible.

        Parameters:
            text (str): Text to wrap.
            width (int): Maximum width for each line.

        Returns:
            List[str]: List of wrapped lines.
        """
        if len(text) <= width:
            return [text]

        lines = []
        words = text.split(' ')
        current_line = ""

        for word in words:
            # If adding this word would exceed width
            if len(current_line) + len(word) + 1 > width:
                if current_line:  # If we have content in current line
                    lines.append(current_line)
                    current_line = word
                else:  # Word itself is longer than width
                    lines.append(word)
                    current_line = ""
            else:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word

        if current_line:
            lines.append(current_line)

        return lines

    @staticmethod
    def process_message_lines(msg: str, available_width: int) -> List[str]:
        """
        Process message by splitting on newlines and wrapping each line.

        Parameters:
            msg (str): Message to process.
            available_width (int): Available width for wrapping.

        Returns:
            List[str]: List of processed lines.
        """
        message_lines = msg.split('\n')
        all_wrapped_lines = []

        for line in message_lines:
            if line.strip():  # If line has content
                wrapped_lines = TextWrapper.wrap_text(line, available_width)
                all_wrapped_lines.extend(wrapped_lines)
            else:  # Empty line
                all_wrapped_lines.append("")

        return all_wrapped_lines
