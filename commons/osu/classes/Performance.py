import commons.osu.classes as osu

class Performance:
    def __init__(self, pp:float, pp_fc:float, accuracy_fc:float, completion:float, star_rating:float):
        self.pp:float = pp
        self.pp_fc:float = pp_fc
        self.accuracy_fc:float = accuracy_fc
        self.completion:float = completion
        self.star_rating:float = star_rating