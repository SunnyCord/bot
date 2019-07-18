import discord

class OsuPerformanceEmbed(discord.Embed):

    def __init__(self, **kwargs):
        __beatmap = kwargs.pop('beatmap')
        __perfinfo = kwargs.pop('perfinfo')

        super().__init__(
            title = f"{__beatmap['title']} [{__beatmap['version']}] ({__beatmap['creator']}) [{__beatmap['difficultyrating']}★] +{__perfinfo['mods']}",
            url=__beatmap['beatmap_url'],
            color = kwargs.pop('color')
            # description = f"> PP: 95%-{__perfinfo['pp_95']} 97%-{__perfinfo['pp_97']} 99%-{__perfinfo['pp_99']} 100%-{__perfinfo['pp_100']}"
        )

        self.set_thumbnail(url=f"https://b.ppy.sh/thumb/{__beatmap['beatmapset_id']}.jpg")
        self.add_field(name='100%', value=f"{__perfinfo['pp_100']}pp", inline=True)
        self.add_field(name='97%', value=f"{__perfinfo['pp_97']}pp", inline=True)
        self.add_field(name='99%', value=f"{__perfinfo['pp_99']}pp", inline=True)
        self.add_field(name='95%', value=f"{__perfinfo['pp_95']}pp", inline=True)

        self.set_footer(text="plz enjoy game")
