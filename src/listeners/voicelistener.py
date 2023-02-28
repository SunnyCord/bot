###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from classes.cog import MetadataCog
from discord.ext import commands

if TYPE_CHECKING:
    from discord import Member
    from discord import VoiceState
    from classes.bot import Sunny


class VoiceListener(
    MetadataCog,
    name="Voice State Update Listener",
    hidden="True",
):
    """Voice State Update Listener"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: Member,
        before: VoiceState,
        after: VoiceState,
    ) -> None:
        player = None
        for node in self.bot.pomice_node_pool.nodes.values():
            player = player or node.get_player(member.guild.id)

        if player is None:
            return

        if member == self.bot.user and after.channel is None:
            await player.destroy()
            return

        auto_disconnect = (
            await self.bot.guild_settings_service.get_auto_disconnect_status(
                member.guild.id,
            )
        )
        if (
            after.channel is None
            and len(before.channel.members) == 1
            and self.bot.user in before.channel.members
            and auto_disconnect
        ):
            await asyncio.sleep(1)
            await player.teardown()
            return


async def setup(bot: Sunny) -> None:
    await bot.add_cog(VoiceListener(bot))
