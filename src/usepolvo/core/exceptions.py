class PolvoError(Exception):
    """Base exception class for all usepolvo errors."""

    def __init__(self, message: str = "An error occurred"):
        self.message = message
        super().__init__(self.message)


class AuthenticationError(PolvoError):
    """Exception raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)


class APIError(PolvoError):
    """Exception raised when an API request fails."""

    def __init__(self, message: str = "API request failed"):
        super().__init__(message)
