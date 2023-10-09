###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import asyncio
from contextlib import suppress
from enum import Enum
from typing import Literal
from typing import TYPE_CHECKING

import aiosu
import discord
from aiordr.models import RenderAddEvent
from aiordr.models import RenderCreateResponse
from aiordr.models import RenderFailEvent
from aiordr.models import RenderFinishEvent
from aiordr.models import RenderProgressEvent
from classes import osudle
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
from models.user import UserConverterDTO
from models.user_preferences import RecordingPreferences
from ui.embeds.osu import OsuDifficultyEmbed
from ui.embeds.osu import OsuLinkEmbed
from ui.embeds.osu import OsuProfileCompactEmbed
from ui.embeds.osu import OsuProfileExtendedEmbed
from ui.embeds.osu import OsuRenderEmbed
from ui.embeds.osu import OsuScoreSingleEmbed
from ui.menus.osu import OsuScoresView
from ui.menus.osu import OsuSkinsView

if TYPE_CHECKING:
    from io import BytesIO
    from typing import Any
    from classes.bot import Sunny


class OsuProfileFlags(commands.FlagConverter, prefix="-"):  # type: ignore
    lazer: bool | None = commands.Flag(
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
    lazer: bool | None = commands.Flag(
        description="Whether to use the lazer client",
        default=None,
    )


class OsuScoreFlags(commands.FlagConverter):
    mode: aiosu.models.Gamemode | None = commands.Flag(
        aliases=["m"],
        description="The osu! mode to search for",
        default=None,
    )
    lazer: bool | None = commands.Flag(
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
        description="Whether to use the lazer client",
        default=None,
    )


class OsuRecordFlags(commands.FlagConverter):
    beatmap_query: str | None = commands.Flag(
        aliases=["b"],
        description="URL or ID of the beatmap. Can be provided instead of replay_file",
        default=None,
    )
    username: str | None = commands.Flag(
        aliases=["u"],
        description="Discord/osu! username or mention. Optional, defaults to author",
        default=None,
    )
    mode: aiosu.models.Gamemode | None = commands.Flag(
        aliases=["m"],
        description="The osu! mode to search for. Optional, defaults to the user's main mode",
        default=None,
    )
    lazer: bool | None = commands.Flag(
        description="Whether to use the lazer client. Optional, defaults to the user's lazer preference",
        default=None,
    )


class UserConverter(commands.Converter):
    async def convert(
        self,
        ctx: commands.Context,
        raw_user: str,
    ) -> discord.Member | None:
        """
        Converts to a ``discord.Member`` (case-insensitive)

        The lookup strategy is as follows (in order):
        1. Lookup by commands.MemberConverter()
        2. Lookup by string
        """
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

        return member


class OsuUserConverter(commands.Converter):
    async def convert(self, ctx: commands.Context, *args: Any) -> UserConverterDTO:
        """
        Converts to an ``aiosu.models.User`` (case-insensitive)

        The lookup strategy is as follows (in order):

        1. Lookup author's profile
        2. Lookup by Discord member
        3. Lookup by osu! query
        """
        raw_user, mode, lazer = args
        client, author_client = None, None
        if lazer is None:
            lazer = await ctx.bot.user_prefs_service.get_lazer(ctx.author.id)

        client_storage: aiosu.v2.ClientStorage = (
            ctx.bot.lazer_storage if lazer else ctx.bot.stable_storage
        )

        params = {}
        if mode is not None:
            params["mode"] = mode

        with suppress(aiosu.exceptions.InvalidClientRequestedError):
            author_client = await client_storage.get_client(id=ctx.author.id)

        if raw_user is None:  # Get author profile
            if author_client is None:
                raise aiosu.exceptions.InvalidClientRequestedError()
            return UserConverterDTO(
                client=author_client,
                author_client=author_client,
                lazer=lazer,
                is_app_client=False,
                user=await author_client.get_me(**params),
            )

        member = await UserConverter().convert(ctx, raw_user)
        if member is not None:  # Get member profile
            with suppress(aiosu.exceptions.InvalidClientRequestedError):
                client = await client_storage.get_client(id=member.id)
                return UserConverterDTO(
                    client=client,
                    author_client=author_client,
                    lazer=lazer,
                    is_app_client=False,
                    user=await client.get_me(**params),
                )

        client = await client_storage.app_client  # Get lookup profile
        try:
            return UserConverterDTO(
                client=client,
                author_client=author_client,
                lazer=lazer,
                is_app_client=True,
                user=await client.get_user(raw_user, **params),
            )
        except aiosu.exceptions.APIException:
            if member is not None:  # Failed to get member profile
                raise aiosu.exceptions.InvalidClientRequestedError()
            raise  # Failed to get lookup profile


class OsuProfileCog(MetadataGroupCog, name="profile", display_parent="osu!"):
    """
    osu! Profile Commands
    """

    __slots__ = ("bot",)

    args_description = {
        "user": "Discord/osu! username or mention",
    }

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    async def get_graph(
        self,
        user: aiosu.models.User,
        mode_id: int,
        lazer: bool,
    ) -> BytesIO:
        try:
            graph = await self.bot.graph_service.get_one(user.id, mode_id, lazer)
        except ValueError:
            graph = await self.bot.run_blocking(graphing.plot_rank_graph, user)
            await self.bot.graph_service.add(user.id, graph, mode_id, lazer)
        return graph

    async def osu_profile_command(
        self,
        ctx: commands.Context,
        username: str | None,
        mode: aiosu.models.Gamemode,
        flags: OsuProfileFlags,
    ) -> None:
        await ctx.defer()
        user_data = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )
        if flags.extended:
            embed = OsuProfileExtendedEmbed(ctx, user_data.user, mode, user_data.lazer)
        else:
            embed = OsuProfileCompactEmbed(ctx, user_data.user, mode, user_data.lazer)
        graph = await self.get_graph(user_data.user, int(mode), user_data.lazer)
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

    __slots__ = ("bot",)

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
        user_data = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        client, user = user_data.client, user_data.user

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
            await OsuScoresView.start(ctx, user, mode, tops, title)
            return

        if flags.position > len(tops):
            await ctx.send(
                f"User **{safe_username}** has no top play at position {flags.position}!",
            )
            return

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
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuTopFlags,
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
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuTopFlags,
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
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuTopFlags,
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
        self,
        ctx: commands.Context,
        user: str | None,
        *,
        flags: OsuTopFlags,
    ) -> None:
        await self.osu_top_command(ctx, user, aiosu.models.Gamemode.CTB, flags)


