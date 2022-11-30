from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from ui.embeds.information import BotInfoEmbed
from ui.embeds.information import ServerInfoEmbed


class Information(commands.Cog):
    """
    Retrieve information about various items.
    """

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="botinfo",
        description="Retrieve information about the bot.",
    )
    async def info_bot_command(self, interaction: discord.Information) -> None:
        embed = BotInfoEmbed(interaction)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="serverinfo",
        description="Retrieve information about the current server.",
    )
    async def info_server_command(self, interaction: discord.Interaction) -> None:
        embed = ServerInfoEmbed(interaction)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Information(bot))
