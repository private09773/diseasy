"""
diseasy/logger.py (v0.2.3)

Builds on the v0.1.1a auto-initializing logger. Adds:
  - safe_dispatch(): wraps event/command callback execution so
    exceptions are caught and logged clearly, instead of vanishing
    into asyncio's "Task exception was never retrieved" warnings
    (which happens today because Client.dispatch() uses
    asyncio.ensure_future() with nothing watching for failures).
  - friendly_error(): translates common Python exceptions into
    plain-language messages for beginners, instead of a raw
    traceback being the first thing they see.
  - log_online()/log_offline(): consistent connection-status
    messages, called from Bot's on_ready listener and gateway close.

DEPENDENCY NOTE: safe_dispatch() is new and not yet wired into
client.py — Client.dispatch() currently does
`asyncio.ensure_future(callback(*args))` directly. For errors to
actually get caught by this module, dispatch() needs to wrap each
callback with safe_dispatch() instead. That's the next file to
touch after this one.
"""

import logging
import sys
import traceback

_initialized = False
log = logging.getLogger("diseasy")


def _init_logging(level=logging.INFO):
    global _initialized
    if _initialized:
        return log

    log.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] diseasy: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    log.addHandler(handler)
    _initialized = True
    return log


def set_log_level(level):
    log.setLevel(level)


def log_online(bot_name: str, guild_count: int = 0):
    """Single consistent 'bot is online' message — called from Bot's
    on_ready listener instead of each project writing its own."""
    log.info(f"✅ Online as {bot_name} — connected to {guild_count} guild(s)")


def log_offline(reason: str = ""):
    """Called when the gateway connection drops or closes."""
    suffix = f": {reason}" if reason else ""
    log.warning(f"⚠️ Disconnected from Discord{suffix}")


# --- Beginner-friendly error translation -----------------------------

_FRIENDLY_MESSAGES = {
    TypeError: (
        "This usually means a command is missing an argument, or was "
        "given the wrong number of them. Check the command's function "
        "signature against how it was called."
    ),
    AttributeError: (
        "Something tried to use a property or method that doesn't "
        "exist on that object. Double-check spelling and that the "
        "object is the type you expect."
    ),
    KeyError: (
        "A dictionary lookup failed — the key you asked for isn't "
        "there. Check option names, environment variable names, or "
        "config keys for typos."
    ),
    NameError: (
        "Something was used before it was defined — check that "
        "variables, functions, or imports exist before they're "
        "referenced."
    ),
    ValueError: (
        "A value was the wrong shape or type for what was expected — "
        "check what's being passed in."
    ),
}


def friendly_error(exc: Exception) -> str:
    """
    Returns a plain-language explanation for a common exception type,
    or a generic fallback for anything not in the map above.
    """
    exc_type = type(exc)
    hint = _FRIENDLY_MESSAGES.get(exc_type)
    base = f"{exc_type.__name__}: {exc}"
    if hint:
        return f"{base}\n    → {hint}"
    return base


async def safe_dispatch(callback, *args):
    """
    Runs an event/command callback and catches any exception,
    logging it clearly (with the friendly hint where available) and
    the real traceback at DEBUG level for anyone who needs the full
    detail, instead of letting it vanish or crash the bot.
    """
    try:
        await callback(*args)
    except Exception as e:
        log.error(f"Error in '{getattr(callback, '__name__', 'callback')}': "
                   f"{friendly_error(e)}")
        log.debug("Full traceback:\n" + "".join(
            traceback.format_exception(type(e), e, e.__traceback__)
        ))
