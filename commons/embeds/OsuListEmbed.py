import discord
import config
import commons.osu.classes as osu
from datetime import datetime
from typing import List

class OsuListEmbed(discord.Embed):

    def __init__(self, title:str, scores:List[osu.Score], beatmaps:List[osu.Beatmap], user:osu.User, style:int = 1, start:int = 1):
        super().__init__(
            title = discord.Embed.Empty,
            color = config.conf.COLOR,
            description = discord.Embed.Empty
        )

        self.set_author(name = title, icon_url = user.mode.icon, url = user.profile_url)
        self.set_thumbnail(url = user.avatar_url)
        self.set_footer(text=f'Plays from {user.server.name.lower()}', icon_url=(user.server.icon if user.server.icon is not None else discord.Embed.Empty))

        index:int
        score:osu.Score
        for index, score in enumerate(scores):
            desc:str = ""
            title:str = ""
            beatmap:osu.Beatmap = beatmaps[index]

            if style == 0:
                #index. artist - title (creator) [version] + modstring [sr]
                title += '\u200b'
                desc += f"**{index + start}. [{beatmap.artist} - {beatmap.title} ({beatmap.creator}) [{beatmap.version}]]({beatmap.beatmap_url}) + {str(score.enabled_mods)} [{round(score.performance.star_rating, 2)}★]**"

            if style == 1:
                title += f"{index + start}. ``{str(score.enabled_mods)}`` [{round(score.performance.star_rating, 2)}★]"

            desc += f"""
> {score.rank.icon} > **{round(score.performance.pp, 2)}PP""" + (f"({round(score.performance.pp_fc, 2)}PP for {round(score.accuracy(True) * 100, 2)}% FC)" if not score.perfect else "") + f"""** > {round(score.accuracy() * 100, 2)}%
> {score.score} > x{score.maxcombo}/{beatmap.max_combo} > [{score.count300}/{score.count100}/{score.count50}/{score.countmiss}]
> {score.date}"""

            self.add_field(name = title, value = desc)