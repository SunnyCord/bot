from __future__ import annotations

from typing import Optional

import discord
import entities.osu as osuClasses
from commons.regex import id_rx
from discord import app_commands
from discord.ext import commands
from ui.embeds.osu import *


class OsuUserConverter(commands.Converter):
    async def convert(self, ctx, *argument) -> osuClasses.User:
        """
        Converts to a ``entities.osu.User`` (case-insensitive)

        The lookup strategy is as follows (in order):

        1. Lookup by commands.MemberConverter()
        2. Lookup by string
        """
        raw_user, server, mode = argument
        user, qtype = None, None

        if raw_user is None:
            user = await ctx.bot.mongoIO.getOsu(ctx.author)
            qtype = "id"
        else:
            try:
                member = await commands.MemberConverter().convert(ctx, raw_user)
                user = await ctx.bot.mongoIO.getOsu(member)
                qtype = "id"
            except commands.MemberNotFound:

                def check(member):
                    return (
                        member.name.lower() == raw_user.lower()
                        or member.display_name.lower() == raw_user.lower()
                        or str(member).lower() == raw_user.lower()
                        or str(member.id) == raw_user
                    )

                if found := discord.utils.find(check, ctx.guild.members):
                    user = await ctx.bot.mongoIO.getOsu(found)
                    qtype = "id"

                user, qtype = raw_user, "string"

        return await ctx.bot.osuAPI.getuser(
            usr=user,
            mode=mode,
            qtype=qtype,
            server=server,
        )


