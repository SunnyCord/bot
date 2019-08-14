import discord
import commons.osu.classes as osuClasses

class OsuProfileEmbed(discord.Embed):

    @classmethod
    def __secondsToText(cls, secs):
        result = "0 seconds"
        if secs >0:
            days = secs//86400
            hours = (secs - days*86400)//3600
            minutes = (secs - days*86400 - hours*3600)//60
            seconds = secs - days*86400 - hours*3600 - minutes*60
            result = ("{0} day{1} ".format(days, "s" if days!=1 else "") if days else "") + \
            ("{0} hour{1} ".format(hours, "s" if hours!=1 else "") if hours else "") + \
            ("{0} minute{1} ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
            ("{0} second{1} ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
        return result

    def __init__(self, **kwargs):
        __userstats = kwargs.pop('userstats')
        __mode = kwargs.pop('modeinfo', osuClasses.Mode.STANDARD)   
        __server = kwargs.get('server', osuClasses.Server.BANCHO)
        super().__init__(
            title=discord.Embed.Empty,
            color=kwargs.pop('color'),
            description=f"**>Rank:** #{__userstats['pp_rank']}\n\
            **>PP:** {__userstats['pp_raw']}\n\
            **>Accuracy:** {__userstats['accuracy']}%\n\
            **>Level:** {__userstats['level']} ({__userstats['level_progress']}%)\n\
            **>Playtime:** {self.__secondsToText(__userstats['total_seconds_played'])}\n\
            **>Playcount:** {__userstats['playcount']}\n\
            **>PP/hour:** {int(__userstats['pp_raw']/__userstats['total_seconds_played']*3600) if __userstats['total_seconds_played'] > 0 else 0}\n\
            **>Ranks/day:** {int(__userstats['pp_raw']/__userstats['total_seconds_played']*86400) if __userstats['total_seconds_played'] > 0 else 0}",
            timestamp=kwargs.pop("timestamp")
        )
        self.set_author(name=f"osu! {__mode.name} stats for {__userstats['username']} on {__server.name.lower()}", url=__userstats["profile_url"], icon_url=__mode.icon)
        self.set_thumbnail(url=__userstats["avatar_url"])
        self.set_footer(text=f"#{__userstats['pp_country_rank']}", icon_url=f"https://osu.ppy.sh/images/flags/{__userstats['country']}.png")