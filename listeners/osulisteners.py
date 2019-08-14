import re
from discord.ext import commands
from commons.osu import osuapiwrap
from commons.osu import osuhelpers

class OsuListeners(commands.Cog, command_attrs=dict(hidden=True), name="osu! Chat Listener"):
    """osu! Message Listeners"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        beatmap = await osuhelpers.getBeatmapFromText(message.content)
        if beatmap is None:
            return
        await message.channel.send(f"Found beatmap {beatmap['title']}")


def setup(bot):
    bot.add_cog(OsuListeners(bot))