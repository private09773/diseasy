# Changelog

All notable changes to Diseasy are documented here.

## v0.2.3

**Added**
- `logger.py` now detects and logs connection errors and online/offline status automatically
- Beginner-friendly error messages — common exceptions (`TypeError`, `AttributeError`, `KeyError`, `NameError`, `ValueError`) are translated into plain-language hints instead of raw tracebacks
- Presence functions (`playing`, `watching`, `listening`, `custom_status`) exposed at the top level — `from diseasy import playing` instead of `from diseasy.presence import playing`
- Real `Embed` class for Embeds v1, matching Discord's actual embed schema — `title`, `description`, `add_field()`, `set_footer()`, `set_thumbnail()`, `set_image()`
- `<var>` resolution now works inside embeds (title, description, fields, footer), not just plain message text

**Fixed**
- `client.dispatch()` no longer silently swallows exceptions from event/command callbacks — they're now caught and logged
- `client.user` is now actually set from the gateway's READY payload (previously never populated)
- `__init__.py` no longer imports a function that didn't exist (`setup_logging`, renamed to `set_log_level` back in 0.1.1a)

---

## v0.2.1

**Added**
- Standalone command support — a `@command`-decorated function defined directly in `main.py` now works, not just inside cogs
- `cogs = []` list pattern for loading all bot features from one place
- Real JSON-backed `fetch()` implementation (insert, fetch, update, delete)
- Gateway presence wiring (`bot.set_presence(...)`)
- Interaction routing by command name, so slash commands dispatch correctly

**Fixed**
- `@slash_command` inside a `Cog` was previously never collected — now works alongside regular `@command`
- `Interaction` now exposes `.command_name` and a real `.send()` method wired to Discord's interaction response endpoint

**Changed**
- Dropped the `.dsy` notation/parser workflow in favor of plain Python — no compile step needed, deployable on any hosting platform as-is

---

## v0.2

- Introduced the notation/"easy syntax" (`.command:`, `.event:`, `.slash:`, `.embed[]`, `.container[]`, `client_import():`, etc.)
- Built `parser.py`, a transpiler that compiles `.dsy` notation files into real Python
- Covered commands, events, slash commands with options, embeds v1, containers (embeds v2), assets, and startup configuration (intents, prefix, token, presence, cog loading) in the notation

---

## v0.1.1

- Logging on bot startup
- 30+ built-in `<var>` variables (user, guild, channel, message, bot, time)
- Early implementation of user permissions

---

## v0.1.0

The first official release of Diseasy — core features and Embeds v2. Permissions coming soon (delivered in v0.1.1).
