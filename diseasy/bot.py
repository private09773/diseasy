"""
diseasy/bot.py

Higher-level Bot class — extends Client with cog loading and
command/event dispatch. Merge with your existing cog-loading logic
if you already have one; the loading mechanics here are a guess at
shape based on your {} cogs notation, not your real loader.
"""

import importlib
import pkgutil

from .client import Client
from .logger import log
from .permissions import Permissions


class Bot(Client):
    def __init__(self, intents=None, prefix="!"):
        super().__init__(intents=intents, prefix=prefix)
        self._cogs = {}

    # ---- cogs ----

    def load_cog(self, cog):
        """
        Register a cog instance. Cogs are expected to expose their
        own commands/events already bound (per your {} notation).
        """
        name = cog.__class__.__name__
        self._cogs[name] = cog
        log.info(f"Loaded cog: {name}")

    def load_extension(self, module_path):
        """
        Import a module by dotted path and call its setup(bot)
        function, discord.py-style.
        """
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
        """
        Auto-discover and load every submodule in a package as an
        extension. Useful for a cogs/ folder full of files.
        """
        package = importlib.import_module(package_name)
        for _, name, _ in pkgutil.iter_modules(package.__path__):
            self.load_extension(f"{package_name}.{name}")

    def unload_cog(self, name):
        if name in self._cogs:
            del self._cogs[name]
            log.info(f"Unloaded cog: {name}")
        else:
            log.warning(f"Tried to unload unknown cog: {name}")

    # ---- overridden lifecycle ----

    def _on_ready(self):
        super()._on_ready()
        log.info(f"{len(self._cogs)} cog(s) loaded")

    # ---- permission-gated command dispatch ----

    def command_with_permissions(self, name, required_perms=None):
        """
        Like .command(), but auto-checks required Discord permission
        flags before invoking (e.g. required_perms=["manage_messages"]).
        """
        required_perms = required_perms or []

        def decorator(func):
            async def wrapper(ctx, *args, **kwargs):
                perms = Permissions(ctx.author)
                if required_perms and not perms.has(*required_perms):
                    log.info(
                        f"{ctx.author} denied '{name}' "
                        f"(missing: {required_perms})"
                    )
                    if hasattr(ctx, "send"):
                        await ctx.send("You don't have permission to do that.")
                    return
                return await func(ctx, *args, **kwargs)

            self._commands[name] = wrapper
            return wrapper

        return decorator
