###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import TYPE_CHECKING

import aiosu
import discord
from classes.cog import MetadataCog
from classes.cog import MetadataGroupCog
from common import graphing
from common import humanizer
from common.crypto import encode_discord_id
from common.helpers import get_beatmap_from_reference
from common.helpers import get_beatmap_from_text
from discord import app_commands
from discord.ext import commands
from discord.utils import escape_markdown
from ui.embeds.osu import OsuDifficultyEmbed
from ui.embeds.osu import OsuLinkEmbed
from ui.embeds.osu import OsuProfileCompactEmbed
from ui.embeds.osu import OsuProfileExtendedEmbed
from ui.embeds.osu import OsuScoreSingleEmbed
from ui.menus.osu import OsuScoresView

if TYPE_CHECKING:
    from typing import Any
    from classes.bot import Sunny


class OsuProfileFlags(commands.FlagConverter, prefix="-"):  # type: ignore
    lazer: bool | None = commands.Flag(
        aliases=["l"],
        description="Whether to use the lazer client",
        default=None,
    )
    extended: bool = commands.Flag(
        aliases=["e"],
        description="Show extended stats",
        default=False,
    )


class OsuTopFlags(commands.FlagConverter, prefix="-"):  # type: ignore
    recent: bool = commands.Flag(
        aliases=["r"],
        description="Sort by date achieved",
        default=False,
    )
    position: int | None = commands.Flag(
        aliases=["p"],
        description="The position of the score to show",
        default=None,
    )
    lazer: bool | None = commands.Flag(
        aliases=["l"],
        description="Whether to use the lazer client",
        default=None,
    )


class OsuRecentFlags(commands.FlagConverter):
    mode: aiosu.models.Gamemode | None = commands.Flag(
        aliases=["m"],
        description="The osu! mode to search for",
        default=None,
    )
    list: bool = commands.Flag(
        aliases=["l"],
        description="Display a list of recent scores",
        default=False,
    )
    include_failed: bool = commands.Flag(
        aliases=["f"],
        description="Include failed scores",
        default=True,
    )


class OsuScoreFlags(commands.FlagConverter):
    mode: aiosu.models.Gamemode | None = commands.Flag(
        aliases=["m"],
        description="The osu! mode to search for",
        default=None,
    )
    lazer: bool | None = commands.Flag(
        aliases=["l"],
        description="Whether to use the lazer client",
        default=None,
    )


class OsuPPFlags(commands.FlagConverter):
    mode: aiosu.models.Gamemode | None = commands.Flag(
        aliases=["m"],
        description="The osu! mode to search for",
        default=None,
    )
    lazer: bool | None = commands.Flag(
        aliases=["l"],
        description="Whether to use the lazer client",
        default=None,
    )


class OsuUserConverter(commands.Converter):
    async def convert(
        self, ctx: commands.Context, *args: Any
    ) -> tuple[aiosu.v2.Client, aiosu.models.User]:
        """
        Converts to an ``aiosu.models.User`` (case-insensitive)

        The lookup strategy is as follows (in order):

        1. Lookup by commands.MemberConverter()
        2. Lookup by string
        """
        raw_user, mode, lazer = args

        if lazer is None:
            lazer = await ctx.bot.user_prefs_service.get_lazer(ctx.author.id)

        client_storage = ctx.bot.stable_storage
        if lazer:
            client_storage = ctx.bot.lazer_storage

        params = {}
        if mode is not None:
            params = {"mode": mode}

        if raw_user is None:
            client = await client_storage.get_client(id=ctx.author.id)
            return (client, await client.get_me(**params), lazer)

        member = None
        try:
            member = await commands.MemberConverter().convert(ctx, raw_user)
        except commands.MemberNotFound:

            def check(member: discord.Member) -> bool:
                return (
                    member.name.lower() == raw_user.lower()
                    or member.display_name.lower() == raw_user.lower()
                    or str(member).lower() == raw_user.lower()
                    or str(member.id) == raw_user
                )

            if found := discord.utils.find(check, ctx.guild.members):
                member = found

        if member is None:
            client = await client_storage.app_client
            return (client, await client.get_user(raw_user, **params), lazer)

        client = await client_storage.get_client(id=member.id)
        return (client, await client.get_me(**params), lazer)


