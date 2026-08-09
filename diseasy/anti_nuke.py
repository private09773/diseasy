"""
diseasy/anti_nuke.py (v0.2.4)

Guards against nuke-bot-style channel creation abuse:

  1. Interval detection — flags a channel creation if it happens
     less than `min_interval_seconds` (default: 5s) after the
     previous one in the same guild. Nuke bots create channels in
     rapid succession (often sub-second); a legitimate admin
     creating channels by hand won't hit this.
  2. Name pattern validation — rejects channel names matching known
     spam/nuke patterns (random alphanumeric strings, repeated
     characters, common nuke-bot naming templates).

Both checks are combined in ChannelGuard.check(), which raises
ChannelCreationBlocked with a specific reason if either check fails.

Active automatically — no setup required. interaction.create_channel()
uses get_default_guard() internally.
"""

import re
import time
from collections import defaultdict

from .errors import ChannelCreationBlocked


_SUSPICIOUS_PATTERNS = [
    re.compile(r"^[a-z0-9]{16,}$", re.IGNORECASE),       # long random string
    re.compile(r"(.)\1{5,}"),                             # 6+ repeated chars in a row
    re.compile(r"nuke[d]?", re.IGNORECASE),
    re.compile(r"^channel[-_]?\d{3,}$", re.IGNORECASE),   # channel-0001, channel_00001, etc.
]


class ChannelGuard:
    def __init__(self, min_interval_seconds: float = 5.0, extra_patterns: list = None):
        self.min_interval_seconds = min_interval_seconds
        self.patterns = list(_SUSPICIOUS_PATTERNS)
        if extra_patterns:
            self.patterns.extend(re.compile(p, re.IGNORECASE) for p in extra_patterns)
        # guild_id -> timestamp of the last recorded creation
        self._last_creation: dict[int, float] = {}

    def _check_interval(self, guild_id: int) -> None:
        last = self._last_creation.get(guild_id)
        if last is None:
            return  # first creation ever seen for this guild — nothing to compare
        elapsed = time.monotonic() - last
        if elapsed < self.min_interval_seconds:
            raise ChannelCreationBlocked(
                f"Channel created too quickly after the last one "
                f"({elapsed:.2f}s < {self.min_interval_seconds}s minimum) — "
                f"possible nuke-bot activity."
            )

    def _check_name_pattern(self, channel_name: str) -> None:
        for pattern in self.patterns:
            if pattern.search(channel_name):
                raise ChannelCreationBlocked(
                    f"Channel name '{channel_name}' matched a blocked pattern "
                    f"({pattern.pattern})."
                )

    def check(self, guild_id: int, channel_name: str) -> None:
        """
        Raises ChannelCreationBlocked if either the interval check or
        the name pattern check fails. Does nothing if creation is
        allowed.
        """
        self._check_interval(guild_id)
        self._check_name_pattern(channel_name)

    def record_creation(self, guild_id: int) -> None:
        """Call this AFTER a channel is actually successfully created,
        so the interval check has something to compare against next time."""
        self._last_creation[guild_id] = time.monotonic()


# --- Automatic default guard ---------------------------------------
# No setup required — interaction.create_channel() uses this
# automatically. Import ChannelGuard yourself only to customize the
# interval or patterns.

_default_guard = ChannelGuard()


def get_default_guard() -> ChannelGuard:
    return _default_guard


def set_default_guard(guard: ChannelGuard) -> None:
    """e.g. diseasy.anti_nuke.set_default_guard(ChannelGuard(min_interval_seconds=10))"""
    global _default_guard
    _default_guard = guard
