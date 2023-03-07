###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from classes.cog import MetadataCog
from discord.ext import commands
from ui.embeds.information import BotInfoEmbed
from ui.embeds.information import HelpEmbed
from ui.embeds.information import ServerInfoEmbed

if TYPE_CHECKING:
    from classes.bot import Sunny


class Information(MetadataCog):
    """
    Retrieve information about various items.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="botinfo",
        description="Retrieve information about the bot.",
    )
    async def info_bot_command(self, ctx: commands.Context) -> None:
        embed = BotInfoEmbed(ctx)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="serverinfo",
        description="Retrieve information about the current server.",
    )
    async def info_server_command(self, ctx: commands.Context) -> None:
        embed = ServerInfoEmbed(ctx)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="help",
        description="Get help with the commands.",
    )
    async def help_command(self, ctx: commands.Context) -> None:
        embed = HelpEmbed(ctx)
        await ctx.send(embed=embed)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Information(bot))
