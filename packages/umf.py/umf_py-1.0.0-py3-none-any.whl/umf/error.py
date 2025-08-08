"""UMF parsing error."""


class UMFError(Exception):
    """The UMF parsing error."""

    def __init__(self, message: str, line: int = None, line_content: str = None):
        """Initialize the UMF error.

        Args:
            message: The error message
            line: The line number where the error occurred
            line_content: The content of the line where the error occurred
        """
        super().__init__(message)

        self.name = "UMFParseError"

        if line is not None:
            self.args = (f"{message} at line {line}",)

            if line_content is not None:
                self.args = (f'{message} at line {line}: "{line_content}"',)
        else:
            self.args = (message,)
