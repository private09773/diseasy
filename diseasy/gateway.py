"""Websocket gateway: connection, heartbeat loop, identify, and
reconnect/resume handling. This is the piece behind .event[] dispatch."""
import asyncio
import json
import random

import aiohttp

from .enums import OpCode


def _op(name: str, fallback: int) -> int:
    return getattr(OpCode, name, fallback)


class Gateway:
    def __init__(self, client, token: str, intents: int):
        self.client = client
        self.token = token
        self.intents = intents
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._heartbeat_interval: float | None = None
        self._session: aiohttp.ClientSession | None = None
        self._heartbeat_task: asyncio.Task | None = None

        self._sequence: int | None = None
        self._session_id: str | None = None
        self._resume_url: str | None = None
        self._original_url: str | None = None
        self._heartbeat_acked = True
        self._should_reconnect = False

    async def connect(self, url: str, resume: bool = False):
        """
        Connects and stays connected for the lifetime of the bot.
        Handles reconnects in a loop rather than recursively, so a
        bot that reconnects many times over days/weeks doesn't build
        up call stack depth with each one.
        """
        self._original_url = self._original_url or url
        current_url = url
        should_resume = resume

        while True:
            self._session = aiohttp.ClientSession()
            self._ws = await self._session.ws_connect(current_url)

            if should_resume and self._session_id is not None:
                await self._resume()

            await self._receive_loop()

            if not self._should_reconnect:
                break

            self._should_reconnect = False
            if self._heartbeat_task:
                self._heartbeat_task.cancel()
            await self._session.close()

            should_resume = self._session_id is not None
            target = self._resume_url or self._original_url
            current_url = f"{target}?v=10&encoding=json"

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

    async def _resume(self):
        payload = {
            "op": _op("RESUME", 6),
            "d": {
                "token": self.token,
                "session_id": self._session_id,
                "seq": self._sequence,
            },
        }
        await self._ws.send_json(payload)

    async def _heartbeat_loop(self):
        # Discord's spec: the first heartbeat fires after
        # heartbeat_interval * a random jitter between 0 and 1.
        jitter = random.random()
        await asyncio.sleep((self._heartbeat_interval / 1000) * jitter)

        while True:
            if not self._heartbeat_acked:
                # Discord never acked the last heartbeat — treat the
                # connection as dead and reconnect instead of hanging.
                self._should_reconnect = True
                if self._ws:
                    await self._ws.close()
                return

            self._heartbeat_acked = False
            await self._ws.send_json({"op": OpCode.HEARTBEAT, "d": self._sequence})
            await asyncio.sleep(self._heartbeat_interval / 1000)

    async def _receive_loop(self):
        async for msg in self._ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue
            payload = json.loads(msg.data)
            op = payload.get("op")

            seq = payload.get("s")
            if seq is not None:
                self._sequence = seq

            if op == OpCode.HELLO:
                self._heartbeat_interval = payload["d"]["heartbeat_interval"]
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                await self._identify()

            elif op == OpCode.DISPATCH:
                event_type = payload.get("t")
                if event_type == "READY":
                    ready_data = payload.get("d", {})
                    self._session_id = ready_data.get("session_id")
                    self._resume_url = ready_data.get("resume_gateway_url")
                self.client._state.parse(event_type, payload["d"])

            elif op == _op("HEARTBEAT_ACK", 11):
                self._heartbeat_acked = True

            elif op == OpCode.HEARTBEAT:
                await self._ws.send_json({"op": OpCode.HEARTBEAT, "d": self._sequence})

            elif op == _op("RECONNECT", 7):
                self._should_reconnect = True
                await self._ws.close()
                return

            elif op == _op("INVALID_SESSION", 9):
                resumable = bool(payload.get("d", False))
                if not resumable:
                    self._session_id = None
                    self._sequence = None
                await asyncio.sleep(random.uniform(1, 5))
                self._should_reconnect = True
                await self._ws.close()
                return

    async def update_presence(self, payload: dict):
        if self._ws is None:
            raise RuntimeError("Cannot update presence — gateway is not connected yet.")
        await self._ws.send_json({"op": OpCode.PRESENCE_UPDATE, "d": payload})

    async def close(self):
        self._should_reconnect = False
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ws:
            await self._ws.close()
        if self._session:
            await self._session.close()
