from __future__ import annotations

from typing import Optional
from typing import TYPE_CHECKING

import aiosu
import discord
from commons.helpers import get_beatmap_from_text
from discord import app_commands
from discord.ext import commands
from models.cog import MetadataCog
from models.cog import MetadataGroupCog
from ui.embeds.osu import OsuProfileEmbed
from ui.embeds.osu import OsuScoreSingleEmbed
from ui.menus.osu import OsuScoresView

if TYPE_CHECKING:
    from typing import Any
    from models.bot import Sunny


class OsuTopFlags(commands.FlagConverter, prefix="-"):  # type: ignore
    recent: Optional[bool] = commands.Flag(
        aliases=["r"],
        description="Sort by date achieved",
        default=False,
    )
    position: Optional[int] = commands.Flag(
        aliases=["p"],
        description="The position of the score to show",
        default=None,
    )


class OsuRecentFlags(commands.FlagConverter):
    mode: Optional[aiosu.models.Gamemode] = commands.Flag(
        aliases=["m"],
        description="The osu! mode to search for",
        default=aiosu.models.Gamemode.STANDARD,
    )
    list: Optional[bool] = commands.Flag(
        aliases=["l"],
        description="Display a list of recent scores",
        default=False,
    )


class OsuScoreFlags(commands.FlagConverter):
    mode: Optional[aiosu.models.Gamemode] = commands.Flag(
        aliases=["m"],
        description="The osu! mode to search for",
        default=aiosu.models.Gamemode.STANDARD,
    )


class OsuUserConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, *args: Any) -> aiosu.models.User:
        """
        Converts to an ``aiosu.models.User`` (case-insensitive)

        The lookup strategy is as follows (in order):

        1. Lookup by commands.MemberConverter()
        2. Lookup by string
        """
        raw_user, mode = args
        user, qtype = None, None

        if raw_user is None:
            user = await ctx.bot.mongoIO.get_osu(ctx.author)
            qtype = "id"
        else:
            try:
                member = await commands.MemberConverter().convert(ctx, raw_user)
                user = await ctx.bot.mongoIO.get_osu(member)
                qtype = "id"
            except commands.MemberNotFound:

                def check(member: discord.Member) -> bool:
                    return (
                        member.name.lower() == raw_user.lower()
                        or member.display_name.lower() == raw_user.lower()
                        or str(member).lower() == raw_user.lower()
                        or str(member.id) == raw_user
                    )

                if found := discord.utils.find(check, ctx.guild.members):
                    user = await ctx.bot.mongoIO.get_osu(found)
                    qtype = "id"

                user, qtype = raw_user, "string"

        return await ctx.bot.client_v1.get_user(
            user,
            mode=mode,
            qtype=qtype,
        )


class OsuProfileCog(MetadataGroupCog, name="profile", display_parent="osu!"):  # type: ignore
    """
    osu! Profile Commands
    """

    args_description = {
        "user": "Discord/osu! username or mention",
    }

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    async def osu_profile_command(
        self,
        ctx: commands.Context,
        username: Optional[str],
        mode: aiosu.models.Gamemode,
    ) -> None:
        await ctx.defer()
        user = await OsuUserConverter().convert(ctx, username, mode)
        await ctx.send(embed=OsuProfileEmbed(ctx, user, mode))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="osu",
        description="Shows osu!std stats for a user",
    )
    @app_commands.describe(**args_description)
    async def osu_std_profile_command(
        self,
        ctx: commands.Context,
        user: Optional[str],
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.STANDARD)

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
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.MANIA)

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
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.TAIKO)

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
    ) -> None:
        await self.osu_profile_command(ctx, user, aiosu.models.Gamemode.CTB)


class OsuTopsCog(MetadataGroupCog, name="top", display_parent="osu!"):  # type: ignore
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
        username: Optional[str],
        mode: aiosu.models.Gamemode,
        flags: OsuTopFlags,
    ) -> None:
        await ctx.defer()
        user = await OsuUserConverter().convert(ctx, username, mode)
        tops = await self.bot.client_v1.get_user_bests(
            user.id,
            qtype="id",
            include_beatmap=True,
        )
        if not tops:
            await ctx.send(f"User **{user.username}** has no top plays!")
            return

        await self.bot.beatmap_service.add(ctx.channel.id, tops[0])

        recent_text = ""
        if flags.recent:
            tops.sort(key=lambda x: x.created_at, reverse=True)
            recent_text = "Recent "

        if flags.position is None:
            title = f"{recent_text}osu! {mode:f} top plays for {user.username}"
            await OsuScoresView.start(ctx, user, mode, tops, title, timeout=30)
        else:
            title = f"**{flags.position}.** {recent_text}osu! {mode:f} top play for **{user.username}**"
            embed = OsuScoreSingleEmbed(ctx, tops[flags.position - 1])
            await embed.prepare()
            await ctx.send(title, embed=embed)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="osutop",
        aliases=["ot"],
        description="Shows osu!std top plays for a user",
    )
    @app_commands.describe(**args_description)
    async def osu_std_top_command(
        self, ctx: commands.Context, user: Optional[str], *, flags: OsuTopFlags
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
        self, ctx: commands.Context, user: Optional[str], *, flags: OsuTopFlags
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
        self, ctx: commands.Context, user: Optional[str], *, flags: OsuTopFlags
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
        self, ctx: commands.Context, user: Optional[str], *, flags: OsuTopFlags
    ) -> None:
        await self.osu_top_command(ctx, user, aiosu.models.Gamemode.CTB, flags)


