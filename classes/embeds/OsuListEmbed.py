import discord
import classes.osu as osu
from typing import List

class OsuListEmbed(discord.Embed):

    def __init__(self, title:str,  color: str, scores:List[osu.Score], beatmaps:List[osu.Beatmap], user:osu.User, positions:List[int] = None, style:int = 1):
        super().__init__(
            title = discord.Embed.Empty,
            color = color,
            description = discord.Embed.Empty
        )

        self.set_author(name = title, icon_url = user.mode.icon, url = user.profile_url)
        self.set_thumbnail(url = user.avatar_url)
        self.set_footer(text=f'Plays from {user.server.name_full}', icon_url=(user.server.icon if user.server.icon is not None else discord.Embed.Empty))

        index:int
        score:osu.Score
        for index, score in enumerate(scores):
            field_description:str = ""
            field_title:str = ""
            beatmap:osu.Beatmap = beatmaps[index]
            if positions is None:
                displayed_index = index + 1
            else:
                displayed_index = positions[index]

            if style == 0:
                #index. artist - title (creator) [version] + modstring [sr]
                field_title += '\u200b'
                field_description += f"**{displayed_index}. [{beatmap.artist} - {beatmap.title} ({beatmap.creator}) [{beatmap.version}]]({beatmap.beatmap_url}) + {str(score.enabled_mods)} [{round(score.performance.star_rating, 2)}★]**"

            if style == 1:
                field_title += f"{displayed_index}. ``{str(score.enabled_mods)}`` [{round(score.performance.star_rating, 2)}★]"

            field_description += f"""
> {score.rank.icon} > **{round(score.performance.pp, 2)}PP""" + (f"({round(score.performance.pp_fc, 2)}PP for {round(score.performance.accuracy_fc, 2)}% FC)" if not score.perfect and score.mode != osu.Mode.MANIA else "") + f"""** > {round(score.performance.accuracy, 2)}%
> {score.score} > x{score.maxcombo}/{beatmap.max_combo} > [{score.count300}/{score.count100}/{score.count50}/{score.countmiss}]
> {score.date}"""

            self.add_field(name = field_title, value = field_description, inline=False)