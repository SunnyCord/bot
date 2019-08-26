import re
from discord.ext import commands
from datetime import datetime
from commons.osu import osuhelpers
from commons.osu import ppwrapper as ppc
from commons.osu import osuapiwrap
import commons.osu.classes as osuClasses
from commons.mongoIO import getOsu, setOsu
from commons.embeds import *
import commons.redisIO as redisIO
import pyttanko as pyt
from typing import List

class osu(commands.Cog, name='osu!'):
    """osu! related commands.\n*Valid Arguments:* ```fix\n-ripple, -akatsuki, akatsukirx, -enjuu```"""

    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def osuset(self, ctx, *, args):
        """Sets the osu! profile for the message author. ``eg. osuset Nice Aesthetics``"""

        try:
            parsedArgs = osuhelpers.parseArgsV2(args=args, customArgs=["user"])
            username = parsedArgs['user']
            profile:osuClasses.User = await osuapiwrap.getuser(username, 'string', server=parsedArgs['server'])
            setOsu(ctx.message.author, profile.user_id)
            await ctx.send(f"osu! profile succesfully set to {profile.username}")

        except ValueError:
            await ctx.send("User has not been found!")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["mania", "taiko", "ctb"])
    async def osu(self, ctx, *, args = None):
        """Shows osu! stats for a user.\nOther variants: ``mania, taiko, ctb``"""

        user = None
        server = osuClasses.Server.BANCHO

        if args is not None:
            parsedArgs = osuhelpers.parseArgs(args=args)
            user = parsedArgs['user']
            qtype = parsedArgs['qtype']
            server = osuClasses.Server.from_name(parsedArgs['server'])

        if not user:
            qtype = "id"
            user = getOsu(ctx.message.author)

        if user and type(user) is str and user.startswith("<@") and user.endswith(">"):
            qtype = "id"
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))

        if not user:
            return await ctx.send("Please set your profile!")

        mode = osuClasses.Mode.fromCommand(ctx.invoked_with)

        try:
            user:osuClasses.User = await osuapiwrap.getuser(usr = user, mode = mode, qtype = qtype, server = server)

        except ValueError:
            return await ctx.send("User has not been found or has not played enough!")

        if (user.playcount is not None) and (user.accuracy is not None):
            result = OsuProfileEmbed(user, mode, self.bot.configs.COLOR)
            return await ctx.send(embed = result)

        else:
            await ctx.send("User has not been found or has not played enough!")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["rs","r"])
    async def recent(self, ctx, *, args = None):
        """Shows recent osu! plays for a user. Modes can be specified ``eg. recent -m 2``.\n*Valid Arguments:* ```fix\n-l, -m```"""

        user = None
        server = osuClasses.Server.BANCHO
        mode = osuClasses.Mode.STANDARD
        limit = 1

        if args is not None:
            parsedArgs = osuhelpers.parseArgs(args=args, validArgs=['-l', '-m'])
            user = parsedArgs['user']
            qtype = parsedArgs['qtype']
            server = osuClasses.Server.from_name(parsedArgs['server'])
            mode = osuClasses.Mode.fromId(parsedArgs['mode'])
            limit = 5 if parsedArgs['recentList'] is True else 1

        if not user:
            qtype = "id"
            user = getOsu(ctx.message.author)

        if user and type(user) is str and user.startswith("<@") and user.endswith(">"):
            qtype = "id"
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))

        if not user:
            return await ctx.send("Please set your profile!")

        try:
            profile:osuClasses.User = await osuapiwrap.getuser(user, qtype, mode, server)
            recent_score:osuClasses.RecentScore = (await osuapiwrap.getrecent(profile, limit))[0]

        except ValueError:
            return await ctx.send("User has not been found or has no recent plays!")

        if self.bot.configs.REDIS is True:
            redisIO.setValue(ctx.message.channel.id, recent_score.beatmap_id)
            redisIO.setValue(f'{ctx.message.channel.id}.mode', mode.id)

        bmapfile:pyt.beatmap = await osuapiwrap.getbmaposu(beatmap_id=recent_score.beatmap_id)
        beatmap:osuClasses.Beatmap = await osuapiwrap.getbmap(recent_score.beatmap_id, mode=mode, server=server, mods=recent_score.enabled_mods)
        beatmap.max_combo = bmapfile.max_combo()

        recent_score.performance = await self.bot.loop.run_in_executor(None, ppc.calculatePlay, bmapfile, recent_score)

        result = OsuRecentEmbed(recent_score, beatmap)

        await ctx.send(f"**Most Recent osu! {mode.name_full} Play for {profile.username} on {server.name.lower()}:**", embed=result)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["ot", "tt", "ct", "mt", "taikotop", "ctbtop", "maniatop"])
    async def osutop(self, ctx, *, args=None):
        """Shows osu! top plays for a user. Modes can be specified ``eg. maniatop``.\n*Valid Arguments:* ```fix\n-r, -p```"""

        user = None
        server = osuClasses.Server.BANCHO
        limit = 5
        mode = osuClasses.Mode.fromCommand( ctx.invoked_with )
        recent:bool = False
        positions:List[int] = range(1, 100)

        if args is not None:
            parsedArgs = osuhelpers.parseArgsV2(args=args, customArgs=['user'])
            user = parsedArgs['user']
            qtype = parsedArgs['qtype']
            server = parsedArgs['server']
            
            if parsedArgs['recent'] is True:
                limit = 100
            elif parsedArgs['position'] is not None:
                limit = min(parsedArgs['position'], 100)

        if not user:
            qtype = "id"
            user = getOsu(ctx.message.author)

        if user and type(user) is str and user.startswith("<@") and user.endswith(">"):
            qtype = "id"
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))

        if not user:
            return await ctx.send("Please set your profile!")

        try:
            profile:osuClasses.User = await osuapiwrap.getuser(user, qtype, mode, server)
            tops:List[osuClasses.RecentScore] = await osuapiwrap.getusrtop(profile, limit)
        except ValueError:
            return await ctx.send("User has not been found or has no plays!")

        if parsedArgs['recent']:
            sorted_tops = sorted(tops, key=lambda x: x.date, reverse=True)
            positions = list(map(lambda top: tops.index(top) + 1, sorted_tops))
            tops = sorted_tops
            
        if parsedArgs['position'] is None:
            tops = tops[:5]
            positions = positions[:5]
        else:
            tops = tops[parsedArgs['position'] - 1 : parsedArgs['position']]
            positions = positions[parsedArgs['position'] - 1 : parsedArgs['position']]

        if self.bot.configs.REDIS is True:
            redisIO.setValue(ctx.message.channel.id, tops[0].beatmap_id)
            redisIO.setValue(f'{ctx.message.channel.id}.mode', mode.id)

        beatmaps = []

        index:int
        top:osuClasses.Score
        for index, top in enumerate(tops):
            beatmap:osuClasses.Beatmap = await osuapiwrap.getbmap(top.beatmap_id, mode=mode, server=server, mods=top.enabled_mods)
            bmapfile:pyt.beatmap = await osuapiwrap.getbmaposu(top.beatmap_id, server)
            beatmap.max_combo = bmapfile.max_combo()
            top.performance = await self.bot.loop.run_in_executor(None, ppc.calculatePlay, bmapfile, top)

            beatmaps.append(beatmap)
        
        result = OsuListEmbed(tops, beatmaps, profile, positions, 0)
        await ctx.send(embed=result)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["c", "s", "scores"])
    async def compare(self, ctx:commands.Context, *, args=None):
        """Shows your best scores on the last linked map."""

        user = None
        beatmap:osuClasses.Beatmap = None
        server = osuClasses.Server.BANCHO
        mode = osuClasses.Mode.STANDARD
        limit = 5

        if args is not None:
            if 'c' == ctx.invoked_with or 'compare' == ctx.invoked_with:
                parsedArgs = osuhelpers.parseArgsV2(args=args, customArgs=["user", "beatmap"])
            elif 's' == ctx.invoked_with or 'scores' == ctx.invoked_with:
                parsedArgs = osuhelpers.parseArgsV2(args=args, customArgs=["beatmap", "user"])
                if parsedArgs['beatmap']:
                    beatmap = await osuhelpers.getBeatmapFromText(parsedArgs['beatmap'])
            user = parsedArgs['user']
            qtype = parsedArgs['qtype']
            server = parsedArgs['server']

            

        if not user:
            qtype = "id"
            user = getOsu(ctx.message.author)

        if user and type(user) is str and user.startswith("<@") and user.endswith(">"):
            qtype = "id"
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))

        if not user:
            return await ctx.send("Please set your profile!")

        if 'c' == ctx.invoked_with or 'compare' == ctx.invoked_with and beatmap is None:
            if self.bot.configs.REDIS is True:
                mode = osuClasses.Mode.fromId(redisIO.getValue(f'{ctx.message.channel.id}.mode'))
                beatmap = await osuapiwrap.getbmap(redisIO.getValue(ctx.message.channel.id), mode=mode, server=server) 
            else:
                beatmap = await osuapiwrap.getbmap(1917158)

        if beatmap is None:
            return

        # try:
        profile:osu.User = await osuapiwrap.getuser(user, qtype, mode, server)
        tops:List[osuClasses.BeatmapScore] = await osuapiwrap.getusrscores(profile, beatmap.beatmap_id, limit)

        # except ValueError:
        #     return await ctx.send("User has not been found or has no plays!")

        index:int
        top:osuClasses.Score
        for index, top in enumerate(tops):
            bmapfile:pyt.beatmap = await osuapiwrap.getbmaposu(beatmap.beatmap_id)
            beatmap.max_combo = bmapfile.max_combo()
            top.performance = await self.bot.loop.run_in_executor(None, ppc.calculatePlay, bmapfile, top)
        
        title = f"Top osu! {mode.name_full} for {profile.username} on {beatmap.title}[{beatmap.version}]"
        result = OsuListEmbed(title, tops, [ beatmap ] * len(tops), profile, 1)

        await ctx.send(embed=result)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["pp"])
    async def perf(self, ctx, *, args=None):
        """Shows information about pp of a certain map"""

        args = osuhelpers.parseArgsV2(args=args, customArgs=["mods", "beatmap"])
        mode = args["mode"]
        
        if args["beatmap"]:
            beatmap:osuClasses.Beatmap = await osuhelpers.getBeatmapFromText(args["beatmap"])
        else:
            beatmap:osuClasses.Beatmap = await osuhelpers.getBeatmapFromHistory(ctx)

        if beatmap is None:
            await ctx.send("Failed to find any maps")
            return

        if self.bot.configs.REDIS is True:
            redisIO.setValue(ctx.message.channel.id, beatmap.beatmap_id)
            redisIO.setValue(f'{ctx.message.channel.id}.mode', mode.id)

        mods:osuClasses.Mods = osuClasses.Mods(args["mods"])

        bmapfile:pyt.beatmap = await osuapiwrap.getbmaposu(beatmap.beatmap_id)
        perfDict = await self.bot.loop.run_in_executor(None, ppc.calculateBeatmap, bmapfile, mods, mode.id)

        result = OsuPerformanceEmbed(beatmap, perfDict)
        await ctx.send(embed=result)

def setup(bot):
    bot.add_cog(osu(bot))
