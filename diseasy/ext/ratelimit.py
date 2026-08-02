"""Command cooldowns: .ratelimit[scope=, rate=, per=], .ratelimit_bucket(),
.on_ratelimit()"""
import time


class Cooldown:
    def __init__(self, *, scope: str = "user", rate: int = 1, per: float = 5.0):
        self.scope = scope
        self.rate = rate
        self.per = per
        self._buckets: dict[str, list[float]] = {}

    def ratelimit_bucket(self, ctx) -> str:
        """Builds the bucket key based on scope: global/guild/user/channel."""
        if self.scope == "global":
            return "global"
        if self.scope == "guild":
            return f"guild:{ctx.guild_id}"
        if self.scope == "channel":
            return f"channel:{ctx.channel_id}"
        return f"user:{ctx.author.id}"

    def check(self, ctx) -> float | None:
        """Returns retry_after in seconds if on cooldown, else None."""
        key = self.ratelimit_bucket(ctx)
        now = time.monotonic()
        window = self._buckets.setdefault(key, [])
        window[:] = [t for t in window if now - t < self.per]
        if len(window) >= self.rate:
            return self.per - (now - window[0])
        window.append(now)
        return None
