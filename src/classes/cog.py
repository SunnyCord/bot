from __future__ import annotations

from discord.ext.commands import Cog
from discord.ext.commands import GroupCog
from typing_extensions import Self


class MetadataCog(Cog):
    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args)
        cls.hidden: bool = kwargs.pop("hidden", False)
        cls.display_parent: str = kwargs.pop("display_parent", None)


class MetadataGroupCog(GroupCog):
    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args)
        cls.hidden: bool = kwargs.pop("hidden", False)
        cls.display_parent: str = kwargs.pop("display_parent", None)
