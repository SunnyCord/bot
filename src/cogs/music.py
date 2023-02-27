from __future__ import annotations

import math
from typing import Optional
from typing import TYPE_CHECKING

import aiohttp
import classes.exceptions as Exceptions
import discord
import lavalink
from commons.regex import track_title_rx
from commons.regex import url_rx
from discord import app_commands
from discord.ext import commands
from lavalink.filters import LowPass

if TYPE_CHECKING:
    from typing import Any
    from classes.bot import Sunny


class LavalinkVoiceClient(discord.VoiceClient):
    """
    This is the preferred way to handle external voice sending
    This client will be created via a cls in the connect method of the channel
    see the following documentation:
    https://discordpy.readthedocs.io/en/latest/api.html#voiceprotocol
    """

    def __init__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable,
    ) -> None:
        self.client = client
        self.channel = channel
        # ensure a client already exists
        if hasattr(self.client, "lavalink"):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            for node in client.config.lavalink:
                self.client.lavalink.add_node(
                    node.host,
                    node.port,
                    node.password,
                    node.region,
                    node.name,
                )
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data: Any) -> None:
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_SERVER_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data: Any) -> None:
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_STATE_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(
        self,
        *,
        timeout: float,
        reconnect: bool,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        """
        Connect the bot to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(
            channel=self.channel,
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that would set channel_id
        # to None doesn't get dispatched after the disconnect
        player.channel_id = None
        self.cleanup()


class Music(commands.GroupCog, name="music"):  # type: ignore
    """
    Commands related to music playback.
    """

    def __init__(self, bot: Sunny) -> None:
        self.bot = bot

        # This ensures the client isn't overwritten during cog reloads.
        if not hasattr(bot, "lavalink"):
            bot.lavalink = lavalink.Client(bot.user.id)
            for node in bot.config.lavalink:
                bot.lavalink.add_node(
                    node.host,
                    node.port,
                    node.password,
                    node.region,
                    node.name,
                )

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self) -> None:
        """Cog unload handler. This removes any event hooks that were registered."""
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx: commands.Context) -> None:
        """Command before-invoke handler."""
        await self.ensure_voice(ctx)
        #  Ensure that the bot and command author share a mutual voicechannel.

    async def ensure_voice(self, ctx: commands.Context) -> None:
        # TODO replace this with a suitable solution for slash commands
        """This check ensures that the bot and command author are in the same voicechannel."""
        player = self.bot.lavalink.player_manager.create(ctx.guild.id)
        # Create returns a player if one exists, otherwise creates.
        # This line is important because it ensures that a player always exists for a guild.

        # Most people might consider this a waste of resources for guilds that aren't playing, but this is
        # the easiest and simplest way of ensuring players are created.

        # These are commands that require the bot to join a voicechannel (i.e. initiating playback).
        # Commands such as volume/skip etc don't require the bot to be in a voicechannel so don't need listing here.
        should_connect = ctx.command.name in ("play",)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise Exceptions.MusicPlayerError("Join a voicechannel first.")

        v_client = ctx.voice_client
        if not v_client:
            if not should_connect:
                raise Exceptions.MusicPlayerError("Not connected.")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if (
                not permissions.connect or not permissions.speak
            ):  # TODO Check user limit too?
                raise Exceptions.MusicPlayerError(
                    "I need the `CONNECT` and `SPEAK` permissions.",
                )

            player.store("channel", ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
            await player.set_volume(50)
        else:
            if v_client.channel.id != ctx.author.voice.channel.id:
                raise Exceptions.MusicPlayerError("You need to be in my voicechannel.")

    async def track_hook(self, event: lavalink.events.Event) -> None:
        if isinstance(event, lavalink.events.TrackStartEvent):
            # This indicates that a track has started, so we can get track data from genius
            if event.track.duration < 30:
                event.player.delete("currentTrackData")
                return

            cleanTitle = track_title_rx.sub("", event.track.title)

            async with aiohttp.ClientSession() as cs:
                async with cs.get(
                    "https://some-random-api.ml/lyrics",
                    params={"title": cleanTitle},
                ) as r:
                    rawData = await r.json()
                    if "error" in rawData:
                        event.player.delete("currentTrackData")
                        return
                    rawData["cleanTitle"] = cleanTitle
                    event.player.store("currentTrackData", rawData)

        elif isinstance(event, lavalink.events.QueueEndEvent):
            # When this track_hook receives a "QueueEndEvent" from lavalink.py
            # it indicates that there are no tracks left in the player's queue.
            # To save on resources, we can tell the bot to disconnect from the voicechannel.
            guild_id = event.player.guild_id
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

    @commands.hybrid_command(
        name="play",
        description="Searches and plays a song from a given query",
    )
    @app_commands.describe(query="URL or keywords for searching")
    async def play_command(self, ctx: commands.Context, *, query: str) -> None:
        # Get the player for this guild from cache.
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        # Remove leading and trailing <>. <> may be used to suppress embedding links in Discord.
        query = query.strip("<>")

        # Check if the user input might be a URL. If it isn't, we can Lavalink do a YouTube search for it instead.
        # SoundCloud searching is possible by prefixing "scsearch:" instead.
        if not url_rx.match(query):
            query = f"ytsearch:{query}"

        # Get the results for the query from Lavalink.
        results = await player.node.get_tracks(query)

        # Results could be None if Lavalink returns an invalid response (non-JSON/non-200 (OK)).
        # ALternatively, resullts.tracks could be an empty array if the query yielded no tracks.
        if not results or not results.tracks:
            return await ctx.send("Nothing found!")

        embed = discord.Embed(color=self.bot.config.color)

        # Valid loadTypes are:
        #   TRACK_LOADED    - single video/direct URL)
        #   PLAYLIST_LOADED - direct URL to playlist)
        #   SEARCH_RESULT   - query prefixed with either ytsearch: or scsearch:.
        #   NO_MATCHES      - query yielded no results
        #   LOAD_FAILED     - most likely, the video encountered an exception during loading.
        if results.load_type == "PLAYLIST_LOADED":
            tracks = results.tracks

            for track in tracks:
                # Add all of the tracks from the playlist to the queue.
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Enqueued!"
            embed.description = f"{results.playlist_info.name} - {len(tracks)} tracks"
        else:
            track = results.tracks[0]
            embed.title = "Track Enqueued"
            embed.description = f"[{track.title}]({track.uri})"

            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        # We don't want to call .play() if the player is playing as that will effectively skip
        # the current track.
        if not player.is_playing:
            await player.play()

    @commands.hybrid_command(
        name="playing",
        description="Shows the currently playing track",
    )
    async def playing_command(self, ctx: commands.Context) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.current:
            return await ctx.send("Nothing is playing.")

        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = "🔴 LIVE"
        else:
            duration = lavalink.utils.format_time(player.current.duration)
        track = f"**[{player.current.title}]({player.current.uri})**\n({position}/{duration})"

        embed = discord.Embed(
            color=self.bot.config.color,
            title="Now Playing",
            description=track,
        )

        if (currentTrackData := player.fetch("currentTrackData")) != None:
            embed.set_thumbnail(url=currentTrackData["thumbnail"]["genius"])
            embed.description += f"\n[LYRICS]({currentTrackData['links']['genius']}) | [ARTIST](https://genius.com/artists/{currentTrackData['author'].replace(' ', '%20')})"

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="queue", description="Shows the player's queue")
    @app_commands.describe(
        page="Page number for the queue",
    )  # TODO replace this with pagination probably
    async def queue_command(self, ctx: commands.Context, page: int = 1) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        playerQueueWithCurrent = [player.current] + player.queue

        if not playerQueueWithCurrent:
            return await ctx.send("Nothing queued.")

        items_per_page = 10
        pages = math.ceil(len(playerQueueWithCurrent) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ""
        for index, track in enumerate(playerQueueWithCurrent[start:end], start=start):
            queue_list += f"`{index + 1}.` [**{track.title}**]({track.uri})\n"

        embed = discord.Embed(
            colour=self.bot.config.color,
            description=f"**{len(playerQueueWithCurrent)} tracks**\n\n{queue_list}",
        )
        embed.set_footer(text=f"Viewing page {page}/{pages}")
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="volume", description="Changes the bot volume")
    @app_commands.describe(volume="Volume percentage")
    async def volume_command(
        self,
        ctx: commands.Context,
        volume: Optional[commands.Range[int, 1, 100]],
    ) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not volume:
            return await ctx.send(f"🔈 | {player.volume * 2}%")

        await player.set_volume(volume / 2)
        await ctx.send(f"🔈 | Set to {player.volume * 2}%")

    @commands.hybrid_command(name="shuffle", description="Shuffles the player's queue")
    async def shuffle_command(self, ctx: commands.Context) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        player.shuffle = not player.shuffle
        await ctx.send("🔀 | Shuffle " + ("enabled" if player.shuffle else "disabled"))

    @commands.hybrid_command(
        name="loop",
        description="Repeats the current song until the command is invoked again",
    )
    async def repeat_command(self, ctx: commands.Context) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        player.repeat = not player.repeat
        await ctx.send("🔁 | Repeat " + ("enabled" if player.repeat else "disabled"))

    @commands.hybrid_command(
        name="seek",
        description="Seeks to a given position in a track",
    )
    async def seek_command(self, ctx: commands.Context, *, seconds: int) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(f"Moved track to **{lavalink.utils.format_time(track_time)}**")

    @commands.hybrid_command(
        name="pause",
        description="Pauses/Resumes the current track",
    )
    async def pause_command(self, ctx: commands.Context) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing.")

        if player.paused:
            await player.set_pause(False)
            await ctx.send("⏯ | Resumed")
        else:
            await player.set_pause(True)
            await ctx.send("⏯ | Paused")

    @commands.hybrid_command(
        name="skip",
        description="Skips the currently playing track",
    )
    async def skip(self, ctx: commands.Context) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        await player.skip()
        await ctx.send("⏭ | Skipped.")

    @commands.hybrid_command(
        name="lowpass",
        description="Sets the strength of the low pass filter",
    )
    @app_commands.describe(strength="Strength of the low pass filter")
    async def lowpass(
        self,
        ctx: commands.Context,
        strength: commands.Range[float, 0, 100],
    ) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        embed = discord.Embed(color=self.bot.config.color, title="Low Pass Filter")

        if strength == 0.0:
            player.remove_filter("lowpass")
            embed.description = "Disabled **Low Pass Filter**"
            return await ctx.send(embed=embed)

        low_pass = LowPass()
        low_pass.update(smoothing=strength)

        await player.set_filter(low_pass)

        embed.description = f"Set **Low Pass Filter** strength to {strength}."
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="disconnect",
        description="Disconnects the player from the voice channel and clears its queue",
    )
    async def disconnect_command(self, ctx: commands.Context) -> None:
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)

        if not ctx.voice_client:
            return await ctx.send("Not connected.")

        if not ctx.author.voice or (
            player.is_connected
            and ctx.author.voice.channel.id != int(player.channel_id)
        ):
            return await ctx.send("You're not in my voicechannel!")

        # Clear the queue to ensure old tracks don't start playing
        # when someone else queues something.
        player.queue.clear()
        # Stop the current track so Lavalink consumes less resources.
        await player.stop()
        # Disconnect from the voice channel.
        await ctx.voice_client.disconnect(force=True)
        await ctx.send("*⃣ | Disconnected.")


async def setup(bot: Sunny) -> None:
    await bot.add_cog(Music(bot))
