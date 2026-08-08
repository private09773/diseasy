"""
diseasy/bot.py

Built on the real Client (client.py). Adds cog loading, standalone
command support, presence, permission-gated commands, button/dropdown
component routing, automatic slash command syncing, and (this update)
specific CommandNeverLoaded/CommandDoesntWork errors instead of
generic log warnings.
"""

import asyncio
import importlib
import pkgutil

from .client import Client
from .logger import log, friendly_error, _init_logging
from .permissions import Permissions, BotPermissions
from .presence import build_presence_payload
from .errors import CommandNeverLoaded, CommandDoesntWork
from .ext.commands.core import Command
from .ext.slash.core import SlashCommand


class Bot(Client):
    def __init__(self, intents=None, prefix="!"):
        super().__init__(intents=intents)
        _init_logging()
        self.prefix = prefix
        self._cogs = {}
        self._standalone_commands: dict[str, Command] = {}
        self._standalone_slash_commands: dict[str, SlashCommand] = {}
        self._components: dict[str, object] = {}

        @self.event(name="on_ready")
        async def _bot_ready(*args):
            log.info(f"{len(self._cogs)} cog(s) loaded")
            await self._sync_slash_commands()

        @self.event(name="on_message")
        async def _bot_on_message(message):
            await self._dispatch_command(message)

        @self.event(name="on_interaction_create")
        async def _bot_on_interaction(interaction):
            if interaction.type == 3:
                await self._dispatch_component(interaction)
            else:
                await self._dispatch_slash_command(interaction)

    # ---- slash command sync ----

    async def _sync_slash_commands(self):
        if not getattr(self, "user", None):
            log.warning("Cannot sync slash commands — bot.user not set yet.")
            return

        all_commands = dict(self._standalone_slash_commands)
        for cog in self._cogs.values():
            all_commands.update(getattr(cog, "__cog_slash_commands__", {}))

        if not all_commands:
            log.info("No slash commands to sync.")
            return

        try:
            payload = [cmd.to_dict() for cmd in all_commands.values()]
            await self._http.register_slash_commands(self.user.id, payload)
            log.info(f"Synced {len(payload)} slash command(s) with Discord.")
        except Exception as e:
            log.error(f"Failed to sync slash commands: {e}")

    # ---- standalone commands ----

    def add_command(self, cmd: Command):
        self._standalone_commands[cmd.name] = cmd
        log.info(f"Registered standalone command: {cmd.name}")

    def add_slash_command(self, cmd: SlashCommand):
        self._standalone_slash_commands[cmd.name] = cmd
        log.info(f"Registered standalone slash command: {cmd.name}")

    def add_component(self, component):
        self._components[component.custom_id] = component
        log.info(f"Registered component: {component.custom_id}")

    def _find_command(self, name: str):
        cmd = self._standalone_commands.get(name)
        if not cmd:
            for cog in self._cogs.values():
                if name in getattr(cog, "__cog_commands__", {}):
                    cmd = cog.__cog_commands__[name]
                    break
        return cmd

    def _find_slash_command(self, name: str):
        cmd = self._standalone_slash_commands.get(name)
        if not cmd:
            for cog in self._cogs.values():
                if name in getattr(cog, "__cog_slash_commands__", {}):
                    cmd = cog.__cog_slash_commands__[name]
                    break
        return cmd

    async def _dispatch_command(self, message):
        if not hasattr(message, "content") or not message.content.startswith(self.prefix):
            return
        name = message.content[len(self.prefix):].split(" ")[0]

        cmd = self._find_command(name)
        if not cmd:
            # CHANGED: specific CommandNeverLoaded instead of a bare
            # log.warning — makes clear this command was never
            # registered at all, distinct from a command that exists
            # but fails when run.
            err = CommandNeverLoaded(name)
            log.warning(str(err))
            return

        try:
            await cmd.invoke(message)
        except Exception as e:
            # CHANGED: wraps the failure as CommandDoesntWork so the
            # log clearly distinguishes "found but broke" from "never
            # existed", while still surfacing the friendly hint.
            wrapped = CommandDoesntWork(name, e)
            log.error(f"{wrapped}\n    → {friendly_error(e)}")

    async def _dispatch_slash_command(self, interaction):
        cmd_name = interaction.command_name
        if not cmd_name:
            return

        cmd = self._find_slash_command(cmd_name)
        if not cmd:
            err = CommandNeverLoaded(cmd_name)
            log.warning(str(err))
            return

        try:
            await cmd.invoke(interaction)
        except Exception as e:
            wrapped = CommandDoesntWork(cmd_name, e)
            log.error(f"{wrapped}\n    → {friendly_error(e)}")

    async def _dispatch_component(self, interaction):
        component = self._components.get(interaction.custom_id)
        if not component:
            log.warning(f"Unknown component clicked: {interaction.custom_id}")
            return

        try:
            if interaction.values:
                await component.invoke(interaction, interaction.values[0])
            else:
                await component.invoke(interaction)
        except Exception as e:
            wrapped = CommandDoesntWork(interaction.custom_id, e)
            log.error(f"{wrapped}\n    → {friendly_error(e)}")

    # ---- cogs ----

    def load_cog(self, cog):
        name = cog.__class__.__name__
        self._cogs[name] = cog
        if hasattr(cog, "cog_load"):
            asyncio.ensure_future(cog.cog_load())
        log.info(f"Loaded cog: {name}")

    def load_extension(self, module_path):
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, "setup"):
                module.setup(self)
                log.info(f"Loaded extension: {module_path}")
            else:
                log.warning(f"{module_path} has no setup(bot) function")
        except Exception as e:
            log.error(f"Failed to load extension {module_path}: {e}")
            raise

    def load_all_extensions(self, package_name):
        package = importlib.import_module(package_name)
        for _, name, _ in pkgutil.iter_modules(package.__path__):
            self.load_extension(f"{package_name}.{name}")

    def unload_cog(self, name):
        if name in self._cogs:
            del self._cogs[name]
            log.info(f"Unloaded cog: {name}")
        else:
            log.warning(f"Tried to unload unknown cog: {name}")

    # ---- presence ----

    async def set_presence(self, activity, status="online"):
        payload = build_presence_payload(activity, status)
        if self._gateway:
            await self._gateway.update_presence(payload)
        else:
            log.warning("Cannot set presence before the bot has connected.")

    # ---- permissions ----

    def get_permissions(self, member) -> Permissions:
        return Permissions(member)

    def get_bot_permissions(self, guild, bot_member) -> BotPermissions:
        return BotPermissions(guild, bot_member)

    def command_with_permissions(self, name, required_perms=None):
        required_perms = required_perms or []

        def decorator(func):
            async def wrapper(ctx, *args, **kwargs):
                perms = Permissions(ctx.author)
                if required_perms and not perms.has(*required_perms):
                    log.info(f"{ctx.author} denied '{name}' (missing: {required_perms})")
                    if hasattr(ctx, "send"):
                        await ctx.send(message="You don't have permission to do that.")
                    return
                return await func(ctx, *args, **kwargs)

            wrapped_cmd = Command(wrapper, name=name)
            self.add_command(wrapped_cmd)
            return wrapper

        return decorator
