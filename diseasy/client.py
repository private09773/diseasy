"""The core Client class users instantiate. Ties together the gateway,
http, and state, and provides .event[]-style registration."""
import asyncio
from collections import defaultdict

from .flags import Intents
from .gateway import Gateway
from .http import HTTPClient
from .state import ConnectionState


class Client:
    def __init__(self, intents: list[str] | Intents | None = None):
        if isinstance(intents, list):
            intents = Intents.from_names(intents)
        self.intents = intents or Intents(0)
        self._listeners: dict[str, list] = defaultdict(list)
        # CHANGED: was ConnectionState(self.dispatch) — state.py now
        # needs the whole client (to reach self._http for interaction
        # responses), not just the bound dispatch method.
        self._state = ConnectionState(self)
        self._http: HTTPClient | None = None
        self._gateway: Gateway | None = None

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
            asyncio.ensure_future(callback(*args))

    async def start(self, token: str):
        self._http = HTTPClient(token)
        await self._http.start()
        gateway_data = await self._http.get_gateway_bot()
        self._gateway = Gateway(self, token, self.intents)
        await self._gateway.connect(gateway_data["url"] + "?v=10&encoding=json")

    def run(self, token: str):
        """Blocking entrypoint — starts the event loop and connects."""
        try:
            asyncio.run(self.start(token))
        except KeyboardInterrupt:
            pass

    async def close(self):
        if self._gateway:
            await self._gateway.close()
        if self._http:
            await self._http.close()
