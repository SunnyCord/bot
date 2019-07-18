from discord.ext import commands

class OsuListeners(commands.Cog, command_attrs=dict(hidden=True), name="osu! Chat Listener"):
    """osu! Message Listeners"""

    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        await self.bot.process_commands(message)


def setup(bot):
    bot.add_cog(OsuListeners(bot))