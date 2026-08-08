"""
diseasy/dashboard.py

Dashboard integration — read-only status/data views, plus
EXPERIMENTAL management actions (unload a cog, change presence)
that let a dashboard actually control a running bot, not just
observe it.

Marked experimental deliberately: no authentication yet (anyone who
can reach the port can manage the bot), limited action set, and the
full feature is planned for v0.5, not considered stable here.

Technical note: Flask runs in a background thread, separate from the
bot's asyncio event loop. Write actions can't safely touch the bot's
state directly from that thread — they're marshalled onto the bot's
real event loop via asyncio.run_coroutine_threadsafe(), so nothing
races with the bot's own message/event handling.
"""

import asyncio
import threading
from flask import Flask, jsonify, request, render_template_string

from .fetch import fetch as fetch_data


STATUS_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Diseasy Dashboard (Experimental)</title>
    <style>
        body { font-family: sans-serif; background: #1e1f22; color: #ddd; padding: 2rem; }
        h1 { color: #5865F2; }
        .stat { background: #2b2d31; padding: 1rem; margin: 0.5rem 0; border-radius: 8px; }
        .label { color: #949ba4; font-size: 0.85rem; }
        .value { font-size: 1.3rem; }
        .warn { color: #f0b132; font-size: 0.85rem; margin-bottom: 1rem; }
    </style>
</head>
<body>
    <h1>{{ bot_name }} — Dashboard</h1>
    <p class="warn">⚠️ Experimental — no authentication. Anyone who can reach this
       port can manage this bot. Full dashboard support is planned for v0.5.</p>
    <div class="stat"><div class="label">Status</div><div class="value">{{ status }}</div></div>
    <div class="stat"><div class="label">Guilds</div><div class="value">{{ guild_count }}</div></div>
    <div class="stat"><div class="label">Cogs Loaded</div><div class="value">{{ cog_count }}</div></div>
</body>
</html>
"""


def _run_on_bot_loop(bot, coro, timeout: float = 5.0):
    """
    Safely runs an async coroutine on the bot's real event loop from
    Flask's background thread, and waits for the result. Raises
    RuntimeError if the bot hasn't recorded its loop yet (i.e. hasn't
    finished starting).
    """
    loop = getattr(bot, "_loop", None)
    if loop is None:
        raise RuntimeError("Bot's event loop isn't available yet — is it running?")
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=timeout)


def create_dashboard_app(bot) -> Flask:
    app = Flask(__name__)

    @app.route("/")
    def index():
        guild_count = len(getattr(bot._state, "guilds", {})) if bot._state else 0
        bot_name = getattr(getattr(bot, "user", None), "name", "Bot")
        return render_template_string(
            STATUS_PAGE,
            bot_name=bot_name,
            status="Online" if getattr(bot, "user", None) else "Starting...",
            guild_count=guild_count,
            cog_count=len(bot._cogs),
        )

    @app.route("/api/status")
    def api_status():
        guild_count = len(getattr(bot._state, "guilds", {})) if bot._state else 0
        bot_name = getattr(getattr(bot, "user", None), "name", None)
        return jsonify({
            "bot_name": bot_name,
            "online": bot_name is not None,
            "guild_count": guild_count,
            "cogs": list(bot._cogs.keys()),
        })

    @app.route("/commands")
    def commands():
        cog_commands = {}
        for cog_name, cog in bot._cogs.items():
            cog_commands[cog_name] = {
                "commands": list(getattr(cog, "__cog_commands__", {}).keys()),
                "slash_commands": list(getattr(cog, "__cog_slash_commands__", {}).keys()),
            }
        return jsonify({
            "standalone_commands": list(bot._standalone_commands.keys()),
            "standalone_slash_commands": list(bot._standalone_slash_commands.keys()),
            "cogs": cog_commands,
        })

    @app.route("/db/<collection>")
    def db_view(collection):
        try:
            data = fetch_data(collection)
            return jsonify({"collection": collection, "documents": data})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ---- EXPERIMENTAL management (write) routes ----

    @app.route("/manage/cog/<name>/unload", methods=["POST"])
    def unload_cog(name):
        if name not in bot._cogs:
            return jsonify({"error": f"Cog '{name}' is not loaded."}), 404
        try:
            async def _do():
                bot.unload_cog(name)
                return True
            _run_on_bot_loop(bot, _do())
            return jsonify({"unloaded": name})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/manage/presence", methods=["POST"])
    def set_presence():
        """
        Body: {"type": "playing"|"watching"|"listening"|"custom",
               "text": "...", "status": "online"|"idle"|"dnd"|"invisible"}
        """
        body = request.get_json(force=True, silent=True) or {}
        activity_type = body.get("type")
        text = body.get("text", "")
        status = body.get("status", "online")

        if activity_type not in ("playing", "watching", "listening", "custom"):
            return jsonify({"error": "type must be playing/watching/listening/custom"}), 400

        try:
            from .presence import playing, watching, listening, custom_status
            builders = {
                "playing": playing, "watching": watching,
                "listening": listening, "custom": custom_status,
            }
            activity = builders[activity_type](text)

            async def _do():
                await bot.set_presence(activity, status=status)
                return True

            _run_on_bot_loop(bot, _do())
            return jsonify({"presence_set": activity_type, "text": text, "status": status})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


def start_dashboard(bot, host: str = "127.0.0.1", port: int = 5000):
    """
    Starts the dashboard in a background thread so it doesn't block
    the bot's own asyncio event loop.
    """
    app = create_dashboard_app(bot)

    def run():
        app.run(host=host, port=port, debug=False, use_reloader=False)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread
