###
# Copyright (c) 2023 NiceAesth. All rights reserved.
###
from __future__ import annotations

from inspect import cleandoc
from typing import TYPE_CHECKING

from aiordr.models import Skin
from ui.embeds.generic import InteractionEmbed

if TYPE_CHECKING:
    from discord import Interaction


class OsuSkinEmbed(InteractionEmbed):
    def __init__(self, interaction: Interaction, skin: Skin):
        title = f"{skin.presentation_name} by {skin.author}"
        description = cleandoc(
            f"""
            version: **{skin.version}** | has cursor middle: **{skin.has_cursor_middle}**
            modified: **{skin.modified}** | used **{skin.times_used}** times
            [download]({skin.url})
            """,
        )
        super().__init__(
            interaction,
            title=title,
            description=description,
        )
        self.set_image(url=skin.low_res_preview_url)
