from __future__ import annotations

from typing import TYPE_CHECKING

import classes.exceptions as Exceptions
import discord

if TYPE_CHECKING:
    from typing import Optional
    from typing import Any
    from classes.bot import Sunny


class mongoIO:
    def __init__(self, bot: Sunny) -> None:
        self.config = bot.config
        self.db = bot.motorClient[self.config.mongo.database]

    async def addUser(
        self,
        member: discord.Member,
        blacklist: bool = False,
        osuID: Optional[int] = None,
        osuServer: int = 0,
    ) -> None:
        await self.db.users.insert_one(
            {
                "blacklisted": blacklist,
                "id": member.id,
                "name": member.name,
                "osu": osuID,
                "preferredServer": osuServer,
            },
        )

    async def removeUser(self, member: discord.Member) -> None:
        await self.db.users.delete_many({"id": member.id})

    async def userExists(self, member: discord.Member) -> bool:
        return (await self.db.users.find_one({"id": {"$eq": member.id}})) is not None

    async def getOsu(self, member: discord.Member) -> int:
        if (
            databaseUser := await self.db.users.find_one({"id": {"$eq": member.id}})
        ) is None:
            raise Exceptions.DatabaseMissingError("osu")
        # if "preferredServer" not in databaseUser:
        #    databaseUser["preferredServer"] = 0
        return databaseUser["osu"]  # , int(databaseUser["preferredServer"])

    async def setOsu(
        self,
        member: discord.Member,
        osuID: int,
        osuServer: int = 0,
    ) -> None:
        if not await self.userExists(member):
            await self.addUser(member, False, osuID)
        else:
            await self.db.users.update_one(
                {"id": member.id},
                {
                    "$set": {"osu": osuID, "preferredServer": osuServer},
                    "$currentDate": {"lastModified": True},
                },
            )

    async def blacklistUser(self, member: discord.Member) -> None:
        if not await self.userExists(member):
            await self.addUser(member, False, member.id)
        else:
            await self.db.users.update_one(
                {"id": member.id},
                {"$set": {"blacklisted": True}, "$currentDate": {"lastModified": True}},
            )

    async def unblacklistUser(self, member: discord.Member) -> None:
        if not await self.userExists(member):
            await self.addUser(member, False, member.id)
        else:
            await self.db.users.update_one(
                {"id": member.id},
                {
                    "$set": {"blacklisted": False},
                    "$currentDate": {"lastModified": True},
                },
            )

    async def isBlacklisted(self, member: discord.Member) -> bool:
        if (
            databaseUser := await self.db.users.find_one({"id": {"$eq": member.id}})
        ) is None:
            return False
        return databaseUser["blacklisted"]

    async def addServer(
        self,
        server: discord.Guild,
        prefix: Optional[str] = None,
    ) -> None:
        await self.db.settings.insert_one({"id": server.id, "prefix": prefix})

    async def removeServer(self, guild: discord.Guild) -> None:
        await self.db.settings.delete_many({"guildID": guild.id})

    async def serverExists(self, server: discord.Guild) -> bool:
        return await self.db.settings.find_one({"id": {"$eq": server.id}}) is not None

    async def getSetting(self, server: discord.Guild, setting: str) -> Any:
        if (
            databaseGuild := await self.db.settings.find_one({"id": {"$eq": server.id}})
        ) is None:
            return None
        return databaseGuild[setting]

    async def setPrefix(self, server: discord.Guild, prefix: str) -> None:
        if not await self.serverExists(server):
            await self.addServer(server, prefix)
        else:
            await self.db.settings.update_one(
                {"id": server.id},
                {"$set": {"prefix": prefix}, "$currentDate": {"lastModified": True}},
            )

    async def wipe(self) -> None:
        await self.db.users.delete_many({})
        await self.db.settings.delete_many({})
