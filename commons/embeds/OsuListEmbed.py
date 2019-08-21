import discord
import config
import commons.osu.classes as osu
from datetime import datetime
from typing import List

class OsuListEmbed(discord.Embed):

    def __init__(self, title:str, scores:List[osu.Score], beatmaps:List[osu.Beatmap], user:osu.User, style:int = 1):
        # __profile = kwargs.pop('profile')
        # __list = kwargs.pop('list')
        # __beatmap = kwargs.pop('beatmap', None)
        # __beatmaps = kwargs.pop('beatmaps', None)
        # __title = kwargs.pop('title')
        # __authorico = kwargs.pop('authorico')
        # __thumbnail = kwargs.pop('thumbnail')
        # __limit = kwargs.pop('limit', 0)
        # __url = kwargs.pop('url')
        # __style = kwargs.pop('style', 0)
        # __footertext = kwargs.pop('footertext', None)
        # __footericon = kwargs.pop('footericon', None)
        # self.ranks = {
        #     "F": "<:F_:504305414846808084>",
        #     "D": "<:D_:504305448673869834>",
        #     "C": "<:C_:504305500364472350>",
        #     "B": "<:B_:504305539291938816>",
        #     "A": "<:A_:504305622297083904>",
        #     "S": "<:S_:504305656266752021>",
        #     "SH": "<:SH:504305700445487105>",
        #     "X": "<:X_:504305739209244672>",
        #     "XH": "<:XH:504305771417305112>",
        #     "SS": "<:X_:504305739209244672>",
        #     "SSH": "<:XH:504305771417305112>"
        # }

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
                desc += f"**{index + 1}. [{beatmap.artist} - {beatmap.title} ({beatmap.creator}) [{beatmap.version}]]({beatmap.beatmap_url}) + {str(score.enabled_mods)} [{round(score.performance.star_rating, 2)}★]**"

            if style == 1:
                title += f"{index+1}. ``{str(score.enabled_mods)}`` [{round(score.performance.star_rating, 2)}★]"

            desc += f"""
> {score.rank.icon} > **{round(score.performance.pp, 2)}PP""" + (f"({round(score.performance.pp_fc, 2)}PP for {round(score.accuracy(True) * 100, 2)}% FC)" if not score.perfect else "") + f"""** > {round(score.accuracy() * 100, 2)}%
> {score.score} > x{score.maxcombo}/{beatmap.max_combo} > [{score.count300}/{score.count100}/{score.count50}/{score.countmiss}]
> {score.date}"""

            self.add_field(name = title, value = desc)