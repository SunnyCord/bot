from enum import Enum
class BeatmapStatus(Enum):
    GRAVEYARD = -2
    WIP = -1
    PENDING = 0
    RANKED = 1
    APPROVED = 2
    QUALIFIED = 3
    LOVED = 4