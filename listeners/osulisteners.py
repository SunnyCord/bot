import re
from discord.ext import commands
from commons.osu import osuapiwrap as osuAPI

class OsuListeners(commands.Cog, command_attrs=dict(hidden=True), name="osu! Chat Listener"):
    """osu! Message Listeners"""

    def __init__(self, bot):

        self.bot = bot
        self.osuAPI = osuAPI.APIService(bot.configs.OSUCFG.token)

    @commands.Cog.listener()
    async def on_message(self, message):
        #pattern = "(https?):\/\/([-\w._]+)(\/[-\w._]\?(.+)?)?(\/b\/([0-9]+)|/s\/([0-9]+)|\/beatmapsets\/([0-9]+)#[a-z]+\/([0-9]+))"
        pattern = "(https?):\/\/([-\w._]+)(\/[-\w._]\?(.+)?)?(\/b\/(?P<bmapid1>[0-9]+)|\/s\/(?P<bmapsetid1>[0-9]+)|\/beatmapsets\/(?P<bmapsetid2>[0-9]+)#(?P<mode>[a-z]+)\/(?P<bmapid2>[0-9]+))"
        result = re.match(pattern, message.content)

        if result is None:
            return await self.bot.process_commands(message)

        s, b = '', ''

        if result.group("bmapid2") is not None:
            s = result.group("bmapsetid2")
            b = result.group("bmapid2")

        elif result.group("bmapid1") is not None:
            b = result.group("bmapid1")

        else:
            s = result.group("bmapset1")

        await message.channel.send(f'Found beatmap {s}/{b}')
        


def setup(bot):
    bot.add_cog(OsuListeners(bot))