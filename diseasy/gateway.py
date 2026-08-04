"""Websocket gateway: connection, heartbeat loop, and identify.
This is the piece behind .event[] dispatch."""
import asyncio
import json

import aiohttp

from .enums import OpCode


class Gateway:
    def __init__(self, client, token: str, intents: int):
        self.client = client
        self.token = token
        self.intents = intents
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._heartbeat_interval: float | None = None
        self._session: aiohttp.ClientSession | None = None
        self._heartbeat_task: asyncio.Task | None = None

    async def connect(self, url: str):
        self._session = aiohttp.ClientSession()
        self._ws = await self._session.ws_connect(url)
        await self._receive_loop()

    async def _identify(self):
        payload = {
            "op": OpCode.IDENTIFY,
            "d": {
                "token": self.token,
                "intents": int(self.intents),
                "properties": {"os": "linux", "browser": "diseasy", "device": "diseasy"},
            },
        }
        await self._ws.send_json(payload)

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(self._heartbeat_interval / 1000)
            await self._ws.send_json({"op": OpCode.HEARTBEAT, "d": None})

    async def _receive_loop(self):
        async for msg in self._ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue
            payload = json.loads(msg.data)
            op = payload.get("op")
            if op == OpCode.HELLO:
                self._heartbeat_interval = payload["d"]["heartbeat_interval"]
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                await self._identify()
            elif op == OpCode.DISPATCH:
                self.client._state.parse(payload["t"], payload["d"])

    async def update_presence(self, payload: dict):
        """
        NEW METHOD — did not exist before. Sends a Discord Gateway
        opcode 3 (PRESENCE_UPDATE) frame, which is how a bot's
        status/activity (Playing, Watching, custom status, etc.)
        actually gets set. Called by Client/Bot.set_presence().

        ASSUMPTION FLAG: uses OpCode.PRESENCE_UPDATE — I don't have
        enums.py, so I don't know for certain that value is defined
        there. Discord's real gateway opcode for this is 3. If
        OpCode.PRESENCE_UPDATE doesn't exist in your enums.py, this
        will raise an AttributeError — add it there (value 3) or
        swap the line below to use the literal integer 3 directly.

        Also requires the websocket to already be connected — calling
        this before connect() has completed will fail since self._ws
        is None.
        """
        if self._ws is None:
            raise RuntimeError(
                "Cannot update presence — gateway is not connected yet."
            )
        try:
            op_value = OpCode.PRESENCE_UPDATE
        except AttributeError:
            op_value = 3  # Discord's real PRESENCE_UPDATE opcode, as a fallback
        await self._ws.send_json({"op": op_value, "d": payload})

    async def close(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ws:
            await self._ws.close()
        if self._session:
            await self._session.close()
