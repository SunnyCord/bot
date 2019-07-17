import pyttanko as pyt
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

def calculatePlay(bmap, mode: int = 0, play = [], calcPP: int = 1):

    count0, count50, count100, count300, countgeki, countkatu = play['countmiss'], play['count50'], play['count100'], play['count300'], play['countgeki'], play['countkatu']
    combo, mods, perfect = play['maxcombo'], play['enabled_mods'], play['perfect']

    if mode == 0 :
        #Standard

        modString = pyt.mods_str(mods)
        accuracy = acc.stdCalc(count0, count50, count100, count300)
        p = pyt.parser()
        beatmap = p.map(bmap)
        objcount = beatmap.ncircles + beatmap.nsliders + beatmap.nspinners
        totalhits = count50 + count100 + count0
        sr = pyt.diff_calc().calc(beatmap, mods)
        pp = 0
        if calcPP == 1:
            pp, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods, n300=count300, n100=count100, n50=count50, nmiss=count0, combo=combo)
        pp_fc = 0
        if perfect == 0:
            pp_fc, _, _, _, _ = pyt.ppv2(sr.aim, sr.speed, bmap=beatmap, mods=mods, n300=objcount - totalhits, n100=count100, n50=count50, nmiss=0, combo=beatmap.max_combo())
            accuracy_fc = acc.stdCalc(0, count50, count100, objcount - totalhits)

        beatmapDict = {
            "title": beatmap.title,
            "artist": beatmap.artist,
            "creator": beatmap.creator,
            "version": beatmap.version,
            "objcount": objcount,
            "mode": beatmap.mode,
            "maxcombo": beatmap.max_combo()
        }

        playDict = {
            "totalhits": totalhits + count0,
            "pp": round(pp, 2),
            "pp_fc": round(pp_fc, 2),
            "accuracy": accuracy,
            "accuracy_fc": 0 if perfect ==1 else accuracy_fc,
            "modString": modString if modString != "nomod" else "NM",
            "rating": round(sr.total, 2),
            "completion": round( ((totalhits+count300)*100)/objcount, 2),
            "mode_icon": "https://i.imgur.com/lT2nqls.png",
            "mode_name": "Standard"
        }

    elif mode == 1:
        #Taiko

        p = pyt.parser()
        beatmap = p.map(bmap)
        beatmapDict = {
            "title": beatmap.title,
            "artist": beatmap.artist,
            "creator": beatmap.creator,
            "version": beatmap.version,
            "objcount": 0,
            "mode": beatmap.mode,
            "maxcombo": None
        }

        playDict = {
            "totalhits": 0,
            "pp": 0,
            "pp_fc": None,
            "accuracy": acc.taikoCalc(count0, count100, count300),
            "accuracy_fc": 0 if perfect == 1 else acc.taikoCalc(0, count100, count300+count0),
            "modString": modString if modString != "nomod" else "NM",
            "rating": "N/A",
            "completion": 100,
            "mode_icon": "https://i.imgur.com/G6bzM0X.png",
            "mode_name": "Taiko"
        }

    elif mode == 2:
        #CTB

        accuracy = acc.ctbCalc(count0, countkatu, count50, count100, count300)
        beatmap = Beatmap(bmap)
        modString = pyt.mods_str(mods)
        #p = pyt.parser()
        #beatmapMetadata = p.map(bmap)
        difficulty = Difficulty(beatmap, mods)
        pp = 0
        if calcPP == 1:
            pp = round(calculate_pp(difficulty, accuracy, combo, count0), 2)
        beatmapDict = {
            "title": "",
            "artist": "",
            "creator": "",
            "version": "",
            "objcount": len(beatmap.hitobjects),
            "mode": 2,
            "maxcombo": beatmap.max_combo
        }
        playDict = {
            "totalhits": 0,
            "pp":  pp,
            "pp_fc": None,
            "accuracy": accuracy,
            "accuracy_fc": 0,
            "modString": modString if modString != "nomod" else "NM",
            "rating": round(difficulty.star_rating, 2),
            "completion": 100,
            "mode_icon": "https://i.imgur.com/EsanYkH.png",
            "mode_name": "Catch the Beat"
        }

    elif mode == 3:
        #Mania

        #p = pyt.parser()
        #beatmap = p.map(bmap)
        #modString = pyt.mods_str(mods)
        beatmapDict = {
            "title": "",#beatmap.title,
            "artist": "",#beatmap.artist,
            "creator": "",#beatmap.creator,
            "version": "",#beatmap.version,
            "objcount": 0,
            "mode": "",#beatmap.mode,
            "maxcombo": None
        }

        playDict = {
            "totalhits": 0,
            "pp": 0,
            "pp_fc": None,
            "accuracy": acc.maniaCalc(count0, count50, count100, countkatu, count300, countgeki),
            "accuracy_fc": 0,
            "modString": osuhelpers.getMods(mods),
            "rating": "N/A",
            "completion": 100,
            "mode_icon": "https://i.imgur.com/0uZM1PZ.png",
            "mode_name": "Mania"
        }

    return beatmapDict, playDict