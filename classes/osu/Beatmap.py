import classes.osu as osu

class Beatmap:
    """Class representing a beatmap
    Attributes
    -----------
    approved : BeatmapStatus
        Whether or not the map has been ranked.
    approved_date : Optional[datetime]
        When the beatmap was ranked, or None.
    submit_date : datetime
        When the beatmap was submitted.
    last_update : datetime
        Last time the map was updated.
    artist : str
        Music metadata.
    beatmap_id : int
        Unique identifier for beatmap.
    beatmapset_id : int
        Unique identifier for set this beatmap belongs to.
    bpm : float
        Speed of map in beats per minute.
    creator : str
        Username of map creator.
    creator_id: int
        ID of the map creator.
    difficultyrating : float
        Star rating of a map.
    diff_aim : float
        Aim portion of difficulty
    diff_speed : float
        Speed portion of difficulty
    diff_size : float
        Circle Size. (CS)
    diff_overall : float
        Overall Difficulty. (OD)
    diff_approach : float
        Approach rate. (AR)
    diff_drain : float
        Health Drain (HP)
    hit_length : int
        Playable time in seconds. (Drain time)
    source : strr cutting edge Python.
        Source of the music
    genre_id : :class:`osuapi.enums.BeatmapGenre`
        Genre of the music.
    language_id : :class:`osuapi.enums.BeatmapLanguage`
        Language of the music.
    title : str
        Title of the song.
    total_length : int
        Total song length in seconds.
    version : str
        Difficulty name.
    file_md5 : str
        md5 hash of map.
    mode : :class:`osuapi.enums.OsuMode`
        Game mode for the map.
    tags : str
        Space delimited tags for the map.
    favourite_count : int
        Number of users that have favorited this map.
    rating : float
        Quality rating of this map
    playcount : int
        Number of times this map has been played (including fails)/
    passcount : int
        Number of times this map has been passed.
    max_combo : Optional[int]
        Maximum possible combo.
    count_normal : int
        Number of normal hitobjects
    count_slider : int
        Number of sliders
    count_spinner : int
        Number of spinners
    download_unavailable : bool
        If the download for this beatmap is unavailable (old map, etc.)
    audio_unavailable : bool
        If the audio for this beatmap is unavailable (DMCA takedown, etc.)
    See Also
    ---------
    <https://osu.ppy.sh/wiki/Beatmaps>
    """
    def __init__(self, json_response:dict, server:osu.Server):
        self.status:osu.BeatmapStatus = osu.BeatmapStatus(int(json_response["approved"]))
        self.approved_date:str = json_response["approved_date"]
        self.submit_date:str = json_response["submit_date"]
        self.last_update:str = json_response["last_update"]
        self.artist:str = json_response["artist"]
        self.beatmap_id:int = int(json_response["beatmap_id"])
        self.beatmapset_id:int = int(json_response["beatmapset_id"])
        self.bpm:float = float(json_response["bpm"])
        self.creator:str = json_response["creator"]
        self.creator_id:int = int(json_response["creator_id"])
        self.difficultyrating:float = float(json_response["difficultyrating"])
        # self.diff_aim:float = float(jsonResponse["diff_aim"]) if jsonResponse["diff_aim"] is not None else None
        # self.diff_speed:float = float(jsonResponse["diff_speed"]) if jsonResponse["diff_speed"] is not None else None
        self.diff_size:float = float(json_response["diff_size"])
        self.diff_overall:float = float(json_response["diff_overall"])
        self.diff_approach:float = float(json_response["diff_approach"])
        self.diff_drain:float = float(json_response["diff_drain"])
        self.hit_length:int = int(json_response["hit_length"])
        self.source:str = json_response["source"]
        self.genre_id:int = int(json_response["genre_id"])
        self.language_id:int = int(json_response["language_id"])
        self.title:str = json_response["title"]
        self.total_length:int = int(json_response["total_length"])
        self.version:str = json_response["version"]
        self.file_md5:str = json_response["file_md5"]
        self.mode:Mode = json_response["mode"]
        self.tags:str = json_response["tags"]
        self.favourite_count:int = int(json_response["favourite_count"])
        self.rating:float = float(json_response["rating"])
        self.playcount:int = int(json_response["playcount"])
        self.passcount:int = int(json_response["passcount"])
        self.count_normal:int = int(json_response["count_normal"])
        self.count_slider:int = int(json_response["count_slider"])
        self.count_spinner:int = int(json_response["count_spinner"])
        self.max_combo:int = int(json_response["max_combo"]) if json_response["max_combo"] is not None else None # - no response from osu!API
        self.download_unavailable:bool = bool(json_response["download_unavailable"])
        self.audio_unavailable:bool = bool(json_response["audio_unavailable"])

        self.beatmap_url = server.url_beatmap + str(self.beatmap_id)

    def __repr__(self):
        return "<{0.__module__}.Beatmap title={0.title} creator={0.creator} id={0.beatmap_id}>".format(self)

    @property
    def url(self):
        return "https://osu.ppy.sh/b/{0.beatmap_id}".format(self)

    @property
    def set_url(self):
        return "https://osu.ppy.sh/s/{0.beatmapset_id}".format(self)
