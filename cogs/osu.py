import discord, aiohttp, re
from io import StringIO
from discord.ext import commands
from datetime import datetime
from commons.osu import osuhelpers
from commons.osu import ppwrapper as ppc
from commons.osu import osuapiwrap as osuAPI
from commons.mongoIO import getOsu, setOsu
from commons.embeds import *
import commons.redisIO as redisIO

class osu(commands.Cog, name='osu!'):
    """osu! related commands.\n*Valid Arguments:* ```fix\n-ripple, -akatsuki, akatsukirx, -enjuu```"""

    def __init__(self,bot):

        self.bot = bot
        self.osuAPI = osuAPI.APIService(bot.configs.OSUCFG.token)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def osuset(self, ctx, *, args):
        """Sets the osu! profile for the message author. ``eg. osuset Nice Aesthetics``"""

        try:
            parsedArgs = osuhelpers.parseArgs(args=args)
            username = parsedArgs['user']
            profile = await self.osuAPI.getuser(usr = username, mode = 0, qtype = 'string', server=parsedArgs['server'])
            setOsu(ctx.message.author, profile['user_id'])
            await ctx.send(f"osu! profile succesfully set to {profile['username']}")

        except ValueError:
            await ctx.send("User has not been found!")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["mania", "taiko", "ctb"])
    async def osu(self, ctx, *, args = None):
        """Shows osu! stats for a user.\nOther variants: ``mania, taiko, ctb``"""
        
        user, server = None, 'bancho'

        if args is not None:
            parsedArgs = osuhelpers.parseArgs(args=args)
            user, qtype, server = parsedArgs['user'], parsedArgs['qtype'], parsedArgs['server']

        if not user:
            qtype = "id"
            user = getOsu(ctx.message.author)

        if user and user.startswith("<@") and user.endswith(">"):
            qtype = "id"
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))

        if not user:
            return await ctx.send("Please set your profile!")

        mode, mode_icon, mode_name = osuhelpers.getModeInfo( ctx.invoked_with )

        try:
            profile = await self.osuAPI.getuser(usr = user, mode = mode, qtype = qtype, server=server)

        except ValueError:
            return await ctx.send("User has not been found or has not played enough!")

        if (profile["playcount"] is not None) and (profile["accuracy"] is not None):
            result = OsuProfileEmbed(color=self.bot.configs.COLOR, userstats=profile, modeinfo={'name': mode_name, 'icon': mode_icon}, timestamp = datetime.utcnow(), server = server)
            return await ctx.send(embed=result)

        else:
            await ctx.send("User has not been found or has not played enough!")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["rs","r"])
    async def recent(self, ctx, *, args = None):
        """Shows recent osu! plays for a user. Modes can be specified ``eg. recent -m 2``.\n*Valid Arguments:* ```fix\n-l, -m```"""
        
        user, server, mode, limit = None, 'bancho', 0, 1

        if args is not None:
            parsedArgs = osuhelpers.parseArgs(args=args, validArgs=['-l', '-m'])
            user, qtype, server, mode = parsedArgs['user'], parsedArgs['qtype'], parsedArgs['server'], parsedArgs['mode']
            limit = 5 if parsedArgs['recentList'] is True else 1

        if not user:
            qtype = "id"
            user = getOsu(ctx.message.author)

        if user and user.startswith("<@") and user.endswith(">"):
            qtype = "id"
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))

        if not user:
            return await ctx.send("Please set your profile!")

        try:
            profile = await self.osuAPI.getuser(usr = user, mode = mode, qtype = qtype, server = server)
            recentp = await self.osuAPI.getrecent(usr = user, mode = mode, qtype = qtype, limit = limit, server = server)

        except ValueError:
            return await ctx.send("User has not been found or has no recent plays!")

        date = datetime.strptime(recentp[0]["date"], "%Y-%m-%d %H:%M:%S")

        if self.bot.configs.REDIS is True:
            redisIO.setValue(ctx.message.channel.id, recentp[0]["beatmap_id"])

        bmapfile = await self.osuAPI.getbmaposu(server=server, mode=mode, b=recentp[0]["beatmap_id"])
        beatmap = await self.osuAPI.getbmap(server=server, mode=mode, b=recentp[0]["beatmap_id"], mods=recentp[0]["enabled_mods"])

        _, playDict = await self.bot.loop.run_in_executor(None, ppc.calculatePlay, bmapfile, mode, recentp[0])

        beatmap[0]['objcount'] = beatmap[0]['count_normal'] + beatmap[0]['count_slider'] + beatmap[0]['count_spinner']
        beatmap[0]['mode'] = mode

        recentp[0]['completion'] = ''
        if recentp[0]["rank"] == 'F' and mode == 0:
            recentp[0]['completion'] = f'\n> **Completion:** {playDict["completion"]}%'
        
        recentp[0]['if_fc'] = '' 
        if recentp[0]["perfect"] == 0 and mode == 0:
            recentp[0]['if_fc'] = f" ({playDict['pp_fc']} for {playDict['accuracy_fc']}% FC)"

        recentp[0]['pp'] = playDict['pp']
        recentp[0]['accuracy'] = playDict['accuracy']
        recentp[0]['modString'] = playDict['modString']

        result = OsuRecentEmbed(color = self.bot.configs.COLOR, timestamp = date, userstats = profile, playinfo = recentp[0],\
        modeinfo = {'name': playDict['mode_name'], 'icon': playDict['mode_icon']}, beatmap = beatmap[0])

        await ctx.send(f"**Most Recent osu! {playDict['mode_name']} Play for {profile['username']} on {server}:**", embed=result)
            
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["ot", "tt", "ct", "mt", "taikotop", "ctbtop", "maniatop"])
    async def osutop(self, ctx, *, args=None):
        """Shows osu! top plays for a user. Modes can be specified ``eg. maniatop``.\n*Valid Arguments:* ```fix\n-r, -p```"""

        user, server, mode, limit, beatmaps = None, 'bancho', 0, 5, []

        parsedArgs = {
            'recentList': False,
            'position': None
        }

        mode, mode_icon, mode_name = osuhelpers.getModeInfo( ctx.invoked_with )

        if args is not None:
            parsedArgs = osuhelpers.parseArgs(args=args, validArgs=['-r', '-p'])
            user, qtype, server = parsedArgs['user'], parsedArgs['qtype'], parsedArgs['server']
            if parsedArgs['recentList'] is True:
                limit = 100

            if parsedArgs['position'] is not None and parsedArgs['recentList'] is False:
                limit = parsedArgs['position']

        if not user:
            qtype = "id"
            user = getOsu(ctx.message.author)

        if user and user.startswith("<@") and user.endswith(">"):
            qtype = "id"
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))

        if not user:
            return await ctx.send("Please set your profile!")

        try:
            profile = await self.osuAPI.getuser(usr = user, mode = mode, qtype = qtype, server = server)
            tops = await self.osuAPI.getusrtop(usr = user, mode = mode, qtype = qtype, limit = limit, server = server)

        except ValueError:
            return await ctx.send("User has not been found or has no plays!")

        if parsedArgs['recentList'] is True:
            tops.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M:%S"), reverse=True)
            tops = tops[:5]

        if parsedArgs['position'] is not None:
            if parsedArgs['recentList'] is True:
                limit = parsedArgs['position']
                tops = [tops[limit-1]]
            else:
                tops = tops[limit-1:]

        if self.bot.configs.REDIS is True:
            redisIO.setValue(ctx.message.channel.id, tops[0]["beatmap_id"])

        for index, _ in enumerate(tops):
            beatmap = await self.osuAPI.getbmap(server=server, mode=mode, b=tops[index]["beatmap_id"], mods=tops[index]["enabled_mods"])
            bmapfile = await self.osuAPI.getbmaposu(server='bancho', mode=mode, b=tops[index]["beatmap_id"])
            _, playDict = await self.bot.loop.run_in_executor(None, ppc.calculatePlay, bmapfile, mode, tops[index])

            beatmaps.append(beatmap[0])
            tops[index]['pp_fc'] = playDict['pp_fc']
            tops[index]['accuracy'] = playDict['accuracy']
            tops[index]['modString'] = playDict['modString']

            tops[index]['if_fc'] = '' 
            if tops[index]["perfect"] == 0 and mode == 0:
                tops[index]['if_fc'] = f" ({playDict['pp_fc']} for {playDict['accuracy_fc']}% FC)"


        result = OsuListEmbed(list = tops, profile = profile, beatmaps = beatmaps, title = f"Top {limit} osu! {mode_name} for {profile['username']}", url = profile['profile_url'],\
        authorico = mode_icon, thumbnail = profile['avatar_url'], color = self.bot.configs.COLOR, limit = limit)

        await ctx.send(embed=result)

def setup(bot):
    bot.add_cog(osu(bot))
