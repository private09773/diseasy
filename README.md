# Diseasy

A from-scratch Python library for building Discord bots — a discord.py-inspired
alternative with its own notation-driven API for commands, cogs, embeds v1/v2,
components, and events.

## Features
- Gateway + REST client built from scratch
- Slash and prefix commands
- Cogs for modular bot organization
- Embeds (classic) and Components (container-based components)
- Buttons, select menus, modals, persistent views
- Task loops, sharding, rate-limit handling

## Installation
```bash
pip install diseasy
```

## Quick Example
``` python
import diseasy

client = diseasy.Client(intents=["guilds", "messages"])

@client.event(name="on_ready")
async def on_ready():
    print("Diseasy is ready.")

client.run("TOKEN") 
```
*The example here is outdated, please refer to the examples folder as it will be updated soon.*

## Documentation
See docs/ for the full API reference and notation spec.

## Contributing
See CONTRIBUTING.md.

## License
GPL — see LICENSE.