class OsuCog(MetadataCog, name="osu!"):  # type: ignore
    """
    osu! related commands.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.hybrid_command(
        name="osuset",
        description="Sets the osu! profile for the message author",
    )
    @app_commands.describe(
        username="Your osu! username",
    )
    async def osu_set_command(
        self,
        ctx: commands.Context,
        username: str,
    ) -> None:
        await ctx.defer()
        profile: aiosu.models.User = await self.bot.client_v1.get_user(
            user_query=username,
            qtype="string",
        )
        # await self.bot.mongoIO.set_osu(
        #     ctx.author,
        #     profile.id,
        # )
        # await ctx.send(
        #     f"osu! profile succesfully set to {profile.username}",
        # )

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
        username: Optional[str],
        *,
        flags: OsuRecentFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode
        user = await OsuUserConverter().convert(ctx, username, mode)
        recents = await self.bot.client_v1.get_user_recents(
            user.id,
            qtype="id",
            mode=mode,
            include_beatmap=True,
            limit=1 if not flags.list else 50,
        )
        if not recents:
            await ctx.send(f"User **{user.username}** has no recent plays!")
            return

        await self.bot.beatmap_service.add(ctx.channel.id, recents[0])

        if flags.list:
            title = f"Recent osu! {mode:f} plays for {user.username}"
            await OsuScoresView.start(ctx, user, mode, recents, title, timeout=30)
        else:
            title = f"Most recent osu! {mode:f} play for **{user.username}**"
            embed = OsuScoreSingleEmbed(ctx, recents[0])
            await embed.prepare()
            await ctx.send(title, embed=embed)

    async def osu_beatmap_scores_command(
        self,
        ctx: commands.Context,
        username: Optional[str],
        mode: aiosu.models.Gamemode,
        beatmap: aiosu.models.Beatmap,
    ) -> None:
        user = await OsuUserConverter().convert(ctx, username, mode)
        scores = await self.bot.client_v1.get_beatmap_scores(
            beatmap.id,
            user_query=user.id,
            qtype="id",
            mode=mode,
            include_beatmap=True,
        )
        if not scores:
            await ctx.send(f"User **{user.username}** has no plays on the beatmap!")
            return

        title = f"osu! {beatmap.mode:f} plays for {user.username}"
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
        username: Optional[str],
    ) -> None:
        await ctx.defer()

        try:
            beatmap = await self.bot.beatmap_service.get_one(ctx.channel.id)
        except ValueError:
            await ctx.send("No beatmap found to compare to.")
            return

        await self.osu_beatmap_scores_command(
            ctx,
            username,
            beatmap.mode,
            beatmap,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="scores",
        aliases=["s"],
        description="Sends osu! scores for a user on a beatmap",
    )
    @app_commands.describe(
        beatmap="URL or ID of the beatmap",
        username="Discord/osu! username or mention",
    )
    async def osu_scores_command(
        self,
        ctx: commands.Context,
        beatmap: str,
        username: Optional[str],
        *,
        flags: OsuScoreFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode
        beatmap_data = get_beatmap_from_text(beatmap)
        if (beatmap_id := beatmap_data["beatmap_id"]) is None:
            await ctx.send("Unknown beatmap ID specified.")
            return

        beatmap = await self.bot.client_v1.get_beatmap(beatmap_id=beatmap_id, mode=mode)
        await self.bot.beatmap_service.add(ctx.channel.id, beatmap)

        await self.osu_beatmap_scores_command(
            ctx,
            username,
            mode,
            beatmap,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="pp",
        description="Shows information about pp of a certain map",
    )
    @app_commands.describe(
        beatmap="URL or ID of the beatmap",
    )
    async def osu_perf_command(
        self,
        ctx: commands.Context,
        beatmap: Optional[str],
        *,
        flags: OsuScoreFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode

        if beatmap:
            beatmap_data = get_beatmap_from_text(beatmap)
            if (beatmap_id := beatmap_data["beatmap_id"]) is None:
                await ctx.send("Unknown beatmap ID specified.")
                return
            beatmap = await self.bot.client_v1.get_beatmap(
                beatmap_id=beatmap_id,
                mode=mode,
            )
            await self.bot.beatmap_service.add(ctx.channel.id, beatmap)
        else:
            beatmap = await self.bot.beatmap_service.get_one(ctx.channel.id)
            if beatmap is None:
                await ctx.send("No beatmap found in cache.")
                return

        await ctx.send("This command is still WIP.")


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OsuCog(bot))
    await bot.add_cog(OsuProfileCog(bot))
    await bot.add_cog(OsuTopsCog(bot))
