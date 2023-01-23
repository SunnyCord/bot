from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from models.cog import MetadataCog

if TYPE_CHECKING:
    from models.bot import Sunny


class Admin(MetadataCog):
    """
    Commands for managing Discord servers.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(
        name="prune",
        description="Deletes a specified amount of messages",
    )
    @app_commands.describe(count="The number of messages to delete")
    async def prune_command(
        self,
        interaction: discord.Interaction,
        count: app_commands.Range[int, 1, 100],
    ) -> None:

        await interaction.response.defer(ephemeral=True)
        resp = await interaction.channel.purge(limit=count, bulk=True)
        await interaction.followup.send(f"Deleted {len(resp)} messages")

    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.command(
        name="clean",
        description="Cleans the chat of the bot's messages",
    )
    async def clean_command(self, interaction: discord.Interaction) -> None:
        def is_me(m: discord.Member) -> bool:
            return m.author == self.bot.user

        await interaction.response.defer(ephemeral=True)
        resp = await interaction.channel.purge(limit=100, check=is_me)
        await interaction.followup.send(f"Deleted {len(resp)} messages")


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Admin(bot))
