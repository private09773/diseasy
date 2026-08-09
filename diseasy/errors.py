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


class ChannelCreationBlocked(DiseasyException):
    """
    Raised when the automatic anti-nuke guard blocks a channel
    creation attempt — either because it happened too soon after a
    previous one, or because the requested name matched a known
    spam/nuke naming pattern.
    """
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class MathError(DiseasyException):
    """
    Raised by diseasy.math_solver when an expression can't be parsed
    or solved — malformed input, an unsupported operation, or (by
    design) any attempted code-injection through the expression
    parser, which fails safely as a parse error rather than executing.
    """


class ConfigError(DiseasyException):
    """Base class for errors loading .env/config.json/config.yml/config.py."""


class ConfigFileNotFound(ConfigError):
    """
    Raised when a config or .env file doesn't exist at the given
    path. Distinct from Python's bare FileNotFoundError so it's
    clear the problem is specifically Diseasy's config loading, not
    some unrelated file operation.
    """
    def __init__(self, path: str):
        self.path = path
        super().__init__(
            f"Config file not found: '{path}'. Check the path is "
            f"correct and the file actually exists relative to where "
            f"the bot is being run from."
        )


class ConfigParseError(ConfigError):
    """
    Raised when a config file exists but couldn't be parsed — invalid
    JSON, invalid YAML, or a syntax error in a config.py file.
    """
    def __init__(self, path: str, original: Exception):
        self.path = path
        self.original = original
        super().__init__(
            f"Couldn't parse config file '{path}': "
            f"{type(original).__name__}: {original}"
        )


class MissingConfigKey(ConfigError):
    """
    Raised when a config file loaded successfully, but a required key
    (e.g. "token", "prefix") is missing from it.
    """
    def __init__(self, key: str, path: str = None):
        self.key = key
        self.path = path
        location = f" in '{path}'" if path else ""
        super().__init__(f"Missing required config key '{key}'{location}.")


class EnvVariableMissing(ConfigError):
    """
    Raised when a required environment variable (typically loaded via
    .env with python-dotenv) isn't set.
    """
    def __init__(self, var_name: str):
        self.var_name = var_name
        super().__init__(
            f"Environment variable '{var_name}' is not set. Add it to "
            f"your .env file, or set it directly in your environment."
        )


class CustomError(DiseasyException):
    """Base class for user-defined errors created via .customerror[]."""

    def __init__(self, name: str, message: str):
        self.name = name
        super().__init__(message)
