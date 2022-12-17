from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from ui.embeds.fun import PollEmbed

if TYPE_CHECKING:
    from classes.bot import Sunny


class Fun(commands.Cog):
    """
    Miscellaneous commands.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="poll", description="Creates a reaction poll")
    @app_commands.describe(text="Text for the poll")
    async def poll_command(
        self, interaction: discord.Interaction, *, text: str
    ) -> None:

        try:
            await interaction.message.delete()
        except discord.Forbidden:
            pass

        embed = PollEmbed(interaction, text)

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        await message.add_reaction("👍")
        await message.add_reaction("👎")
        await message.add_reaction("🤷")

    @app_commands.command(name="ping", description="Pings the bot")
    async def ping_command(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(
            f"🏓 Pong!: {self.bot.latency*1000:.2f}ms",
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Fun(bot))
