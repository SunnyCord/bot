###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from discord.ui import View
from discord.utils import MISSING

if TYPE_CHECKING:
    from typing import Any
    from discord.ext import commands
    from discord import Interaction


class BaseView(View, abc.ABC):
    async def on_timeout(self) -> None:
        self.clear_items()
        self.stop()
        await self.message.edit(view=self)

    @classmethod
    async def start(cls, ctx: commands.Context, *args: Any, **kwargs: Any) -> View:
        _file = kwargs.pop("file", None)
        _content = kwargs.pop("content", None)
        timeout = kwargs.pop("timeout", 300)
        view = cls(ctx, *args, timeout=timeout, **kwargs)
        await view.initial.prepare()
        view.message = await ctx.send(
            _content,
            embed=view.initial,
            view=view,
            file=_file,
        )
        return view


class BaseInteractionView(View, abc.ABC):
    async def on_timeout(self) -> None:
        self.clear_items()
        self.stop()
        await self.message.edit(view=self)

    @classmethod
    async def start(
        cls,
        interaction: Interaction,
        *args: Any,
        **kwargs: Any,
    ) -> View:
        timeout = kwargs.pop("timeout", 300)
        _file = kwargs.pop("file", MISSING)
        _content = kwargs.pop("content", None)
        view = cls(interaction, *args, timeout=timeout, **kwargs)
        await view.initial.prepare()
        view.message = await interaction.response.send_message(
            _content,
            embed=view.initial,
            view=view,
            file=_file,
        )
        return view
