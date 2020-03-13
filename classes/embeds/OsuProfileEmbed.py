import discord
import classes.osu as osu
from datetime import datetime

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

    def __init__(self, user:osu.User, mode:osu.Mode, color:str):
        super().__init__(
            title=discord.Embed.Empty,
            color=color,
            description=f"> **Rank:** #{user.pp_rank}\n\
> **PP:** {user.pp_raw}\n\
> **Accuracy:** {round(user.accuracy, 2)}%\n\
> **Level:** {int(user.level)} ({user.level_progress}%)\n\
> **Playtime:** {self.__secondsToText(user.total_seconds_played)}\n\
> **Playcount:** {user.playcount}\n\
> **PP/hour:** {int(user.pp_raw/user.total_seconds_played*3600) if user.total_seconds_played > 0 else 0}",
            timestamp=datetime.utcnow()
        )
        self.set_author(name=f"osu! {mode.name_full} stats for {user.username} on {user.server.name_full}", url=user.profile_url, icon_url=mode.icon)
        self.set_thumbnail(url=user.avatar_url)
        self.set_footer(text=f"#{user.pp_country_rank}", icon_url=f"https://osu.ppy.sh/images/flags/{user.country}.png")