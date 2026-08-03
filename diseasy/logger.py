"""
diseasy/logger.py (v0.1.1a)

Logging is now fully automatic — Client.__init__ calls
_init_logging() itself. Users no longer need to import log or call
setup_logging() manually; it's already active the moment a Client
or Bot is instantiated.
"""

import logging
import sys

_initialized = False
log = logging.getLogger("diseasy")


def _init_logging(level=logging.INFO):
    """
    Called automatically by Client.__init__. Safe to call multiple
    times — only configures handlers once.
    """
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
    """Still available for users who want to override the default level."""
    log.setLevel(level)
