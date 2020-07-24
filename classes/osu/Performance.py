class Performance:
    def __init__(self, pp:float, pp_fc:float, accuracy:float, accuracy_fc:float, completion:float, star_rating:float, max_combo:int):
        self.pp:float = pp
        self.pp_fc:float = pp_fc
        self.accuracy:float = accuracy
        self.accuracy_fc:float = accuracy_fc
        self.completion:float = completion
        self.star_rating:float = star_rating
        self.max_combo:int = max_combo

class BeatmapPerformance:
    def __init__(self, pp_100:float, pp_99:float, pp_97:float, pp_95:float, star_rating:float, max_combo:int, mods):
        self.pp_100 = pp_100
        self.pp_99 = pp_99
        self.pp_97 = pp_97
        self.pp_95 = pp_95
        self.star_rating = star_rating
        self.max_combo = max_combo
        self.mods = mods