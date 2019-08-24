from enum import Enum

class Mod(Enum):
    """Bitwise Flags representing osu! mods.
    Notes
    -----
    .. code:: python
        # Check if a given flag is set.
        OsuMod.HardRock in flags
        # Check if a given flag is not set.
        OsuMod.HardRock not in flags
        # Check if all given flags are set.
        flags.contains_all(OsuMod.Hidden | OsuMod.HardRock)
        # Check if any of given flags are set.
        OsuMod.keyMod in flags
    """
    NoMod = (0, "")
    NoFail = (1, "NF")
    Easy = (2, "EZ")
    TouchDevice = (4, "TD")
    Hidden = (8, "HD")
    HardRock = (16, "HR")
    SuddenDeath = (32, "SD")
    DoubleTime = (64, "DT")
    Relax = (128, "RX")
    HalfTime = (256, "HT")
    Nightcore = (512, "NC")  # Only set along with DoubleTime. i.e: NC only gives 576
    Flashlight = (1024, "FL")
    Autoplay = (2048, "")
    SpunOut = (4096, "SO")
    Autopilot = (8192, "AP")  # Called Relax2 on osu api documentation
    Perfect = (16384, "PF")  # Only set along with SuddenDeth. i.e: PF only gives 16416
    Key4 = (32768, "4K")
    Key5 = (65536, "5K")
    Key6 = (131072, "6K")
    Key7 = (262144, "7K")
    Key8 = (524288, "8K")
    FadeIn = (1048576, "FI")
    Random = (2097152, "RD")
    LastMod = (4194304)
    Key9 = (16777216, "9K")
    Key10 = (33554432, "10K")
    Key1 = (67108864, "1K")
    Key3 = (134217728, "3K")
    Key2 = (268435456, "2K")

    def __init__(self, value, short_name=""):
        self.bitmask = value
        self.short_name = short_name

    def __int__(self):
        return self.bitmask

    def __format__(self, format_spec):
        """Format an OsuMod.
        Formats
        -------
        s
            short_name e.g. HDHR
        l
            long_name e.g. Hidden HardRock"""
        if format_spec == "s":
            return self.short_name
        elif format_spec == "l":
            return self.long_name
        else:
            return self.__str__()

    @classmethod
    def get_by_short_name(cls, mod_str):
        for mod in list(Mod):
            if mod.short_name == mod_str:
                return mod
        return None