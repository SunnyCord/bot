from __future__ import annotations

from typing import Optional
from typing import Union

import classes.osu as osuClasses
import discord
from classes.embeds.osu import *
from commons.regex import id_rx
from discord import app_commands
from discord.ext import commands


class OsuProfileGroup(app_commands.Group):
    @staticmethod
    async def osu_profile_command(
        interaction: discord.Interaction,
        mode: osuClasses.Mode,
        user: Optional[str],
        server: Optional[osuClasses.Server],
    ):
        await interaction.response.send_message(f"YO {user} {server} {mode}")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="osu",
        description="Shows osu!std stats for a user",
    )
    @app_commands.describe()
    async def osu_std_profile_command(
        self,
        interaction: discord.Interaction,
        user: Optional[str],
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(
            interaction,
            osuClasses.Mode.STANDARD,
            user,
            server,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="mania",
        description="Shows osu!mania stats for a user.",
    )
    @app_commands.describe()
    async def osu_mania_profile_command(
        self,
        interaction: discord.Interaction,
        user: Union[str],
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(interaction, osuClasses.Mode.MANIA, user, server)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="taiko",
        description="Shows osu!taiko stats for a user.",
    )
    @app_commands.describe()
    async def osu_taiko_profile_command(
        self,
        interaction: discord.Interaction,
        user: Optional[str],
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(interaction, osuClasses.Mode.TAIKO, user, server)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="ctb",
        description="Shows osu!ctb stats for a user.",
    )
    @app_commands.describe()
    async def osu_ctb_profile_command(
        self,
        interaction: discord.Interaction,
        user: Optional[str],
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ):
        await self.osu_profile_command(interaction, osuClasses.Mode.CTB, user, server)


class OsuCog(commands.Cog, name="osu!"):
    """
    osu! related commands.\n*Valid Arguments:* ```fix\n-ripple, -akatsuki```
    """

    def __init__(self, bot) -> None:
        self.bot = bot
        bot.tree.add_command(
            OsuProfileGroup(name="profile", description="Shows osu! stats for a user"),
        )

    @commands.command(
        aliases=[
            "osuset",
            "osu",
            "mania",
            "taiko",
            "ctb",
            "osutop",
            "ot",
            "maniatop",
            "mt",
            "taikotop",
            "tt",
            "ctbtop",
            "ct",
            "perf",
            "pp",
            "recent",
            "rs",
            "r",
            "compare",
            "c",
        ],
        name="",
        hidden=True,
    )
    async def depr_warn_command(self, ctx):
        await ctx.send(
            "This bot now uses slash commands! Old commands have been deprecated. Please look at the new syntax.",
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(
        name="osuset",
        description="Sets the osu! profile for the message author",
    )
    @app_commands.describe(username="Your username", server="The server")
    async def osu_set_command(
        self,
        interaction: discord.Interaction,
        username: str,
        server: Optional[osuClasses.Server] = osuClasses.Server.BANCHO,
    ) -> None:
        profile: osuClasses.User = await self.bot.osuAPI.getuser(
            username,
            "string",
            server=server,
        )
        await self.bot.mongoIO.setOsu(
            interaction.user,
            profile.user_id,
            server.id,
        )
        await interaction.response.send_message(
            f"osu! {server.name_full} profile succesfully set to {profile.username}",
        )

    # @commands.cooldown(1, 1, commands.BucketType.user)
    # @commands.command(aliases=["mania", "taiko", "ctb"])
    # async def osu(self, ctx, *, args=None):


#
#    user = None
#    server = osuClasses.Server.BANCHO
#
#    if args is not None:
#        parsedArgs = self.bot.osuHelpers.parseArgs(args=args)
#        user = parsedArgs["user"]
#        qtype = parsedArgs["qtype"]
#        server = osuClasses.Server.from_name(parsedArgs["server"])
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
#    mode = osuClasses.Mode.fromCommand(ctx.invoked_with)
#    user: osuClasses.User = await self.bot.osuAPI.getuser(
#        usr=user,
#        mode=mode,
#        qtype=qtype,
#        server=server,
#    )
#
#    if (user.playcount is not None) and (user.accuracy is not None):
#        result = OsuProfileEmbed(user, mode, self.bot.config.color)
#        return await ctx.send(embed=result)
#
#    else:
#        await ctx.send("User has not been found or has not played enough!")
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
