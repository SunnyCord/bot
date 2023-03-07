###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from classes.cog import MetadataCog

if TYPE_CHECKING:
    from discord import Member
    from discord import VoiceState
    from classes.bot import Sunny
    from classes.pomice import Player


class VoiceListener(
    MetadataCog,
    name="Voice State Update Listener",
    hidden="True",
):
    """Voice State Update Listener"""

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @MetadataCog.listener()
    async def on_voice_state_update(
        self,
        member: Member,
        before: VoiceState,
        after: VoiceState,
    ) -> None:
        player: Player = None
        for node in self.bot.pomice_node_pool.nodes.values():
            player = player or node.get_player(member.guild.id)

        if player is None:
            return

        if member == self.bot.user and after.channel is None:
            await player.destroy()
            return

        if (
            after.channel is None
            and len(before.channel.members) == 1
            and self.bot.user in before.channel.members
            and player.guild_settings.voice_auto_disconnect
        ):
            await asyncio.sleep(1)
            await player.teardown()
            return


async def setup(bot: Sunny) -> None:
    await bot.add_cog(VoiceListener(bot))
