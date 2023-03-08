###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from classes.cog import MetadataCog
from discord import app_commands
from discord.ext import commands

if TYPE_CHECKING:
    from classes.bot import Sunny


class Settings(MetadataCog):
    """
    Commands user for changing server-based settings.
    """

    __slots__ = ("bot",)

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="forgetme",
        description="Deletes all of your data from the bot.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def forget_command(self, ctx: commands.Context) -> None:
        await self.bot.user_service.delete(ctx.author.id)
        await ctx.send("Your data has been successfully deleted. Sorry to see you go!")

    @commands.hybrid_command(
        name="prefix",
        description="Changes the bot's prefix for this server.",
    )
    @app_commands.describe(
        prefix="The new prefix for the bot. Leave blank to reset to default.",
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_permissions(manage_guild=True)
    async def prefix_command(self, ctx: commands.Context, prefix: str = "") -> None:
        if not prefix:
            await ctx.send("Prefix has been reset to default.")
            return await self.bot.guild_settings_service.clear_prefix(ctx.guild.id)
        await self.bot.guild_settings_service.set_prefix(ctx.guild.id, prefix)
        await ctx.send(f"Prefix has been set to `{prefix}`.")

    @commands.hybrid_command(
        name="togglelisteners",
        description="Toggles message listeners for the server.",
    )
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def toggle_listeners_command(self, ctx: commands.Context) -> None:
        listener = await self.bot.guild_settings_service.toggle_listener(ctx.guild.id)
        await ctx.send(
            f"Message listeners have been {'enabled' if listener else 'disabled'}.",
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Settings(bot))
