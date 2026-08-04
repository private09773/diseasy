"""
diseasy/parser.py

Transpiles Diseasy's beginner-facing notation into real Python using
confirmed real decorators/classes. Covers:

  - .event: / .command: / .slash: blocks (send:, option_from:, slashopt:)
  - Assets: .asset-embed[], .asset-noembed[], .asset-getfrom[]
  - Embeds v1: .embed[], .embedtitle(), .embed_descriptor(),
    .embedinline(), .embedasset.from[<.asset-embed>]
  - Embeds v2 / containers: .container[], .containertext[]:,
    .containerseperator, .container_src.image[]:
  - Startup: client_import(): / container.startup[...]: / cog.load() /
    intents.load[] / prefix.set() / token.load() / client.run()

LIMITATIONS / ASSUMPTIONS (flagged, not hidden):
- Asset/embed/container translation emits plain Python dicts/lists —
  no confirmed real Embed/Asset/Container class exists to build
  instead; shape is best-effort from the notation alone.
- Startup's container.startup[...] presence config is wired to
  set_presence()/build_presence_payload() from presence.py, which is
  ITSELF unconfirmed against a real gateway.update_presence() method
  (flagged back when presence.py was built). If that method doesn't
  exist yet, presence-setting will fail at runtime, not at parse time.
- cog.load(/cog/all) maps to bot.load_all_extensions("cogs") —
  confirmed real method — but wrapped in error handling modeled after
  discord.py's ExtensionNotFound/ExtensionFailed, which are NOT real
  Diseasy exception classes (none confirmed to exist) — generic
  RuntimeError is used instead, clearly labeled.
- token.load(env=...) raises a clear error if the env var is missing,
  similar in spirit to discord.py's LoginFailure — again, this is a
  plain ValueError, not a confirmed real Diseasy exception type.
"""

import re

VAR_TOKEN_RE = re.compile(r"<([\w\.]+)>")

HEADER_EVENT_RE = re.compile(r'^\.event:\s*(\w+)\s*$')
HEADER_COMMAND_RE = re.compile(r'^\.command:\s*(\w+)(?:,\s*description="([^"]*)")?\s*$')
HEADER_SLASH_RE = re.compile(r'^\.slash:\s*(\w+)(?:,\s*description="([^"]*)")?\s*$')
SLASHOPT_RE = re.compile(
    r'^slashopt:\s*(\w+)(?:,\s*type="(\w+)")?(?:,\s*required=(true|false))?\s*$'
)
OPTION_FROM_RE = re.compile(r'^(\w+)\s*=\s*option_from:"([^"]+)"\s*$')
SEND_RE = re.compile(r'^send:\s*(.+)$')

ASSET_EMBED_RE = re.compile(r'^\.asset-embed\[source="([^"]*)"\]\s*$')
ASSET_NOEMBED_RE = re.compile(r'^\.asset-noembed\[source="([^"]*)"\]\s*$')
ASSET_GETFROM_RE = re.compile(
    r'^\.asset-getfrom\[internet=(true|false),\s*source="([^"]*)"\]\s*$'
)

EMBED_START_RE = re.compile(r'^\.embed\[\]\s*$')
EMBED_TITLE_RE = re.compile(r'^\.embedtitle\("([^"]*)"\)\s*$')
EMBED_DESC_RE = re.compile(r'^\.embed_descriptor\("([^"]*)"\)\s*$')
EMBED_INLINE_RE = re.compile(r'^\.embedinline\(\)\s*$')
EMBED_ASSET_FROM_RE = re.compile(r'^\.embedasset\.from\[<\.asset-embed>\]\s*$')

CONTAINER_START_RE = re.compile(r'^\.container\[\]\s*$')
CONTAINER_TEXT_RE = re.compile(r'^\.containertext\[\]:\s*"([^"]*)"\s*$')
CONTAINER_SEP_RE = re.compile(r'^\.containerseperator\s*$')
CONTAINER_SRC_IMAGE_RE = re.compile(r'^\.container_src\.image\[\]:\s*"([^"]*)"\s*$')

