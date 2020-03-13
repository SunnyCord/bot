import classes.osu as osu

class Mods:
    def __init__(self, mods):
        self._mod_list:list = []

        if isinstance(mods, str):
            mods = mods.upper()
            for i in range(0, len(mods), 2):
                mod_str:str = mods[i:i+2]
                mod:osu.Mod = osu.Mod.get_by_short_name(mod_str)
                if mod is not None and mod not in self._mod_list:
                    self._mod_list.append(mod)

        if isinstance(mods, int):
            for mod in list(osu.Mod):
                if int(mod) & mods:
                    self._mod_list.append(mod)

    def __int__(self):
        result:int = 0
        for mod in self._mod_list:
            result += mod.bitmask
        return result

    def __str__(self):
        if len(self._mod_list) == 0:
            return "NM"

        result:str = ""
        for mod in self._mod_list:
            if osu.Mod.Nightcore in self._mod_list and mod is osu.Mod.DoubleTime:
                continue
            if osu.Mod.Perfect in self._mod_list and mod is osu.Mod.SuddenDeath:
                continue

            result += mod.short_name
        return result