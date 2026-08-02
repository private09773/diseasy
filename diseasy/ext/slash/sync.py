"""Registers slash commands with Discord via the HTTP client
(bulk overwrite endpoint, matching .slashcommand[]/.slashoption[] definitions)."""


async def sync_commands(client, application_id: int, commands: list) -> dict:
    payload = [cmd.to_dict() for cmd in commands]
    return await client._http.register_slash_commands(application_id, payload)
