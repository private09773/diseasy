"""The core Client class users instantiate. Ties together the gateway,
http, and state, and provides .event[]-style registration."""
import asyncio
from collections import defaultdict

from .flags import Intents
from .gateway import Gateway
from .http import HTTPClient
from .state import ConnectionState
from .logger import log, log_online, log_offline, safe_dispatch


class Client:
    def __init__(self, intents: list[str] | Intents | None = None):
        if isinstance(intents, list):
            intents = Intents.from_names(intents)
        self.intents = intents or Intents(0)
        self._listeners: dict[str, list] = defaultdict(list)
        self._state = ConnectionState(self)
        self._http: HTTPClient | None = None
        self._gateway: Gateway | None = None

        @self.event(name="on_ready")
        async def _log_ready(*args):
            guild_count = len(getattr(self._state, "guilds", {}))
            bot_name = getattr(getattr(self, "user", None), "name", "bot")
            log_online(bot_name, guild_count)

    def event(self, name: str):
        """Decorator: @client.event(name="on_message") to register a raw
        gateway-style event handler."""
        def decorator(func):
            event_key = name.removeprefix("on_")
            self._listeners[event_key].append(func)
            return func
        return decorator

    def dispatch(self, event_name: str, *args):
        for callback in self._listeners.get(event_name, []):
            asyncio.ensure_future(safe_dispatch(callback, *args))

    async def start(self, token: str):
        """
        CHANGED (v0.2.4ab): wrapped in try/finally so self._http and
        self._gateway are ALWAYS closed, even if the gateway
        connection drops unexpectedly or raises mid-session. This is
        what was causing the "Unclosed client session" warnings —
        previously, any exception during connect()/the receive loop
        left both aiohttp sessions dangling with nothing to close them.
        """
        self._http = HTTPClient(token)
        await self._http.start()
        try:
            gateway_data = await self._http.get_gateway_bot()
            self._gateway = Gateway(self, token, self.intents)
            await self._gateway.connect(gateway_data["url"] + "?v=10&encoding=json")
        except Exception as e:
            log_offline(str(e))
            raise
        finally:
            await self.close()

    def run(self, token: str):
        """Blocking entrypoint — starts the event loop and connects."""
        try:
            asyncio.run(self.start(token))
        except KeyboardInterrupt:
            pass
        except Exception as e:
            log.error(f"Diseasy failed to start: {e}")
            raise

    async def close(self):
        """
        CHANGED (v0.2.4ab): now safe to call multiple times (e.g. once
        from start()'s finally block, and again if the user calls it
        manually) — each check guards against a None or already-closed
        resource instead of assuming both exist.
        """
        if self._gateway:
            await self._gateway.close()
        if self._http:
            await self._http.close()
        log_offline("closed")
