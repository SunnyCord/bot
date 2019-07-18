import discord

class OsuRecentEmbed(discord.Embed):

    def __init__(self, **kwargs):
        __userstats = kwargs.pop('userstats')
        __playinfo = kwargs.pop('playinfo')
        __mode = kwargs.pop('mode')
        __beatmap = kwargs.pop('beatmap')
        ranks = {
            "F": "<:F_:504305414846808084>",
            "D": "<:D_:504305448673869834>",
            "C": "<:C_:504305500364472350>",
            "B": "<:B_:504305539291938816>",
            "A": "<:A_:504305622297083904>",
            "S": "<:S_:504305656266752021>",
            "SH": "<:SH:504305700445487105>",
            "X": "<:X_:504305739209244672>",
            "XH": "<:XH:504305771417305112>",
            "SS": "<:X_:504305739209244672>",
            "SSH": "<:XH:504305771417305112>"
        }
        nomstat = ["Unranked", "Ranked", "Approved", "Qualified", "Loved"]
        super().__init__(
            title=discord.Embed.Empty,
            color=kwargs.pop('color'),
            description=f"> {ranks[__playinfo['rank']]} > **{__playinfo['pp']}PP{__playinfo['if_fc']}** > {__playinfo['accuracy']}%\n\
            > {__playinfo['score']} > x{__playinfo['maxcombo']}/\
            {__playinfo['maxcombo']} > [{__playinfo['count300']}/\
            {__playinfo['count100']}/\
            {__playinfo['count50']}/\
            {__playinfo['countmiss']}]{__playinfo['completion']}",
            timestamp=kwargs.pop("timestamp")
        )
        self.set_author(name=f"{__beatmap['title']} [{__beatmap['version']}] ({__beatmap['creator']}) +{__playinfo['modString']} [{__beatmap['difficultyrating']}★]",\
        url=f"https://osu.ppy.sh/b/{__playinfo['beatmap_id']}", icon_url=__userstats["avatar_url"])
        self.set_thumbnail(url=f"https://b.ppy.sh/thumb/{__beatmap['beatmapset_id']}.jpg")
        self.set_footer(text=f"{nomstat[__beatmap['approved']]} | osu! {__mode.name} Play", icon_url=__mode.icon)