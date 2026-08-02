import pytest

from diseasy.errors import MissingPermissions, CommandOnCooldown, CustomError


def test_missing_permissions_message():
    err = MissingPermissions(["manage_messages", "kick_members"])
    assert "manage_messages" in str(err)
    assert err.missing == ["manage_messages", "kick_members"]


def test_command_on_cooldown_retry_after():
    err = CommandOnCooldown(3.5)
    assert err.retry_after == 3.5


def test_custom_error():
    err = CustomError(name="ExampleError", message="something broke")
    assert err.name == "ExampleError"
    assert str(err) == "something broke"
