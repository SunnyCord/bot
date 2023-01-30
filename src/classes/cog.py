from __future__ import annotations

from typing import Any

from discord.ext.commands import Cog
from discord.ext.commands import GroupCog


class MetadataCog(Cog):
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args)
        cls.hidden = kwargs.pop("hidden", False)
        cls.display_parent = kwargs.pop("display_parent", None)


class MetadataGroupCog(GroupCog):
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args)
        cls.hidden = kwargs.pop("hidden", False)
        cls.display_parent = kwargs.pop("display_parent", None)
