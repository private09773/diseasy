"""
diseasy/bot.py

Built on the real Client (client.py) — uses .event()/dispatch()/
_listeners. Adds cog loading, standalone command support, presence,
permission-gated commands, and (v0.2.4) button/dropdown component
routing alongside slash command routing.
"""

import asyncio
import importlib
import pkgutil

from .client import Client
from .logger import log, _init_logging
from .permissions import Permissions, BotPermissions
from .presence import build_presence_payload
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
        self._components: dict[str, object] = {}  # custom_id -> Button/Dropdown

        @self.event(name="on_ready")
        async def _bot_ready(*args):
            log.info(f"{len(self._cogs)} cog(s) loaded")

        @self.event(name="on_message")
        async def _bot_on_message(message):
            await self._dispatch_command(message)

        @self.event(name="on_interaction_create")
        async def _bot_on_interaction(interaction):
            if interaction.type == 3:  # MESSAGE_COMPONENT (button/dropdown)
                await self._dispatch_component(interaction)
            else:  # 2 = APPLICATION_COMMAND (slash command)
                await self._dispatch_slash_command(interaction)

    # ---- standalone commands (main.py-level, not inside a cog) ----

    def add_command(self, cmd: Command):
        self._standalone_commands[cmd.name] = cmd
        log.info(f"Registered standalone command: {cmd.name}")

    def add_slash_command(self, cmd: SlashCommand):
        self._standalone_slash_commands[cmd.name] = cmd
        log.info(f"Registered standalone slash command: {cmd.name}")

    def add_component(self, component):
        """Registers a Button or Dropdown so its custom_id routes
        correctly when a real click/selection comes in."""
        self._components[component.custom_id] = component
        log.info(f"Registered component: {component.custom_id}")

    async def _dispatch_command(self, message):
        if not hasattr(message, "content") or not message.content.startswith(self.prefix):
            return
        name = message.content[len(self.prefix):].split(" ")[0]

        cmd = self._standalone_commands.get(name)
        if not cmd:
            for cog in self._cogs.values():
                if name in getattr(cog, "__cog_commands__", {}):
                    cmd = cog.__cog_commands__[name]
                    break

        if cmd:
            try:
                await cmd.invoke(message)
            except Exception as e:
                log.error(f"Command '{name}' raised an error: {e}")

    async def _dispatch_slash_command(self, interaction):
        cmd_name = interaction.command_name
        if not cmd_name:
            return

        cmd = self._standalone_slash_commands.get(cmd_name)
        if not cmd:
            for cog in self._cogs.values():
                if cmd_name in getattr(cog, "__cog_slash_commands__", {}):
                    cmd = cog.__cog_slash_commands__[cmd_name]
                    break

        if cmd:
            try:
                await cmd.invoke(interaction)
            except Exception as e:
                log.error(f"Slash command '{cmd_name}' raised an error: {e}")
        else:
            log.warning(f"Unknown slash command invoked: {cmd_name}")

    async def _dispatch_component(self, interaction):
        component = self._components.get(interaction.custom_id)
        if not component:
            log.warning(f"Unknown component clicked: {interaction.custom_id}")
            return

        try:
            if interaction.values:
                # Dropdown — Discord sends selected value(s) as a list;
                # single-select dropdowns use the first one.
                await component.invoke(interaction, interaction.values[0])
            else:
                # Button
                await component.invoke(interaction)
        except Exception as e:
            log.error(f"Component '{interaction.custom_id}' raised an error: {e}")

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
