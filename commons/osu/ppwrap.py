import aiohttp
import classes.osu as osu
from typing import List

class ppAPI():

    def __init__(self, URL, secret):
        self.__secret = secret
        self.__URL = URL
        self.__session = aiohttp.ClientSession()
    
    async def calculateScore(self, score):

        payload = {
            "secret": self.__secret,
            "mode": int(score.mode),
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

        resp = await self.__session.post(f"{self.__URL}/api", json=payload)

        result = await resp.json()

        return osu.Performance(result['pp'], 0, 0, 0, result['sr'], result['max_combo'])
    
    async def calculateBeatmap(self, beatmap, mods, mode: int = None):

        if mode is None:
            mode = beatmap.mode
        
        # To-do



    
