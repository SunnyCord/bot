import discord, asyncio
from discord.ext import commands

class CronTask(commands.Cog):
    """Database maintenance task"""
    def __init__(self, bot):
        self.bot = bot
        self.task = self.bot.loop.create_task(self.cron())

    async def cron(self):

        await self.bot.wait_until_ready()

        while not self.bot.is_closed():

            mutes = await self.bot.mongoIO.getExpiredMutes()

            for mute in mutes:
                guild = await self.bot.ensure_guild(mute['guildID'])
                member = await self.bot.ensure_member(mute['memberID'], guild)
                rolem = discord.utils.get(guild.roles, name='Muted')
                if rolem in member.roles:
                    try:
                        await member.remove_roles(rolem)
                        await self.bot.mongoIO.unmuteUser(member, guild)
                    except Exception:
                        print(f'User {member.name} could not be unmuted!')

            await asyncio.sleep(10) # Check every 10 seconds

def setup(bot):
    bot.add_cog(CronTask(bot))