# --- Startup notation ---
CLIENT_IMPORT_RE = re.compile(r'^client_import\(\):\s*$')
CONTAINER_STARTUP_START_RE = re.compile(r'^container\.startup\[\s*$')
CONTAINER_STARTUP_END_RE = re.compile(r'^\]:\s*$')
COG_LOAD_RE = re.compile(r'^cog\.load\(/cog/all\):\s*$')
COG_LOAD_SINGLE_RE = re.compile(r'^cog\.load\("([^"]+)"\):\s*$')
INTENTS_LOAD_RE = re.compile(r'^intents\.load\[([^\]]*)\]:\s*$')
PREFIX_SET_RE = re.compile(r'^prefix\.set\("([^"]*)"\):\s*$')
TOKEN_LOAD_RE = re.compile(r'^token\.load\(env="([^"]*)"\):\s*$')
CLIENT_RUN_RE = re.compile(r'^client\.run\(\):\s*$')


def _rewrite_string_vars(raw_string_literal: str, local_vars_name="locals()") -> str:
    def replace(match):
        token = match.group(1)
        return f"{{__dsl_resolve('{token}', ctx, {local_vars_name})}}"

    body = raw_string_literal[1:-1]
    new_body = VAR_TOKEN_RE.sub(replace, body)
    if VAR_TOKEN_RE.search(raw_string_literal):
        return f'f"{new_body}"'
    return f'"{new_body}"'


def _quote_and_rewrite(text: str) -> str:
    return _rewrite_string_vars(f'"{text}"')


