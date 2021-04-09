from enum import Enum

class Animal(Enum):
    CAT = ('Cat', '🐈')
    DOG = ('Dog', '🐕')
    FOX = ('Fox', '🦊')
    BIRD = ('Bird', '🐦')
    BIRB = BIRD # Required alias for the API
    DUCK = ('Duck', '🦆')
    PANDA = ('Panda', '🐼')
    KOALA = ('Koala', '🐨')

    def __init__(self, display_name:str, icon:str):
        self.display_name = display_name
        self.icon = icon

    @staticmethod
    def from_name(param:str) -> 'Animal':
        return Animal[param.upper()]

    @classmethod
    def list(cls):
        return list(map(lambda c: c.display_name.lower(), cls))