from __future__ import annotations

import discord


class ContextEmbed(discord.Embed):
    def __init__(self, ctx: discord.ext.commands.Context, **kwargs):
        super().__init__(color=ctx.bot.config.color, **kwargs)


class ContextAuthorEmbed(InteractionEmbed):
    def __init__(self, ctx: discord.ext.commands.Context, **kwargs):
        super().__init__(ctx, **kwargs)
        self.set_author(name=ctx.author.name, icon_url=ctx.author.avatar)
