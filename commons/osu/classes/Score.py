import commons.osu.classes as osu

class Score:
    """Abstract class representing a score.
    Attributes
    -----------
    score : int
        The score value
    maxcombo : int
        Largest combo achieved
    count50 : int
        Number of "50" hits.
        In catch: number of "droplet" hits
    count100 : int
        Number of "100" hits
        In taiko: number of "good" hits
        In catch: number of "drop" hits
    count300 : int
        Number of "300" hits
        In taiko: number of "great" hits
        In catch: number of "fruit" hits
    countmiss : int
        Number of misses
        In catch: number of "fruit" or "drop" misses
    countkatu : int
        Number of "katu" sections (only 100s and 300s)
        In taiko: number of "double good" hits
        In mania: number of "200" hits
        In catch: number of "droplet" misses
    countgeki : int
        Number of "geki" sections (only 300s)
        In taiko: number of "double great" hits
        In mania: number of "rainbow 300" hits
    perfect : bool
        If the play is a full combo (maxcombo is maximal)
    user_id : int
        ID of user who played.
    rank :  str
        Letter rank achieved
    See Also
    ---------
    <https://osu.ppy.sh/wiki/Score>
    """
    def __init__(self, jsonResponse):
        self.score:int = jsonResponse["score"]
        self.maxcombo:int = jsonResponse["maxcombo"]
        self.count50:int = jsonResponse["count50"]
        self.count100:int = jsonResponse["count100"]
        self.count300:int = jsonResponse["count300"]
        self.countmiss:int = jsonResponse["countmiss"]
        self.countkatu:int = jsonResponse["countkatu"]
        self.countgeki:int = jsonResponse["countgeki"]
        self.perfect:bool = jsonResponse["perfect"]
        self.user_id:int = jsonResponse["user_id"]
        self.rank:str = jsonResponse["rank"]

    def accuracy(self, mode: osu.Mode):
        """Calculated accuracy.
        See Also
        --------
        <https://osu.ppy.sh/help/wiki/Accuracy>
        """
        if mode is osu.Mode.STANDARD:
            return (
                (6 * self.count300 + 2 * self.count100 + self.count50) /
                (6 * (self.count300 + self.count100 + self.count50 + self.countmiss)))
        if mode is osu.Mode.TAIKO:
            return (
                (self.count300 + self.countgeki + (0.5*(self.count100 + self.countkatu))) /
                (self.count300 + self.countgeki + self.count100 + self.countkatu + self.countmiss))
        if mode is osu.Mode.MANIA:
            return (
                (6 * (self.countgeki + self.count300) + 4 * self.countkatu + 2 * self.count100 + self.count50) /
                (6 * (self.countgeki + self.count300 + self.countkatu + self.count100 + self.count50 + self.countmiss)))
        if mode is osu.Mode.CTB:
            return (
                (self.count50 + self.count100 + self.count300) /
                (self.count50 + self.count100 + self.count300 + self.countmiss + self.countkatu))

class BeatmapScore(Score):
    """Class representing a score attached to a beatmap.
    See :class:`Score`
    Attributes
    -----------
    username : str
        Name of user.
    pp : Optional[float]
        How much PP the score is worth, or None if not eligible for PP.
    enabled_mods : :class:`osuapi.enums.OsuMod`
        Enabled modifiers
    date : datetime
        When the score was played.
    score_id : int
        ID of score.
    replay_available : bool
        If a replay is available.
    See Also
    ---------
    <https://osu.ppy.sh/wiki/Score>
    """

    def __init__(self, jsonResponse):
        self.username:str = jsonResponse["username"]
        self.pp:float = jsonResponse["pp"]
        self.enabled_mods:osu.Mod = osu.Mod.fromStr(jsonResponse["enabled_mods"])
        self.date:str = jsonResponse["date"]
        self.score_id:int = jsonResponse["score_id"]
        self.replay_available:bool = jsonResponse["replay_available"]

    def __repr__(self):
        return "<{0.__module__}.BeatmapScore user_id={0.user_id} score_id={0.score_id} date={0.date}>".format(self)

    def __hash__(self):
        return hash(self.score_id)

    def __eq__(self, other):
        return self.score_id == other.score_id