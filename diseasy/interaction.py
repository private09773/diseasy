# NOTE: Interaction currently lives inside diseasy/ext/slash/core.py
# (there wasn't a separate interaction.py file in what we've seen) —
# this is that class updated, ready to paste over the existing
# Interaction class in core.py. If you do want it split into its own
# file, this can be saved as diseasy/ext/slash/interaction.py and
# imported into core.py instead.

class Interaction:
    """Wraps a raw interaction payload and exposes <option.from""> access."""

    def __init__(self, data: dict, http=None):
        self._data = data
        self._http = http
        self.id = data.get("id")
        self.token = data.get("token")
        self._options = {
            opt["name"]: opt.get("value")
            for opt in data.get("data", {}).get("options", [])
        }

    def option_from(self, name: str):
        """Equivalent to the notation's <option.from"name">."""
        return self._options.get(name)

    async def send(self, message: str = "", *, embed=None, components=None, ephemeral=False):
        """
        Responds to this interaction. Requires self._http to have
        been set at construction time.

        ASSUMPTION FLAG: whatever code currently constructs
        Interaction(data) — likely in gateway.py on INTERACTION_CREATE —
        needs to change to Interaction(data, http=self._http) for this
        to work. That call site hasn't been located/confirmed yet.
        """
        if self._http is None:
            raise RuntimeError(
                "Interaction has no HTTP client attached — it must be "
                "constructed with Interaction(data, http=client._http)."
            )
        return await self._http.create_interaction_response(
            self.id,
            self.token,
            content=message,
            embeds=[embed] if embed else None,
            components=components,
            ephemeral=ephemeral,
        )
