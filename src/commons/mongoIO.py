from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import models.exceptions as Exceptions

if TYPE_CHECKING:
    from typing import Optional
    from typing import Any
    from models.bot import Sunny


class mongoIO:
    def __init__(self, bot: Sunny) -> None:
        self.config = bot.config
        self.db = bot.motorClient[self.config.mongo.database]

    async def add_user(
        self,
        member: discord.Member,
        blacklist: bool = False,
        osu_id: Optional[int] = None,
        osu_server: int = 0,
    ) -> None:
        await self.db.users.insert_one(
            {
                "id": member.id,
                "name": member.name,
                "blacklisted": blacklist,
                "osu": osu_id,
                "preferredServer": osu_server,
            },
        )

    async def remove_user(self, member: discord.Member) -> None:
        await self.db.users.delete_many({"id": member.id})

    async def user_exists(self, member: discord.Member) -> bool:
        return (await self.db.users.find_one({"id": {"$eq": member.id}})) is not None

    async def get_osu(self, member: discord.Member) -> int:
        if (
            databaseUser := await self.db.users.find_one({"id": {"$eq": member.id}})
        ) is None:
            raise Exceptions.DatabaseMissingError("osu")
        # if "preferredServer" not in databaseUser:
        #    databaseUser["preferredServer"] = 0
        return databaseUser["osu"]  # , int(databaseUser["preferredServer"])

    async def set_osu(
        self,
        member: discord.Member,
        osu_id: int,
        osu_server: int = 0,
    ) -> None:
        if not await self.user_exists(member):
            await self.add_user(member, False, osu_id)
        else:
            await self.db.users.update_one(
                {"id": member.id},
                {
                    "$set": {"osu": osu_id, "preferredServer": osu_server},
                    "$currentDate": {"lastModified": True},
                },
            )

    async def blacklist_user(self, member: discord.Member) -> None:
        if not await self.user_exists(member):
            await self.add_user(member, False, member.id)
        else:
            await self.db.users.update_one(
                {"id": member.id},
                {"$set": {"blacklisted": True}, "$currentDate": {"lastModified": True}},
            )

    async def unblacklist_user(self, member: discord.Member) -> None:
        if not await self.user_exists(member):
            await self.add_user(member, False, member.id)
        else:
            await self.db.users.update_one(
                {"id": member.id},
                {
                    "$set": {"blacklisted": False},
                    "$currentDate": {"lastModified": True},
                },
            )

    async def is_blacklisted(self, member: discord.Member) -> bool:
        if (
            db_user := await self.db.users.find_one({"id": {"$eq": member.id}})
        ) is None:
            return False
        return db_user["blacklisted"]

    async def add_guild(
        self,
        guild: discord.Guild,
        prefix: Optional[str] = None,
    ) -> None:
        await self.db.settings.insert_one({"id": guild.id, "prefix": prefix})

    async def remove_guild(self, guild: discord.Guild) -> None:
        await self.db.settings.delete_many({"guildID": guild.id})

    async def guild_exists(self, guild: discord.Guild) -> bool:
        return await self.db.settings.find_one({"id": {"$eq": guild.id}}) is not None

    async def get_setting(self, guild: discord.Guild, setting: str) -> Any:
        if (
            db_guild := await self.db.settings.find_one({"id": {"$eq": guild.id}})
        ) is None:
            return None
        return db_guild[setting]

    async def set_prefix(self, guild: discord.Guild, prefix: str) -> None:
        if not await self.guild_exists(guild):
            await self.add_guild(guild, prefix)
        else:
            await self.db.settings.update_one(
                {"id": guild.id},
                {"$set": {"prefix": prefix}, "$currentDate": {"lastModified": True}},
            )

    async def wipe(self) -> None:
        await self.db.users.delete_many({})
        await self.db.settings.delete_many({})