TOGGLEABLE_SETTINGS = Literal[
    "show_hit_error_meter",
    "show_unstable_rate",
    "show_score",
    "show_hp_bar",
    "show_combo_counter",
    "show_pp_counter",
    "show_key_overlay",
    "show_scoreboard",
    "show_borders",
    "show_mods",
    "show_result_screen",
    "show_danser_logo",
    "show_hit_counter",
    "show_aim_error_meter",
    "use_beatmap_colors",
    "objects_rainbow",
    "cursor_rainbow",
    "cursor_trail",
    "cursor_trail_glow",
    "cursor_scale_to_cs",
    "draw_follow_points",
    "draw_combo_numbers",
    "load_storyboard",
    "load_video",
    "play_nightcore_samples",
]

VOLUME_SETTINGS = Literal[
    "global",
    "music",
    "hitsound",
]

DIM_SETTINGS = Literal[
    "intro",
    "ingame",
    "break",
]


class OsuRecordSettingsCog(
    MetadataGroupCog,
    name="recordsettings",
    display_parent="osu!",
):
    """
    osu! Record Settings Commands
    """

    __slots__ = ("bot",)

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="show",
        description="Shows your osu! record settings",
    )
    async def osu_record_show_command(
        self,
        interaction: discord.Interaction,
    ) -> None:
        settings = await self.bot.recording_prefs_service.get_safe(interaction.user.id)

        settings_dict = settings.model_dump(exclude={"discord_id"})
        settings_str = ""
        # 3 items per line
        for i, (key, value) in enumerate(settings_dict.items()):
            if i % 3 == 0:
                settings_str += "\n"
            if isinstance(value, Enum):
                value = value.value
            settings_str += f"{key}: {value}, "

        settings_str = settings_str.rstrip(", ")

        await interaction.response.send_message(
            f"Your osu! record settings are:\n```prolog{settings_str}```",
            ephemeral=True,
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="skins",
        description="Show the available skins",
    )
    @app_commands.describe(
        search="The search query",
    )
    async def osu_record_skins_command(
        self,
        interaction: discord.Interaction,
        search: str | None,
    ) -> None:
        params = {
            "page_size": 35,
        }
        if search:
            params["search"] = search

        settings = await self.bot.recording_prefs_service.get_safe(interaction.user.id)

        skins = await self.bot.ordr_client.get_skins(**params)
        if len(skins.skins) == 0:
            await interaction.response.send_message(
                "No skins found.",
                ephemeral=True,
                delete_after=10,
            )
            return

        await OsuSkinsView.start(
            interaction,
            skins.skins,
            content=f"Current skin: **{settings.skin}**",
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="toggle",
        description="Toggles a setting",
    )
    @app_commands.describe(
        setting="The setting to toggle",
    )
    async def osu_record_toggle_command(
        self,
        interaction: discord.Interaction,
        setting: TOGGLEABLE_SETTINGS,
    ) -> None:
        value = await self.bot.recording_prefs_service.toggle_option(
            interaction.user.id,
            setting,
        )
        setting_name = setting.replace("_", " ").title()
        await interaction.response.send_message(
            f"**{setting_name}** is now **{'enabled' if value else 'disabled'}**.",
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="volume",
        description="Changes the volume used for recording",
    )
    @app_commands.describe(
        setting="The volume to change",
        value="The new value",
    )
    async def osu_record_volume_command(
        self,
        interaction: discord.Interaction,
        setting: VOLUME_SETTINGS,
        value: app_commands.Range[int, 0, 100],
    ) -> None:
        await self.bot.recording_prefs_service.set_option(
            interaction.user.id,
            f"{setting}_volume",
            value,
        )
        await interaction.response.send_message(
            f"**{setting.title()}** volume is now **{value}**.",
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="dim",
        description="Changes the background dim used for recording",
    )
    @app_commands.describe(
        setting="The dim to change",
        value="The new value",
    )
    async def osu_record_dim_command(
        self,
        interaction: discord.Interaction,
        setting: DIM_SETTINGS,
        value: app_commands.Range[int, 0, 100],
    ) -> None:
        await self.bot.recording_prefs_service.set_option(
            interaction.user.id,
            f"{setting}_bg_dim",
            value,
        )
        await interaction.response.send_message(
            f"**{setting.title()}** dim is now **{value}**.",
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @app_commands.command(
        name="cursorsize",
        description="Changes the cursor size used for recording",
    )
    @app_commands.describe(
        value="The new value",
    )
    async def osu_record_cursorsize_command(
        self,
        interaction: discord.Interaction,
        value: app_commands.Range[float, 0.5, 2.0],
    ) -> None:
        await self.bot.recording_prefs_service.set_option(
            interaction.user.id,
            "cursor_size",
            value,
        )
        await interaction.response.send_message(f"**Cursor Size** is now **{value}**.")


class OsudleCog(MetadataGroupCog, name="osudle"):
    """
    osu!dle guessing game
    """

    __slots__ = (
        "bot",
        "running_games",
    )

    args_description = {
        "mode": "The osu! gamemode to get beatmaps from",
    }

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.running_games: dict[int, osudle.BaseOsudleGame] = {}

    async def start_game(
        self,
        interaction: discord.Interaction,
        mode: aiosu.models.Gamemode,
        game: osudle.BaseOsudleGame,
    ) -> None:
        channel = interaction.channel

        if channel.id in self.running_games:
            await interaction.response.send_message(
                f"A game is already running in {channel}",
            )
            return

        self.running_games[channel.id] = game

        try:
            await game.start_game(interaction, mode)
        except asyncio.TimeoutError:
            del self.running_games[channel.id]

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(
        name="song",
        description="Starts a new game based on beatmap preview audio",
    )
    @app_commands.describe(**args_description)
    async def osudle_song_command(
        self,
        interaction: discord.Interaction,
        mode: aiosu.models.Gamemode = aiosu.models.Gamemode.STANDARD,
    ) -> None:
        await self.start_game(
            interaction,
            mode,
            osudle.OsudleSongGame(),
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(
        name="background",
        description="Starts a new game based on beatmap backgrounds",
    )
    @app_commands.describe(**args_description)
    async def osudle_background_command(
        self,
        interaction: discord.Interaction,
        mode: aiosu.models.Gamemode = aiosu.models.Gamemode.STANDARD,
    ) -> None:
        await self.start_game(
            interaction,
            mode,
            osudle.OsudleBackgroundGame(),
        )

    @commands.cooldown(1, 2, commands.BucketType.user)
    @app_commands.command(
        name="skip",
        description="Skips the current beatmap",
    )
    async def osudle_skip_command(
        self,
        interaction: discord.Interaction,
    ) -> None:
        channel = interaction.channel

        if channel.id not in self.running_games:
            await interaction.response.send_message("No game is running.")
            return

        self.running_games[channel.id].interaction = interaction
        try:
            await self.running_games[channel.id].do_next()
        except asyncio.TimeoutError:
            del self.running_games[channel.id]

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(
        name="stop",
        description="Stops the current game",
    )
    async def osudle_stop_command(
        self,
        interaction: discord.Interaction,
    ) -> None:
        channel = interaction.channel

        if channel.id not in self.running_games:
            await interaction.response.send_message("No game is running.")
            return

        self.running_games[channel.id].interaction = interaction
        await self.running_games[channel.id].stop_game()
        del self.running_games[channel.id]


class OsuCog(MetadataCog, name="osu!"):
    """
    osu! related commands.
    """

    __slots__ = ("bot", "config_v2")

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.config_v2 = self.bot.config.osu_api

    @commands.command(
        name="osuset",
        aliases=["link"],
        hidden=True,
    )
    async def legacy_osu_set_command(
        self,
        ctx: commands.Context,
    ) -> None:
        await ctx.send("Please use the `/osuset` command instead.")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @app_commands.command(
        name="osuset",
        description="Sets the osu! profile for the message author",
    )
    async def osu_set_command(
        self,
        interaction: discord.Interaction,
    ) -> None:
        url = aiosu.utils.auth.generate_url(
            client_id=self.config_v2.client_id,
            redirect_uri=self.config_v2.redirect_uri,
            state=encode_discord_id(interaction.user.id, self.bot.aes),
        )
        await interaction.response.send_message(
            embed=OsuLinkEmbed(interaction, url),
            ephemeral=True,
        )

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
        user_data = await OsuUserConverter().convert(ctx, username, mode, flags.lazer)

        client, user = user_data.client, user_data.user

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
            await OsuScoresView.start(ctx, user, mode, recents, title)
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
        user_data = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            lazer,
        )

        client, user, lazer = user_data.client, user_data.user, user_data.lazer

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
            try:
                beatmap = await self.bot.beatmap_service.get_one(ctx.channel.id)
            except ValueError:
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
        pp: commands.Range[float, 0, 10000],
        username: str | None,
        *,
        flags: OsuPPFlags,
    ) -> None:
        await ctx.defer()
        mode = flags.mode

        user_data = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        user, client = user_data.user, user_data.client

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

        new_rank = await self.bot.osu_daily_client.get_closest_rank(
            final + bonus,
            mode.id,
        )

        await ctx.send(
            f"**{safe_username}** would gain **{final - initial:.2f}pp** if they got a **{pp:.2f}pp** score, bringing them up to **{final + bonus:.2f}pp** (**#{new_rank}**).",
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.hybrid_command(
        name="ppforrank",
        description="Shows pp required for a certain rank",
    )
    @app_commands.describe(
        rank="Rank to calculate required pp for",
        mode="The osu! mode to search for",
    )
    async def osu_pp_for_rank_command(
        self,
        ctx: commands.Context,
        rank: commands.Range[int, 1, 1000000],
        mode: aiosu.models.Gamemode = aiosu.models.Gamemode.STANDARD,
    ) -> None:
        await ctx.defer()

        pp = await self.bot.osu_daily_client.get_closest_pp(rank, mode.id)

        await ctx.send(
            f"**{pp:.2f}pp** is required for **#{rank}** in **{mode.name_full}**.",
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

        user_data = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        user, client = user_data.user, user_data.client

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
            f"{safe_username} has a bonus of **{bonus:.2f}pp** from submitted scores.",
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

        user_data = await OsuUserConverter().convert(
            ctx,
            username,
            mode,
            flags.lazer,
        )

        user, client = user_data.user, user_data.client

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

    async def record_from_file(
        self,
        ctx: commands.Context,
        recording_prefs: RecordingPreferences,
        replay_file: discord.Attachment,
    ) -> RenderCreateResponse:
        if not replay_file.filename.endswith(".osr"):
            await ctx.send("You must upload a valid .osr file.")
            return

        render_options = recording_prefs.get_render_options()
        return await self.bot.ordr_client.create_render(
            username=ctx.author.name,
            skin=recording_prefs.skin,
            replay_url=replay_file.url,
            render_options=render_options,
        )

    async def record_from_flags(
        self,
        ctx: commands.Context,
        recording_prefs: RecordingPreferences,
        flags: OsuRecordFlags,
    ) -> RenderCreateResponse:
        if flags.beatmap_query is None:
            await ctx.send("You must specify a beatmap ID or a beatmap link.")
            return

        beatmap_ids = get_beatmap_from_text(flags.beatmap_query)

        beatmap_id = beatmap_ids.get("beatmap_id")
        if beatmap_id is None:
            await ctx.send(
                "You must specify a valid beatmap ID or a beatmap link.",
            )
            return

        user_data = await OsuUserConverter().convert(
            ctx,
            flags.username,
            flags.mode,
            flags.lazer,
        )

        user = user_data.user
        client = user_data.client
        if user_data.is_app_client:
            if not user_data.author_client:
                raise aiosu.exceptions.InvalidClientRequestedError()
            client = user_data.author_client

        mode = flags.mode or user.playmode

        scores = await client.get_user_beatmap_scores(
            user.id,
            beatmap_id,
            mode=mode,
        )

        if not scores:
            await ctx.send("No scores found on this beatmap.")
            return

        score = scores[0]

        replay_file = await client.get_score_replay(score.id, mode)
        render_options = recording_prefs.get_render_options()

        return await self.bot.ordr_client.create_render(
            username=ctx.author.name,
            skin=recording_prefs.skin,
            replay_url=replay_file.url,
            render_options=render_options,
        )

    @commands.cooldown(1, 300, commands.BucketType.user)
    @commands.hybrid_command(
        name="record",
        description="Records a score",
    )
    @app_commands.describe(
        replay_file="Replay file. Optional, if provided other arguments will be ignored",
    )
    async def osu_record_command(
        self,
        ctx: commands.Context,
        replay_file: discord.Attachment | None,
        *,
        flags: OsuRecordFlags,
    ) -> None:
        await ctx.defer()

        client = self.bot.ordr_client
        recording_prefs = await self.bot.recording_prefs_service.get_safe(ctx.author.id)

        if replay_file is not None:
            render = await self.record_from_file(ctx, recording_prefs, replay_file)
        else:
            render = await self.record_from_flags(ctx, recording_prefs, flags)

        if render is None:
            return

        message = await ctx.send("Starting render...")

        @client.on_render_added
        async def render_added(event: RenderAddEvent) -> None:
            if event.render_id == render.render_id:
                await message.edit(
                    content=None,
                    embed=OsuRenderEmbed(ctx, "Rendering...", ""),
                )

        @client.on_render_progress
        async def render_progress(event: RenderProgressEvent) -> None:
            if event.render_id == render.render_id:
                await message.edit(
                    content=None,
                    embed=OsuRenderEmbed(ctx, event.description, event.progress),
                )

        @client.on_render_finish
        async def render_finish(event: RenderFinishEvent) -> None:
            if event.render_id == render.render_id:
                await message.edit(
                    content=f"Render finished! {event.video_url}",
                    embed=None,
                )

        @client.on_render_fail
        async def render_fail(event: RenderFailEvent) -> None:
            if event.render_id == render.render_id:
                await message.edit(content="Render failed!", embed=None)


async def setup(bot: Sunny) -> None:
    await bot.add_cog(OsuCog(bot))
    await bot.add_cog(OsuProfileCog(bot))
    await bot.add_cog(OsuTopsCog(bot))
    await bot.add_cog(OsuRecordSettingsCog(bot))
    await bot.add_cog(OsudleCog(bot))
