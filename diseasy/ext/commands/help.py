"""A minimal built-in help command generator."""


class HelpCommand:
    def __init__(self, client):
        self.client = client

    def generate(self) -> str:
        lines = ["Available commands:"]
        for name, cmd in getattr(self.client, "commands", {}).items():
            lines.append(f"  {name} — {cmd.description or 'no description'}")
        return "\n".join(lines)
