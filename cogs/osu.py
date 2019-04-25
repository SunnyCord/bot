import discord, aiohttp, re, aiofiles, redis
from io import StringIO
from discord.ext import commands
from datetime import datetime
from commons import checks
from commons import ppwrapper as ppc
from commons import accuracycalculator as acc
import config as cfg
from commons.mongoIO import getOsu, setOsu
import commons.redisIO as redisIO

def get_config():
    if cfg.DEBUG==True:
        return cfg.debugConf
    else:
        return cfg.conf

def secondsToText(secs):
    days = secs//86400
    hours = (secs - days*86400)//3600
    minutes = (secs - days*86400 - hours*3600)//60
    seconds = secs - days*86400 - hours*3600 - minutes*60
    result = ("{0} day{1} ".format(days, "s" if days!=1 else "") if days else "") + \
    ("{0} hour{1} ".format(hours, "s" if hours!=1 else "") if hours else "") + \
    ("{0} minute{1} ".format(minutes, "s" if minutes!=1 else "") if minutes else "") + \
    ("{0} second{1} ".format(seconds, "s" if seconds!=1 else "") if seconds else "")
    return result
	
def getMods(number): # TODO - REMOVE THIS AFTER REWORK
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
    if number & 1<<15:  mod_list.append('4 KEY')
    if number & 1<<16:  mod_list.append('5 KEY')
    if number & 1<<17:  mod_list.append('6 KEY')
    if number & 1<<18:  mod_list.append('7 KEY')
    if number & 1<<19:  mod_list.append('8 KEY')
    if number & 1<<20:  mod_list.append('FI')
    if number & 1<<24:  mod_list.append('9 KEY')
    if number & 1<<25:  mod_list.append('10 KEY')
    if number & 1<<26:  mod_list.append('1 KEY')
    if number & 1<<27:  mod_list.append('3 KEY')
    if number & 1<<28:  mod_list.append('2 KEY')
    return ''.join(mod_list)

