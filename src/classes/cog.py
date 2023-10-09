###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from typing import Any

from discord.ext.commands import Cog
from discord.ext.commands import GroupCog


class MetadataCog(Cog):
    __slots__ = ("hidden", "display_parent")

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args)
        cls.hidden: bool = kwargs.pop("hidden", False)
        cls.display_parent: str | None = kwargs.pop("display_parent", None)


class MetadataGroupCog(GroupCog):
    __slots__ = ("hidden", "display_parent")

    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        super().__init_subclass__(*args)
        cls.hidden: bool = kwargs.pop("hidden", False)
        cls.display_parent: str | None = kwargs.pop("display_parent", None)
