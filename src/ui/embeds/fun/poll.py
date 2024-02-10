###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

import random
from typing import TYPE_CHECKING

from ui.embeds.generic import ContextAuthorEmbed

if TYPE_CHECKING:
    from typing import Any

    from discord.ext.commands import Context

poll_images = [
    "https://i.imgur.com/t1OssGQ.gif",
    "https://i.imgur.com/rq3QKdT.gif",
    "https://i.imgur.com/oKXjDX0.png",
    "https://i.imgur.com/F74SdLm.png",
    "https://i.imgur.com/f4t0sE9.gif",
    "https://i.imgur.com/j2YSiXV.png",
    "https://i.imgur.com/0ZNpgim.png",
    "https://i.imgur.com/OvyoPJx.png",
    "https://i.imgur.com/UXV5P4M.png",
    "https://i.imgur.com/uYctlHl.png",
    "https://i.imgur.com/uko36bU.png",
    "https://i.imgur.com/fJOVzvd.png",
    "https://i.imgur.com/WQOLAnX.gif",
    "https://i.imgur.com/1aBQtFA.png",
    "https://i.imgur.com/oaEjRop.png",
    "https://i.imgur.com/SUEQfWS.gif",
]


class PollEmbed(ContextAuthorEmbed):
    def __init__(self, ctx: Context, text: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            ctx,
            title="Poll",
            description=text,
            timestamp=ctx.message.created_at,
            *args,
            **kwargs,
        )
        self.set_thumbnail(url=random.choice(poll_images))