class OsuProfileCog(MetadataGroupCog, name="profile", display_parent="osu!"):
    """
    osu! Profile Commands
    """

    args_description = {
        "user": "Discord/osu! username or mention",
    }

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    async def get_graph(self, user: aiosu.models.User, lazer: bool):
        try:
            graph = await self.bot.graph_service.get_one(user.id, lazer)
        except ValueError:
            graph = await self.bot.run_blocking(graphing.plot_rank_graph, user)
            await self.bot.graph_service.add(user.id, graph, lazer)
        return graph

    async def osu_profile_command(
        self,
        ctx: commands.Context,
        username: str | None,
        mode: aiosu.models.Gamemode,
        flags: OsuProfileFlags,
    ) -> None:
        await ctx.defer()
        _, user, lazer = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )
        if flags.extended:
            embed = OsuProfileExtendedEmbed(ctx, user, mode, lazer)
        else:
            embed = OsuProfileCompactEmbed(ctx, user, mode, lazer)
        graph = await self.get_graph(user, lazer)
        embed.set_image(url="attachment://rank_graph.png")
        await ctx.send(embed=embed, file=discord.File(graph, "rank_graph.png"))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="osu",
        description="Shows osu!std stats for a user",
    )
    @app_commands.describe(**args_description)
    async def osu_std_profile_command(
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuProfileFlags,
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.STANDARD, flags)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="mania",
        description="Shows osu!mania stats for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_mania_profile_command(
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuProfileFlags,
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.MANIA, flags)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="taiko",
        description="Shows osu!taiko stats for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_taiko_profile_command(
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuProfileFlags,
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.TAIKO, flags)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="ctb",
        description="Shows osu!ctb stats for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_ctb_profile_command(
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuProfileFlags,
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.CTB, flags)


class OsuTopsCog(MetadataGroupCog, name="top", display_parent="osu!"):
    """
    osu! Tops Commands
    """

    args_description = {
        "user": "Discord/osu! username or mention",
    }

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    async def osu_top_command(
        self,
        ctx: commands.Context,
        username: str | None,
        mode: aiosu.models.Gamemode,
        flags: OsuTopFlags,
    ) -> None:
        await ctx.defer()
        client, user, _ = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        safe_username = escape_markdown(user.username)

        tops = await client.get_user_bests(
            user.id,
            mode=mode,
            limit=100,
            new_format=True,
        )
        if not tops:
            await ctx.send(f"User **{safe_username}** has no top plays!")
            return

        await self.bot.beatmap_service.add(ctx.channel.id, tops[0].beatmap)

        recent_text = ""
        if flags.recent:
            tops.sort(key=lambda x: x.created_at, reverse=True)
            recent_text = "Recent "

        if flags.position is None:
            title = f"{recent_text}osu! {mode:f} top plays for {safe_username}"
            await OsuScoresView.start(ctx, user, mode, tops, title, timeout=30)
        else:
            title = f"{humanizer.ordinal(flags.position)} {recent_text}osu! {mode:f} top play for {safe_username}"
            embed = OsuScoreSingleEmbed(ctx, tops[flags.position - 1], title)
            await embed.prepare()
            await ctx.send(embed=embed)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="osutop",
        aliases=["ot"],
        description="Shows osu!std top plays for a user",
    )
    @app_commands.describe(**args_description)
    async def osu_std_top_command(
        self, ctx: commands.Context, user: str | None, *, flags: OsuTopFlags
    ) -> None:
        await self.osu_top_command(ctx, user, aiosu.models.Gamemode.STANDARD, flags)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="maniatop",
        aliases=["mt"],
        description="Shows osu!mania top plays for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_mania_top_command(
        self, ctx: commands.Context, user: str | None, *, flags: OsuTopFlags
    ) -> None:
        await self.osu_top_command(ctx, user, aiosu.models.Gamemode.MANIA, flags)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="taikotop",
        aliases=["tt"],
        description="Shows osu!taiko top plays for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_taiko_top_command(
        self, ctx: commands.Context, user: str | None, *, flags: OsuTopFlags
    ) -> None:
        await self.osu_top_command(ctx, user, aiosu.models.Gamemode.TAIKO, flags)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="ctbtop",
        aliases=["ct"],
        description="Shows osu!ctb top plays for a user.",
    )
    @app_commands.describe(**args_description)
    async def osu_ctb_top_command(
        self, ctx: commands.Context, user: str | None, *, flags: OsuTopFlags
    ) -> None:
        await self.osu_top_command(ctx, user, aiosu.models.Gamemode.CTB, flags)


