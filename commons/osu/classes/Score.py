import commons.osu.classes as osu

from datetime import datetime

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
        In taiko: number of "good" hitscombo
        In catch: number of "drop" hitscombo
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
    def __init__(self, json_response, server:osu.Server = osu.Server.BANCHO, mode:osu.Mode = osu.Mode.STANDARD):
        self.server = server
        self.mode = mode
        self.score:int = int(json_response["score"])
        try:
            self.maxcombo:int = int(json_response["maxcombo"])
        except KeyError: #Relax Server Formatting
            self.maxcombo:int = int(json_response["max_combo"])
        try:
            self.count50:int = int(json_response["count50"])
        except KeyError:
            self.count50:int = int(json_response["count_50"])
        try:
            self.count100:int = int(json_response["count100"])
        except KeyError:
            self.count100:int = int(json_response["count_100"])
        try:
            self.count300:int = int(json_response["count300"])
        except KeyError:
            self.count300:int = int(json_response["count_300"])
        try:
            self.countmiss:int = int(json_response["countmiss"])
        except KeyError:
            self.countmiss:int = int(json_response["count_miss"])
        try:
            self.countkatu:int = int(json_response["countkatu"])
        except KeyError:
            self.countkatu:int = int(json_response["count_katu"])
        try:
            self.countgeki:int = int(json_response["countgeki"])
        except KeyError:
            self.countgeki:int = int(json_response["count_geki"])
        try:
            self.perfect:bool = bool(int(json_response["perfect"]))
        except KeyError:
            self.perfect:bool = bool(int(json_response["full_combo"]))
        if self.server is osu.Server.AKATSUKIRX or self.server is osu.Server.SIROHIRX:
            self.perfect = True
        try:
            self.user_id:int = int(json_response["user_id"])
        except KeyError:
            self.user_id:int = int(json_response["id"])
        self.rank:osu.Rank = osu.Rank[json_response["rank"]]
        try:
            self.enabled_mods:osu.Mod = osu.Mods(int(json_response["enabled_mods"]))
        except KeyError:
            self.enabled_mods:osu.Mod = osu.Mods(int(json_response["mods"]))
        self.performance:osu.Performance = None
        try:
            self.pp:float = float(json_response["pp"] or 0)
        except Exception:
            self.pp = 0
        try:
            self.date:datetime = datetime.strptime(json_response["date"], "%Y-%m-%d %H:%M:%S")
        except KeyError:
            cleanedDate = json_response['time'].split('+', 1)[0]
            self.date:datetime = datetime.strptime(cleanedDate, "%Y-%m-%dT%H:%M:%S")

    def accuracy(self):
        """Calculated accuracy.
        See Also
        --------
        <https://osu.ppy.sh/help/wiki/Accuracy>
        """
        if self.mode is osu.Mode.STANDARD:
            return (
                (6 * self.count300 + 2 * self.count100 + self.count50) /
                (6 * (self.count300 + self.count100 + self.count50 + self.countmiss)))
        if self.mode is osu.Mode.TAIKO:
            return (
                (self.count300 + self.countgeki + (0.5*(self.count100 + self.countkatu))) /
                (self.count300 + self.countgeki + self.count100 + self.countkatu + self.countmiss))
        if self.mode is osu.Mode.MANIA:
            return (
                (6 * (self.countgeki + self.count300) + 4 * self.countkatu + 2 * self.count100 + self.count50) /
                (6 * (self.countgeki + self.count300 + self.countkatu + self.count100 + self.count50 + self.countmiss)))
        if self.mode is osu.Mode.CTB:
            return (
                (self.count50 + self.count100 + self.count300) /
                (self.count50 + self.count100 + self.count300 + self.countmiss + self.countkatu))

    def total_hits(self):
        return self.count300 + self.count100 + self.count50 + self.countmiss

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

    def __init__(self, json_response, server:osu.Server = osu.Server.BANCHO, mode:osu.Mode = osu.Mode.STANDARD):
        super().__init__(json_response, server, mode)
        # self.username:str = json_response["username"]
        self.pp:float = float(json_response["pp"] or 0)
        self.score_id:int = int(json_response["score_id"])
        self.replay_available:bool = bool(json_response["replay_available"])

    def __repr__(self):
        return "<{0.__module__}.BeatmapScore user_id={0.user_id} score_id={0.score_id} date={0.date}>".format(self)

    def __hash__(self):
        return hash(self.score_id)

    def __eq__(self, other):
        return self.score_id == other.score_id


class RecentScore(Score):
    """Class representing a recent score.
    See :class:`Score`
    Attributes
    -----------
    beatmap_id : int
        Beatmap the score is for.
    enabled_mods : :class:`osuapi.enums.OsuMod`
        Enabled modifiers

    date : datetime

        When the score was played.

    See Also
    ---------
    <https://osu.ppy.sh/wiki/Score>
    """
    def __init__(self, json_response, server:osu.Server = osu.Server.BANCHO, mode:osu.Mode = osu.Mode.STANDARD):
        super().__init__(json_response, server, mode)
        try:
            self.beatmap_id:int = int(json_response["beatmap_id"])
        except KeyError:
            self.beatmap_id:int = int(json_response["beatmap"]["beatmap_id"])

    def __repr__(self):
        return "<{0.__module__}.SoloScore user_id={0.user_id} beatmap_id={0.beatmap_id} date={0.date}>".format(self)