class OsuProfileCog(commands.GroupCog, name="profile"):
    """
    osu! Profile Commands
    """

    args_description = {
        "user": "Discord/osu! username or mention",
        "server": "The osu! server to search on",
    }

    def __init__(self, bot) -> None:
        self.bot = bot

    async def osu_profile_command(
        self,
        ctx: commands.Context,
        user: str,
        server: osuClasses.Server,
        mode: osuClasses.Mode,
    ):
        user = await OsuUserConverter().convert(ctx, user, server, mode)
        return await ctx.send(embed=OsuProfileEmbed(user, mode, self.bot.config.color))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="osu",
        description="Shows osu!std stats for a user",
    )
    @app_commands.describe(**args_description)
    async def osu_std_profile_command(
        self,
        ctx: commands.Context,
        user: Optional[str],  # TODO specify preferences
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(
            ctx,
            user,
            server,
            osuClasses.Mode.STANDARD,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="mania",
        description="Shows osu!mania stats for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_mania_profile_command(
        self,
        ctx: commands.Context,
        user: Optional[str],
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(
            ctx,
            user,
            server,
            osuClasses.Mode.MANIA,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="taiko",
        description="Shows osu!taiko stats for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_taiko_profile_command(
        self,
        ctx: commands.Context,
        user: Optional[str],
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(
            ctx,
            user,
            server,
            osuClasses.Mode.TAIKO,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="ctb",
        description="Shows osu!ctb stats for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_ctb_profile_command(
        self,
        ctx: commands.Context,
        user: Optional[str],
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(
            ctx,
            user,
            server,
            osuClasses.Mode.CTB,
        )


class OsuTopsCog(commands.GroupCog, name="top"):
    """
    osu! Tops Commands
    """

    args_description = {
        "user": "Discord/osu! username or mention",
        "server": "The osu! server to search on",
    }

    def __init__(self, bot) -> None:
        self.bot = bot

    async def osu_top_command(
        self,
        ctx: commands.Context,
        user: str,
        server: osuClasses.Server,
        mode: osuClasses.Mode,
    ):
        user = await OsuUserConverter().convert(ctx, user, server, mode)
        tops: List[osuClasses.RecentScore] = await self.bot.osuAPI.getusrtop(user, 5)
        return await ctx.send(embed=OsuProfileEmbed(user, mode, self.bot.config.color))


class OsuCog(commands.Cog, name="osu!"):
    """
    osu! related commands.\n*Valid Arguments:* ```fix\n-ripple, -akatsuki```
    """

    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(
        name="osuset",
        description="Sets the osu! profile for the message author",
    )
    @app_commands.describe(
        username="Your osu! username",
        server="The osu! server to search on",
    )
    async def osu_set_command(
        self,
        ctx: commands.Context,
        username: str,
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ) -> None:
        profile: osuClasses.User = await self.bot.osuAPI.getuser(
            username,
            "string",
            server=server,
        )
        await self.bot.mongoIO.setOsu(
            ctx.author,
            profile.user_id,
            server.id,
        )
        await ctx.send(
            f"osu! {server.name_full} profile succesfully set to {profile.username}",
        )


#
# @commands.cooldown(1, 1, commands.BucketType.user)
# @commands.command(aliases=["rs", "r"])
# async def recent(self, ctx, *, args=None):
#    """Shows recent osu! plays for a user. Modes can be specified ``eg. recent -m 2``.\n*Valid Arguments:* ```fix\n-l, -m```"""
#
#    user = None
#    server = osuClasses.Server.BANCHO
#    mode = osuClasses.Mode.STANDARD
#    limit = 1
#
#    if args is not None:
#        parsedArgs = self.bot.osuHelpers.parseArgs(
#            args=args,
#            validArgs=["-l", "-m"],
#        )
#        user = parsedArgs["user"]
#        qtype = parsedArgs["qtype"]
#        server = osuClasses.Server.from_name(parsedArgs["server"])
#        mode = osuClasses.Mode.fromId(parsedArgs["mode"])
#        limit = 5 if parsedArgs["recentList"] is True else 1
#
#    if not user:
#        qtype = "id"
#        user, serverID = await self.bot.mongoIO.getOsu(ctx.author)
#        server = osuClasses.Server.from_id(serverID)
#
#    if (
#        user
#        and isinstance(user, str)
#        and user.startswith("<@")
#        and user.endswith(">")
#    ):
#        qtype = "id"
#        mentioned_id = int(id_rx.sub(r"", user))
#        mentioned = await self.bot.ensure_member(mentioned_id, ctx.guild)
#        user, serverID = await self.bot.mongoIO.getOsu(mentioned)
#        server = osuClasses.Server.from_id(serverID)
#
#    profile: osuClasses.User = await self.bot.osuAPI.getuser(
#        user,
#        qtype,
#        mode,
#        server,
#    )
#    recent_score: osuClasses.RecentScore = (
#        await self.bot.osuAPI.getrecent(profile, limit)
#    )[0]
#
#    if self.bot.redisIO is not None:
#        self.bot.redisIO.setValue(ctx.message.channel.id, recent_score.beatmap_id)
#        self.bot.redisIO.setValue(f"{ctx.message.channel.id}.mode", mode.id)
#
#    beatmap: osuClasses.Beatmap = await self.bot.osuAPI.getbmap(
#        recent_score.beatmap_id,
#        mode=mode,
#        server=server,
#        mods=recent_score.enabled_mods,
#    )
#
#    recent_score.performance = await self.bot.ppAPI.calculateScore(recent_score)
#    recent_score.performance.pp = (
#        recent_score.pp if recent_score.pp != 0 else recent_score.performance.pp
#    )
#    beatmap.max_combo = (
#        beatmap.max_combo
#        if beatmap.max_combo
#        else recent_score.performance.max_combo
#    )
#
#    result = OsuRecentEmbed(recent_score, beatmap, self.bot.config.color)
#
#    await ctx.send(
#        f"**Most Recent osu! {mode.name_full} Play for {profile.username} on {server.name_full}:**",
#        embed=result,
#    )
#
# @commands.cooldown(1, 1, commands.BucketType.user)
# @commands.command(
#    aliases=["ot", "tt", "ct", "mt", "taikotop", "ctbtop", "maniatop"],
# )
# async def osutop(self, ctx, *, args=None):
#    """Shows osu! top plays for a user. Modes can be specified ``eg. maniatop``.\n*Valid Arguments:* ```fix\n-r, -p```"""
#
#    user = None
#    server = osuClasses.Server.BANCHO
#    limit = 5
#    mode = osuClasses.Mode.fromCommand(ctx.invoked_with)
#    recent: bool = False
#    positions: List[int] = range(1, 101)
#    parsedArgs = None
#
#    if args is not None:
#        parsedArgs = self.bot.osuHelpers.parseArgsV2(args=args, customArgs=["user"])
#        user = parsedArgs["user"]
#        qtype = parsedArgs["qtype"]
#        server = parsedArgs["server"]
#
#        if parsedArgs["recent"] is True:
#            limit = 100
#        elif parsedArgs["position"] is not None:
#            limit = min(parsedArgs["position"], 100)
#
#    if not user:
#        qtype = "id"
#        user, serverID = await self.bot.mongoIO.getOsu(ctx.author)
#        server = osuClasses.Server.from_id(serverID)
#
#    if (
#        user
#        and isinstance(user, str)
#        and user.startswith("<@")
#        and user.endswith(">")
#    ):
#        qtype = "id"
#        mentioned_id = int(id_rx.sub(r"", user))
#        mentioned = await self.bot.ensure_member(mentioned_id, ctx.guild)
#        user, serverID = await self.bot.mongoIO.getOsu(mentioned)
#        server = osuClasses.Server.from_id(serverID)
#
#    profile: osuClasses.User = await self.bot.osuAPI.getuser(
#        user,
#        qtype,
#        mode,
#        server,
#    )
#    tops: List[osuClasses.RecentScore] = await self.bot.osuAPI.getusrtop(
#        profile,
#        limit,
#    )
#
#    if parsedArgs:
#        if parsedArgs["recent"]:
#            sorted_tops = sorted(tops, key=lambda x: x.date, reverse=True)
#            positions = list(map(lambda top: tops.index(top) + 1, sorted_tops))
#            tops = sorted_tops
#
#        if parsedArgs["position"] is None:
#            tops = tops[:5]
#            positions = positions[:5]
#        else:
#            tops = tops[parsedArgs["position"] - 1 : parsedArgs["position"]]
#            positions = positions[
#                parsedArgs["position"] - 1 : parsedArgs["position"]
#            ]
#    else:
#        tops = tops[:5]
#        positions = positions[:5]
#
#    if self.bot.redisIO is not None:
#        self.bot.redisIO.setValue(ctx.message.channel.id, tops[0].beatmap_id)
#        self.bot.redisIO.setValue(f"{ctx.message.channel.id}.mode", mode.id)
#
#    beatmaps = []
#
#    index: int
#    top: osuClasses.Score
#    for index, top in enumerate(tops):
#        beatmap: osuClasses.Beatmap = await self.bot.osuAPI.getbmap(
#            top.beatmap_id,
#            mode=mode,
#            server=server,
#            mods=top.enabled_mods,
#        )
#
#        top.performance = await self.bot.ppAPI.calculateScore(top, mode)
#        top.performance.pp = top.pp if top.pp else top.performance.pp
#        beatmap.max_combo = (
#            beatmap.max_combo if beatmap.max_combo else top.performance.max_combo
#        )
#
#        beatmaps.append(beatmap)
#
#    title = f"Top plays on osu! {profile.mode.name_full} for {profile.username}"
#    result = OsuListEmbed(
#        title,
#        self.bot.config.color,
#        tops,
#        beatmaps,
#        profile,
#        positions,
#        0,
#    )
#    await ctx.send(embed=result)
#
# @commands.cooldown(1, 1, commands.BucketType.user)
# @commands.command(aliases=["c", "s", "scores"])
# async def compare(self, ctx: commands.Context, *, args=None):
#    """Shows your best scores on the last linked map."""
#
#    user = None
#    beatmap: osuClasses.Beatmap = None
#    server = osuClasses.Server.BANCHO
#    mode = osuClasses.Mode.STANDARD
#    limit = 5
#
#    if args is not None:
#        if "c" == ctx.invoked_with or "compare" == ctx.invoked_with:
#            parsedArgs = self.bot.osuHelpers.parseArgsV2(
#                args=args,
#                customArgs=["user", "beatmap"],
#            )
#        elif "s" == ctx.invoked_with or "scores" == ctx.invoked_with:
#            parsedArgs = self.bot.osuHelpers.parseArgsV2(
#                args=args,
#                customArgs=["beatmap", "user"],
#            )
#            if parsedArgs["beatmap"]:
#                beatmap = await self.bot.osuHelpers.getBeatmapFromText(
#                    parsedArgs["beatmap"],
#                )
#                if self.bot.redisIO is not None:
#                    self.bot.redisIO.setValue(
#                        ctx.message.channel.id,
#                        beatmap.beatmap_id,
#                    )
#                    self.bot.redisIO.setValue(
#                        f"{ctx.message.channel.id}.mode",
#                        mode.id,
#                    )
#        user = parsedArgs["user"]
#        qtype = parsedArgs["qtype"]
#        server = parsedArgs["server"]
#
#    if not user:
#        qtype = "id"
#        user, serverID = await self.bot.mongoIO.getOsu(ctx.author)
#        server = osuClasses.Server.from_id(serverID)
#
#    if (
#        user
#        and isinstance(user, str)
#        and user.startswith("<@")
#        and user.endswith(">")
#    ):
#        qtype = "id"
#        mentioned_id = int(id_rx.sub(r"", user))
#        mentioned = await self.bot.ensure_member(mentioned_id, ctx.guild)
#        user, serverID = await self.bot.mongoIO.getOsu(mentioned)
#        server = osuClasses.Server.from_id(serverID)
#
#    if "c" == ctx.invoked_with or "compare" == ctx.invoked_with and beatmap is None:
#        if self.bot.redisIO is not None:
#            modeID = self.bot.redisIO.getValue(f"{ctx.message.channel.id}.mode")
#            beatmapID = self.bot.redisIO.getValue(ctx.message.channel.id)
#            if modeID is None or beatmapID is None:
#                return
#            mode = osuClasses.Mode.fromId(modeID)
#            beatmap = await self.bot.osuAPI.getbmap(
#                beatmapID,
#                mode=mode,
#                server=server,
#            )
#        else:
#            return ctx.send(
#                "Redis is disabled in the config. Please contact the owner of this instance!",
#            )
#
#    if beatmap is None:
#        return
#
#    profile: osuClasses.User = await self.bot.osuAPI.getuser(
#        user,
#        qtype,
#        mode,
#        server,
#    )
#    tops: List[osuClasses.BeatmapScore] = await self.bot.osuAPI.getusrscores(
#        profile,
#        beatmap.beatmap_id,
#        limit,
#    )
#
#    top: osuClasses.Score
#    for _, top in enumerate(tops):
#        top.performance = await self.bot.ppAPI.calculateScore(top)
#        top.performance.pp = top.pp if top.pp != 0 else top.performance.pp
#        beatmap.max_combo = (
#            beatmap.max_combo
#            if beatmap.max_combo != 0
#            else top.performance.max_combo
#        )
#
#    title = f"Top osu! {mode.name_full} for {profile.username} on {beatmap.title}[{beatmap.version}]"
#    result = OsuListEmbed(
#        title,
#        self.bot.config.color,
#        tops,
#        [beatmap] * len(tops),
#        profile,
#    )
#
#    await ctx.send(embed=result)
#
# @commands.cooldown(1, 1, commands.BucketType.user)
# @commands.command(aliases=["pp"])
# async def perf(self, ctx, *, args=None):
#    """Shows information about pp of a certain map"""
#
#    args = self.bot.osuHelpers.parseArgsV2(
#        args=args,
#        customArgs=["mods", "beatmap"],
#    )
#    mode = args["mode"]
#
#    if args["beatmap"]:
#        beatmap: osuClasses.Beatmap = await self.bot.osuHelpers.getBeatmapFromText(
#            args["beatmap"],
#        )
#    else:
#        beatmap: osuClasses.Beatmap = (
#            await self.bot.osuHelpers.getBeatmapFromHistory(ctx)
#        )
#
#    if beatmap is None:
#        await ctx.send("Failed to find any maps")
#        return
#
#    if self.bot.redisIO is not None:
#        self.bot.redisIO.setValue(ctx.message.channel.id, beatmap.beatmap_id)
#        self.bot.redisIO.setValue(f"{ctx.message.channel.id}.mode", mode.id)
#
#    mods: osuClasses.Mods = osuClasses.Mods(args["mods"])
#
#    perf = await self.bot.ppAPI.calculateBeatmap(beatmap.beatmap_id, mods, mode)
#
#    result = OsuPerformanceEmbed(beatmap, perf, self.bot.config.color)
#    await ctx.send(embed=result)
#


async def setup(bot):
    await bot.add_cog(OsuCog(bot))
    await bot.add_cog(OsuProfileCog(bot))
    await bot.add_cog(OsuTopsCog(bot))
