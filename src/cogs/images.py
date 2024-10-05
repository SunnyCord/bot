###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Literal

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from classes.cog import MetadataGroupCog
from models.enums.animals import Animal

if TYPE_CHECKING:
    from classes.bot import Sunny


class Image(MetadataGroupCog, name="image"):
    """
    Various image-related commands.
    """

    __slots__ = "bot"

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="avatar", description="Gets a user's avatar")
    @app_commands.describe(
        user="(Optional) The user you want the avatar for",
        avatar_type="The type of avatar you want",
    )
    async def avatar_command(
        self,
        interaction: discord.Interaction,
        user: discord.User | None,
        avatar_type: Literal["guild", "profile"] = "profile",
    ) -> None:
        if user is None:
            user = interaction.user
        avatar = user.avatar if avatar_type == "profile" else user.display_avatar

        embed = discord.Embed(
            title=f"{user}'s {avatar_type} avatar.",
            color=self.bot.config.color,
        ).set_image(url=avatar)
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="animal", description="Sends a random animal image")
    @app_commands.describe(animal="Name of the animal")
    async def animal_command(
        self,
        interaction: discord.Interaction,
        animal: Animal,
    ) -> None:
        async with self.bot.aiohttp_session.get(
            f"https://some-random-api.com/animal/{animal.name}",
        ) as r:
            res = await r.json()

        embed = discord.Embed(
            title=animal.icon,
            description=f"**{animal.display_name} Fact:**\n{res['fact']}",
            color=self.bot.config.color,
        ).set_image(url=res["image"])
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="wink", description="Wink")
    async def wink_command(self, interaction: discord.Interaction) -> None:
        async with self.bot.aiohttp_session.get(
            "https://some-random-api.com/animu/wink",
        ) as r:
            res = await r.json()

        embed = discord.Embed(
            title=f"{interaction.user} winks 😉",
            color=self.bot.config.color,
        ).set_image(url=res["link"])
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="pat", description="Give someone a pat")
    @app_commands.describe(user="User to pat")
    async def pat_command(
        self,
        interaction: discord.Interaction,
        user: discord.User | None,
    ) -> None:
        async with self.bot.aiohttp_session.get(
            "https://some-random-api.com/animu/pat",
        ) as r:
            res = await r.json()

        embed = discord.Embed(
            title=f'{interaction.user} pats {f"themselves. 😔" if user is None else f"{user} <:lewd:545969728527663114>"}',
            color=self.bot.config.color,
        ).set_image(url=res["link"])
        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(name="hug", description="Give someone a hug")
    @app_commands.describe(user="User to hug")
    async def hug_command(
        self,
        interaction: discord.Interaction,
        user: discord.User | None,
    ) -> None:
        async with self.bot.aiohttp_session.get(
            "https://some-random-api.com/animu/hug",
        ) as r:
            res = await r.json()

        embed = discord.Embed(
            title=f'{interaction.user} hugs {f"themselves. 😔" if user is None else f"{user} <:lewd:545969728527663114>"}',
            color=self.bot.config.color,
        ).set_image(url=res["link"])
        await interaction.response.send_message(embed=embed)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Image(bot))
