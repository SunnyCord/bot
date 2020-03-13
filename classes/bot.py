import discord
from motor import motor_asyncio
from classes.config import Config
from commons.mongoIO import mongoIO

class Sunny(discord.ext.commands.AutoShardedBot):

    @staticmethod
    async def __get_prefix(self, message):
        """A callable Prefix for our bot. This could be edited to allow per server prefixes."""
        if await self.mongoIO.isBlacklisted(message.author) or not message.guild:
            return ' '
        guildPref = await self.mongoIO.getSetting(message.guild, 'prefix') if message.guild else None
        result = self.config.command_prefixes + [guildPref] if guildPref is not None else self.config.command_prefixes
        return discord.ext.commands.when_mentioned_or(*result)(self, message)

    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description"),
            command_prefix=self.__get_prefix,
            activity=kwargs.pop("activity")
        )
        self.config=Config.fromJSON("config.json")
        self.motorClient = motor_asyncio.AsyncIOMotorClient(self.config.mongo['URI'], serverSelectionTimeoutMS=self.config.mongo['timeout'])
        self.mongoIO = mongoIO(self)

    async def on_message(self, msg): # Ignore messages
        if not self.is_ready() or msg.author.bot:
           return
        await self.process_commands(msg)

    async def is_owner(self, user: discord.User):
        if user.id in self.config.owners:
            return True

        # Else fall back to the original
        return await super().is_owner(user)
    
