"""
diseasy/client.py

Core Client class — connection lifecycle, startup logging, and
integration points for permissions + variables.

NOTE: This is a scaffold. Merge the logging/lifecycle pieces into
your existing gateway/REST implementation rather than replacing it
wholesale — your actual WebSocket connect, heartbeat, and event
dispatch logic isn't reproduced here since I don't have it.
"""

import time
import datetime

from .logger import log
from .permissions import Permissions
from .variables import VARIABLES


class Client:
    def __init__(self, intents=None, prefix="!"):
        self.intents = intents or []
        self.prefix = prefix
        self.start_time = None
        self.user = None          # set once IDENTIFY/READY completes
        self.guilds = []          # populated on READY / GUILD_CREATE
        self.latency = 0.0
        self._events = {}
        self._commands = {}

    # ---- registration decorators ----

    def event(self, name):
        def decorator(func):
            self._events[name] = func
            return func
        return decorator

    def command(self, name):
        def decorator(func):
            self._commands[name] = func
            return func
        return decorator

    # ---- lifecycle ----

    def run(self, token):
        """
        Entry point. Wire this into your actual gateway connect call.
        """
        log.info("Diseasy is starting up...")
        self.start_time = datetime.datetime.utcnow()

        try:
            self._connect(token)
        except Exception as e:
            log.error(f"Failed to start: {e}")
            raise

    def _connect(self, token):
        """
        Placeholder for your actual gateway handshake
        (IDENTIFY, HELLO, HEARTBEAT, READY dispatch, etc).
        Call self._on_ready() once READY is received.
        """
        raise NotImplementedError(
            "Wire this into your existing gateway connection logic."
        )

    def _on_ready(self):
        log.info(f"Logged in as {self.user.name} (ID: {self.user.id})")
        log.info(f"Connected to {len(self.guilds)} guild(s)")
        log.info(f"Prefix: '{self.prefix}' | Intents: {self.intents}")

        handler = self._events.get("on_ready")
        if handler:
            handler()

    @property
    def uptime(self):
        if not self.start_time:
            return None
        return datetime.datetime.utcnow() - self.start_time

    # ---- helpers used by commands/events ----

    def get_permissions(self, member) -> Permissions:
        return Permissions(member)

    def resolve_variable(self, name, ctx):
        """
        Look up a registered <> variable by name and evaluate it
        against the current context.
        """
        func = VARIABLES.get(name)
        if func is None:
            log.warning(f"Unknown variable referenced: <{name}>")
            return None
        return func(ctx)
