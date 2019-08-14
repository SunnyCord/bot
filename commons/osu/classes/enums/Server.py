from enum import Enum

class Server(Enum):
    BANCHO = (0, 'https://i.imgur.com/0aZpJjl.png')
    RIPPLE = (1, 'https://i.imgur.com/l4tTouZ.png')
    AKATSUKI = (2, 'https://i.imgur.com/ic7kEkO.png')
    AKATSUKIRX = (3, 'https://i.imgur.com/ic7kEkO.png')
    ENJUU = (4, 'https://i.imgur.com/OO6MrW7.png')
    GATARI = (5, 'https://i.imgur.com/IAkYdrI.png')

    def __init__(self, id:int, icon:str):
        self.__id = id
        self.__icon = icon

    # Maybe there is a better way to provide public members for an enum
    @property
    def id(self) -> str:
        return self.__id

    @property
    def icon(self) -> str:
        return self.__icon

    @staticmethod
    def fromName(param:str) -> 'Server':
        if param.startswith('-'):
            param = param[1:]
        
        for server in list(Server):
            if server.name.lower() == param.lower():
                return server