def _indent_level(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _split_blocks(lines):
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        header = line.strip()
        header_indent = _indent_level(line)
        body = []
        i += 1
        while i < len(lines) and (not lines[i].strip() or _indent_level(lines[i]) > header_indent):
            if lines[i].strip():
                body.append(lines[i])
            i += 1
        blocks.append((header, body))
    return blocks


def _translate_body(lines, param_name: str):
    output = []
    embed_open = False
    container_open = False
    embed_warned = False
    container_warned = False

    for line in lines:
        stripped = line.strip()

        m = ASSET_EMBED_RE.match(stripped)
        if m:
            output.append(f'__asset = {{"source": "{m.group(1)}", "embed": True}}')
            continue
        m = ASSET_NOEMBED_RE.match(stripped)
        if m:
            output.append(f'__asset = {{"source": "{m.group(1)}", "embed": False}}')
            continue
        m = ASSET_GETFROM_RE.match(stripped)
        if m:
            internet, source = m.groups()
            output.append(
                f'__asset = {{"source": "{source}", '
                f'"internet": {"True" if internet == "true" else "False"}}}'
            )
            continue

        m = EMBED_START_RE.match(stripped)
        if m:
            if embed_open and not embed_warned:
                output.append("# WARNING: multiple .embed[] blocks — overwrites __embed.")
                embed_warned = True
            output.append("__embed = {}")
            embed_open = True
            continue
        m = EMBED_TITLE_RE.match(stripped)
        if m:
            output.append(f'__embed["title"] = {_quote_and_rewrite(m.group(1))}')
            continue
        m = EMBED_DESC_RE.match(stripped)
        if m:
            output.append(f'__embed["description"] = {_quote_and_rewrite(m.group(1))}')
            continue
        m = EMBED_INLINE_RE.match(stripped)
        if m:
            output.append('__embed["inline"] = True')
            continue
        m = EMBED_ASSET_FROM_RE.match(stripped)
        if m:
            output.append('__embed["asset"] = __asset')
            continue

        m = CONTAINER_START_RE.match(stripped)
        if m:
            if container_open and not container_warned:
                output.append("# WARNING: multiple .container[] blocks — overwrites __container.")
                container_warned = True
            output.append("__container = []")
            container_open = True
            continue
        m = CONTAINER_TEXT_RE.match(stripped)
        if m:
            output.append(
                f'__container.append({{"type": "text", "content": {_quote_and_rewrite(m.group(1))}}})'
            )
            continue
        m = CONTAINER_SEP_RE.match(stripped)
        if m:
            output.append('__container.append({"type": "separator"})')
            continue
        m = CONTAINER_SRC_IMAGE_RE.match(stripped)
        if m:
            output.append(f'__container.append({{"type": "image", "source": "{m.group(1)}"}})')
            continue

        m = OPTION_FROM_RE.match(stripped)
        if m:
            var_name, opt_name = m.groups()
            output.append(f'{var_name} = {param_name}.option_from("{opt_name}")')
            continue

        m = SEND_RE.match(stripped)
        if m:
            raw = m.group(1).strip()
            if raw.startswith('"') and raw.endswith('"'):
                raw = _rewrite_string_vars(raw)
            send_kwargs = f"message={raw}"
            if embed_open:
                send_kwargs += ", embed=__embed"
            if container_open:
                send_kwargs += ", components=__container"
            output.append(f'await {param_name}.send({send_kwargs})')
            continue

        def replace_quoted(match):
            return _rewrite_string_vars(match.group(0))

        if '"' in stripped:
            output.append(re.sub(r'"[^"]*"', replace_quoted, stripped))
        else:
            output.append(
                VAR_TOKEN_RE.sub(
                    lambda mm: f"{{__dsl_resolve('{mm.group(1)}', ctx, locals())}}", stripped
                )
            )

    return output


def _translate_startup(body):
    """
    Translates client_import():'s body into real setup code —
    intents, prefix, token loading, presence, cog loading, all with
    discord.py-style error handling (generic exceptions, since no
    confirmed real Diseasy exception classes exist).
    """
    out = []
    intents_list = "[]"
    prefix_val = '"!"'

    i = 0
    presence_lines = []
    while i < len(body):
        stripped = body[i].strip()

        if CONTAINER_STARTUP_START_RE.match(stripped):
            i += 1
            entries = {}
            while i < len(body) and not CONTAINER_STARTUP_END_RE.match(body[i].strip()):
                entry_line = body[i].strip().strip(",")
                kv_match = re.match(r'^"([\w.]+)=([\w]+)"$', entry_line)
                if kv_match:
                    entries[kv_match.group(1)] = kv_match.group(2)
                i += 1
            i += 1  # skip the closing "]:"

            status = entries.get("status", "online")
            status_map = {"invis": "invisible"}
            status = status_map.get(status, status)
            cstatus = entries.get("cstatus")
            cstatus_text = entries.get("cstatus.text")

            out.append(f'__presence_status = "{status}"')
            if cstatus:
                out.append(f'from diseasy.presence import {cstatus if cstatus != "custom" else "custom_status"}')
                if cstatus == "custom":
                    out.append(f'__activity = custom_status("{cstatus_text or ""}")')
                else:
                    out.append(f'__activity = {cstatus}("")  # NOTE: no text supplied in container.startup[]')
                presence_lines.append(
                    'await bot.set_presence(__activity, status=__presence_status)  '
                    '# ASSUMPTION: gateway.update_presence() not confirmed to exist'
                )
            continue

        m = COG_LOAD_RE.match(stripped)
        if m:
            out.append("try:")
            out.append('    bot.load_all_extensions("cogs")')
            out.append("except Exception as e:")
            out.append(
                '    raise RuntimeError(f"Failed to load one or more cogs: {e}") from e'
            )
            i += 1
            continue

        m = COG_LOAD_SINGLE_RE.match(stripped)
        if m:
            ext_name = m.group(1)
            out.append("try:")
            out.append(f'    bot.load_extension("{ext_name}")')
            out.append("except Exception as e:")
            out.append(
                f'    raise RuntimeError(f"Failed to load extension \'{ext_name}\': {{e}}") from e'
            )
            i += 1
            continue

        m = INTENTS_LOAD_RE.match(stripped)
        if m:
            names = [n.strip() for n in m.group(1).split(",") if n.strip()]
            intents_list = "[" + ", ".join(f'"{n}"' for n in names) + "]"
            i += 1
            continue

        m = PREFIX_SET_RE.match(stripped)
        if m:
            prefix_val = f'"{m.group(1)}"'
            i += 1
            continue

        m = TOKEN_LOAD_RE.match(stripped)
        if m:
            env_var = m.group(1)
            out.insert(0, "import os")
            out.append(f'TOKEN = os.getenv("{env_var}")')
            out.append("if not TOKEN:")
            out.append(
                f'    raise ValueError('
                f'"No token found — set the {env_var} environment variable '
                f'(e.g. in a .env file)." )'
            )
            i += 1
            continue

        i += 1  # unrecognized line inside client_import(), skip

    return out, intents_list, prefix_val, presence_lines


def parse(source: str) -> str:
    lines = source.split("\n")
    blocks = _split_blocks(lines)

    output = [
        "# Auto-generated by diseasy.dsl.parser — do not hand-edit.",
        "from dotenv import load_dotenv",
        "import diseasy",
        "from diseasy.ext.commands import command",
        "from diseasy.ext.slash import slash_command",
        "from diseasy.dsl.runtime import resolve as __dsl_resolve",
        "",
        "load_dotenv()",
        "",
    ]

    bot_constructed = False

    for header, body in blocks:
        if CLIENT_IMPORT_RE.match(header):
            setup_lines, intents_list, prefix_val, presence_lines = _translate_startup(body)
            for line in setup_lines:
                if line.startswith("import os"):
                    output.insert(1, line)
                else:
                    output.append(line)
            output.append(f'bot = diseasy.Bot(intents={intents_list}, prefix={prefix_val})')
            bot_constructed = True
            if presence_lines:
                output.append('')
                output.append('@bot.event(name="on_ready")')
                output.append('async def _dsl_apply_presence(*args):')
                for pline in presence_lines:
                    output.append("    " + pline)
            output.append("")
            continue

        if CLIENT_RUN_RE.match(header):
            if not bot_constructed:
                output.append(
                    "# ERROR: client.run() called before client_import() defined `bot` "
                    "and TOKEN — check block order."
                )
            output.append("try:")
            output.append("    bot.run(TOKEN)")
            output.append("except Exception as e:")
            output.append(
                '    raise RuntimeError(f"Diseasy failed to start: {e}") from e'
            )
            output.append("")
            continue

        m = HEADER_EVENT_RE.match(header)
        if m:
            event_name = m.group(1)
            fn_name = f"_evt_{event_name}"
            output.append(f'@bot.event(name="{event_name}")')
            output.append(f"async def {fn_name}(*args, ctx=None):")
            translated = _translate_body(body, "ctx")
            if not translated:
                output.append("    pass")
            for line in translated:
                output.append("    " + line)
            output.append("")
            continue

        m = HEADER_COMMAND_RE.match(header)
        if m:
            cmd_name, desc = m.groups()
            desc = desc or ""
            output.append(f'@command(name="{cmd_name}", description="{desc}")')
            output.append(f"async def {cmd_name}(ctx):")
            translated = _translate_body(body, "ctx")
            if not translated:
                output.append("    pass")
            for line in translated:
                output.append("    " + line)
            output.append("")
            continue

        m = HEADER_SLASH_RE.match(header)
        if m:
            cmd_name, desc = m.groups()
            desc = desc or ""
            options = []
            remaining_body = []
            for line in body:
                om = SLASHOPT_RE.match(line.strip())
                if om:
                    opt_name, opt_type, opt_required = om.groups()
                    opt_type = opt_type or "str"
                    opt_required = "True" if (opt_required or "true") == "true" else "False"
                    options.append((opt_name, opt_type, opt_required))
                else:
                    remaining_body.append(line)

            output.append(f'@slash_command(name="{cmd_name}", description="{desc}")')
            output.append(f"async def {cmd_name}(interaction):")
            translated = _translate_body(remaining_body, "interaction")
            if not translated:
                output.append("    pass")
            for line in translated:
                output.append("    " + line)
            for opt_name, opt_type, opt_required in options:
                output.append(
                    f'{cmd_name}.slashoption(name="{opt_name}", type="{opt_type}", '
                    f'required={opt_required})'
                )
            output.append("")
            continue

        output.append(f"# Unrecognized block header, skipped: {header}")

    return "\n".join(output)


def parse_file(path: str) -> str:
    with open(path, "r") as f:
        return parse(f.read())


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python parser.py <file.dsy>")
        sys.exit(1)
    print(parse_file(sys.argv[1]))

# =========================================================================
# STARTUP-FILE NOTATION (added on top of the command/embed parser above)
#
# Covers: client_import(): / container.startup[...]: / cog.load(...): /
# intents.load[...]: / prefix.set(...): / token.load(env=""):/ client.run():
#
# ASSUMPTION FLAG: the exact semantics of "python.client_event(diseasy.startup)"
# inside cog.load(): were not fully clear from your example — I've
# interpreted it as "wrap startup in error handling and log failures,
# discord.py-style" and generated that, but this is inference on my
# part, not something confirmed against real Diseasy behavior.
#
# ASSUMPTION FLAG: bot.set_presence(...) usage below assumes the
# presence.py + gateway wiring from earlier in this conversation is
# in place. That wiring's gateway-side (update_presence on Gateway)
# was never confirmed to exist in your real gateway.py.
# =========================================================================

TOP_CLIENT_IMPORT_RE = re.compile(r'^client_import\(\):\s*$')
TOP_CONTAINER_STARTUP_RE = re.compile(r'^container\.startup\[\s*$')
TOP_CONTAINER_STARTUP_END_RE = re.compile(r'^\]?:\s*$')
TOP_COG_LOAD_RE = re.compile(r'^cog\.load\(([^)]*)\):\s*$')
TOP_INTENTS_LOAD_RE = re.compile(r'^intents\.load\[([^\]]*)\]:\s*$')
TOP_PREFIX_SET_RE = re.compile(r'^prefix\.set\("([^"]*)"\):\s*$')
TOP_TOKEN_LOAD_RE = re.compile(r'^token\.load\(env="([^"]*)"\):\s*$')
TOP_CLIENT_RUN_RE = re.compile(r'^client\.run\(\):\s*$')
STARTUP_ARG_RE = re.compile(r'"(\w[\w.]*)=([\w/]+)"')


def _parse_startup_container(lines, idx):
    """Parses a multi-line container.startup[ ... ]: block starting at idx.
    Returns (status, cstatus_type, cstatus_text, next_idx)."""
    status = "online"
    cstatus_type = None
    cstatus_text = None
    idx += 1
    while idx < len(lines) and not TOP_CONTAINER_STARTUP_END_RE.match(lines[idx].strip()):
        for m in STARTUP_ARG_RE.finditer(lines[idx]):
            key, value = m.groups()
            if key == "status":
                status = value
            elif key == "cstatus":
                cstatus_type = value
            elif key == "cstatus.text":
                cstatus_text = value
        idx += 1
    return status, cstatus_type, cstatus_text, idx + 1  # skip the closing "]:"


_STATUS_MAP = {
    "online": "online", "idle": "idle", "dnd": "dnd", "invis": "invisible",
}
_CSTATUS_MAP = {
    "play": "playing", "watch": "watching", "listen": "listening", "custom": "custom",
}


def parse_startup(source: str) -> str:
    """
    Parses a startup-file notation source (client_import()/client.run())
    into real Python using diseasy.Bot, load_all_extensions, and
    error-wrapped startup — discord.py-style error messages on failure.
    """
    lines = source.split("\n")
    out = [
        "# Auto-generated by diseasy.dsl.parser (startup file) — do not hand-edit.",
        "import os",
        "import diseasy",
        "from dotenv import load_dotenv",
        "",
        "load_dotenv()",
        "",
    ]

    intents_value = '["guilds", "messages"]'
    prefix_value = '"!"'
    token_env_var = "DISCORD_TOKEN"
    status = "online"
    cstatus_type = None
    cstatus_text = None
    cog_load_arg = None

    i = 0
    while i < len(lines):
        stripped = lines[i].strip()

        if TOP_CLIENT_IMPORT_RE.match(stripped):
            i += 1
            continue

        if TOP_CONTAINER_STARTUP_RE.match(stripped):
            status, cstatus_type, cstatus_text, i = _parse_startup_container(lines, i)
            continue

        m = TOP_INTENTS_LOAD_RE.match(stripped)
        if m:
            names = [n.strip() for n in m.group(1).split(",") if n.strip()]
            intents_value = "[" + ", ".join(f'"{n}"' for n in names) + "]"
            i += 1
            continue

        m = TOP_PREFIX_SET_RE.match(stripped)
        if m:
            prefix_value = f'"{m.group(1)}"'
            i += 1
            continue

        m = TOP_TOKEN_LOAD_RE.match(stripped)
        if m:
            token_env_var = m.group(1)
            i += 1
            continue

        m = TOP_COG_LOAD_RE.match(stripped)
        if m:
            cog_load_arg = m.group(1).strip()
            # skip the nested body line(s) under cog.load(), e.g.
            # "python.client_event(diseasy.startup)" — inferred meaning:
            # wrap startup in try/except logging, handled globally below,
            # so nothing extra to emit per-line here.
            i += 1
            while i < len(lines) and (not lines[i].strip() or _indent_level(lines[i]) > _indent_level(lines[i - 1] if lines[i-1].strip() else "")):
                if lines[i].strip():
                    pass  # consumed, semantics folded into global error wrapping
                i += 1
                if i < len(lines) and _indent_level(lines[i]) == 0:
                    break
            continue

        if TOP_CLIENT_RUN_RE.match(stripped):
            i += 1
            continue

        i += 1  # unrecognized top-level line, skip

    # --- Emit real, error-wrapped setup code ---
    out.append(f'TOKEN = os.getenv("{token_env_var}")')
    out.append("if not TOKEN:")
    out.append(f'    raise RuntimeError(')
    out.append(f'        "Diseasy: no token found in environment variable '
                f'\'{token_env_var}\'. "')
    out.append(f'        "Add it to your .env file before starting the bot."')
    out.append(f"    )")
    out.append("")
    out.append(f"bot = diseasy.Bot(intents={intents_value}, prefix={prefix_value})")
    out.append("")

    if cstatus_type or status != "online":
        real_status = _STATUS_MAP.get(status, "online")
        out.append("from diseasy.presence import playing, watching, listening, custom_status")
        out.append("")
        out.append('@bot.event(name="on_ready")')
        out.append("async def _apply_startup_presence(*args):")
        if cstatus_type == "custom" and cstatus_text:
            out.append(f'    activity = custom_status("{cstatus_text}")')
        elif cstatus_type in _CSTATUS_MAP:
            builder = {"play": "playing", "watch": "watching", "listen": "listening"}.get(cstatus_type)
            out.append(f'    activity = {builder}("{cstatus_text or ""}")')
        else:
            out.append("    activity = None")
        out.append("    if activity:")
        out.append(f'        await bot.set_presence(activity, status="{real_status}")')
        out.append("")

    out.append("try:")
    if cog_load_arg:
        folder = cog_load_arg.strip("/").split("/")[0] if "/" in cog_load_arg else cog_load_arg
        out.append(f'    bot.load_all_extensions("{folder}")')
    out.append("except ModuleNotFoundError as e:")
    out.append('    print(f"[Diseasy] Cog folder not found: {e}")')
    out.append("    raise")
    out.append("except Exception as e:")
    out.append('    print(f"[Diseasy] One or more cogs failed to load: {e}")')
    out.append("    raise")
    out.append("")

    out.append("try:")
    out.append("    bot.run(TOKEN)")
    out.append("except Exception as e:")
    out.append('    print(f"[Diseasy] Bot failed to start: {e}")')
    out.append("    raise")
    out.append("")

    return "\n".join(out)
