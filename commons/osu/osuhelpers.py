from commons.osu import osuClasses

def getModeInfo(invoke):
    
    if invoke in ["osu", "osutop", "ot"]:
        return osuClasses.Mode()

    if invoke in ["taiko", "taikotop", "tt"]:
        return osuClasses.Mode(id=1)

    if invoke in ["ctb", "ctbtop", "ct"]:
        return osuClasses.Mode(id=2)

    if invoke in ["mania", "maniatop", "mt"]:
        return osuClasses.Mode(id=3)

    return osuClasses.Mode()

def parseArgs(**kwargs):

    args = kwargs.pop("args")
    validArgs = kwargs.pop("validArgs") if 'validArgs' in kwargs else []

    qtype = "string"
    server = 'bancho'
    mode = 0
    position = None
    recentList = False

    args = args.split(" ")
    
    if '-bancho' in args:
        args.pop(args.index('-bancho'))

    if '-ripple' in args:
        server = 'ripple'
        args.pop(args.index('-ripple'))

    if '-akatsukirx' in args:
        server = 'akatsukirx'
        args.pop(args.index('-akatsukirx'))

    if '-akatsuki' in args:
        server = 'akatsuki'
        args.pop(args.index('-akatsuki'))

    if '-enjuu' in args:
        server = 'enjuu'
        args.pop(args.index('-enjuu'))

    if '-r' in args and '-r' in validArgs:
        recentList = True
        args.pop(args.index('-r'))

    if '-l' in args and '-l' in validArgs:
        recentList = True
        args.pop(args.index('-l'))

    if '-m' not in args:
        mode = 0

    elif '-m' in validArgs:
        try:
            mode = int(args[args.index('-m') + 1])
            args.pop(args.index('-m') + 1)
        except Exception:
            mode = 0
        args.pop(args.index('-m'))

    if '-p' in validArgs and '-p' in args:
        try:
            position = int(args[args.index('-p') + 1])
            args.pop(args.index('-p') + 1)
        except Exception:
            position = 0
        args.pop(args.index('-p'))

    user = ' '.join(args)

    parsedArgs = {
        'qtype': qtype,
        'mode': mode,
        'server': server,
        'recentList': recentList,
        'user': user,
        'position': position
    }

    return parsedArgs

def getMods(number):
    mod_list= []
    if number == 0:	mod_list.append('NM')
    if number & 1<<0:   mod_list.append('NF')
    if number & 1<<1:   mod_list.append('EZ')
    if number & 1<<2:   mod_list.append('TD')
    if number & 1<<3:   mod_list.append('HD')
    if number & 1<<4:   mod_list.append('HR')
    if number & 1<<14:  mod_list.append('PF')
    elif number & 1<<5:   mod_list.append('SD')
    if number & 1<<9:   mod_list.append('NC')
    elif number & 1<<6: mod_list.append('DT')
    if number & 1<<7:   mod_list.append('RX')
    if number & 1<<8:   mod_list.append('HT')
    if number & 1<<10:  mod_list.append('FL')
    if number & 1<<12:  mod_list.append('SO')
    if number & 1<<15:  mod_list.append('4K')
    if number & 1<<16:  mod_list.append('5K')
    if number & 1<<17:  mod_list.append('6K')
    if number & 1<<18:  mod_list.append('7K')
    if number & 1<<19:  mod_list.append('8K')
    if number & 1<<20:  mod_list.append('FI')
    if number & 1<<24:  mod_list.append('9K')
    if number & 1<<25:  mod_list.append('10K')
    if number & 1<<26:  mod_list.append('1K')
    if number & 1<<27:  mod_list.append('3K')
    if number & 1<<28:  mod_list.append('2K')
    return ''.join(mod_list)