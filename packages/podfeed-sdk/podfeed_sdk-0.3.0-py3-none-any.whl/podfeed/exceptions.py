"""Exceptions for the Podfeed SDK."""


class PodfeedError(Exception):
    """Base exception for Podfeed SDK errors."""

    pass


class PodfeedAuthError(PodfeedError):
    """Exception raised for authentication-related errors."""

    pass


class PodfeedAPIError(PodfeedError):
    """Exception raised for API-related errors."""

    def __init__(self, message: str, status_code: int = None, error_code: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
