import os
import discord
import logging
from discord.ext import commands
from motor import motor_asyncio
from classes.config import Config
from commons.mongoIO import mongoIO
from commons.osu.ppwrap import ppAPI
from commons.helpers import list_module
from commons.osu.osuapiwrap import osuAPI
from commons.osu.osuhelpers import osuHelper

logger = logging.getLogger()


class Sunny(commands.AutoShardedBot):
    async def setup_hook(self):
        await self.load_extension("jishaku")

        module_folders = ["listeners", "cogs", "tasks"]
        for module in module_folders:
            for extension in list_module(module):
                name = f"{module}.{os.path.splitext(extension)[0]}"
                try:
                    await self.load_extension(name)
                except Exception as e:
                    logging.error(f"Failed loading module {name} : {e}")

    @staticmethod
    async def __get_prefix(self, message):
        """A callable Prefix for our bot. This also has the ability to ignore certain messages by passing an empty string."""
        guildPref = await self.mongoIO.getSetting(message.guild, "prefix")
        result = self.config.command_prefixes.copy()
        if guildPref is not None:
            result += [guildPref]
        return commands.when_mentioned_or(*result)(self, message)

    @staticmethod
    async def ensure_member(query, guild: discord.Guild):
        if (member := guild.get_member(query)) is None:
            member = await guild.fetch_member(query)
        return member

    def __init__(self, **kwargs) -> None:
        super().__init__(
            description="Sunny Bot",
            command_prefix=self.__get_prefix,
            intents=discord.Intents.all(),
            # activity=discord.Activity(),
            help_command=None,
        )
        self.config = Config.fromJSON("config.json")
        self.motorClient = motor_asyncio.AsyncIOMotorClient(
            self.config.mongo["URI"],
            serverSelectionTimeoutMS=self.config.mongo["timeout"],
        )
        self.mongoIO = mongoIO(self)
        self.osuAPI = osuAPI(self.config.osuAPI)
        self.osuHelpers = osuHelper(self)
        self.ppAPI = ppAPI(self.config.ppAPI["URL"], self.config.ppAPI["secret"])

    def run(self, **kwargs) -> None:
        super().run(
            self.config.token, log_level="INFO", **kwargs
        )  # self.config.log_level

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
