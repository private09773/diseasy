from diseasy.enums import OpCode
from diseasy.flags import Intents


def test_opcode_values():
    assert OpCode.DISPATCH == 0
    assert OpCode.HELLO == 10
    assert OpCode.HEARTBEAT_ACK == 11


def test_intents_from_names():
    intents = Intents.from_names(["guilds", "messages"])
    assert Intents.guilds in intents
    assert Intents.messages in intents
    assert Intents.members not in intents
