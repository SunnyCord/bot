import aiohttp, discord
import commons.redisIO as redisIO
from io import BytesIO
from discord.ext import commands
from commons.osu.osuhelpers import osuHelper
from classes.embeds.BeatmapEmbed import BeatmapEmbed

class OsuListeners(commands.Cog, command_attrs=dict(hidden=True), name="osu! Chat Listener"):
    """osu! Message Listeners"""

    def __init__(self, bot):
        self.bot = bot
        self.osuhelpers = osuHelper(bot.config.osuAPI)

    @commands.Cog.listener()
    async def on_message(self, message):
        beatmap = await self.osuhelpers.getBeatmapFromText(message.content, True)
        if beatmap is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://b.ppy.sh/preview/{beatmap.beatmapset_id}.mp3") as resp:
                if resp.status==200:
                    f=BytesIO(await resp.read())

        if self.bot.config.redis is True:
            redisIO.setValue(message.channel.id, beatmap.beatmap_id)
            redisIO.setValue(f'{message.channel.id}.mode', beatmap.mode)

        await message.channel.send(embed=BeatmapEmbed(beatmap, self.bot.config.color), file=discord.File(f, filename="Preview.mp3"))


def setup(bot):
    bot.add_cog(OsuListeners(bot))