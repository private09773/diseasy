# Diseasy Spec — Updated

**Status note:** As of v0.2.1, Diseasy dropped the `.dsy` notation
(the `.command:`/`.event:`/`.slash:` syntax and its parser) in favor
of plain Python. The table below maps each notation concept to
what's actually real today, so this doc stops describing syntax
that no longer reflects how Diseasy is used.

Legend for status column:
- ✅ **Built & tested** — real Python API, confirmed working
- ⚠️ **Notation only** — was designed, never implemented in Python
- ❌ **Retired** — the notation syntax itself is no longer used

---

## Symbol Legend (historical — describes the retired notation)

| Symbol | Meaning |
|--------|---------|
| `.`    | Functions |
| `[]`   | Container |
| `()`   | Text, embed, and other responses |
| `<>`   | Variables |
| `{}`   | Cogs container |

`<>` variables are the one piece of this legend still real and in
active use — see below.

---

## Variables — ✅ Built & tested

`<var>` tokens resolve automatically inside any string passed to
`ctx.send()`/`interaction.send()`, including inside `Embed` fields.
No f-string needed.

```python
await ctx.send(message="Welcome to <guild.name>, <user.name>!")
```

30+ built-in variables exist (user, guild, channel, message, bot,
time). Custom ones can be registered:

```python
from diseasy.variables import register

@register("custom.greeting")
def _greeting(ctx):
    return f"Hey, {ctx.author.name}!"
```

---

## Assets — ⚠️ Notation only, never implemented

```
.asset-embed[source="example.jpg"]
.asset-noembed[source="example.jpg"]
.asset-getfrom[internet=true/false, source="example.com"]
```

No real Python equivalent exists yet. Attaching an image to an
`Embed` today is done directly:

```python
embed.set_image("https://example.com/image.jpg")
```

---

## Embeds v1 — ✅ Built & tested (different syntax than the notation)

The notation (`.embed[]`, `.embedtitle()`, etc.) was retired. The
real, tested class:

```python
from diseasy import Embed

embed = Embed(title="Server Rules", description="Please read <guild.name>'s rules", color=0x5865F2)
embed.add_field(name="Rule 1", value="Be nice", inline=True)
embed.set_footer("Requested by <user.name>")

await ctx.send(message="Here are the rules:", embed=embed)
```

`<var>` tokens resolve automatically in title, description, field
name/value, and footer.

---

## Embeds v2 (Components / Containers) — ⚠️ Notation only, never implemented

```
.container[]
.containertext[]
.containerseperator
.container_src.image[]
.container_src.thumbnail[]
.containersection[]
.containergallery[]
.containerfile[]
.containeractionrow[]
.containerspoiler[]
```

None of this exists in real Python. No `Container` class has been
built.

---

## Buttons / Selects — ✅ Built & tested (different syntax than the notation)

Modals are still ⚠️ notation-only — no real implementation exists.

```python
from diseasy.components import Button, Dropdown

button = Button(label="Create Channel", style="primary", custom_id="create_channel_btn")

@button.on_click
async def handle_click(interaction):
    await interaction.create_channel(name="new-channel")

bot.add_component(button)

dropdown = Dropdown(custom_id="channel_type_select", placeholder="Pick a type")
dropdown.add_option(label="Text", value="text")

@dropdown.on_select
async def handle_select(interaction, value):
    await interaction.send(message=f"You picked {value}")

bot.add_component(dropdown)
```

Real Discord component payload shape confirmed (`type: 2` buttons,
`type: 3` selects), routed correctly by interaction type, distinct
from slash commands.

---

## Events / Commands / Cogs — ✅ Built & tested (different syntax than the notation)

```python
@bot.event(name="on_ready")
async def on_ready(*args):
    print("Bot is online.")

@command(name="ping", description="Replies with pong")
async def ping(ctx):
    await ctx.send(message="Pong!")

bot.add_command(ping)
```

Cogs — `{cog_name}:` notation retired, real class-based instead:

```python
from diseasy.ext.commands.cog import Cog

class Moderation(Cog):
    @command(name="kick", description="Kicks a member")
    async def kick(self, ctx, member):
        await member.kick()
        await ctx.send(message=f"Kicked {member.name}")

def setup(bot):
    bot.load_cog(Moderation())
```

```python
bot.load_extension("cogs.moderation")
bot.load_all_extensions("cogs")   # auto-discovers every file in the folder
```

`cogs = []` list pattern is the recommended way to organize a whole
bot (see main.py examples).

---

## Slash Commands — ✅ Built & tested (different syntax than the notation)

```python
from diseasy.ext.slash import slash_command

@slash_command(name="greet", description="Greets someone")
async def greet(interaction):
    name = interaction.option_from("name")
    await interaction.send(message=f"Hello {name}!")

greet.slashoption(name="name", type="str", required=True)
```

`<option.from"name">` notation → real method: `interaction.option_from("name")`.

---

## Anti-Nuke Channel Creation — ✅ Built & tested (new, not in the original spec)

Not part of the original notation spec, but real and shipped as of
v0.2.4 — automatic, no setup required:

```python
await interaction.create_channel(name=channel_name)
```

Guards against rapid creation (< 5 seconds apart) and suspicious
name patterns automatically.

---

## Errors / Views / Tasks / Sharding / Config — ⚠️ Notation only, never implemented

```
.error[scope=](<ctx>, <error>):
.view[timeout=]:
.task[seconds=/minutes=/hours=]:
.shard[count=]
.config[source=]
```

None of these have a real Python implementation yet. The closest
real equivalents that do exist:
- **Errors:** caught automatically via `client.dispatch()`'s
  `safe_dispatch()` wrapper, logged with beginner-friendly messages —
  not a per-command `.error[]` decorator yet.
- **Config:** no dedicated loader — plain `config.py` or `config.json`
  loaded with normal Python, no Diseasy-specific convention.
- Views, tasks, and sharding have no implementation at all yet.

---

## Fetch (Local Database) — ✅ Built & tested (not in the original spec)

Not part of the original notation spec, but real and shipped as of
v0.2.1 — JSON-backed only (no MongoDB/SQL):

```python
from diseasy import fetch, insert, update, delete

insert("users", {"id": 123, "points": 10})
user = fetch("users", filter={"id": 123})
update("users", filter={"id": 123}, changes={"points": 100})
```

---

## Voice

Explicitly out of scope for Diseasy — not a design goal.
