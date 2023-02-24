from __future__ import annotations

from enum import Enum


class GamemodeIcon(Enum):
    STANDARD = "https://i.imgur.com/SlBf7z2.png"
    TAIKO = "https://i.imgur.com/Rk5iWCi.png"
    CTB = "https://i.imgur.com/DGg9KDE.png"
    MANIA = "https://i.imgur.com/KZggy59.png"

    def __str__(self) -> str:
        return self.value

    @property
    def icon(self) -> str:
        return self.value
