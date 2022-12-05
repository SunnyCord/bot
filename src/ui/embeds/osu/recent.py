from __future__ import annotations

import aiosu
from discord.ext import commands
from ui.embeds.generic import ContextEmbed


class OsuRecentEmbed(ContextEmbed):
    def __init__(self, ctx: commands.Context, score: aiosu.classes.Score):
        super.__init__(ctx)
