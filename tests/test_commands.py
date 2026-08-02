import asyncio

from diseasy.ext.commands import command, Cog


def test_command_arg_chain():
    @command(name="ban", description="Ban a user")
    async def ban(ctx, user):
        return user

    ban.arg("user", type="user", required=True)
    assert ban.name == "ban"
    assert ban.args[0].name == "user"
    assert ban.args[0].type == "user"


def test_cog_collects_commands():
    class MyCog(Cog):
        @command(name="hi", description="Say hi")
        async def hi(self, ctx):
            return "hi"

    cog = MyCog()
    assert "hi" in cog.__cog_commands__


def test_command_invoke():
    @command(name="echo")
    async def echo(ctx, text):
        return text

    result = asyncio.run(echo.invoke(None, "hello"))
    assert result == "hello"
