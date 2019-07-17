import aiohttp
from io import StringIO

class APIService:

    def __init__(self, token):

        self.__token = token

        self.__bmapURLModes = ['osu', 'taiko', 'fruits', 'mania']

        self.__API_URLs = [
            {
                'getuser': lambda usr, mode, qtype: f'https://osu.ppy.sh/api/get_user?k={self.__token}&u={usr}&m={mode}&type={qtype}',
                'getbmap': lambda mode, s, b, limit, mods: f'https://osu.ppy.sh/api/get_beatmaps?k={self.__token}&m={mode}&a=1{f"&b={b}" if b is not None else ""}{f"&b={s}" if s is not None else ""}&mods={mods}{f"&limit={limit}" if limit is not None else ""}',
                'getusrtop': lambda usr, mode, qtype, limit: f'https://osu.ppy.sh/api/get_user_best?k={self.__token}&u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getrecent': lambda usr, mode, qtype, limit: f'https://osu.ppy.sh/api/get_user_recent?k={self.__token}&u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getbmaposu': lambda b: f'https://osu.ppy.sh/osu/{b}',
                'getavatar': lambda usr: f'https://a.ppy.sh/{usr}',
                'getprofileurl': lambda usr: f'https://osu.ppy.sh/users/{usr}',
                'getbmapurl': lambda mode, s, b: f'https://osu.ppy.sh/beatmapsets/{s}#{self.__bmapURLModes[mode]}/{b}',
                'getusrscores': lambda usr, mode, b, qtype, limit: f'https://osu.ppy.sh/api/get_scores?k={self.__token}&u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}&b={b}'
            },
            {
                'getuser': lambda usr, mode, qtype: f'https://ripple.moe/api/get_user?u={usr}&m={mode}&type={qtype}',
                'getbmap': lambda mode, s, b, limit, mods: f'https://ripple.moe/api/get_beatmaps?m={mode}&a=1{f"&b={b}" if b is not None else ""}{f"&b={s}" if s is not None else ""}{f"&limit={limit}" if limit is not None else ""}',
                'getusrtop': lambda usr, mode, qtype, limit: f'https://ripple.moe/api/get_user_best?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getrecent': lambda usr, mode, qtype, limit: f'https://ripple.moe/api/get_user_recent?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getbmaposu': lambda b: f'https://ripple.moe/osu/{b}',
                'getavatar': lambda usr: f'https://a.ripple.moe/{usr}',
                'getprofileurl': lambda usr: f'https://ripple.moe/u/{usr}',
                'getbmapurl': lambda mode, s, b: f'https://ripple.moe/b/{b}?mode={mode}',
                'getusrscores': lambda usr, mode, b, qtype, limit: f'https://ripple.moe/api/get_scores?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}&b={b}'
            },
            {
                'getuser': lambda usr, mode, qtype: f'https://akatsuki.pw/api/get_user?u={usr}&m={mode}&type={qtype}',
                'getbmap': lambda mode, s, b, limit, mods: f'https://akatsuki.pw/api/get_beatmaps?m={mode}&a=1{f"&b={b}" if b is not None else ""}{f"&b={s}" if s is not None else ""}{f"&limit={limit}" if limit is not None else ""}',
                'getusrtop': lambda usr, mode, qtype, limit: f'https://akatsuki.pw/api/get_user_best?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getrecent': lambda usr, mode, qtype, limit: f'https://akatsuki.pw/api/get_user_recent?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getbmaposu': lambda b: f'https://osu.ppy.sh/osu/{b}',
                'getavatar': lambda usr: f'https://a.akatsuki.pw/{usr}',
                'getprofileurl': lambda usr: f'https://akatsuki.pw/u/{usr}',
                'getbmapurl': lambda mode, s, b: f'https://akatsuki.pw/b/{b}?mode={mode}',
                'getusrscores': lambda usr, mode, b, qtype, limit: f'https://akatsuki.pw/api/get_scores?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}&b={b}'
            },
            {
                'getuser': lambda usr, mode, qtype: f'http://akatsuki.pw/api/v1/users/rxfull?{"name" if qtype is "string" else "id"}={usr}',
                'getbmap': lambda mode, s, b, limit, mods: f'https://akatsuki.pw/api/get_beatmaps?m={mode}&a=1{f"&b={b}" if b is not None else ""}{f"&b={s}" if s is not None else ""}{f"&limit={limit}" if limit is not None else ""}',
                'getusrtop': lambda usr, mode, qtype, limit: f'https://akatsuki.pw/api/get_user_best?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getrecent': lambda usr, mode, qtype, limit: f'https://akatsuki.pw/api/get_user_recent?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getbmaposu': lambda b: f'https://osu.ppy.sh/osu/{b}',
                'getavatar': lambda usr: f'https://a.akatsuki.pw/{usr}',
                'getprofileurl': lambda usr: f'https://akatsuki.pw/rx/u/{usr}',
                'getbmapurl': lambda mode, s, b: f'https://akatsuki.pw/b/{b}?mode={mode}',
                'getusrscores': lambda usr, mode, b, qtype, limit: f'https://akatsuki.pw/api/get_scores?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}&b={b}'
            },
            {
                'getuser': lambda usr, mode, qtype: f'https://enjuu.click/api/get_user?u={usr}&m={mode}&type={qtype}',
                'getbmap': lambda mode, s, b, limit, mods: f'https://enjuu.click/api/get_beatmaps?m={mode}&a=1{f"&b={b}" if b is not None else ""}{f"&b={s}" if s is not None else ""}{f"&limit={limit}" if limit is not None else ""}',
                'getusrtop': lambda usr, mode, qtype, limit: f'https://enjuu.click/api/get_user_best?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getrecent': lambda usr, mode, qtype, limit: f'https://enjuu.click/api/get_user_recent?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}',
                'getbmaposu': lambda b: f'https://osu.ppy.sh/osu/{b}',
                'getavatar': lambda usr: f'https://a.enjuu.click/{usr}',
                'getprofileurl': lambda usr: f'https://enjuu.click/u/{usr}',
                'getbmapurl': lambda mode, s, b: f'https://enjuu.click/b/{b}?mode={mode}',
                'getusrscores': lambda usr, mode, b, qtype, limit: f'https://enjuu.click/api/get_scores?u={usr}&m={mode}&type={qtype}{f"&limit={limit}" if limit is not None else ""}&b={b}'
            }
        ]

        self.__osuServers = {
            'bancho': 0,
            'ripple': 1,
            'akatsuki': 2,
            'akatsukirx': 3,
            'enjuu': 4,
            'gatari': 5
        }

    def __convAkaRXProfile(self, res, mode = 0): #Converts akatsuki!rx fullrx API response to a bancho-like one
        modes = {0: "std", 1: "taiko", 2: "ctb", 3: "mania"}
        if res['code'] != 200:
            raise ValueError("Invalid query or API down.")
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
                "total_seconds_played": res[modes[mode]]['playtime'],
                "pp_country_rank": res[modes[mode]]['country_leaderboard_rank'],
                "events": []
            }
        ]

    def __cleanProfileRes(self, res):
        res[0]["pp_rank"] = int(res[0]["pp_rank"])
        res[0]["pp_country_rank"] = int(res[0]["pp_country_rank"])
        res[0]["pp_raw"] = float(res[0]["pp_raw"])
        res[0]["accuracy"] = round(float(res[0]["accuracy"]), 2) if res[0]["accuracy"] is not None else None
        res[0]["total_seconds_played"] = int(res[0]["total_seconds_played"])
        res[0]["playcount"] = int(res[0]["playcount"]) if res[0]["playcount"] is not None else None
        res[0]["country"] = res[0]["country"] if res[0]["country"] is not None else "XX"
        res[0]["level"] = int(float(res[0]["level"]))
        res[0]["level_progress"] = round((float(res[0]["level"])%1*100), 2)

        return res
    
    def __cleanBmapRes(self, res):
        for index, diff in enumerate(res):
            res[index]['beatmapset_id'] = int(diff['beatmapset_id'])
            res[index]['approved'] = int(diff['approved'])
            res[index]['difficultyrating'] = round(float(diff['difficultyrating']), 2)

        return res

    def __cleanRecentRes(self, res):
        for index, play in enumerate(res):
            res[index]['countmiss'] = int(play['countmiss'])
            res[index]['count50'] = int(play['count50'])
            res[index]['count100'] = int(play['count100'])
            res[index]['count300'] = int(play['count300'])
            res[index]['countgeki'] = int(play['countgeki'])
            res[index]['countkatu'] = int(play['countkatu'])
            res[index]['maxcombo'] = int(play['maxcombo'])
            res[index]['enabled_mods'] = int(play['enabled_mods'])
            res[index]['perfect'] = int(play['perfect'])

        return res

    def __cleanTopRes(self, res):
        return self.__cleanRecentRes(res)

    def __cleanMods(self, modnum, mode):
        cleanModNum = 0
        if modnum & 1<<9: cleanModNum += 64
        elif modnum & 1<<6: cleanModNum += 64
        if modnum & 1<<4: cleanModNum += 16

        return cleanModNum

    async def getuser(self, **kwargs):

        usr = kwargs.pop('usr')

        mode = kwargs.pop('mode') if 'mode' in kwargs else 0

        qtype = kwargs.pop('qtype') if 'qtype' in kwargs else 'id'

        server = self.__osuServers[kwargs.pop('server')] if 'server' in kwargs else 0

        async with aiohttp.ClientSession() as cs:
            async with cs.get( self.__API_URLs[server]['getuser'](usr, mode, qtype) ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    if server is 3:
                        res = self.__convAkaRXProfile(res)
                    if server is not 0:
                        res[0]['total_seconds_played'] = 0
                    res[0]['avatar_url'], res[0]['profile_url'] = self.__API_URLs[server]['getavatar'](res[0]['user_id']), self.__API_URLs[server]['getprofileurl'](res[0]['user_id'])
                    return self.__cleanProfileRes(res)[0]

    async def getbmap(self, **kwargs):

        mode = kwargs.pop('mode') if 'mode' in kwargs else 0

        s = kwargs.pop('s') if 's' in kwargs else None

        b = kwargs.pop('b') if 'b' in kwargs else None

        server = self.__osuServers[kwargs.pop('server')] if 'server' in kwargs else 0

        limit = kwargs.pop('limit') if 'limit' in kwargs else 1

        mods = self.__cleanMods(kwargs.pop('mods'), mode) if 'mods' in kwargs else 0

        async with aiohttp.ClientSession() as cs:
            async with cs.get( self.__API_URLs[server]['getbmap'](mode, s, b, limit, mods) ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    res[0]['beatmap_url'] = self.__API_URLs[server]['getbmapurl'](mode, res[0]['beatmapset_id'], b)
                    return self.__cleanBmapRes(res)

    async def getbmaposu(self, **kwargs):

        b = kwargs.pop('b')

        server = self.__osuServers[kwargs.pop('server')] if 'server' in kwargs else 0

        async with aiohttp.ClientSession() as cs:
            async with cs.get( self.__API_URLs[server]['getbmaposu'](b) ) as r:
                return StringIO(await r.text())

    async def getrecent(self, **kwargs):

        usr = kwargs.pop('usr')

        mode = kwargs.pop('mode') if 'mode' in kwargs else 0

        qtype = kwargs.pop('qtype') if 'qtype' in kwargs else 'id'

        limit = kwargs.pop('limit') if 'limit' in kwargs else None

        server = self.__osuServers[kwargs.pop('server')] if 'server' in kwargs else 0

        async with aiohttp.ClientSession() as cs:
            async with cs.get( self.__API_URLs[server]['getrecent'](usr, mode, qtype, limit) ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    return self.__cleanRecentRes(res)

    async def getusrtop(self, **kwargs):

        usr = kwargs.pop('usr')

        mode = kwargs.pop('mode') if 'mode' in kwargs else 0

        qtype = kwargs.pop('qtype') if 'qtype' in kwargs else 'id'

        limit = kwargs.pop('limit') if 'limit' in kwargs else None

        server = self.__osuServers[kwargs.pop('server')] if 'server' in kwargs else 0

        async with aiohttp.ClientSession() as cs:
            async with cs.get( self.__API_URLs[server]['getusrtop'](usr, mode, qtype, limit) ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    return self.__cleanTopRes(res)

    async def getusrscores(self, **kwargs):

        usr = kwargs.pop('usr')

        mode = kwargs.pop('mode') if 'mode' in kwargs else 0

        b = kwargs.pop('b')

        qtype = kwargs.pop('qtype') if 'qtype' in kwargs else 'id'

        limit = kwargs.pop('limit') if 'limit' in kwargs else None

        server = self.__osuServers[kwargs.pop('server')] if 'server' in kwargs else 0

        async with aiohttp.ClientSession() as cs:
            async with cs.get( self.__API_URLs[server]['getusrscores'](usr, mode, b, qtype, limit) ) as r:
                res = await r.json()
                if res == []:
                    raise ValueError("Invalid query or API down.")
                else:
                    return self.__cleanTopRes(res)
