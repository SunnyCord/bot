import discord
from discord.ext import commands


class VoiceListener(
    commands.Cog, command_attrs=dict(hidden=True), name="Voice State Update Listener"
):
    """Voice State Update Listener"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = self.bot.lavalink.player_manager.get(member.guild.id)

        if player is None or not player.is_connected:
            return

        # Disconnect if channel is empty
        channel = await self.bot.fetch_channel(player.channel_id)
        if len(channel.members) == 1:
            player.queue.clear()
            await player.stop()
            await member.guild.change_voice_state(channel=None)


async def setup(bot):
    await bot.add_cog(VoiceListener(bot))
