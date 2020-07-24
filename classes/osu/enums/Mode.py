from enum import Enum

class Mode(Enum):
    STANDARD = (0, 'https://i.imgur.com/lT2nqls.png', 'Standard', 'STD')
    TAIKO = (1, 'https://i.imgur.com/G6bzM0X.png', 'Taiko', 'T')
    CTB = (2, 'https://i.imgur.com/EsanYkH.png', 'Catch the Beat', 'CTB')
    MANIA = (3, 'https://i.imgur.com/0uZM1PZ.png', 'Mania', 'M')

    def __init__(self, id:int, icon:str, name_full:str, name_short:str):
        self.id:int = id
        self.icon:str = icon
        self.name_full:str = name_full
        self.name_short:str = name_short

    def __int__(self):
        return self.id

    @staticmethod
    def fromId(id) -> 'Mode':
        if not isinstance(id, int):
            id = int(id)

        for mode in list(Mode):
            if mode.id == id:
                return mode

    @staticmethod
    def fromCommand(command) -> 'Mode':
        if command in ["osu", "osutop", "ot"]:
            return Mode.STANDARD

        if command in ["taiko", "taikotop", "tt"]:
            return Mode.TAIKO

        if command in ["ctb", "ctbtop", "ct"]:
            return Mode.CTB

        if command in ["mania", "maniatop", "mt"]:
            return Mode.MANIA
