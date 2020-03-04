import re, aiohttp, discord
from io import BytesIO
from discord.ext import commands
from commons.osu import osuapiwrap
from commons.osu import osuhelpers
from commons.mongoIO import getOsu
from commons.embeds.BeatmapEmbed import BeatmapEmbed

class OsuListeners(commands.Cog, command_attrs=dict(hidden=True), name="osu! Chat Listener"):
    """osu! Message Listeners"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        beatmap = await osuhelpers.getBeatmapFromText(message.content)
        if beatmap is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://b.ppy.sh/preview/{beatmap.beatmapset_id}.mp3") as resp:
                if resp.status==200:
                    f=BytesIO(await resp.read())
        botReply = await message.channel.send(embed=BeatmapEmbed(beatmap), file=discord.File(f, filename="Preview.mp3"))


def setup(bot):
    bot.add_cog(OsuListeners(bot))