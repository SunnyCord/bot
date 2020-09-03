import aiohttp
import classes.osu as osu

class ppAPI():

    def __init__(self, URL, secret):
        self.__secret = secret
        self.__URL = URL
        self.__session = aiohttp.ClientSession()

    async def calculateScore(self, score, mode:int = None):

        if mode is None:
            mode = score.mode

        payload = {
            "secret": self.__secret,
            "mode": int(mode),
            "score": score.score,
            "count300": score.count300,
            "count100": score.count100,
            "count50": score.count50,
            "count0": score.countmiss,
            "katus": score.countkatu,
            "geki": score.countgeki,
            "combo": score.maxcombo,
            "mods": int(score.enabled_mods),
            "mapID": score.beatmap_id
        }

        resp = await self.__session.post(f"{self.__URL}/api/score", json=payload)

        result = await resp.json()

        pp_fc, acc_fc = 0, 0
        if score.maxcombo != result['max_combo'] and result['mode'] != 3:
            objcount = result['objcount']
            mistimedhits = payload['count50'] + payload['count100'] + payload['count0']
            payload['combo'] = result['max_combo']
            payload['count300'] =  objcount - mistimedhits
            payload['count0'] = 0
            if result['mode'] == 2:
                payload['count50'] += payload['katus']
                payload['katus'] = 0
            resp_fc = await self.__session.post(f"{self.__URL}/api/score", json=payload)
            result_fc = await resp_fc.json()
            pp_fc, acc_fc = result_fc['pp'], result_fc['accuracy']

        return osu.Performance(result['pp'], pp_fc, result['accuracy'], acc_fc, result['completion'], result['sr'], result['max_combo'])

    async def calculateBeatmap(self, beatmapID, mods, mode: int = None):

        if mode is None:
            mode = beatmap.mode

        payload = {
            "secret": self.__secret,
            "mode": int(mode),
            "mods": int(mods),
            "mapID": beatmapID
        }

        resp = await self.__session.post(f"{self.__URL}/api/map", json=payload)

        result = await resp.json()

        return osu.BeatmapPerformance(result['pp_100'], result['pp_99'], result['pp_97'], result['pp_95'], result['sr'], result['max_combo'], mods)
