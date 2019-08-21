import discord
import commons.osu.classes as osu
import config

class OsuPerformanceEmbed(discord.Embed):

    def __init__(self, beatmap:osu.Beatmap, perf_info:dict):
        super().__init__(
            title = f"{beatmap.title} [{beatmap.version}] ({beatmap.creator}) [{round(perf_info['star_rating'], 2)}★] +{str(perf_info['mods'])}",
            url=beatmap.beatmap_url,
            color = config.conf.COLOR
        )
        
        self.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmap.beatmapset_id}.jpg")
        self.add_field(name='100%', value=f"{perf_info['pp_100']}pp", inline=True)
        self.add_field(name='97%', value=f"{perf_info['pp_97']}pp", inline=True)
        self.add_field(name='99%', value=f"{perf_info['pp_99']}pp", inline=True)
        self.add_field(name='95%', value=f"{perf_info['pp_95']}pp", inline=True)

        self.set_footer(text="plz enjoy game")
