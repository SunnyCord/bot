###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from models.guild_settings import GuildSettings
from repository.guild_settings import GuildSettingsRepository


class GuildSettingsService:
    """Guild Settings Service"""

    def __init__(self, repository: GuildSettingsRepository) -> None:
        self.repository = repository

    async def get_one(self, guild_id: int) -> GuildSettings:
        """Get guild settings from database.

        Args:
            guild_id (int): Guild ID.

        Raises:
            ValueError: Settings not found.

        Returns:
            GuildSettings: Guild settings.
        """
        return await self.repository.get_one(guild_id)

    async def get_safe(self, guild_id: int) -> GuildSettings:
        """Get guild settings from database.

        Args:
            guild_id (int): Guild ID.

        Returns:
            GuildSettings: Guild settings.
        """
        try:
            return await self.repository.get_one(guild_id)
        except ValueError:
            return GuildSettings(guild_id=guild_id)

    async def get_many(self) -> list[GuildSettings]:
        """Get all guild settings from database.

        Returns:
            list[GuildSettings]: List of guild settings.
        """
        return await self.repository.get_many()

    async def add(self, guild_settings: GuildSettings) -> None:
        """Add new guild settings to database.

        Args:
            guild_settings (GuildSettings): Guild settings.
        """
        await self.repository.add(guild_settings)

    async def update(self, guild_settings: GuildSettings) -> None:
        """Update guild settings.

        Args:
            guild_settings (GuildSettings): Guild settings.
        """
        await self.repository.update(guild_settings)

    async def delete(self, guild_id: int) -> None:
        """Delete guild settings.

        Args:
            guild_id (int): Guild ID.
        """
        await self.repository.delete(guild_id)

    async def create(self, guild_id: int) -> GuildSettings:
        """Create default settings for guild.

        Args:
            guild_id (int): Guild ID.

        Returns:
            GuildSettings: Guild settings.
        """
        settings = GuildSettings(guild_id=guild_id)
        await self.add(settings)
        return settings

    async def get_prefix(self, guild_id: int) -> str:
        """Get guild prefix.

        Args:
            guild_id (int): Guild ID.

        Returns:
            str: Guild prefix.
        """
        settings = await self.get_safe(guild_id)
        return settings.prefix

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        """Set guild prefix.

        Args:
            guild_id (int): Guild ID.
            prefix (str): Guild prefix.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            settings = await self.create(guild_id)

        settings.prefix = prefix
        await self.update(settings)

    async def clear_prefix(self, guild_id: int) -> None:
        """Clear guild prefix.

        Args:
            guild_id (int): Guild ID.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            return

        settings.prefix = ""
        await self.update(settings)

    async def get_listener_status(self, guild_id: int) -> bool:
        """Get listener status.

        Args:
            guild_id (int): Guild ID.

        Returns:
            bool: Listener status.
        """
        settings = await self.get_safe(guild_id)
        return settings.use_listeners

    async def toggle_listener(self, guild_id: int) -> bool:
        """Toggle listener status.

        Args:
            guild_id (int): Guild ID.

        Returns:
            bool: Listener status.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            settings = await self.create(guild_id)

        settings.use_listeners = not settings.use_listeners
        await self.update(settings)
        return settings.use_listeners

    async def get_auto_disconnect_status(self, guild_id: int) -> bool:
        """Get auto disconnect status.

        Args:
            guild_id (int): Guild ID.

        Returns:
            bool: Auto disconnect status.
        """
        settings = await self.get_safe(guild_id)
        return settings.voice_auto_disconnect

    async def toggle_auto_disconnect(self, guild_id: int) -> bool:
        """Toggle auto disconnect status.

        Args:
            guild_id (int): Guild ID.

        Returns:
            bool: Auto disconnect status.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            settings = await self.create(guild_id)

        settings.voice_auto_disconnect = not settings.voice_auto_disconnect
        await self.update(settings)
        return settings.voice_auto_disconnect

    async def set_dj_role(self, guild_id: int, role_id: int) -> None:
        """Set DJ role.

        Args:
            guild_id (int): Guild ID.
            role_id (int): Role ID.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            settings = await self.create(guild_id)

        settings.dj_role = role_id
        await self.update(settings)

    async def get_premium_booster(self, guild_id: int) -> int:
        """Get premium booster.

        Args:
            guild_id (int): Guild ID.

        Returns:
            int: Booster ID.
        """
        settings = await self.get_safe(guild_id)
        return settings.booster

    async def set_premium_booster(self, guild_id: int, booster_id: int) -> None:
        """Set premium booster.

        Args:
            guild_id (int): Guild ID.
            booster_id (int): Booster ID.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            settings = await self.create(guild_id)

        settings.booster = booster_id
        await self.update(settings)

    async def remove_premium_booster(self, guild_id: int) -> None:
        """Remove premium booster.

        Args:
            guild_id (int): Guild ID.
        """
        try:
            settings = await self.get_one(guild_id)
        except ValueError:
            return

        settings.booster = None
        await self.update(settings)

    async def get_user_boosts(self, user_id: int) -> list[int]:
        """Get all guilds boosted by user.

        Args:
            user_id (int): User ID.

        Returns:
            list[int]: List of guild IDs.
        """
        return await self.repository.get_user_boosts(user_id)

    async def get_user_boosts_count(self, user_id: int) -> int:
        """Get user boosts count.

        Args:
            user_id (int): User ID.

        Returns:
            int: Boosts count.
        """
        return await self.repository.get_user_boosts_count(user_id)

    async def get_all_boosted_guilds(self) -> list[int]:
        """Get all guilds that are boosted.

        Returns:
            list[int]: List of guild IDs.
        """
        return await self.repository.get_all_boosted_guilds()
