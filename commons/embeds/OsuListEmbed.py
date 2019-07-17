import discord
from datetime import datetime

class OsuListEmbed(discord.Embed):

    def __init__(self, **kwargs):
        __profile = kwargs.pop('profile')
        __list = kwargs.pop('list')
        __beatmap = kwargs.pop('beatmap', None)
        __beatmaps = kwargs.pop('beatmaps', None)
        __title = kwargs.pop('title')
        __authorico = kwargs.pop('authorico')
        __thumbnail = kwargs.pop('thumbnail')
        __limit = kwargs.pop('limit', 0)
        __url = kwargs.pop('url')
        __style = kwargs.pop('style', 0)
        self.ranks = {
            "F": "<:F_:504305414846808084>",
            "D": "<:D_:504305448673869834>",
            "C": "<:C_:504305500364472350>",
            "B": "<:B_:504305539291938816>",
            "A": "<:A_:504305622297083904>",
            "S": "<:S_:504305656266752021>",
            "SH": "<:SH:504305700445487105>",
            "X": "<:X_:504305739209244672>",
            "XH": "<:XH:504305771417305112>"
        }

        super().__init__(
            title = discord.Embed.Empty,
            color = kwargs.pop('color'),
            description = discord.Embed.Empty
        )

        self.set_author(name = __title, icon_url = __authorico, url = __url)
        self.set_thumbnail(url = __thumbnail)
        for index, item in enumerate(__list):
            
            descAppend = ""
            previewIndex = index+1

            if len(__list) == 1:
                previewIndex = __limit

            if __style == 0:
                #index. artist - title (creator) [version] + modstring [sr]
                title = '\u200b'
                descAppend = f"**{previewIndex}. [{__beatmaps[index]['artist']} - {__beatmaps[index]['title']} ({__beatmaps[index]['creator']}) [{__beatmaps[index]['version']}]]({__beatmaps[index]['beatmap_url']}) + {item['modString']} [{__beatmaps[index]['difficultyrating']}★]**"

            if __style == 1:
                title = f"{index}. ``{item['modString']}`` [{__beatmaps[index]['difficultyrating']}★]"

            self.add_element(item, __beatmaps[index], title, descAppend)

    def add_element(self, element, beatmap, title, descAppend = ""):

        desc = descAppend

        desc += f"\n> {self.ranks[element['rank']]} > **{round(float(element['pp']), 2)}pp**{element['if_fc']} > {element['accuracy']}%\n\
        > {element['maxcombo']}x/{beatmap['max_combo']}x > [{element['count300']}/{element['count100']}/{element['count50']}/{element['countmiss']}]\n\
        > {datetime.strptime(element['date'], '%Y-%m-%d %H:%M:%S')}\n"

        self.add_field(name = title, value = desc)