class osu(commands.Cog, name='osu!'):
    """osu! related commands."""
    def __init__(self,bot):
        self.bot = bot
        self.ranks = {
            "F": "<:F_:504305414846808084>",
            "D": "<:D_:504305448673869834>",
            "C": "<:C_:504305500364472350>",
            "B": "<:B_:504305539291938816>",
            "A": "<:A_:504305622297083904>",
            "S": "<:S_:504305656266752021>",
            "SH": "<:SH:504305700445487105>",
            "X": "<:X_:504305739209244672>",
            "XH": "<:XH:504305771417305112>"
        }
        self.nomstat = ["Unranked", "Ranked", "Approved", "Qualified", "Loved"]
    
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command()
    async def osuset(self, ctx, username):
        """Sets the osu! profile for the message author."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://osu.ppy.sh/api/get_user?k={cfg.OSU_API}&u={username}&m=0') as r:
                res = await r.json()
                if res != []:
                    setOsu(ctx.message.author, res[0]['username'])
                    await ctx.send(f"osu! profile succesfully set to {res[0]['username']}")
                else:
                    await ctx.send("User has not been found!")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["mania", "taiko", "ctb"])
    async def osu(self, ctx, user = None):
        """Shows osu! stats for a user. Modes can be specified."""
        if not user:
            user = getOsu(ctx.message.author)
        if user and user.startswith("<@") and user.endswith(">"):
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))
        if not user:
            return await ctx.send("Please set your profile!")
        if ctx.invoked_with == "osu":
            mode = 0
            mode_icon = "https://i.imgur.com/lT2nqls.png"
            mode_name = "Standard"
        if ctx.invoked_with == "taiko":
            mode = 1
            mode_icon = "https://i.imgur.com/G6bzM0X.png"
            mode_name = "Taiko"
        if ctx.invoked_with == "ctb":
            mode = 2
            mode_icon = "https://i.imgur.com/EsanYkH.png"
            mode_name = "Catch the Beat"
        if ctx.invoked_with =="mania":
            mode=3
            mode_icon = "https://i.imgur.com/0uZM1PZ.png"
            mode_name = "Mania"
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://osu.ppy.sh/api/get_user?k={cfg.OSU_API}&u={user}&m={mode}&type=string') as r:
                res = await r.json()
                if res != []:
                    if (res[0]["playcount"] is not None) and (res[0]["accuracy"] is not None):
                        id = res[0]["user_id"]
                        pp_rank = int(res[0]["pp_rank"])
                        pp_country_rank = int(res[0]["pp_country_rank"])
                        pp_raw = float(res[0]["pp_raw"])
                        accuracy = round(float(res[0]["accuracy"]), 2)
                        total_seconds_played = int(res[0]["total_seconds_played"])
                        playcount = res[0]["playcount"]
                        country = res[0]["country"]
                        if country is None:
                            country = "XX"
                        level = int(float(res[0]["level"]))
                        level_progress = round((float(res[0]["level"])%1*100), 2)
                        username = res[0]["username"]
                        desc=f"**>Rank:** #{pp_rank}\n**>PP:** {pp_raw}\n**>Accuracy:** {accuracy}%\n**>Level:** {level} ({level_progress}%)\n**>Playtime:** {secondsToText(total_seconds_played)}\n**>Playcount:** {playcount}\n**>PP/hour:** {int(pp_raw/total_seconds_played*3600)}\n**>Ranks/day:** {int(pp_rank/total_seconds_played*86400)}"
                        embed=discord.Embed(title=discord.Embed.Empty, color=get_config().COLOR, description=desc, timestamp=datetime.utcnow())
                        embed.set_author(name=f"osu! {mode_name} stats for {username}", url=f"https://osu.ppy.sh/users/{id}", icon_url=mode_icon)
                        embed.set_thumbnail(url=f"https://a.ppy.sh/{id}")
                        embed.set_footer(text=f"#{pp_country_rank}", icon_url=f"https://osu.ppy.sh/images/flags/{country}.png")
                        await ctx.send(embed=embed)
                else:
                    await ctx.send("User has not been found or has not played enough!")  

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["rs","r"])
    async def recent(self, ctx, *, input = None):
        """Shows recent osu! plays for a user. Modes can be specified."""
        if input is None:
            user = getOsu(ctx.message.author)
            mode = 0
        else:
            input = input.split(" ")
            if '-m' not in input:
                user = ''.join(input)
                mode = 0
            else:
                try:
                    mode = int(input[input.index('-m') + 1])
                    input.pop(input.index('-m') + 1)
                except IndexError:
                    mode = 0
                input.pop(input.index('-m'))
                user = ''.join(input)
                if not user:
                    user = getOsu(ctx.message.author)
        if user is not None and user.startswith("<@") and user.endswith(">"):
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))
        if not user:
            return await ctx.send("Please set your profile!")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f"https://osu.ppy.sh/api/get_user_recent?k={cfg.OSU_API}&u={user}&m={mode}&type=string") as r:
                recentp = await r.json()
        if recentp != []:
            if_fc = ""
            date = datetime.strptime(recentp[0]["date"], "%Y-%m-%d %H:%M:%S")  
            redisIO.setValue(ctx.message.channel.id, recentp[0]["beatmap_id"])
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f'https://osu.ppy.sh/osu/{recentp[0]["beatmap_id"]}') as r:
                        bmap = StringIO(await r.text())
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://osu.ppy.sh/api/get_beatmaps?k={cfg.OSU_API}&b={recentp[0]['beatmap_id']}&limit=1") as r:
                    beatmap = await r.json()
            beatmapset_id = int(beatmap[0]["beatmapset_id"])
            status = int(beatmap[0]["approved"])
            beatmapDict, playDict = ppc.calculatePlay(bmap, mode, int(recentp[0]["countmiss"]), int(recentp[0]["count50"]), int(recentp[0]["count100"]), int(recentp[0]["count300"]), int(recentp[0]["countgeki"]), int(recentp[0]["countkatu"]), int(recentp[0]["maxcombo"]), int(recentp[0]["enabled_mods"]), int(recentp[0]["perfect"]))
            status = self.nomstat[status]
            completion = f'\n> **Completion:** {playDict["completion"]}%' if recentp[0]["rank"] == 'F' and mode == 0 else ''
            if_fc = '' if int(recentp[0]["perfect"]) == 1 else f" ({playDict['pp_fc']} for {playDict['accuracy_fc']}% FC)"
            rankemoji = self.ranks[recentp[0]["rank"]]
            desc = f"> {rankemoji} > **{playDict['pp']}PP{if_fc}** > {playDict['accuracy']}%\n> {recentp[0]['score']} > x{recentp[0]['maxcombo']}/{beatmapDict['maxcombo']} > [{recentp[0]['count300']}/{recentp[0]['count100']}/{recentp[0]['count50']}/{recentp[0]['countmiss']}]{completion}"
            embed = discord.Embed(title=discord.Embed.Empty, color=get_config().COLOR, description = desc, timestamp=date)
            embed.set_author(name=f"{beatmapDict['title']} [{beatmapDict['version']}] ({beatmapDict['creator']}) +{playDict['modString']} [{playDict['rating']}★]", url=f"https://osu.ppy.sh/b/{recentp[0]['beatmap_id']}", icon_url=f"https://a.ppy.sh/{recentp[0]['user_id']}")
            embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmapset_id}.jpg")
            embed.set_footer(text=f"{status} | osu! {playDict['mode_name']} Play", icon_url=playDict['mode_icon'])
            await ctx.send(f"**Most Recent osu! {playDict['mode_name']} Play for {user}:**",embed=embed)   
        else:
            await ctx.send("User has not been found or has no recent plays!")  
    
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=["ot", "tt", "ct", "mt", "taikotop", "ctbtop", "maniatop"])
    async def osutop(self, ctx, *, user=None):
        limit = 5
        spec = False
        recentFirst = False
        if user:
            user = user.split(" ")
            if '-p' in user:
                try:
                    limit = int(user[user.index('-p') + 1])
                    user.pop(user.index('-p') + 1)
                    spec = True
                except IndexError:
                    limit = 5
                user.pop(user.index('-p'))
            if '-r' in user:
                recentFirst = True
                user.remove('-r')
            user = ''.join(user)
        if not user:
            user = getOsu(ctx.message.author)
        if user and user.startswith("<@") and user.endswith(">"):
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))
        if not user:
            return await ctx.send("Please set your profile!")
        if ctx.invoked_with == "osutop" or ctx.invoked_with == "ot":
            mode = 0
        if ctx.invoked_with == "taikotop" or ctx.invoked_with == "tt":
            mode = 1
        if ctx.invoked_with == "ctbtop" or ctx.invoked_with == "ct":
            mode = 2
        if ctx.invoked_with =="maniatop" or ctx.invoked_with == "mt":
            mode=3
        if mode == 0:
            mode_icon = "https://i.imgur.com/lT2nqls.png"
            mode_name = "Standard"
        if mode == 1:
            mode_icon = "https://i.imgur.com/G6bzM0X.png"
            mode_name = "Taiko"
        if mode == 2:
            mode_icon = "https://i.imgur.com/EsanYkH.png"
            mode_name = "Catch the Beat"
        if mode == 3:
            mode_icon = "https://i.imgur.com/0uZM1PZ.png"
            mode_name = "Mania"
        if not recentFirst:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://osu.ppy.sh/api/get_user_best?k={cfg.OSU_API}&m={mode}&limit={limit}&u={user}&type=string") as r:
                    tops = await r.json()
        else:
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f"https://osu.ppy.sh/api/get_user_best?k={cfg.OSU_API}&m={mode}&limit=100&u={user}&type=string") as r:
                    tops = await r.json()
        if tops == []:
            return await ctx.send("User has not been found or has no plays!")  
        uid = tops[0]["user_id"]
        if spec:
            tops = tops[limit-1:]
        elif recentFirst:
            tops.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d %H:%M:%S"), reverse=True)
            tops = tops[:5]
        redisIO.setValue(ctx.message.channel.id, tops[0]["beatmap_id"])
        desc = ""
        for index, play in enumerate(tops):
            rank = play["rank"]
            rankemoji = self.ranks[rank]
            pp = float(play["pp"])
            perfect = int(play["perfect"])
            count50 = int(play["count50"])
            count100 = int(play["count100"])
            count300 = int(play["count300"])
            count0 = int(play["countmiss"])
            countgeki = int(play["countgeki"])
            countkatu = int(play["countkatu"])
            beatmap_id = play["beatmap_id"]
            modnum = int(play["enabled_mods"])
            mods = getMods(modnum)
            bestcombo = int(play["maxcombo"])
            date = datetime.strptime(play["date"], "%Y-%m-%d %H:%M:%S") 
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f'https://osu.ppy.sh/osu/{beatmap_id}') as r:
                    if r.status == 200:
                        bmap = StringIO(await r.text())
            async with aiohttp.ClientSession() as cs2:
                async with cs2.get(f"https://osu.ppy.sh/api/get_beatmaps?k={cfg.OSU_API}&b={beatmap_id}&limit=1") as r2:
                    beatmap = await r2.json()
                    beatmap = beatmap[0]
            maxcombo = int(beatmap["max_combo"]) if beatmap["max_combo"] else None
            diff = beatmap["version"]
            beatmap_title = f"{beatmap['artist']} - {beatmap['title']} ({beatmap['creator']}) [{diff}]"
            if_fc=""
            if mode == 0:
                accuracy = acc.stdCalc(count0, count50, count100, count300)
                sr, __, pp_fc = await self.bot.loop.run_in_executor(None, ppc.stdCalc, bmap, count0, count50, count100, count300, bestcombo, modnum, perfect, maxcombo)
                if perfect == 0:
                    accuracy_fc = acc.stdCalc(0, count50, count100, count300+count0)
                    if_fc = f" ({pp_fc}PP for {accuracy_fc}% FC)"
                mode_icon = "https://i.imgur.com/lT2nqls.png"
                mode_name = "Standard"
            if mode == 1:
                accuracy = acc.taikoCalc(count0, count100, count300)
                sr, __ = await self.bot.loop.run_in_executor(None, ppc.taikoCalc, bmap, modnum)
                mode_icon = "https://i.imgur.com/G6bzM0X.png"
                mode_name = "Taiko"
            if mode == 2:
                accuracy = acc.ctbCalc(count0, countkatu, count50, count100, count300)
                sr, __, maxcombo = await self.bot.loop.run_in_executor(None, ppc.ctbCalc, bmap, accuracy/100, count0, modnum, bestcombo)
                mode_icon = "https://i.imgur.com/EsanYkH.png"
                mode_name = "Catch the Beat"
            if mode == 3:
                accuracy = acc.maniaCalc(count0, count50, count100, countkatu, count300, countgeki)
                sr, __ = await self.bot.loop.run_in_executor(None, ppc.maniaCalc)
                mode_icon = "https://i.imgur.com/0uZM1PZ.png"
                mode_name = "Mania"
            if spec:
                index = limit-1
            desc = desc + f"\n{index+1}. [**{beatmap_title}**](https://osu.ppy.sh/b/{beatmap_id}) + **{mods}** [{sr}★]" + '\n' + f"> {rankemoji} > **{pp}pp**{if_fc} > {accuracy}%\n> {bestcombo}x/{maxcombo}x > [{count300}/{count100}/{count50}/{count0}]\n> {date}\n"
        embed = discord.Embed(title=discord.Embed.Empty, color=get_config().COLOR, description=desc)
        embed.set_author(name=f"Top {limit} osu! {mode_name} for {user}", url=f"https://osu.ppy.sh/users/{uid}", icon_url=mode_icon)
        embed.set_thumbnail(url=f"https://a.ppy.sh/{uid}")
        await ctx.send(embed=embed)
            
    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(aliases=['c'])
    async def compare(self, ctx, user = None):
        beatmap_id = redisIO.getValue(ctx.message.channel.id)
        mode = 0
        if beatmap_id is None:
            return await ctx.send("No beatmap found.")
        if user is None:
            user = getOsu(ctx.message.author)
        if user is not None and user.startswith("<@") and user.endswith(">"):
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))
        if not user:
            return await ctx.send("Please set your profile!")
        user.replace(" ", "_")
        desc = ""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://osu.ppy.sh/api/get_scores?k={cfg.OSU_API}&b={beatmap_id}&u={user}&type=string&limit=5') as r:
                tops = await r.json()
        async with aiohttp.ClientSession() as cs2:
                async with cs2.get(f"https://osu.ppy.sh/api/get_beatmaps?k={cfg.OSU_API}&b={beatmap_id}&limit=1") as r2:
                    beatmap = await r2.json()
                    beatmap = beatmap[0]
        if tops == []:
            return await ctx.send('User has no play on the beatmap!')
        for index, play in enumerate(tops):
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f'https://osu.ppy.sh/osu/{beatmap_id}') as r:
                    if r.status == 200:
                        bmap = StringIO(await r.text())
            uid = play["user_id"]
            rank = play["rank"]
            rankemoji = self.ranks[rank]
            date = datetime.strptime(play["date"], "%Y-%m-%d %H:%M:%S") 
            if_fc=""
            beatmapset_id = beatmap['beatmapset_id']
            status = int(beatmap["approved"])
            status = self.nomstat[status]
            #(bmap, mode: int = 0, count0: int = 0, count50: int = 0, count100: int = 0, count300: int= 0, countgeki: int = 0, countkatu: int = 0, combo: int = 0, mods: int = 0, perfect: int = 0):
            beatmapDict, playDict = ppc.calculatePlay(bmap, mode, int(play["countmiss"]), int(play["count50"]), int(play["count100"]), int(play["count300"]), int(play["countgeki"]), int(play["countkatu"]), int(play["maxcombo"]), int(play["enabled_mods"]), int(play["perfect"]), 0)
            beatmap_title = f"{beatmapDict['artist']} - {beatmapDict['title']} ({beatmapDict['creator']}) [{beatmapDict['version']}]"
            if_fc = '' if int(play[0]["perfect"]) == 1 else f" ({playDict['pp_fc']} for {playDict['accuracy_fc']}% FC)"
            desc = desc + f"\n{index+1}. ``{playDict['modString']}`` [{playDict['rating']}★]" + '\n' + f"> {rankemoji} > **{round(float(play['pp']), 2)}pp**{if_fc} > {playDict['accuracy']}%\n> {play['score']} > x{play['maxcombo']}/{beatmapDict['maxcombo']} > [{play['count300']}/{play['count100']}/{play['count50']}/{play['countmiss']}]\n> {date}\n"
        embed = discord.Embed(title=discord.Embed.Empty, color=get_config().COLOR, description=desc)
        embed.set_author(name=f"Top osu! {playDict['mode_name']} for {user} on {beatmap_title}", url=f"https://osu.ppy.sh/b/{beatmap_id}", icon_url=f"https://a.ppy.sh/{uid}")
        embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmapset_id}.jpg")
        embed.set_footer(icon_url=playDict['mode_icon'], text=status)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(osu(bot))
