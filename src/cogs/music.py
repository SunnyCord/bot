###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import math
from typing import Literal

import pomice
from classes.bot import Sunny
from classes.cog import MetadataGroupCog
from classes.exceptions import MusicPlayerError
from classes.pomice import Player
from common.humanizer import milliseconds_to_duration
from discord import app_commands
from discord.ext import commands
from ui.embeds.music import MusicPlaylistEmbed
from ui.embeds.music import MusicTrackEmbed
from ui.menus.music import MusicQueueView


def is_privileged(ctx: commands.Context) -> bool:
    """Check whether the user is allowed to bypass requirements."""
    player: Player = ctx.voice_client

    return player.dj == ctx.author or ctx.author.guild_permissions.kick_members


class Music(MetadataGroupCog, name="music"):
    """
    Commands for music playback.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot
        self.pomice = bot.pomice_node_pool

    def required(self, ctx: commands.Context) -> int:
        """Get required number of votes based on channel members"""
        player: Player = ctx.voice_client
        channel = self.bot.get_channel(player.channel.id)
        required = math.ceil((len(channel.members) - 1) / 2.5)

        if ctx.command.name == "stop":
            if len(channel.members) == 3:
                required = 2

        return required

    @MetadataGroupCog.listener()
    async def on_pomice_track_end(self, player: Player, track: pomice.Track, _) -> None:
        if player.queue.is_empty:
            await player.teardown()
            return
        await player.do_next()

    @MetadataGroupCog.listener()
    async def on_pomice_track_stuck(
        self,
        player: Player,
        track: pomice.Track,
        _,
    ) -> None:
        await player.do_next()

    @MetadataGroupCog.listener()
    async def on_pomice_track_exception(
        self,
        player: Player,
        track: pomice.Track,
        _,
    ) -> None:
        await player.do_next()

    async def ensure_voice(self, ctx: commands.Context) -> None:
        """Ensure voice state."""
        does_not_require_voice = ctx.command.name in ("autodisconnect",)
        should_connect = ctx.command.name in ("play",)
        player: Player | None = ctx.voice_client

        if does_not_require_voice:
            return

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise MusicPlayerError("Join a voice channel first!")

        if not player or not player.is_connected:
            if not should_connect:
                raise MusicPlayerError("Not connected.")

            await ctx.author.voice.channel.connect(
                cls=Player,
                self_deaf=True,
            )
            player: Player = ctx.voice_client

            await player.set_volume(20)
            await player.set_context(ctx=ctx)
            return

        if player.channel.id != ctx.author.voice.channel.id:
            raise MusicPlayerError("You are not in my voice channel.")

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """Ensure voice state."""
        await self.ensure_voice(ctx)

    @commands.hybrid_command(
        name="play",
        aliaes=["p"],
        description="Searches for and plays a song",
    )
    @app_commands.describe(query="URL or keywords for searching")
    async def play_command(self, ctx: commands.Context, *, query: str) -> None:
        player: Player = ctx.voice_client

        await ctx.defer()
        results = await player.get_tracks(query, ctx=ctx)

        if not results:
            await ctx.send("Nothing found!")
            return

        if isinstance(results, pomice.Playlist):
            embed = MusicPlaylistEmbed(ctx, results.tracks)
            for track in results.tracks:
                player.queue.put(track)
        else:
            track = results[0]
            embed = MusicTrackEmbed(ctx, track, title="Added to queue")
            player.queue.put(track)

        if not player.is_playing:
            await player.do_next()
            return

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="playing",
        aliases=["np"],
        description="Shows the current track",
    )
    async def playing_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if not player.current:
            await ctx.send("Nothing is playing!")
            return

        await ctx.send(embed=MusicTrackEmbed(ctx, player.current))

    @commands.hybrid_command(
        name="queue",
        aliases=["q"],
        description="Shows the current queue",
    )
    async def queue_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if player.queue.is_empty:
            await ctx.send("Queue is empty!")
            return

        queue = player.queue.get_queue()
        await MusicQueueView.start(ctx, queue)

    @commands.hybrid_command(
        name="recommend",
        description="Recommends a track based on the current track",
    )
    async def recommend_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if not player.current:
            await ctx.send("Nothing is playing!")
            return

        results = await player.get_recommendations(track=player.current, ctx=ctx)

        if not results:
            await ctx.send("Nothing found!")
            return

        await MusicQueueView.start(ctx, results, title="Recommended tracks")

    @commands.hybrid_command(
        name="seek",
        description="Seeks to a position in the current track",
    )
    @app_commands.describe(position="Position to seek to (in seconds)")
    async def seek_command(self, ctx: commands.Context, position: int) -> None:
        player: Player = ctx.voice_client

        if not player.current:
            await ctx.send("Nothing is playing!")
            return

        if not player.current.is_seekable:
            await ctx.send("You cannot seek this track!")
            return

        position *= 1000

        if is_privileged(ctx):
            await player.seek(position)
            await ctx.send(
                f"⏭ | An admin or DJ has seeked the player to {milliseconds_to_duration(player.position)}.",
            )
            return

        if ctx.author == player.current.requester:
            await player.seek(position)
            await ctx.send(
                f"⏭ | The song requester has seeked the player to {milliseconds_to_duration(player.position)}.",
            )
            return

        await ctx.send("⏭ | You are not allowed to seek the player.")

    @commands.hybrid_command(
        name="pause",
        description="Pauses the current track",
    )
    async def pause_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if player.is_paused:
            await ctx.send("⏯ | Track is already paused.", delete_after=10)

        if is_privileged(ctx):
            await ctx.send("⏯ | An admin or DJ has paused the player.", delete_after=10)
            player.pause_votes.clear()

            await player.set_pause(True)
            return

        required = self.required(ctx)
        player.pause_votes.add(ctx.author)

        if len(player.pause_votes) >= required:
            await ctx.send("⏯ | Vote to pause passed. Pausing player.", delete_after=10)
            player.pause_votes.clear()
            await player.set_pause(True)
            return

        await ctx.send(
            f"⏯ | {ctx.author.mention} has voted to pause the player. Votes: {len(player.pause_votes)}/{required}",
            delete_after=15,
        )

    @commands.hybrid_command(
        name="resume",
        description="Resumes the current track",
    )
    async def resume_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if not player.is_paused:
            await ctx.send("⏯ | Track is not paused.", delete_after=10)

        if is_privileged(ctx):
            await ctx.send(
                "⏯ | An admin or DJ has resumed the player.",
                delete_after=10,
            )
            player.resume_votes.clear()

            await player.set_pause(False)
            return

        required = self.required(ctx)
        player.resume_votes.add(ctx.author)

        if len(player.resume_votes) >= required:
            await ctx.send(
                "⏯ | Vote to resume passed. Resuming player.",
                delete_after=10,
            )
            player.resume_votes.clear()
            await player.set_pause(False)
            return

        await ctx.send(
            f"⏯ | {ctx.author.mention} has voted to resume the player. Votes: {len(player.resume_votes)}/{required}",
            delete_after=15,
        )

    @commands.hybrid_command(
        name="skip",
        description="Skips the currently playing track",
    )
    async def skip_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if is_privileged(ctx):
            await ctx.send("⏭ | An admin or DJ has skipped the song.", delete_after=10)
            player.skip_votes.clear()

            await player.stop()
            return

        if ctx.author == player.current.requester:
            await ctx.send(
                "⏭ | The song requester has skipped the song.",
                delete_after=10,
            )
            player.skip_votes.clear()

            await player.stop()
            return

        required = self.required(ctx)
        player.skip_votes.add(ctx.author)

        if len(player.skip_votes) >= required:
            await ctx.send("⏭ | Vote to skip passed. Skipping song.", delete_after=10)
            player.skip_votes.clear()
            await player.stop()
            return

        await ctx.send(
            f"⏭ | {ctx.author.mention} has voted to skip the song. Votes: {len(player.skip_votes)}/{required} ",
            delete_after=15,
        )

    @commands.hybrid_command(
        name="shuffle",
        description="Shuffle the player queue",
    )
    async def shuffle_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if player.queue.count < 3:
            await ctx.send(
                "There aren't enough songs for me to shuffle!",
                delete_after=15,
            )
            return

        if is_privileged(ctx):
            await ctx.send(
                "🔀 | An admin or DJ has shuffled the queue.",
                delete_after=10,
            )
            player.shuffle_votes.clear()
            return player.queue.shuffle()

        required = self.required(ctx)
        player.shuffle_votes.add(ctx.author)

        if len(player.shuffle_votes) >= required:
            await ctx.send(
                "🔀 | Vote to shuffle passed. Shuffling the queue.",
                delete_after=10,
            )
            player.shuffle_votes.clear()
            player.queue.shuffle()
            return

        await ctx.send(
            f"🔀 | {ctx.author.mention} has voted to shuffle the queue. Votes: {len(player.shuffle_votes)}/{required}",
            delete_after=15,
        )

    @commands.hybrid_command(
        name="volume",
        description="Changes the playback volume",
    )
    @app_commands.describe(volume="Volume percentage")
    async def volume_command(
        self,
        ctx: commands.Context,
        volume: commands.Range[int, 1, 100],
    ) -> None:
        player: Player = ctx.voice_client

        if not is_privileged(ctx):
            await ctx.send(
                "🔈 | Only the DJ or admins may change the volume",
                delete_after=10,
            )
            return

        await player.set_volume(volume)
        await ctx.send(f"🔈 | Set to {volume}%", delete_after=10)

    @commands.hybrid_command(
        name="nightcore",
        description="uguu~~",
    )
    async def nightcore_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if not is_privileged(ctx):
            await ctx.send("🎶 | Only the DJ or admins may have fun", delete_after=10)
            return

        enabled = player.filters.has_filter(filter_tag="nightcore")
        if enabled:
            await player.remove_filter("nightcore", fast_apply=True)
            await ctx.send("🎶 | Nightcore mode disabled!")
            return

        nightcore = pomice.Timescale.nightcore()
        await player.add_filter(nightcore, fast_apply=True)
        await ctx.send("🎶 | Nightcore mode enabled!", delete_after=10)

    @commands.hybrid_command(
        name="vaporwave",
        description="aesthetic",
    )
    async def vaporwave_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if not is_privileged(ctx):
            await ctx.send("🎶 | Only the DJ or admins may have fun", delete_after=10)
            return

        enabled = player.filters.has_filter(filter_tag="vaporwave")
        if enabled:
            await player.remove_filter("vaporwave", fast_apply=True)
            await ctx.send("🎶 | Ｖａｐｏｒｗａｖｅ mode disabled!", delete_after=10)
            return

        vaporwave = pomice.Timescale.vaporwave()
        await player.add_filter(vaporwave, fast_apply=True)
        await ctx.send("🎶 | Ｖａｐｏｒｗａｖｅ mode enabled!", delete_after=10)

    @commands.hybrid_command(
        name="lowpass",
        description="Suppresses high frequencies",
    )
    @app_commands.describe(strength="Strength of the lowpass filter")
    async def lowpass_command(
        self,
        ctx: commands.Context,
        strength: commands.Range[float, 0, 100],
    ) -> None:
        player: Player = ctx.voice_client

        if not is_privileged(ctx):
            await ctx.send("🎶 | Only the DJ or admins may have fun", delete_after=10)
            return

        enabled = player.filters.has_filter(filter_tag="lowpass")
        if enabled:
            await player.remove_filter("lowpass", fast_apply=True)

        if strength == 0:
            await ctx.send("🎶 | Lowpass filter disabled", delete_after=10)
            return

        lowpass = pomice.LowPass(tag="lowpass", smoothing=strength)
        await player.add_filter(lowpass, fast_apply=True)
        await ctx.send(
            f"🎶 | Lowpass filter enabled with strength {strength}%",
            delete_after=10,
        )

    @commands.hybrid_command(
        name="vibrato",
        description="Vibrato effect",
    )
    async def vibrato_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if not is_privileged(ctx):
            await ctx.send("🎶 | Only the DJ or admins may have fun", delete_after=10)
            return

        enabled = player.filters.has_filter(filter_tag="vibrato")
        if enabled:
            await player.remove_filter("vibrato", fast_apply=True)
            await ctx.send("🎶 | Vibrato effect disabled!", delete_after=10)
            return

        vibrato = pomice.Vibrato(tag="vibrato", frequency=10, depth=1)
        await player.add_filter(vibrato, fast_apply=True)
        await ctx.send("🎶 | Vibrato effect enabled!", delete_after=10)

    @commands.hybrid_command(
        name="clearfilters",
        description="Clears all filters",
    )
    async def clear_filters_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if not is_privileged(ctx):
            await ctx.send("🎶 | Only the DJ or admins may have fun", delete_after=10)
            return

        await player.reset_filters()
        await ctx.send("🎶 | Filters cleared!", delete_after=10)

    @commands.hybrid_command(
        name="loop",
        description="Sets the loop mode for the player",
    )
    @app_commands.describe(loop_mode="Loop mode")
    async def loop_command(
        self,
        ctx: commands.Context,
        loop_mode: Literal["OFF", "TRACK", "QUEUE"],
    ) -> None:
        player: Player = ctx.voice_client

        if not is_privileged(ctx):
            await ctx.send(
                "🔁 | Only the DJ or admins may change the loop mode",
                delete_after=10,
            )
            return

        if loop_mode == "OFF":
            player.disable_loop()
            await ctx.send("🔁 | Loop mode disabled", delete_after=10)
            return

        await player.set_loop_mode(pomice.LoopMode[loop_mode])
        await ctx.send(f"🔁 | Loop mode set to {loop_mode}", delete_after=10)

    @commands.hybrid_command(
        name="stop",
        aliases=["disconnect", "dc"],
        description="Stops playing and clears the queue" "",
    )
    async def disconnect_command(self, ctx: commands.Context) -> None:
        player: Player = ctx.voice_client

        if is_privileged(ctx):
            await ctx.send(
                "*⃣ | An admin or DJ has stopped the player.",
                delete_after=10,
            )
            await player.teardown()
            return

        required = self.required(ctx)
        player.stop_votes.add(ctx.author)

        if len(player.stop_votes) >= required:
            await ctx.send(
                "*⃣ | Vote to stop passed. Stopping the player.",
                delete_after=10,
            )
            await player.teardown()
            return

        await ctx.send(
            f"*⃣ | {ctx.author.mention} has voted to stop the player. Votes: {len(player.stop_votes)}/{required}",
            delete_after=15,
        )

    @commands.hybrid_command(
        name="autodisconnect",
        description="Toggles voice channel auto-disconnect",
    )
    @commands.has_permissions(manage_guild=True)
    async def auto_disconnect_command(self, ctx: commands.Context) -> None:
        value = await self.bot.guild_settings_service.toggle_auto_disconnect(
            ctx.guild.id,
        )
        await ctx.send(
            f"🔌 | Auto-disconnect is now {'enabled' if value else 'disabled'}",
        )


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Music(bot))
