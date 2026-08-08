"""
diseasy/runtime.py

Resolves <var> tokens (e.g. <bot.name>, <guild.member_count>,
<member.name>) at runtime — usable directly in plain Python, not
just in parser-generated code. This is what lets a cog write:

    await ctx.send(message="Welcome to <guild.name>!")

...without needing an f-string or the .dsy notation at all — the
sending code (ctx.send / interaction.send) calls resolve_vars() on
the message before it goes out.
"""

import re

from diseasy.variables import VARIABLES

VAR_TOKEN_RE = re.compile(r"<([\w\.]+)>")


def resolve(token: str, ctx, local_vars: dict = None):
    """
    token examples: "bot.name", "member.name", "guild.member_count"

    Resolution order:
      1. The registered <> variable registry (VARIABLES) — exact match.
      2. Local variables passed in, with dotted attribute access
         (e.g. "member.name" -> local_vars["member"].name).
    """
    local_vars = local_vars or {}

    if token in VARIABLES:
        return VARIABLES[token](ctx)

    parts = token.split(".")
    root_name = parts[0]
    if root_name in local_vars:
        value = local_vars[root_name]
        for attr in parts[1:]:
            value = getattr(value, attr)
        return value

    raise NameError(
        f"Could not resolve <{token}> — not a registered variable "
        f"and no local '{root_name}' in scope."
    )


def resolve_vars(text: str, ctx, local_vars: dict = None) -> str:
    """
    Replaces every <token> found in `text` with its resolved value,
    returning a plain string. This is what ctx.send/interaction.send
    call automatically — most code never needs to call this directly.
    """
    if "<" not in text:
        return text

    def replace(match):
        token = match.group(1)
        try:
            return str(resolve(token, ctx, local_vars))
        except NameError:
            # Leave unresolved tokens as-is rather than crashing a
            # send() call over a typo — matches discord.py's general
            # leniency around message content.
            return match.group(0)

    return VAR_TOKEN_RE.sub(replace, text)
