###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import tasks

from classes.cog import MetadataCog
from common.logging import logger
from common.premium import check_premium

if TYPE_CHECKING:
    from classes.bot import Sunny


class CronTask(MetadataCog, hidden=True):
    """Database maintenance task"""

    __slots__ = ("bot",)

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.premium_task.start()

    def cog_unload(self) -> None:
        self.premium_task.cancel()

    @tasks.loop(seconds=300)
    async def premium_task(self) -> None:
        premium_guilds = await self.bot.guild_settings_service.get_all_boosted_guilds()
        for guild_id in premium_guilds:
            booster_id = await self.bot.guild_settings_service.get_premium_booster(
                guild_id,
            )
            is_premium = await check_premium(booster_id, self.bot)
            if not is_premium:
                await self.bot.guild_settings_service.set_premium_booster(
                    guild_id,
                    None,
                )
                logger.info(
                    f"Removed premium from guild {guild_id} due to expiration on booster {booster_id}",
                )

    @premium_task.before_loop
    async def before_premium_task(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: Sunny) -> None:
    await bot.add_cog(CronTask(bot))
