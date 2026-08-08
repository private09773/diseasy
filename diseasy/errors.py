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


class CommandNeverLoaded(CommandError):
    """
    Raised when a command name is invoked (by message or interaction)
    but was never registered with the bot — neither as a standalone
    command nor inside any loaded cog. This is different from a
    command that exists but fails when run: this means the bot never
    knew about it in the first place.

    Common causes: a cog file exists but was never passed to
    load_extension()/load_all_extensions(), a typo in the command
    name at the call site vs. its @command(name=...) definition, or
    a cog's setup(bot) function forgot to call bot.load_cog(...).
    """
    def __init__(self, command_name: str):
        self.command_name = command_name
        super().__init__(
            f"Command '{command_name}' was invoked but was never loaded. "
            f"Check that its cog is included in your cogs = [] list (or "
            f"passed to load_extension/load_all_extensions), and that the "
            f"command name matches exactly."
        )


class CommandDoesntWork(CommandError):
    """
    Raised when a registered command WAS found and invoked, but
    raised an exception while running. Wraps the original exception
    so both the command name and the real cause are available.

    Different from CommandNeverLoaded: this means the bot found and
    ran the command — something inside the command's own code failed.
    """
    def __init__(self, command_name: str, original: Exception):
        self.command_name = command_name
        self.original = original
        super().__init__(
            f"Command '{command_name}' was found and run, but raised an "
            f"error: {type(original).__name__}: {original}"
        )


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
