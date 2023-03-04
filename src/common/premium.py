from __future__ import annotations

from typing import Callable

import discord
from discord import app_commands
from discord import Interaction
from discord.app_commands import AppCommandError
from discord.app_commands import CheckFailure as AppCheckFailure
from discord.ext import commands
from discord.ext.commands import CheckFailure
from discord.ext.commands import CommandError
from discord.ext.commands import Context


class SupportServerMissing(AppCommandError, CommandError):
    pass


class PremiumMissing(AppCheckFailure, CheckFailure):
    pass


async def check_premium(
    user_id: int,
    bot: discord.Client,
    error: str = None,
) -> bool:
    if await bot.is_owner(bot.get_user(user_id)):
        return True

    member = await bot.support_guild.fetch_member(user_id)
    if not member:
        raise SupportServerMissing(
            f"You must join the support server and link your Ko-Fi to gain premium! Join here: {bot.config.support_invite}",
        )

    if bot.premium_role not in member.roles:
        if error:
            raise PremiumMissing(error)
        else:
            return False
    return True


async def user_premium_interaction(interaction: Interaction) -> bool:
    return await check_premium(
        interaction.user.id,
        interaction.client,
        "You must have premium to use this command! Find out more about premium by using the `premium` commands.",
    )


async def user_premium_context(ctx: Context) -> bool:
    return await check_premium(
        ctx.author.id,
        ctx.bot,
        "You must have premium to use this command! Find out more about premium by using the `premium` commands.",
    )


async def guild_premium_interaction(interaction: Interaction) -> bool:
    premium_booster = await interaction.bot.guild_settings_service.get_premium_booster(
        interaction.guild.id,
    )
    if not premium_booster:
        raise PremiumMissing(
            "This server does not have premium! Find out more about premium by using the `premium` commands.",
        )
    return True


async def guild_premium_context(ctx: Context) -> bool:
    premium_booster = await ctx.bot.guild_settings_service.get_premium_booster(
        ctx.guild.id,
    )
    if not premium_booster:
        raise PremiumMissing(
            "This server does not have premium! Find out more about premium by using the `premium` commands.",
        )
    return True


async def user_or_guild_premium_interaction(interaction: Interaction) -> bool:
    try:
        return await user_premium_interaction(interaction)
    except PremiumMissing:
        pass

    try:
        return await guild_premium_interaction(interaction)
    except PremiumMissing:
        pass

    raise PremiumMissing(
        "You must have premium or boost the server to use this command! Find out more about premium by using the `premium` commands.",
    )


async def user_or_guild_premium_context(ctx: Context) -> bool:
    try:
        return await user_premium_context(ctx)
    except PremiumMissing:
        pass

    try:
        return await guild_premium_context(ctx)
    except PremiumMissing:
        pass

    raise PremiumMissing(
        "You must have premium or boost the server to use this command! Find out more about premium by using the `premium` commands.",
    )


def is_user_premium(type="context") -> Callable:
    return (
        commands.check(user_premium_context)
        if type == "context"
        else app_commands.check(user_premium_interaction)
    )


def is_guild_premium(type="context") -> Callable:
    return (
        commands.check(guild_premium_context)
        if type == "context "
        else app_commands.check(guild_premium_interaction)
    )


def is_guild_or_user_premium(type="context") -> Callable:
    return (
        commands.check(user_or_guild_premium_context)
        if type == "context"
        else app_commands.check(user_or_guild_premium_interaction)
    )
