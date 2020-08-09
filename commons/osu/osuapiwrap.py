import aiohttp
from io import StringIO
import classes.osu as osu
import pyttanko as pyt
from typing import List

class osuAPI():

    def __init__(self, token):
        self.__token = token

    @staticmethod
    def __convAkaRXProfile(res, mode = 0): #Converts akatsuki!rx fullrx API response to a bancho-like one
            modes = {0: "std", 1: "taiko", 2: "ctb", 3: "mania"}
            if res['code'] != 200:
                raise ValueError("Invalid query or API down.")
            try:
                return [
                    {
                        "user_id": res['id'],
                        "username": res['username'],
                        "join_date": res['registered_on'],
                        "count300": 0,
                        "count100": 0,
                        "count50": 0,
                        "playcount": res[modes[mode]]['playcount'],
                        "ranked_score": res[modes[mode]]['ranked_score'],
                        "total_score": res[modes[mode]]['total_score'],
                        "pp_rank": res[modes[mode]]['global_leaderboard_rank'],
                        "level": res[modes[mode]]['level'],
                        "pp_raw": res[modes[mode]]['pp'],
                        "accuracy": res[modes[mode]]['accuracy'],
                        "count_rank_ss": 0,
                        "count_rank_ssh": 0,
                        "count_rank_s": 0,
                        "count_rank_sh": 0,
                        "count_rank_a": 0,
                        "country": res['country'],
                        "total_seconds_played": res[modes[mode]]['play_time'],
                        "pp_country_rank": res[modes[mode]]['country_leaderboard_rank'],
                        "events": []
                    }
                ]
            except KeyError:
                return [
                    {
                        "user_id": res['id'],
                        "username": res['username'],
                        "join_date": res['registered_on'],
                        "count300": 0,
                        "count100": 0,
                        "count50": 0,
                        "playcount": res[modes[mode]]['playcount'],
                        "ranked_score": res[modes[mode]]['ranked_score'],
                        "total_score": res[modes[mode]]['total_score'],
                        "pp_rank": res[modes[mode]]['global_leaderboard_rank'],
                        "level": res[modes[mode]]['level'],
                        "pp_raw": res[modes[mode]]['pp'],
                        "accuracy": res[modes[mode]]['accuracy'],
                        "count_rank_ss": 0,
                        "count_rank_ssh": 0,
                        "count_rank_s": 0,
                        "count_rank_sh": 0,
                        "count_rank_a": 0,
                        "country": res['country'],
                        "total_seconds_played": res[modes[mode]]['total_playtime'],
                        "pp_country_rank": res[modes[mode]]['country_leaderboard_rank'],
                        "events": []
                    }
                ]

    async def getuser(
            self,
            usr,
            qtype:str='id',
            mode:osu.Mode=osu.Mode.STANDARD,
            server:osu.Server=osu.Server.BANCHO) -> osu.User:
        async with aiohttp.ClientSession() as cs:
            params = {
                'k': self.__token,
                'u': usr,
                'm': mode.id,
                'type': qtype
            }

            if server is not osu.Server.BANCHO:
                params.pop('k')
                if server is osu.Server.AKATSUKIRX:
                    if qtype == 'id':
                        params['id'] = usr
                    else:
                        params['name'] = usr

            async with cs.get( server.api_getuser, params = params ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    if server is osu.Server.AKATSUKIRX:
                        res = self.__convAkaRXProfile(res)
                    if server is not osu.Server.BANCHO:
                        res[0]['total_seconds_played'] = 0
                    return osu.User(res[0], server, mode)

    async def getbmap(
            self,
            beatmap_id:int=None,
            beatmapset_id:int=None,
            mode:osu.Mode=osu.Mode.STANDARD,
            server:osu.Server=osu.Server.BANCHO,
            mods:osu.Mods=osu.Mods(0),
            limit:int=1) -> osu.Beatmap:
        # mods = __cleanMods(kwargs.pop('mods', 0), mode)
        async with aiohttp.ClientSession() as cs:
            params = {
                'k': self.__token,
                'm': mode.id,
                'mods': int(mods),
                'limit': limit,
                'a': 1
            }

            if beatmap_id is None:
                params['s'] = beatmapset_id
            else:
                params['b'] = beatmap_id
            async with cs.get( server.api_getbmap, params=params ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    return osu.Beatmap(res[0], server)

    async def getbmaposu(
            self,
            beatmap_id:int,
            server:osu.Server=osu.Server.BANCHO) -> pyt.beatmap:

        async with aiohttp.ClientSession() as cs:
            async with cs.get( server.api_getbmaposu + str(beatmap_id) ) as r:
                return pyt.parser().map(StringIO(await r.text()))

    async def getrecent(
            self,
            user:osu.User,
            limit:int=1) -> osu.RecentScore:
        async with aiohttp.ClientSession() as cs:
            params = {
                'k': self.__token,
                'u': user.user_id,
                'type': 'id',
                'm': user.mode.id,
                'limit': limit
            }

            if user.server is not osu.Server.BANCHO:
                params.pop('k')
                if user.server is osu.Server.AKATSUKIRX:
                    params['rx'] = 1
                    if params['type'] == 'id':
                        params['id'] = user.user_id
                    else:
                        params['name'] = user.username

            async with cs.get( user.server.api_getrecent, params=params ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    if user.server is osu.Server.AKATSUKIRX:
                        res = res['scores']
                    return list(map(lambda recent: osu.RecentScore(recent, user.server, user.mode), res))

    async def getusrtop(
            self,
            user:osu.User,
            limit:int = 1) -> List[osu.RecentScore]:
        async with aiohttp.ClientSession() as cs:
            params = {
                'k': self.__token,
                'u': user.user_id,
                'type': 'id',
                'limit': limit,
                'm': user.mode.id
            }

            if user.server is not osu.Server.BANCHO:
                params.pop('k')
                if user.server is osu.Server.AKATSUKIRX:
                    params['rx'] = 1
                    if params['type'] == 'id':
                        params['id'] = user.user_id
                    else:
                        params['name'] = user.username

            async with cs.get( user.server.api_getusrtop, params=params ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    if user.server is osu.Server.AKATSUKIRX:
                        res = res['scores']
                    return list(map(lambda top: osu.RecentScore(top), res))

    async def getusrscores(
            self,
            user:osu.User,
            beatmap_id:int,
            limit:int = 1
        ) -> List[osu.BeatmapScore]:
        async with aiohttp.ClientSession() as cs:
            params = {
                'k': self.__token,
                'u': user.user_id,
                'type': 'id',
                'b': beatmap_id,
                'm': user.mode.id
            }

            if user.server is not osu.Server.BANCHO:
                params.pop('k')
                if user.server is osu.Server.AKATSUKIRX:
                    params['rx'] = 1
                    if params['type'] == 'id':
                        params['id'] = user.user_id
                    else:
                        params['name'] = user.username

            async with cs.get( user.server.api_getusrscores, params=params ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    if user.server is not osu.Server.BANCHO:
                        try:
                            res = res['scores']
                        except Exception:
                            pass
                    return list(map(lambda score: osu.BeatmapScore(score, beatmap_id), res[:limit]))
