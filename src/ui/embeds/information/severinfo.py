###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from ui.embeds.generic import ContextEmbed

if TYPE_CHECKING:
    from typing import Any
    from discord.ext.commands import Context


class ServerInfoEmbed(ContextEmbed):
    def __init__(self, ctx: Context, *args: Any, **kwargs: Any) -> None:
        super().__init__(ctx, timestamp=ctx.message.created_at, *args, **kwargs)
        self.set_thumbnail(url=ctx.guild.icon)
        self.set_footer(
            text=ctx.bot.user.name,
            icon_url=ctx.bot.user.avatar,
        )

        self.add_field(
            name="Name (ID)",
            value=f"{ctx.guild} ({ctx.guild.id})",
            inline=False,
        )
        self.add_field(name="Owner", value=ctx.guild.owner, inline=False)
        self.add_field(
            name="Verification Level",
            value=ctx.guild.verification_level,
        )
        self.add_field(name="Members", value=ctx.guild.member_count)
        self.add_field(
            name="Text Channels",
            value=len(
                list(
                    filter(
                        lambda x: isinstance(x, discord.channel.TextChannel),
                        ctx.guild.channels,
                    ),
                ),
            ),
        )
        self.add_field(name="Roles", value=len(ctx.guild.roles))
        self.add_field(name="Emotes", value=len(ctx.guild.emojis))
        self.add_field(
            name="Created On:",
            value=f"<t:{ctx.guild.created_at.timestamp():.0f}:R>",
        )
