VARIABLES = {}

def register(name):
    def decorator(func):
        VARIABLES[name] = func
        return func
    return decorator


# ---- User ----
@register("user.name")
def _user_name(ctx): return ctx.author.name

@register("user.id")
def _user_id(ctx): return ctx.author.id

@register("user.mention")
def _user_mention(ctx): return ctx.author.mention

@register("user.discriminator")
def _user_discriminator(ctx): return getattr(ctx.author, "discriminator", None)

@register("user.avatar")
def _user_avatar(ctx): return str(ctx.author.avatar_url) if hasattr(ctx.author, "avatar_url") else None

@register("user.joined_at")
def _user_joined_at(ctx): return getattr(ctx.author, "joined_at", None)

@register("user.guild_join.at")
def _user_guild_join_at(ctx): return getattr(ctx.author, "guild_joined_at", None)
    
@register("user.top_role")
def _user_top_role(ctx): return getattr(ctx.author, "top_role", None)

@register("user.is_bot")
def _user_is_bot(ctx): return ctx.author.bot


# ---- Guild ----
@register("guild.name")
def _guild_name(ctx): return ctx.guild.name

@register("guild.id")
def _guild_id(ctx): return ctx.guild.id

@register("guild.member_count")
def _guild_member_count(ctx): return ctx.guild.member_count

@register("guild.owner")
def _guild_owner(ctx): return ctx.guild.owner

@register("guild.owner_id")
def _guild_owner_id(ctx): return ctx.guild.owner_id

@register("guild.icon")
def _guild_icon(ctx): return str(ctx.guild.icon_url) if hasattr(ctx.guild, "icon_url") else None

@register("guild.created_at")
def _guild_created_at(ctx): return ctx.guild.created_at

@register("guild.region")
def _guild_region(ctx): return getattr(ctx.guild, "region", None)

@register("guild.boost_count")
def _guild_boost_count(ctx): return getattr(ctx.guild, "premium_subscription_count", None)


# ---- Channel ----
@register("channel.name")
def _channel_name(ctx): return ctx.channel.name

@register("channel.id")
def _channel_id(ctx): return ctx.channel.id

@register("channel.mention")
def _channel_mention(ctx): return ctx.channel.mention

@register("channel.topic")
def _channel_topic(ctx): return getattr(ctx.channel, "topic", None)

@register("channel.is_nsfw")
def _channel_is_nsfw(ctx): return getattr(ctx.channel, "nsfw", False)

@register("channel.category")
def _channel_category(ctx): return getattr(ctx.channel, "category", None)


# ---- Message ----
@register("message.id")
def _message_id(ctx): return ctx.message.id

@register("message.content")
def _message_content(ctx): return ctx.message.content

@register("message.created_at")
def _message_created_at(ctx): return ctx.message.created_at

@register("message.attachments")
def _message_attachments(ctx): return len(ctx.message.attachments)

@register("message.jump_url")
def _message_jump_url(ctx): return getattr(ctx.message, "jump_url", None)


# ---- Bot / Client ----
@register("bot.name")
def _bot_name(ctx): return ctx.bot.user.name

@register("bot.id")
def _bot_id(ctx): return ctx.bot.user.id

@register("bot.latency")
def _bot_latency(ctx): return round(ctx.bot.latency * 1000)

@register("bot.guild_count")
def _bot_guild_count(ctx): return len(ctx.bot.guilds)

@register("bot.uptime")
def _bot_uptime(ctx): return getattr(ctx.bot, "uptime", None)


# ---- Time ----
@register("time.now")
def _time_now(ctx):
    import datetime
    return datetime.datetime.utcnow()

@register("time.timestamp")
def _time_timestamp(ctx):
    import time
    return int(time.time())