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

    async def close(self):
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ws:
            await self._ws.close()
        if self._session:
            await self._session.close()
