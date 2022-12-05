from __future__ import annotations

import abc
from typing import TYPE_CHECKING

from discord.ext import commands
from discord.ui import View

if TYPE_CHECKING:
    from typing import Any


class BaseView(View, abc.ABC):
    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
        await self.message.edit(view=self)

    @classmethod
    async def start(cls, ctx: commands.Context, *args: Any, **kwargs: Any) -> View:
        view = cls(ctx, *args, **kwargs)
        await view.initial.prepare()
        view.message = await ctx.send(embed=view.initial, view=view)
        return view
