import discord
from discord.ext import commands
import aiohttp
from datetime import datetime
from commons import checks
import config as cfg
from commons.calc import calc_pp
from commons.mongoIO import getOsu, setOsu
import re
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

def getMods(number):
    mod_list= []
    if number == 0:	mod_list.append('NM')
    if number & 1<<0:   mod_list.append('NF')
    if number & 1<<1:   mod_list.append('EZ')
    if number & 1<<3:   mod_list.append('HD')
    if number & 1<<4:   mod_list.append('HR')
    if number & 1<<5:   mod_list.append('SD')
    if number & 1<<9:   mod_list.append('NC')
    elif number & 1<<6: mod_list.append('DT')
    if number & 1<<7:   mod_list.append('RX')
    if number & 1<<8:   mod_list.append('HT')
    if number & 1<<10:  mod_list.append('FL')
    if number & 1<<12:  mod_list.append('SO')
    if number & 1<<14:  mod_list.append('PF')
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
	
class osu:

    def __init__(self,bot):
        self.bot = bot
    
    @commands.cooldown(1, 5, commands.BucketType.user)
    @checks.is_blacklisted()
    @commands.command()
    async def osuset(self, ctx, username):
        """Sets the osu! profile for the message author."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get(f'https://osu.ppy.sh/api/get_user?k={cfg.OSU_API}&u={username}&m=0') as r:
                res = await r.json()
                if res != []:
                    setOsu(ctx.message.author, username)
                    await ctx.send(f"osu! profile succesfully set to {res[0]['username']}")
                else:
                    await ctx.send("User has not been found!")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @checks.is_blacklisted()
    @commands.command(aliases=["mania", "taiko", "ctb"])
    async def osu(self, ctx, user = None):
        """Shows osu! stats for a user. Modes can be specified."""
        if not user:
            user = getOsu(ctx.message.author)
        if user.startswith("<@") and user.endswith(">"):
            user = getOsu(ctx.guild.get_member(int(re.sub('[^0-9]','', user))))
        if not user:
            await ctx.send("Please set your profile!")
        else:
            if ctx.invoked_with == "osu":
                mode = 0
            if ctx.invoked_with == "taiko":
                mode = 1
            if ctx.invoked_with == "ctb":
                mode = 2
            if ctx.invoked_with =="mania":
                mode=3
            async with aiohttp.ClientSession() as cs:
                async with cs.get(f'https://osu.ppy.sh/api/get_user?k={cfg.OSU_API}&u={user}&m={mode}') as r:
                    res = await r.json()
                    if res != []:
                        if (res[0]["playcount"] is not None) and (res[0]["accuracy"] is not None):
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
                            desc=f"**🠺Rank:** #{pp_rank} ({country}#{pp_country_rank})\n**🠺PP:** {pp_raw}\n**🠺Accuracy:** {accuracy}%\n**🠺Level:** {level} ({level_progress}%)\n**🠺Playtime:** {secondsToText(total_seconds_played)}\n**🠺Playcount:** {playcount}\n**🠺PP/hour:** {int(pp_raw/total_seconds_played*3600)}\n**🠺Ranks/day:** {int(pp_rank/total_seconds_played*86400)}"
                            embed=discord.Embed(title=discord.Embed.Empty, color=get_config().COLOR, description=desc, timestamp=datetime.utcnow())
                            embed.set_author(name=f"osu! {mode_name} stats for {username}", url=f"https://osu.ppy.sh/users/{id}", icon_url=mode_icon)
                            embed.set_thumbnail(url=f"https://a.ppy.sh/{id}")
                            embed.set_footer(text=f"#{pp_country_rank}", icon_url=f"https://osu.ppy.sh/images/flags/{country}.png")
                            await ctx.send(embed=embed)
                        else:
                            await ctx.send("User has not been found or has not played enough!")  
                    else:
                        await ctx.send("User has not been found or has not played enough!")  

    @commands.cooldown(1, 1, commands.BucketType.user)
    @checks.is_blacklisted()
    @commands.command()
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
            await ctx.send("Please set your profile!")
        else:
            async with aiohttp.ClientSession() as cs1:
                async with cs1.get(f'https://osu.ppy.sh/api/get_user_recent?k={cfg.OSU_API}&u={user}&m={mode}') as r1:
                    recentp = await r1.json()
            if recentp != []:
                    modnum = int(recentp[0]["enabled_mods"])
                    score = int(recentp[0]["score"])
                    beatmap_id = int(recentp[0]["beatmap_id"])
                    bestcombo = int(recentp[0]["maxcombo"])
                    count0 = int(recentp[0]["countmiss"])
                    count50 = int(recentp[0]["count50"])
                    count100 = int(recentp[0]["count100"])
                    count300 = int(recentp[0]["count300"])
                    perfect = int(recentp[0]["perfect"])
                    uid = int(recentp[0]["user_id"])
                    rank = recentp[0]["rank"]
                    date = datetime.strptime(recentp[0]["date"], "%Y-%m-%d %H:%M:%S")
                    async with aiohttp.ClientSession() as cs2:
                        async with cs2.get(f'https://osu.ppy.sh/api/get_beatmaps?k={cfg.OSU_API}&b={beatmap_id}&limit=1') as r2:
                            beatmap = await r2.json()
                    beatmapset_id = int(beatmap[0]["beatmapset_id"])
                    title = beatmap[0]["title"]
                    creator = beatmap[0]["creator"]
                    sr = round(float(beatmap[0]["difficultyrating"]), 2)
                    diff = beatmap[0]["version"]
                    status = int(beatmap[0]["approved"])
                    maxcombo = beatmap[0]["max_combo"]
                    mods = getMods(modnum)
                    accuracy = round(float((50*count50+100*count100+300*count300)/(300*(count0+count50+count100+count300))*100), 2)
                    if rank == "F":
                        rankemoji = "<:F_:504305414846808084>"
                    if rank == "D":
                        rankemoji = "<:D_:504305448673869834>"
                    if rank == "C":
                        rankemoji = "<:C_:504305500364472350>"
                    if rank == "B":
                        rankemoji = "<:B_:504305539291938816>"
                    if rank == "A":
                        rankemoji = "<:A_:504305622297083904>"
                    if rank == "S":
                        rankemoji = "<:S_:504305656266752021>"
                    if rank == "SH":
                        rankemoji = "<:SH:504305700445487105>"
                    if rank == "X":
                        rankemoji = "<:X_:504305739209244672>"
                    if rank == "XH":
                        rankemoji = "<:XH:504305771417305112>"
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
                    if_fc = ""
                    if mode == 0:
                        ppcalc = calc_pp(f"https://osu.ppy.sh/b/{beatmap_id}", accuracy, mods, bestcombo, count0)
                        pp = ppcalc.splitlines()[1]
                        sr = ppcalc.splitlines()[0]
                        if perfect == 0:
                            accuracy_fc = round(float((50*count50+100*count100+300*count300)/(300*(count50+count100+count300))*100), 2)
                            ppcalc = calc_pp(f"https://osu.ppy.sh/b/{beatmap_id}", accuracy, mods, int(maxcombo), 0)
                            if_fc = f"({ppcalc.splitlines()[1]}PP for {accuracy_fc}% FC)"
                    else:
                        pp = "Only STD PP supported 😦"
                    if status == 4:
                        status = "Loved"
                    if status == 3:
                        status = "Qualified"
                    if status == 2:
                        status = "Approved"
                    if status == 1:
                        status = "Ranked"
                    desc = f"🠺 {rankemoji} 🠺 **{pp}PP {if_fc}** 🠺 {accuracy}%\n🠺 {score} 🠺 x{bestcombo}/{maxcombo} 🠺 [{count300}/{count100}/{count50}/{count0}]"
                    embed = discord.Embed(title=discord.Embed.Empty, color=get_config().COLOR, description = desc, timestamp=date)
                    embed.set_author(name=f"{title} [{diff}] ({creator}) +{mods} [{sr}★]", url=f"https://osu.ppy.sh/b/{beatmap_id}", icon_url=f"https://a.ppy.sh/{uid}")
                    embed.set_thumbnail(url=f"https://b.ppy.sh/thumb/{beatmapset_id}.jpg")
                    embed.set_footer(text=f"{status} | osu! {mode_name} Play", icon_url=mode_icon)
                    await ctx.send(f"**Most Recent osu! {mode_name} Play for {user}:**",embed=embed)
                            
            else:
                await ctx.send("User has not been found or has no recent plays!")  

def setup(bot):
    bot.add_cog(osu(bot))