import classes.osu as osu

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
    def __init__(self, json_response:dict, server:osu.Server=osu.Server.BANCHO, mode:osu.Mode=osu.Mode.STANDARD):
        self.user_id:int = int(json_response["user_id"])
        self.username:int = json_response["username"]
        self.count300:int = int(json_response["count300"] or 0)
        self.count100:int = int(json_response["count100"] or 0)
        self.count50:int = int(json_response["count50"] or 0)
        self.playcount:int = int(json_response["playcount"] or 0)
        self.ranked_score:int = int(json_response["ranked_score"] or 0)
        self.total_score:int = int(json_response["total_score"] or 0)
        self.pp_rank:int = int(json_response["pp_rank"] or 0)
        self.level:float = float(json_response["level"] or 0)
        self.pp_raw:float = float(json_response["pp_raw"] or 0)
        self.total_seconds_played:int = int(json_response["total_seconds_played"] or 0)
        self.accuracy:float = float(json_response["accuracy"] or 0)
        self.count_rank_ss:int = int(json_response["count_rank_ss"] or 0)
        self.count_rank_s:int = int(json_response["count_rank_s"] or 0)
        self.count_rank_a:int = int(json_response["count_rank_a"] or 0)
        self.country:str = json_response["country"]
        self.pp_country_rank:int = int(json_response["pp_country_rank"] or 0)
        #self.events = Attribute(JsonList(UserEvent))

        # Fields that might not exist in the json
        if "count_rank_ssh" in json_response and json_response["count_rank_ssh"] is not None:
            self.count_rank_ssh:int = int(json_response["count_rank_ssh"])
        else:
            self.count_rank_ssh:int = 0

        if "count_rank_sh" in json_response and json_response["count_rank_sh"] is not None:
            self.count_rank_sh:int = int(json_response["count_rank_sh"])
        else:
            self.count_rank_sh:int = 0

        if "join_date" in json_response and json_response["join_date"] is not None:
            self.join_date:int = json_response["join_date"]
        else:
            self.join_date:int = None

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