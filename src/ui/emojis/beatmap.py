from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import aiosu


class BeatmapDifficultyIcon(Enum):
    EASY_0 = "<:easy_0:601433333565751299>"
    EASY_1 = "<:easy_1:601433689989185556>"
    EASY_2 = "<:easy_2:601433993337896979>"
    EASY_3 = "<:easy_3:601434398474108929>"
    NORMAL_0 = "<:normal_0:601433401265881109>"
    NORMAL_1 = "<:normal_1:601433753570508800>"
    NORMAL_2 = "<:normal_2:601434111575457793>"
    NORMAL_3 = "<:normal_3:601434449993007114>"
    HARD_0 = "<:hard_0:601433454860697631>"
    HARD_1 = "<:hard_1:601433808704634890>"
    HARD_2 = "<:hard_2:601434207515967633>"
    HARD_3 = "<:hard_3:601434538421256194>"
    INSANE_0 = "<:insane_0:601433508677943326>"
    INSANE_1 = "<:insane_1:601433854892310538>"
    INSANE_2 = "<:insane_2:601434269910564865>"
    INSANE_3 = "<:insane_3:601434670449819658>"
    EXTRA_0 = "<:extra_0:601433587761545239>"
    EXTRA_1 = "<:extra_1:601433898395762696>"
    EXTRA_2 = "<:extra_2:601434330920910874>"
    EXTRA_3 = "<:extra_3:601434717287350302>"
    EXPERT_0 = "<:expert_0:659557929028026380>"
    EXPERT_1 = "<:expert_1:659557929174958082>"
    EXPERT_2 = "<:expert_2:659557929070100502>"
    EXPERT_3 = "<:expert_3:659557929698983987>"

    def __init__(self, icon: str) -> None:
        self.icon: str = icon

    @classmethod
    def get_from_sr(
        cls,
        sr: float,
        mode: aiosu.classes.Gamemode,
    ) -> BeatmapDifficultyIcon:
        if sr < 2:
            return cls[f"EASY_{mode.id}"]
        if sr < 2.7:
            return cls[f"NORMAL_{mode.id}"]
        if sr < 4:
            return cls[f"HARD_{mode.id}"]
        if sr < 5.3:
            return cls[f"INSANE_{mode.id}"]
        if sr < 6.5:
            return cls[f"EXTRA_{mode.id}"]
        return cls[f"EXPERT_{mode.id}"]
