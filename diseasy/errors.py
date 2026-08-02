"""Exception hierarchy for Diseasy.

Maps onto the notation's .error_types["CommandNotFound", ...] list.
"""


class DiseasyException(Exception):
    """Base exception for anything raised by Diseasy."""


class GatewayError(DiseasyException):
    """Raised when the gateway connection fails or is closed unexpectedly."""


class HTTPException(DiseasyException):
    """Raised when a REST request to Discord's API fails."""

    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"HTTP {status}: {message}")


class CommandError(DiseasyException):
    """Base class for all command-related errors."""


class CommandNotFound(CommandError):
    pass


class MissingPermissions(CommandError):
    def __init__(self, missing: list[str]):
        self.missing = missing
        super().__init__(f"Missing permissions: {', '.join(missing)}")


class CommandOnCooldown(CommandError):
    def __init__(self, retry_after: float):
        self.retry_after = retry_after
        super().__init__(f"Command on cooldown, retry after {retry_after:.2f}s")


class BadArgument(CommandError):
    pass


class CheckFailure(CommandError):
    pass


class CustomError(DiseasyException):
    """Base class for user-defined errors created via .customerror[]."""

    def __init__(self, name: str, message: str):
        self.name = name
        super().__init__(message)
