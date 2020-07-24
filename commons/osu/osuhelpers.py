import re
import classes.osu as osu
import commons.redisIO as redisIO

patternBeatmapLink = re.compile(r"(https?):\/\/([-\w._]+)(\/[-\w._]\?(.+)?)?(\/b(eatmaps)?\/(?P<bmapid1>[0-9]+)|\/s\/(?P<bmapsetid1>[0-9]+)|\/beatmapsets\/(?P<bmapsetid2>[0-9]+)(#(?P<mode>[a-z]+)\/(?P<bmapid2>[0-9]+))?)")
patternBeatmapId = re.compile(r"^(?P<bmapid>[0-9]+)$")

class osuHelper():

    def __init__(self, bot):
        self.bot = bot
        self.osuAPI = self.bot.osuAPI

    @staticmethod
    def parseArgsV2(**kwargs):
        args = kwargs.pop("args")
        customArgs = kwargs.pop("customArgs") if 'customArgs' in kwargs else []

        qtype = "string"
        server = osu.Server.BANCHO
        mode = osu.Mode.STANDARD
        position = None
        recent = False
        l_flag = False

        if args is None:
            args = []
        else:
            args = args.split(" ")

        if '-bancho' in args:
            server = osu.Server.BANCHO
            args.pop(args.index('-bancho'))

        if '-ripple' in args:
            server = osu.Server.RIPPLE
            args.pop(args.index('-ripple'))

        if '-akatsukirx' in args:
            server = osu.Server.AKATSUKIRX
            args.pop(args.index('-akatsukirx'))

        if '-akatsuki' in args:
            server = osu.Server.AKATSUKI
            args.pop(args.index('-akatsuki'))

        if '-enjuu' in args:
            server = osu.Server.ENJUU
            args.pop(args.index('-enjuu'))

        if '-r' in args:
            recent = True
            args.pop(args.index('-r'))

        if '-l' in args:
            l_flag = True
            args.pop(args.index('-l'))

        if '-m' in args:
            try:
                mode = osu.Mode.fromId(int(args[args.index('-m') + 1]))
                args.pop(args.index('-m') + 1)
            except Exception:
                mode = osu.Mode.STANDARD
            args.pop(args.index('-m'))

        if '-p' in args:
            try:
                position = int(args[args.index('-p') + 1])
                args.pop(args.index('-p') + 1)
            except Exception:
                position = 0
            args.pop(args.index('-p'))

        parsedArgs = {
            'qtype': qtype,
            'mode': mode,
            'server': server,
            'position': position,
            'recent': recent,
            'l_flag': l_flag
        }

        for index, name in enumerate(customArgs):
            if index > len(args) - 1:
                parsedArgs[name] = None
            else:
                parsedArgs[name] = args[index]

        return parsedArgs

    @staticmethod
    def parseArgs(**kwargs):
        args = kwargs.pop("args")
        validArgs = kwargs.pop("validArgs") if 'validArgs' in kwargs else []

        qtype = "string"
        server = 'bancho'
        mode = 0
        position = None
        recentList = False

        args = args.split(" ")

        if '-bancho' in args:
            args.pop(args.index('-bancho'))

        if '-ripple' in args:
            server = 'ripple'
            args.pop(args.index('-ripple'))

        if '-akatsukirx' in args:
            server = 'akatsukirx'
            args.pop(args.index('-akatsukirx'))

        if '-akatsuki' in args:
            server = 'akatsuki'
            args.pop(args.index('-akatsuki'))

        if '-enjuu' in args:
            server = 'enjuu'
            args.pop(args.index('-enjuu'))

        if '-r' in args and '-r' in validArgs:
            recentList = True
            args.pop(args.index('-r'))

        if '-l' in args and '-l' in validArgs:
            recentList = True
            args.pop(args.index('-l'))

        if '-m' not in args:
            mode = 0

        elif '-m' in validArgs:
            try:
                mode = int(args[args.index('-m') + 1])
                args.pop(args.index('-m') + 1)
            except Exception:
                mode = 0
            args.pop(args.index('-m'))

        if '-p' in validArgs and '-p' in args:
            try:
                position = int(args[args.index('-p') + 1])
                args.pop(args.index('-p') + 1)
            except Exception:
                position = 0
            args.pop(args.index('-p'))

        user = ' '.join(args)

        parsedArgs = {
            'qtype': qtype,
            'mode': mode,
            'server': server,
            'recentList': recentList,
            'user': user,
            'position': position
        }

        return parsedArgs

    @staticmethod
    def getMods(number):
        mod_list= []
        if number == 0:	mod_list.append('NM')
        if number & 1<<0:   mod_list.append('NF')
        if number & 1<<1:   mod_list.append('EZ')
        if number & 1<<2:   mod_list.append('TD')
        if number & 1<<3:   mod_list.append('HD')
        if number & 1<<4:   mod_list.append('HR')
        if number & 1<<14:  mod_list.append('PF')
        elif number & 1<<5:   mod_list.append('SD')
        if number & 1<<9:   mod_list.append('NC')
        elif number & 1<<6: mod_list.append('DT')
        if number & 1<<7:   mod_list.append('RX')
        if number & 1<<8:   mod_list.append('HT')
        if number & 1<<10:  mod_list.append('FL')
        if number & 1<<12:  mod_list.append('SO')
        if number & 1<<15:  mod_list.append('4K')
        if number & 1<<16:  mod_list.append('5K')
        if number & 1<<17:  mod_list.append('6K')
        if number & 1<<18:  mod_list.append('7K')
        if number & 1<<19:  mod_list.append('8K')
        if number & 1<<20:  mod_list.append('FI')
        if number & 1<<24:  mod_list.append('9K')
        if number & 1<<25:  mod_list.append('10K')
        if number & 1<<26:  mod_list.append('1K')
        if number & 1<<27:  mod_list.append('3K')
        if number & 1<<28:  mod_list.append('2K')
        return ''.join(mod_list)

    async def getBeatmapFromText(self, text, ignoreID = False) -> osu.Beatmap:
        resultLink = patternBeatmapLink.match(text)
        if resultLink is not None:
            setId, beatmapId = None, None
            if resultLink.group("bmapsetid2") is not None:
                setId = int(resultLink.group("bmapsetid2"))
                if resultLink.group("bmapid2") is not None:
                    beatmapId = int(resultLink.group("bmapid2"))
            elif resultLink.group("bmapid1") is not None:
                beatmapId = int(resultLink.group("bmapid1"))
            else:
                setId = int(resultLink.group("bmapset1"))
            return await self.osuAPI.getbmap(beatmapId, setId)

        if not ignoreID:
            resultId = patternBeatmapId.match(text)
            if resultId is not None:
                beatmapId = int(resultId.group("bmapid"))
                return await self.osuAPI.getbmap(beatmapId)

        return None

    async def getBeatmapFromHistory(self, ctx) -> osu.Beatmap:
        beatmap_id = redisIO.getValue(ctx.message.channel.id)
        if beatmap_id is None:
            return None

        mode = osu.Mode.fromId(redisIO.getValue(f'{ctx.message.channel.id}.mode'))
        return await self.osuAPI.getbmap(beatmap_id, mode=mode)