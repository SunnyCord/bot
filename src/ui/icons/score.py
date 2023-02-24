from __future__ import annotations

from enum import Enum


class ScoreRankIcon(Enum):
    F = "<:rankingF:1078460449525346464>"
    D = "<:rankingD:1078459098519048273>"
    C = "<:rankingC:1078459097348837466>"
    B = "<:rankingB:1078459096128303134>"
    A = "<:rankingA:1078459093309722654>"
    S = "<:rankingS:1078459102843375656>"
    SH = "<:rankingSH:1078459101383770193>"
    SHD = "<:rankingSH:1078459101383770193>"
    X = "<:rankingX:1078459252835893328>"
    XH = "<:rankingXH:1078459105297051648>"
    XHD = "<:rankingXH:1078459105297051648>"
    SS = "<:rankingX:1078459252835893328>"
    SSH = "<:rankingXH:1078459105297051648>"
    SSHD = "<:rankingXH:1078459105297051648>"

    def __str__(self) -> str:
        return self.icon

    @property
    def icon(self) -> str:
        return self.value
