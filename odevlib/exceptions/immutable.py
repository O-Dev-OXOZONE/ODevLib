from typing import Optional


class ImmutableException(Exception):
    """
    Raised when attempted to modify immutable resource.
    """

    def __init__(self, message: str, ui_message: Optional[str] = None):
        super().__init__(message)
        self.ui_message = ui_message
