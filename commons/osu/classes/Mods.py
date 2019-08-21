import commons.osu.classes as osu

class Mods:
    def __init__(self, mods):
        self._mod_list:list = []
        for mod in list(osu.Mod):
            if type(mods) is str and mod.short_name in mods or type(mods) is int and int(mod) & mods:
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
            result += mod.short_name
        return result