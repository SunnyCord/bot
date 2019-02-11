def stdCalc(count0: int, count50: int, count100: int, count300: int):
    accuracy = round(float((50*count50+100*count100+300*count300)/(300*(count0+count50+count100+count300))*100), 2)
    return accuracy

def maniaCalc(count0: int, count50: int, count100: int, count200: int, count300: int, countmax: int):
    accuracy = round(float((50*count50+100*count100+200*count200+300*(count300+countmax))/(300*(count0+count50+count100+count200+count300+countmax))*100), 2)
    return accuracy

def ctbCalc(count0drop: int, count0fruit: int, countdroplet: int, countdrop: int, countfruit: int):
    accuracy = round(float((countdroplet + countdrop + countfruit)/(count0drop+count0fruit+countdroplet+countdrop+countfruit)*100), 2)
    return accuracy

def taikoCalc(countbad: int, countgood: int, countgreat: int):
    accuracy = round(float((countgood/2 + countgreat) / (countbad + countgood + countgreat)*100), 2)
    return accuracy
