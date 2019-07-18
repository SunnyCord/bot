
class Mode:

    def __init__(self, **kwargs):

        __modeDict = [
            {
                'id': 0,
                'icon': 'https://i.imgur.com/lT2nqls.png',
                'name': 'Standard',
                'nameShort': 'STD'
            },
            {
                'id': 1,
                'icon': 'https://i.imgur.com/G6bzM0X.png',
                'name': 'Taiko',
                'nameShort': 'T'
            },
            {
                'id': 2,
                'icon': 'https://i.imgur.com/EsanYkH.png',
                'name': 'Catch the Beat',
                'nameShort': 'CTB'
            },
            {
                'id': 3,
                'icon': 'https://i.imgur.com/0uZM1PZ.png',
                'name': 'Mania',
                'nameShort': 'M'
            }

        ]

        __idArg = kwargs.pop ('id', 0)

        self.id = __modeDict[__idArg]['id']
        self.icon = __modeDict[__idArg]['icon']
        self.name = __modeDict[__idArg]['name']
        self.nameShort = __modeDict[__idArg]['nameShort']

class Server:

    def __init__(self, **kwargs):

        __serverDict = [
            {
                'id': 0,
                'icon': 'https://i.imgur.com/0aZpJjl.png',
                'name': 'Bancho'
            },
            {
                'id': 1,
                'icon': 'https://i.imgur.com/l4tTouZ.png',
                'name': 'Ripple'
            },
            {
                'id': 2,
                'icon': 'https://i.imgur.com/ic7kEkO.png',
                'name': 'Akatsuki'
            },
            {
                'id': 3,
                'icon': 'https://i.imgur.com/ic7kEkO.png',
                'name': 'Akatsuki Relax'
            },
            {
                'id': 4,
                'icon': 'https://i.imgur.com/OO6MrW7.png',
                'name': 'enjuu'
            },
            {
                'id': 5,
                'icon': 'https://i.imgur.com/IAkYdrI.png',
                'name': 'Gatari'
            }

        ]


        __osuServers = {
            'bancho': 0,
            'ripple': 1,
            'akatsuki': 2,
            'akatsukirx': 3,
            'enjuu': 4,
            'gatari': 5
        }

        __idArg = kwargs.pop ('id', None)
        __queryString = kwargs.pop('string', None)

        if __idArg is None:

            if __queryString is None:
                __idArg = 0

            else:

                try:
                    __idArg = __osuServers[__queryString]

                except KeyError:
                    __idArg = 0

        self.id = __serverDict[__idArg]['id']
        self.icon = __serverDict[__idArg]['icon']
        self.name = __serverDict[__idArg]['name']
