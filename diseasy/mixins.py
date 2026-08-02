"""Shared mixins for Diseasy model objects."""


class Hashable:
    """Gives a model object identity-based equality and hashing via its .id."""

    __slots__ = ()

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.id >> 22
