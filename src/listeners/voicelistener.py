from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands
from models.cog import MetadataCog

if TYPE_CHECKING:
    from discord import Member
    from discord import VoiceState
    from models.bot import Sunny


class VoiceListener(
    MetadataCog,
    name="Voice State Update Listener",
    hidden="True",
):  # type: ignore
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
        player = self.bot.lavalink.player_manager.get(member.guild.id)

        if player is None or not player.is_connected:
            return

        # Disconnect if channel is empty
        channel = await self.bot.fetch_channel(player.channel_id)
        if len(channel.members) == 1:
            player.queue.clear()
            await player.stop()
            await member.guild.change_voice_state(channel=None)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(VoiceListener(bot))
