import aiohttp
from io import StringIO
import classes.osu as osu
import pyttanko as pyt
from typing import List
from classes.exceptions import OsuAPIError

class osuAPI():

    def __init__(self, token):
        self.__token = token

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

            try:
                async with cs.get( server.api_getuser, params = params ) as r:
                    if (res := await r.json()) == []:
                        raise ValueError("Response is empty.")
                    else:
                        if server is not osu.Server.BANCHO:
                            res[0]['total_seconds_played'] = 0
                        return osu.User(res[0], server, mode)

            except Exception:
                raise OsuAPIError(server, "get_user", "Invalid query or API down.")

    async def getbmap(
            self,
            beatmap_id:int=None,
            beatmapset_id:int=None,
            mode:osu.Mode=osu.Mode.STANDARD,
            server:osu.Server=osu.Server.BANCHO,
            mods:osu.Mods=osu.Mods(0),
            limit:int=1) -> osu.Beatmap:
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

            try:
                async with cs.get( server.api_getbmap, params=params ) as r:
                    if (res := await r.json()) == []:
                        raise ValueError("Response is empty.")
                    else:
                        return osu.Beatmap(res[0], server)

            except Exception:
                raise OsuAPIError(server, "get_beatmap", "Invalid query or API down.")

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

            try:
                async with cs.get( user.server.api_getrecent, params=params ) as r:
                    if (res := await r.json()) == []:
                        raise ValueError("Response is empty.")
                    else:
                        return list(map(lambda recent: osu.RecentScore(recent, user.server, user.mode), res))

            except Exception:
                raise OsuAPIError(user.server, "get_recent","Invalid query or API down.")

    async def getusrtop(self, user:osu.User, limit:int = 1) -> List[osu.RecentScore]:

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

            try:
                async with cs.get( user.server.api_getusrtop, params=params ) as r:
                    if (res := await r.json()) == []:
                        raise ValueError("Response is empty.")
                    else:
                        return list(map(lambda top: osu.RecentScore(top), res))

            except Exception:
                raise OsuAPIError(user.server, "get_user_top","Invalid query or API down.")


    async def getusrscores(self, user:osu.User, beatmap_id:int, limit:int = 1) -> List[osu.BeatmapScore]:

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

            try:
                async with cs.get( user.server.api_getusrscores, params=params ) as r:
                    if (res := await r.json()) == []:
                        raise ValueError("Response is empty.")
                    else:
                        if user.server is not osu.Server.BANCHO:
                            try:
                                res = res['scores']
                            except Exception:
                                pass
                        return list(map(lambda score: osu.BeatmapScore(score, beatmap_id), res[:limit]))

            except Exception:
                raise OsuAPIError(user.server, "get_user_scores","Invalid query or API down.")

