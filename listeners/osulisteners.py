import re
from discord.ext import commands
from commons.osu import osuapiwrap as osuAPI

class OsuListeners(commands.Cog, command_attrs=dict(hidden=True), name="osu! Chat Listener"):
    """osu! Message Listeners"""

    def __init__(self, bot):

        self.bot = bot
        self.osuAPI = osuAPI.APIService(bot.configs.OSUCFG.token)
        self.pattern = re.compile("(https?):\/\/([-\w._]+)(\/[-\w._]\?(.+)?)?(\/b\/(?P<bmapid1>[0-9]+)|\/s\/(?P<bmapsetid1>[0-9]+)|\/beatmapsets\/(?P<bmapsetid2>[0-9]+)#(?P<mode>[a-z]+)\/(?P<bmapid2>[0-9]+))")

    @commands.Cog.listener()
    async def on_message(self, message):

        result = re.match(self.pattern, message.content)

        if result is None:
            return

        s, b = None, None
        if result.group("bmapid2") is not None:
            s = result.group("bmapsetid2")
            b = result.group("bmapid2")

        elif result.group("bmapid1") is not None:
            b = result.group("bmapid1")

        else:
            s = result.group("bmapset1")

        beatmap = await self.osuAPI.getbmap(b=b, s=s)
        await message.channel.send(f"Found beatmap {beatmap[0]['title']}")



def setup(bot):
    bot.add_cog(OsuListeners(bot))