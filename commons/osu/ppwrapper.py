import pyttanko as pyt
import commons.osu.classes as osu
from commons.osu.catchthepp.osu_parser.beatmap import Beatmap
from commons.osu.catchthepp.osu.ctb.difficulty import Difficulty
from commons.osu.catchthepp.ppCalc import calculate_pp
from commons.osu import accuracycalculator as acc
from commons.osu import osuhelpers


def getObjectCount(bmap):
    p = pyt.parser()
    beatmap = p.map(bmap)
    return beatmap.ncircles + beatmap.nsliders + beatmap.nspinners

def getBeatmapCompletion(totalhits: int, objcount: int):
    return round( (totalhits*100)/objcount, 2)

def stdCalc(bmap, count0: int, count50: int, count100: int, count300: int, combo: int, mods: int, perfect: int, max_combo: int):
    p = pyt.parser()
    beatmap = p.map(bmap)
    objcount = beatmap.ncircles + beatmap.nsliders + beatmap.nspinners
    totalhits = count50 + count100 + count300
    sr = pyt.diff_calc().calc(beatmap, mods)
    pp, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods, n300=count300, n100=count100, n50=count50, nmiss=count0, combo=combo)
    pp_fc = 0
    if perfect == 0:
        pp_fc, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods, n300=objcount - totalhits, n100=count100, n50=count50, nmiss=0, combo=max_combo)
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

def calculateBeatmap(beatmap:pyt.beatmap, mods:osu.Mods, mode:osu.Mode = osu.Mode.STANDARD):
    if mode == 0:
        # Standard
        mods_bitmask = int(mods)
        sr = pyt.diff_calc().calc(beatmap, mods_bitmask)
        objcount = beatmap.ncircles + beatmap.nsliders + beatmap.nspinners

        n300, n100, n50 = pyt.acc_round(100, objcount, 0)
        pp_100, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods_bitmask, n300=n300, n100=n100, n50=n50, nmiss=0)

        n300, n100, n50 = pyt.acc_round(99, objcount, 0)
        pp_99, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods_bitmask, n300=n300, n100=n100, n50=n50, nmiss=0)

        n300, n100, n50 = pyt.acc_round(97, objcount, 0)
        pp_97, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods_bitmask, n300=n300, n100=n100, n50=n50, nmiss=0)

        n300, n100, n50 = pyt.acc_round(95, objcount, 0)
        pp_95, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods_bitmask, n300=n300, n100=n100, n50=n50, nmiss=0)

        perfDict = {
            "pp_100": round(pp_100, 2),
            "pp_99": round(pp_99, 2),
            "pp_97": round(pp_97, 2),
            "pp_95": round(pp_95, 2),
            "mods": mods,
            "star_rating": sr.total
        }

    return perfDict

def calculatePlay(beatmap:pyt.beatmap, score:osu.Score, calcPP:int = 1) -> osu.Performance:
    
    if score.mode == osu.Mode.STANDARD:
        objcount = beatmap.ncircles + beatmap.nsliders + beatmap.nspinners
        sr = pyt.diff_calc().calc(beatmap, int(score.enabled_mods))

        if calcPP == 1:
            pp, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=int(score.enabled_mods), n300=score.count300, n100=score.count100, n50=score.count50, nmiss=score.countmiss, combo=score.maxcombo)
        
        accuracy_fc = ((objcount - score.count100 - score.count50) * 6 + score.count100 * 2 + score.count50) / (objcount * 6)
        n300, n100, n50 = pyt.acc_round(accuracy_fc * 100, objcount, 0)
        pp_fc, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=int(score.enabled_mods), n300=n300, n100=n100, n50=n50, nmiss=0, combo=beatmap.max_combo())
            
        return osu.Performance(pp, pp_fc, accuracy_fc, round((score.total_hits() * 100) / objcount, 2), sr.total)

    # elif score.mode == osu.Mode.CTB:
    #     accuracy = acc.ctbCalc(score.countmiss, score.countkatu, score.count50, score.count100, score.count300)
    #     beatmap = Beatmap(beatmap)
    #     difficulty = Difficulty(beatmap, int(score.enabled_mods))
    #     pp = 0
    #     if calcPP == 1:
    #         pp = round(calculate_pp(difficulty, accuracy, score.combo, score.countmiss), 2)
    #     return osu.Performance(pp, 0, accuracy, 0, 100)