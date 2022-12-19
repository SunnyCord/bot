from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from classes.cog import MetadataCog
from discord import app_commands
from discord.ext import commands
from ui.embeds.information import BotInfoEmbed
from ui.embeds.information import ServerInfoEmbed

if TYPE_CHECKING:
    from classes.bot import Sunny


class Information(MetadataCog):
    """
    Retrieve information about various items.
    """

    def __init__(self, bot: Sunny) -> None:
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


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Information(bot))
