import pyttanko as pyt
from commons.catchthepp.osu_parser.beatmap import Beatmap
from commons.catchthepp.osu.ctb.difficulty import Difficulty
from commons.catchthepp.ppCalc import calculate_pp



def stdCalc(bmap, count0: int, count50: int, count100: int, count300: int, combo: int, mods: int, perfect: int, max_combo: int):
    p = pyt.parser()
    beatmap = p.map(bmap)
    sr = pyt.diff_calc().calc(beatmap, mods)
    pp, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods, n300=count300, n100=count100, n50=count50, nmiss=count0, combo=combo)
    pp_fc = 0
    if perfect == 0:
        pp_fc, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods, n300=count300+count0, n100=count100, n50=count50, nmiss=0, combo=max_combo)
    return round(sr.total, 2), round(pp, 2), round(pp_fc, 2)

def taikoCalc(bmap, mods: int):
    #p = pyt.parser()
    #beatmap = p.map(bmap)
    #sr = pyt.diff_calc().calc(beatmap, mods)
    #pp, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap)
    #return round(sr.total, 2), round(pp, 2)
    return "N/A", "Not implemented."

def ctbCalc(bmap, accuracy: float, count0: int, mods: int, max_combo: int):
    beatmap = Beatmap(bmap)
    difficulty = Difficulty(beatmap, mods)
    return round(difficulty.star_rating, 2), round(calculate_pp(difficulty, accuracy, max_combo, count0), 2), beatmap.max_combo

def maniaCalc():
    return "N/A", "Not implemented."