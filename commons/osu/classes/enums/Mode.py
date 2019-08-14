from enum import Enum

class Mode(Enum):
    STANDARD = (0, 'https://i.imgur.com/lT2nqls.png', 'Standard', 'STD')
    TAIKO = (1, 'https://i.imgur.com/G6bzM0X.png', 'Taiko', 'T')
    CTB = (2, 'https://i.imgur.com/EsanYkH.png', 'Catch the Beat', 'CTB')
    MANIA = (3, 'https://i.imgur.com/0uZM1PZ.png', 'Mania', 'M')
    
    def __init__(self, id:int, icon:str, nameFull:str, nameShort:str):
        self.__id = id
        self.__icon = icon
        self.__nameFull = nameFull
        self.__nameShort = nameShort


    # Maybe there is a better way to provide public members for an enum
    @property
    def id(self) -> str:
        return self.__id

    @property
    def icon(self) -> str:
        return self.__icon

    @property
    def nameFull(self) -> str:
        return self.__nameFull 

    @property        
    def nameShort(self) -> str:
        return self.__nameShort

    @staticmethod
    def fromId(id) -> 'Mode':
        if type(id) is not 'int':
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
