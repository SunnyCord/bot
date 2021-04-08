import discord, asyncio
from discord.utils import get
from discord.ext import commands

class CronTask(commands.Cog):
    """Database maintenance task"""
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.cron())

    async def cron(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            await asyncio.sleep(300) # Check every 5 minutes

def setup(bot):
    bot.add_cog(CronTask(bot))