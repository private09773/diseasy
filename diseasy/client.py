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
        self._loop: asyncio.AbstractEventLoop | None = None

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
        Stores a reference to the running event loop (self._loop) —
        needed so anything outside the bot's own thread (like the
        dashboard's Flask server, running in a background thread) can
        safely schedule work onto it via
        asyncio.run_coroutine_threadsafe(), instead of touching bot
        state directly from a different thread.
        """
        self._loop = asyncio.get_running_loop()
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
        if self._gateway:
            await self._gateway.close()
        if self._http:
            await self._http.close()
        log_offline("closed")
