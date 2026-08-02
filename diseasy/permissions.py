import discord

class Permissions:
    """Wraps discord.Permissions for Diseasy's own permission checks."""

    def __init__(self, member: discord.Member):
        self.member = member
        self.perms = member.guild_permissions

    def has(self, *flags: str) -> bool:
        """Check if the member has ALL given permission flags.
        Example: perms.has("manage_messages", "kick_members")
        """
        return all(getattr(self.perms, flag, False) for flag in flags)

    def has_any(self, *flags: str) -> bool:
        return any(getattr(self.perms, flag, False) for flag in flags)

    def is_admin(self) -> bool:
        return self.perms.administrator

    def is_owner(self, guild: discord.Guild) -> bool:
        return self.member.id == guild.owner_id