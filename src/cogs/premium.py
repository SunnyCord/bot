###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction
from discord import app_commands

from classes.cog import MetadataGroupCog
from common import premium
from ui.embeds.information import UserPremiumEmbed

if TYPE_CHECKING:
    from classes.bot import Sunny


class Premium(MetadataGroupCog, name="premium"):
    """
    Commands for managing premium perks.
    """

    __slots__ = ("bot",)

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @app_commands.command(
        name="info",
        description="Shows information about premium perks.",
    )
    async def info_command(self, interaction: Interaction) -> None:
        is_premium = await premium.check_premium(interaction.user.id, self.bot)
        if not is_premium:
            await interaction.response.send_message(
                f"You are not a premium user. Consider supporting the bot to unlock premium perks! {self.bot.config.premium.premium_url}",
            )
            return

        guilds_boosted = await self.bot.guild_settings_service.get_user_boosts(
            interaction.user.id,
        )

        guilds = []
        for guild in guilds_boosted:
            try:
                guild = await self.bot.fetch_guild(guild)
            except Exception:
                # This could also be handled by removing the guild from the database, not in here though.
                await self.bot.guild_settings_service.set_premium_booster(
                    guild.id,
                    None,
                )
                continue

            guilds.append(guild)

        await interaction.response.send_message(
            embed=UserPremiumEmbed(interaction, guilds),
        )

    @premium.is_user_premium("interaction")
    @app_commands.command(
        name="boost",
        description="Boosts the current server for premium perks.",
    )
    async def boost_command(self, interaction: Interaction) -> None:
        current_booster_id = await self.bot.guild_settings_service.get_premium_booster(
            interaction.guild.id,
        )
        if current_booster_id is not None:
            current_booster = interaction.guild.get_member(current_booster_id)
            await interaction.response.send_message(
                f"This server is already boosted by **{current_booster}**.",
                ephemeral=True,
            )
            return

        current_boost_count = (
            await self.bot.guild_settings_service.get_user_boosts_count(
                interaction.user.id,
            )
        )
        if current_boost_count >= self.bot.config.premium.boost_limit and not (
            await self.bot.is_owner(interaction.user)
        ):
            await interaction.response.send_message(
                "You have reached the maximum number of servers you can boost. Please unboost a server before boosting another!",
                ephemeral=True,
            )
            return

        await self.bot.guild_settings_service.set_premium_booster(
            interaction.guild.id,
            interaction.user.id,
        )

        await interaction.response.send_message("You are now boosting this server!")

    @premium.is_user_premium("interaction")
    @app_commands.command(
        name="unboost",
        description="Unboosts the current server.",
    )
    async def unboost_command(self, interaction: Interaction) -> None:
        current_booster_id = await self.bot.guild_settings_service.get_premium_booster(
            interaction.guild.id,
        )
        if current_booster_id is None:
            await interaction.response.send_message(
                "This server is not currently boosted.",
                ephemeral=True,
            )
            return

        if current_booster_id != interaction.user.id:
            await interaction.response.send_message(
                "You are not the current booster of this server!",
                ephemeral=True,
            )
            return

        await self.bot.guild_settings_service.set_premium_booster(
            interaction.guild.id,
            None,
        )
        await interaction.response.send_message(
            "You are no longer boosting this server.",
        )

    @app_commands.command(
        name="guildinfo",
        description="Shows information about the current server's premium perks.",
    )
    async def guildinfo_command(self, interaction: Interaction) -> None:
        current_booster_id = await self.bot.guild_settings_service.get_premium_booster(
            interaction.guild.id,
        )
        if current_booster_id is None:
            await interaction.response.send_message(
                "This server is not currently boosted.",
                ephemeral=True,
            )
            return

        current_booster = interaction.guild.get_member(current_booster_id)
        await interaction.response.send_message(
            f"This server is boosted by **{current_booster}**.",
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Premium(bot))
