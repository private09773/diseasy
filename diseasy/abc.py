"""Abstract interfaces shared across models."""
from abc import ABC, abstractmethod


class Snowflake(ABC):
    """Anything with a Discord snowflake id."""

    id: int


class Messageable(ABC):
    """Anything that supports .send() — channels, users, interactions."""

    @abstractmethod
    async def send(self, content: str = None, *, embed=None, view=None):
        ...
