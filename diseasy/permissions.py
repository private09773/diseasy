"""
diseasy/permissions.py (v0.1.1a)

Expands on v0.1.1's user-only Permissions class by adding a
BotPermissions class for checking what the bot itself can do in a
guild/channel — important before attempting actions that would
otherwise fail with a 403 from Discord's API.
"""


class Permissions:
    """User-level permission checks (unchanged from v0.1.1)."""

    def __init__(self, member):
        self.member = member
        self.perms = member.guild_permissions

    def has(self, *flags):
        return all(getattr(self.perms, flag, False) for flag in flags)

    def has_any(self, *flags):
        return any(getattr(self.perms, flag, False) for flag in flags)

    def is_admin(self):
        return self.perms.administrator

    def is_owner(self, guild):
        return self.member.id == guild.owner_id


class BotPermissions:
    """
    New in v0.1.1a — checks what the bot itself can do, using the
    bot's own member object in a guild. Useful for pre-flight checks
    before attempting an action that would otherwise fail.
    """

    def __init__(self, guild, bot_member):
        self.guild = guild
        self.member = bot_member
        self.perms = bot_member.guild_permissions

    def can(self, *flags):
        return all(getattr(self.perms, flag, False) for flag in flags)

    def can_any(self, *flags):
        return any(getattr(self.perms, flag, False) for flag in flags)

    def highest_role_position(self):
        return self.member.top_role.position

    def can_act_on(self, target_member):
        """
        Whether the bot's top role sits above the target member's
        top role — required for actions like kick/ban/role changes.
        """
        return self.highest_role_position() > target_member.top_role.position


def check_bot_permissions(guild, bot_member, *required_flags):
    """
    Convenience helper: raises a clear error instead of letting the
    action fail silently or with an opaque Discord 403.
    """
    bp = BotPermissions(guild, bot_member)
    if not bp.can(*required_flags):
        missing = [f for f in required_flags if not getattr(bp.perms, f, False)]
        raise PermissionError(
            f"Bot is missing required permission(s): {', '.join(missing)}"
        )
