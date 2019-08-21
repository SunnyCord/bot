import commons.osu.classes as osu

class User:
    """Class representing a user.
    Attributes
    -----------
    user_id : int
        User's unique identifier.
    username : str
        User's name.
    count300 : int
        Career total of "300" hits.
    count100 : int
        Career total of "100" hits.
    count50 : int
        Career total of "50" hits.
    playcount : int
        Career total play count.
    ranked_score : int
        Total sum of the best scores from all the ranked beatmaps played online.
    total_score : int
        Total sum of all scores on ranked beatmaps, including failed trails.
    pp_rank : int
        Global ranking place.
    level: float
        User's level
    pp_raw: float
        User's performance points
    total_seconds_played: int
        User's total playtime
    accuracy : float
        Weighted average of accuracy on top plays.
    count_rank_ssh : int
        Career total of SSH ranks.
    count_rank_ss : int
        Career total of SS ranks.
    count_rank_sh : int
        Career total of SH ranks.
    count_rank_s : int
        Career total of S ranks.
    count_rank_a : int
        Career total of A ranks.
    country : str
        Country the user is registered to.
    pp_country_rank : int
        Country ranking place.
    events : list[dict]
        Information about recent "interesting" events.
    See Also
    ---------
    <https://osu.ppy.sh/wiki/Score>
    """
    def __init__(self, jsonResponse:dict, server:osu.Server=osu.Server.BANCHO, mode:osu.Mode=osu.Mode.STANDARD):
        self.user_id:int = int(jsonResponse["user_id"])
        self.username:int = jsonResponse["username"]
        self.count300:int = int(jsonResponse["count300"])
        self.count100:int = int(jsonResponse["count100"])
        self.count50:int = int(jsonResponse["count50"])
        self.playcount:int = int(jsonResponse["playcount"])
        self.ranked_score:int = int(jsonResponse["ranked_score"])
        self.total_score:int = int(jsonResponse["total_score"])
        self.pp_rank:int = int(jsonResponse["pp_rank"])
        self.level:float = float(jsonResponse["level"])
        self.pp_raw:float = float(jsonResponse["pp_raw"])
        self.total_seconds_played:int = int(jsonResponse["total_seconds_played"])
        self.accuracy:float = float(jsonResponse["accuracy"])
        self.count_rank_ssh:int = int(jsonResponse["count_rank_ssh"])
        self.count_rank_ss:int = int(jsonResponse["count_rank_ss"])
        self.count_rank_sh:int = int(jsonResponse["count_rank_sh"])
        self.count_rank_s:int = int(jsonResponse["count_rank_s"])
        self.count_rank_a:int = int(jsonResponse["count_rank_a"])
        self.country:str = jsonResponse["country"]
        self.pp_country_rank:int = int(jsonResponse["pp_country_rank"])
        #self.events = Attribute(JsonList(UserEvent))
        self.join_date:str = jsonResponse["join_date"]

        self.server:osu.Server = server
        self.mode:osu.Mode = mode
        self.avatar_url:str = server.url_avatar + str(self.user_id)
        self.profile_url:str = server.url_profile + str(self.user_id)

    @property
    def total_hits(self):
        return self.count300 + self.count100 + self.count50

    @property
    def level_progress(self):
        return round((float(self.level)%1*100), 2)

    def __repr__(self):
        return "<{0.__module__}.User username={0.username} user_id={0.user_id}>".format(self)

    def __str__(self):
        return self.username