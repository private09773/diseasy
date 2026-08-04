"""REST wrapper: request(), routes, and per-route rate-limit locking.
Corresponds to the notation's HTTP side of things (sending messages,
registering slash commands, etc.)."""
import asyncio

import aiohttp

API_BASE = "https://discord.com/api/v10"


class Route:
    def __init__(self, method: str, path: str, **params):
        self.method = method
        self.path = path.format(**params)
        self.url = API_BASE + self.path


class HTTPClient:
    def __init__(self, token: str):
        self.token = token
        self._session: aiohttp.ClientSession | None = None
        self._locks: dict[str, asyncio.Lock] = {}

    async def start(self):
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Bot {self.token}"}
        )

    async def close(self):
        if self._session:
            await self._session.close()

    def _lock_for(self, route: Route) -> asyncio.Lock:
        self._locks.setdefault(route.path, asyncio.Lock())
        return self._locks[route.path]

    async def request(self, route: Route, **kwargs):
        from .errors import HTTPException
        async with self._lock_for(route):
            async with self._session.request(route.method, route.url, **kwargs) as resp:
                data = await resp.json(content_type=None)
                if resp.status >= 400:
                    raise HTTPException(resp.status, str(data))
                return data

    async def get_gateway_bot(self):
        return await self.request(Route("GET", "/gateway/bot"))

    async def send_message(self, channel_id: int, *, content=None, embeds=None, components=None):
        payload = {}
        if content is not None:
            payload["content"] = content
        if embeds is not None:
            payload["embeds"] = embeds
        if components is not None:
            payload["components"] = components
        return await self.request(
            Route("POST", "/channels/{channel_id}/messages", channel_id=channel_id),
            json=payload,
        )

    async def register_slash_commands(self, application_id: int, commands: list[dict]):
        return await self.request(
            Route("PUT", "/applications/{application_id}/commands", application_id=application_id),
            json=commands,
        )

    async def create_interaction_response(self, interaction_id: int, interaction_token: str,
                                           *, content=None, embeds=None, components=None,
                                           ephemeral=False):
        """
        Responds to a slash command / component interaction.
        Discord requires this within 3 seconds of receiving the
        interaction, via a different endpoint than regular messages.

        NEW METHOD — did not exist in the original file. Needed
        because Interaction.send() (in ext/slash/core.py) has
        nothing else in HTTPClient it could call.
        """
        data = {}
        if content is not None:
            data["content"] = content
        if embeds is not None:
            data["embeds"] = embeds
        if components is not None:
            data["components"] = components
        if ephemeral:
            data["flags"] = 64  # EPHEMERAL flag

        payload = {
            "type": 4,  # CHANNEL_MESSAGE_WITH_SOURCE
            "data": data,
        }
        return await self.request(
            Route(
                "POST",
                "/interactions/{interaction_id}/{interaction_token}/callback",
                interaction_id=interaction_id,
                interaction_token=interaction_token,
            ),
            json=payload,
        )