class OsuCog(MetadataCog, name="osu!"):
    """
    osu! related commands.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.config_v2 = self.bot.config.osuAPIv2

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(
        name="osuset",
        description="Sets the osu! profile for the message author",
    )
    async def osu_set_command(
        self,
        ctx: commands.Context,
    ) -> None:
        await ctx.send("Please access the thread to link your osu! account.")
        thread = await ctx.channel.create_thread(
            name="osu! Profile Link",
            auto_archive_duration=60,
            invitable=False,
        )
        url = aiosu.utils.auth.generate_url(
            client_id=self.config_v2.client_id,
            redirect_uri=self.config_v2.redirect_uri,
            state=encode_discord_id(ctx.author.id, self.bot.aes),
        )
        await thread.add_user(ctx.author)
        await thread.send(embed=OsuLinkEmbed(ctx, url))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="lazertoggle",
        description="Toggles whether osu! commands use lazer stats by default or not",
    )
    async def lazer_toggle_command(
        self,
        ctx: commands.Context,
    ) -> None:
        lazer = await self.bot.user_prefs_service.toggle_lazer(ctx.author.id)
        default = "lazer" if lazer else "stable"
        await ctx.send(f"Defaulting to {default} stats for osu! commands.")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="recent",
        aliases=["rs", "r"],
        description="Shows recent osu! scores for a user",
    )
    @app_commands.describe(
        username="Discord/osu! username or mention",
    )
    async def osu_recent_command(
        self,
        ctx: commands.Context,
        username: str | None,
        *,
        flags: OsuRecentFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode
        client, user, _ = await OsuUserConverter().convert(ctx, username, mode, True)

        safe_username = escape_markdown(user.username)

        if mode is None:
            mode = user.playmode
        recents = await client.get_user_recents(
            user.id,
            mode=mode,
            limit=1 if not flags.list else 50,
            include_fails=flags.include_failed,
            new_format=True,
        )
        if not recents:
            await ctx.send(f"User **{safe_username}** has no recent plays!")
            return

        await self.bot.beatmap_service.add(ctx.channel.id, recents[0].beatmap)

        if flags.list:
            title = f"Recent osu! {mode:f} plays for {safe_username}"
            await OsuScoresView.start(ctx, user, mode, recents, title, timeout=30)
            return

        title = f"Most recent osu! {mode:f} play for {safe_username}"
        embed = OsuScoreSingleEmbed(ctx, recents[0], title)
        await embed.prepare()
        await ctx.send(embed=embed)

    async def osu_beatmap_scores_command(
        self,
        ctx: commands.Context,
        username: str | None,
        mode: aiosu.models.Gamemode,
        beatmap: aiosu.models.Beatmap,
        lazer: bool,
    ) -> None:
        client, user, lazer = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            lazer,
        )

        safe_username = escape_markdown(user.username)

        scores = await client.get_user_beatmap_scores(
            user.id,
            beatmap.id,
            mode=mode,
        )
        if not scores:
            await ctx.send(f"User **{safe_username}** has no plays on the beatmap!")
            return

        for score in scores:
            score.beatmap = beatmap

        title = f"osu! {beatmap.mode:f} plays for {safe_username}"
        await OsuScoresView.start(
            ctx,
            user,
            mode,
            scores,
            title,
            True,
            timeout=30,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="compare",
        aliases=["c", "gap"],
        description="Compares osu! scores for a user",
    )
    @app_commands.describe(
        username="Discord/osu! username or mention",
    )
    async def osu_compare_command(
        self,
        ctx: commands.Context,
        username: str | None,
        *,
        flags: OsuScoreFlags,
    ) -> None:
        await ctx.defer()
        mode, lazer = flags.mode, flags.lazer

        client = await self.bot.stable_storage.app_client

        if ctx.message.reference:
            beatmap_data = get_beatmap_from_reference(ctx.message.reference)
            beatmap_id = beatmap_data.get("beatmap_id")
            if beatmap_id is None:
                await ctx.send("No beatmap found to compare to.")
                return
            beatmap = await client.get_beatmap(beatmap_id)
        else:
            try:
                beatmap = await self.bot.beatmap_service.get_one(ctx.channel.id)
            except ValueError:
                await ctx.send("No beatmap found to compare to.")
                return

        if mode is None:
            mode = beatmap.mode

        await self.osu_beatmap_scores_command(
            ctx,
            username,
            mode,
            beatmap,
            lazer,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="scores",
        aliases=["s"],
        description="Sends osu! scores for a user on a beatmap",
    )
    @app_commands.describe(
        beatmap_query="URL or ID of the beatmap",
        username="Discord/osu! username or mention",
    )
    async def osu_scores_command(
        self,
        ctx: commands.Context,
        beatmap_query: str,
        username: str | None,
        *,
        flags: OsuScoreFlags,
    ) -> None:
        await ctx.defer()
        mode, lazer = flags.mode, flags.lazer

        beatmap_data = get_beatmap_from_text(beatmap_query)
        if (beatmap_id := beatmap_data["beatmap_id"]) is None:
            await ctx.send("Unknown beatmap ID specified.")
            return

        client = await self.bot.stable_storage.app_client
        beatmap = await client.get_beatmap(beatmap_id)
        await self.bot.beatmap_service.add(ctx.channel.id, beatmap)

        if mode is None:
            mode = beatmap.mode

        await self.osu_beatmap_scores_command(
            ctx,
            username,
            mode,
            beatmap,
            lazer,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="pp",
        description="Shows information about pp of a certain map",
    )
    @app_commands.describe(
        beatmap_query="URL or ID of the beatmap",
        mods="Mods to calculate pp with",
    )
    async def osu_perf_command(
        self,
        ctx: commands.Context,
        beatmap_query: str | None,
        mods: str = "",
        *,
        flags: OsuPPFlags,
    ) -> None:
        await ctx.defer()

        mode = flags.mode
        mods = aiosu.models.Mods(mods)
        client = await self.bot.stable_storage.app_client

        beatmap_data = None
        if ctx.message.reference:
            beatmap_data = get_beatmap_from_reference(ctx.message.reference)
        elif beatmap_query:
            beatmap_data = get_beatmap_from_text(beatmap_query)

        if not beatmap_data:
            beatmap = await self.bot.beatmap_service.get_one(ctx.channel.id)
            if beatmap is None:
                await ctx.send("No beatmap found in cache.")
                return
        else:
            beatmap_id = beatmap_data.get("beatmap_id")
            if beatmap_id is None:
                await ctx.send("Unknown beatmap ID specified.")
                return

            beatmap = await client.get_beatmap(beatmap_id)
            await self.bot.beatmap_service.add(ctx.channel.id, beatmap)

        if mode is None:
            mode = beatmap.mode

        if beatmap.beatmapset is None:
            beatmap.beatmapset = await client.get_beatmapset(beatmap.beatmapset_id)

        difficulty_attributes = await client.get_beatmap_attributes(
            beatmap.id,
            mode=mode,
            mods=mods,
        )

        await ctx.send(
            embed=OsuDifficultyEmbed(
                ctx,
                beatmap,
                difficulty_attributes,
                mods,
            ),
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="whatif",
        description="Shows potential pp gain for a given score",
    )
    @app_commands.describe(
        username="Discord/osu! username or mention",
        pp="Amount of pp to simulate",
    )
    async def osu_whatif_command(
        self,
        ctx: commands.Context,
        pp: float,
        username: str | None,
        *,
        flags: OsuPPFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode

        client, user, _ = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        total_pp_with_bonus = user.statistics.pp

        if mode is None:
            mode = user.playmode

        tops = await client.get_user_bests(user.id, mode=mode, limit=100)

        safe_username = escape_markdown(user.username)

        if pp < tops[-1].pp:
            await ctx.send(
                f"{safe_username} would **not** gain any pp if they got a **{pp:.2f}pp** score.",
            )
            return

        pps_list = [top.pp for top in tops]
        weights = [top.weight.percentage for top in tops]

        initial_weighted_pps = [
            pp * weight / 100 for pp, weight in zip(pps_list, weights)
        ]
        initial = sum(initial_weighted_pps)

        bonus = total_pp_with_bonus - initial

        pps_list.append(pp)
        pps_list.sort(reverse=True)
        final_weighted_pps = [
            pp * weight / 100 for pp, weight in zip(pps_list, weights)
        ]
        final = sum(final_weighted_pps[:100])

        await ctx.send(
            f"{safe_username} would gain **{final - initial:.2f}pp** if they got a **{pp:.2f}pp** score, bringing them up to **{final + bonus:.2f}pp**.",
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="bonus",
        description="Shows bonus pp for a user",
    )
    @app_commands.describe(
        username="Discord/osu! username or mention",
    )
    async def osu_bonus_command(
        self,
        ctx: commands.Context,
        username: str | None,
        *,
        flags: OsuPPFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode

        client, user, _ = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        safe_username = escape_markdown(user.username)

        if user.is_restricted:
            await ctx.send(
                f"{safe_username} is restricted, therefore we cannot calculate their bonus pp.",
            )
            return

        total_pp_with_bonus = user.statistics.pp

        if mode is None:
            mode = user.playmode

        tops = await client.get_user_bests(user.id, mode=mode, limit=100)

        pps_list = [top.pp for top in tops]
        weights = [top.weight.percentage for top in tops]

        initial_weighted_pps = [
            pp * weight / 100 for pp, weight in zip(pps_list, weights)
        ]
        initial = sum(initial_weighted_pps)

        bonus = total_pp_with_bonus - initial

        await ctx.send(
            f"{safe_username} has a bonus of **{bonus:.2f}pp** from playcount.",
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="recalcpp",
        description="Recalculates pp for a user (without bonus pp)",
    )
    @app_commands.describe(
        username="Discord/osu! username or mention",
    )
    async def osu_recalculate_pp_command(
        self,
        ctx: commands.Context,
        username: str | None,
        *,
        flags: OsuPPFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode

        client, user, _ = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        safe_username = escape_markdown(user.username)

        if mode is None:
            mode = user.playmode

        tops = await client.get_user_bests(user.id, mode=mode, limit=100)

        pps_list = [top.pp for top in tops]
        weights = [top.weight.percentage for top in tops]

        initial_weighted_pps = [
            pp * weight / 100 for pp, weight in zip(pps_list, weights)
        ]
        initial = sum(initial_weighted_pps)

        await ctx.send(f"{safe_username} has **{initial:.2f}pp** (without bonus pp).")


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OsuCog(bot))
    await bot.add_cog(OsuProfileCog(bot))
    await bot.add_cog(OsuTopsCog(bot))
