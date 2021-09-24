import discord
from discord.ext import commands
from motor import motor_asyncio
from classes.config import Config
from commons.mongoIO import mongoIO
from commons.osu.ppwrap import ppAPI
from commons.osu.osuapiwrap import osuAPI
from commons.osu.osuhelpers import osuHelper

class Sunny(commands.AutoShardedBot):

    @staticmethod
    async def __get_prefix(self, message):
        """A callable Prefix for our bot. This also has the ability to ignore certain messages by passing an empty string."""
        guildPref = await self.mongoIO.getSetting(message.guild, 'prefix')
        result = self.config.command_prefixes.copy()
        if guildPref is not None:
            result += [guildPref]
        return commands.when_mentioned_or(*result)(self, message)

    @staticmethod
    async def ensure_member(query, guild: discord.Guild):
        if (member := guild.get_member(query)) is None:
            member = await guild.fetch_member(query)
        return member

    def __init__(self, **kwargs):
        intents = discord.Intents.default()
        intents.members=True
        super().__init__(
            description=kwargs.pop("description"),
            command_prefix=self.__get_prefix,
            intents=intents, # To be reverted to discord.Intents.all() once verification complete
            activity=kwargs.pop("activity")
        )
        self.config=Config.fromJSON("config.json")
        self.motorClient = motor_asyncio.AsyncIOMotorClient(self.config.mongo['URI'], serverSelectionTimeoutMS=self.config.mongo['timeout'])
        self.mongoIO = mongoIO(self)
        self.osuAPI = osuAPI(self.config.osuAPI)
        self.osuHelpers = osuHelper(self)
        self.ppAPI = ppAPI(self.config.ppAPI["URL"], self.config.ppAPI["secret"])

    async def ensure_guild(self, query):
        if (guild := self.get_guild(query)) is None:
            guild = await self.fetch_guild(query)
        return guild

    async def on_message(self, msg):
        ignore = not msg.guild
        ignore |= msg.author.bot
        ignore |= not self.is_ready()
        ignore |= await self.mongoIO.isBlacklisted(msg.author)
        if ignore:
           return
        await self.process_commands(msg)

    async def is_owner(self, user: discord.User):
        if user.id in self.config.owners:
            return True
        # Else fall back to the original
        return await super().is_owner(user)

