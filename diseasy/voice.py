"""
diseasy/voice.py (v0.3.2, diseasy[voice] extra)

Scoped deliberately to CONNECT/DISCONNECT only — no audio playback or
receiving. That's real Discord voice protocol: join a voice channel,
complete the voice gateway handshake, and be able to leave cleanly.

Full audio (UDP transport, Opus encoding, playback) is a separate,
much larger feature for a later version.

Real protocol flow:
  1. Bot sends VOICE_STATE_UPDATE (op 4) on the MAIN gateway.
  2. Discord replies with VOICE_STATE_UPDATE + VOICE_SERVER_UPDATE
     dispatch events (session_id, token, endpoint).
  3. Bot opens a SEPARATE websocket to the voice endpoint.
  4. Voice handshake: HELLO(8) -> IDENTIFY(0) -> READY(2), then a
     regular heartbeat loop, same shape as the main gateway's.

Usage:
    from diseasy.voice import VoiceClient

    voice = VoiceClient(bot, guild_id=123, channel_id=456)
    await voice.connect()
    # ... later ...
    await voice.disconnect()
"""

import asyncio
import json

import aiohttp


class VoiceOpCode:
    IDENTIFY = 0
    SELECT_PROTOCOL = 1
    READY = 2
    HEARTBEAT = 3
    SESSION_DESCRIPTION = 4
    SPEAKING = 5
    HEARTBEAT_ACK = 6
    RESUME = 7
    HELLO = 8
    RESUMED = 9
    CLIENT_DISCONNECT = 13


class VoiceClient:
    def __init__(self, bot, guild_id: int, channel_id: int):
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id

        self.session_id: str | None = None
        self.token: str | None = None
        self.endpoint: str | None = None
        self.ssrc: int | None = None

        self.connected = False
        self._ws: aiohttp.ClientWebSocketResponse | None = None
        self._http_session: aiohttp.ClientSession | None = None
        self._heartbeat_task: asyncio.Task | None = None
        self._heartbeat_interval: float | None = None

        # Set by state.py once VOICE_STATE_UPDATE/VOICE_SERVER_UPDATE
        # dispatch events arrive for this guild.
        self._state_update_event = asyncio.Event()
        self._server_update_event = asyncio.Event()

    # ---- called by state.py when the relevant dispatch events arrive ----

    def _on_voice_state_update(self, data: dict):
        self.session_id = data.get("session_id")
        self._state_update_event.set()

    def _on_voice_server_update(self, data: dict):
        self.token = data.get("token")
        raw_endpoint = data.get("endpoint")
        # Discord sometimes includes a port suffix here; the voice
        # gateway URL itself never needs one.
        self.endpoint = raw_endpoint.split(":")[0] if raw_endpoint else None
        self._server_update_event.set()

    # ---- connect / disconnect ----

    async def connect(self, timeout: float = 10.0):
        """
        Joins the voice channel and completes the voice gateway
        handshake. Does not set up audio — connected=True just means
        the bot is present in the channel and the voice websocket is
        alive.
        """
        if self.bot._gateway is None:
            raise RuntimeError("Bot must be connected to the main gateway first.")

        await self.bot._gateway.update_voice_state(self.guild_id, self.channel_id)

        try:
            await asyncio.wait_for(self._state_update_event.wait(), timeout=timeout)
            await asyncio.wait_for(self._server_update_event.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            raise RuntimeError(
                "Timed out waiting for Discord's voice state/server update — "
                "check the bot has permission to join this voice channel."
            )

        if not self.endpoint or not self.token or not self.session_id:
            raise RuntimeError("Missing voice connection info after Discord's response.")

        self._http_session = aiohttp.ClientSession()
        self._ws = await self._http_session.ws_connect(
            f"wss://{self.endpoint}?v=8"
        )

        await self._voice_handshake()
        self.connected = True

    async def _voice_handshake(self):
        async for msg in self._ws:
            if msg.type != aiohttp.WSMsgType.TEXT:
                continue
            payload = json.loads(msg.data)
            op = payload.get("op")

            if op == VoiceOpCode.HELLO:
                self._heartbeat_interval = payload["d"]["heartbeat_interval"]
                await self._identify()
            elif op == VoiceOpCode.READY:
                self.ssrc = payload["d"].get("ssrc")
                self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                return  # handshake complete — connect() takes over from here

    async def _identify(self):
        payload = {
            "op": VoiceOpCode.IDENTIFY,
            "d": {
                "server_id": str(self.guild_id),
                "user_id": str(self.bot.user.id),
                "session_id": self.session_id,
                "token": self.token,
            },
        }
        await self._ws.send_json(payload)

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(self._heartbeat_interval / 1000)
            await self._ws.send_json({"op": VoiceOpCode.HEARTBEAT, "d": 0})

    async def disconnect(self):
        """Leaves the voice channel and closes the voice websocket."""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._ws:
            await self._ws.close()
        if self._http_session:
            await self._http_session.close()

        if self.bot._gateway:
            await self.bot._gateway.update_voice_state(self.guild_id, None)

        self.connected = False
