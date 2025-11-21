"""Игра крестики-нолики в консоли.
"""
import numpy as np

PlayingField = []

def clearPlayingField():
    """Отчистить игровое поле
    Args:
        None
    Returns:
        None
    """
    global PlayingField
    PlayingField = [['-','-','-'],
                    ['-','-','-'],
                    ['-','-','-']]

def printPlayingField():
    """Отобразить игровое поле
    Args:
        None
    Returns:
        None
    """
    
    strNum = 0
    print(' ',0,1,2)
    for string in PlayingField:
        print(strNum,*string)
        strNum += 1
        
def setXO(sym:str, x:int, y:int):
    """Установить Х или О на игровое поле
    Args:
        sym (str): Символ (крестик или нолик)
        x (int): координата по горизонтали
        y (int): координата по вертикали
    Returns:
        None
    """
    
    PlayingField[int(y)][int(x)] = sym

def check() -> str:
    """Проверить не победил ли один из игроков
    Args:
        None
    Returns:
        'X' or 'O' or None
    """
    
    for i in range(2):
        if PlayingField[i][0] == PlayingField[i][1] == PlayingField[i][2] in ['x', 'o']:
            return PlayingField[i][0]
        if PlayingField[0][i] == PlayingField[1][i] == PlayingField[2][i] in ['x', 'o']:
            return PlayingField[0][i]
    if PlayingField[0][0] == PlayingField[1][1] == PlayingField[2][2] in ['x', 'o']:
            return PlayingField[1][1]
    if PlayingField[0][2] == PlayingField[1][1] == PlayingField[2][0] in ['x', 'o']:
        return PlayingField[1][1]
    
def check_2():
    strCount = len(PlayingField)
    if len(set([PlayingField[i][i] for i in range(strCount)])) == 1 and PlayingField[0][0] in ['x', 'o']:
        return PlayingField[0][0]
    if len(set([PlayingField[i][strCount-i-1] for i in range(strCount)])) == 1 and PlayingField[0][strCount-1] in ['x', 'o']:
        return PlayingField[0][strCount-1]


def start():
    clearPlayingField()    
    printPlayingField()
    sym = 'X'
    while True:
        setXO(sym, *str(input(f'Куда поставить {sym} (x y): ')).split())
        sym = 'O' if sym == 'X' else 'X'
        printPlayingField()
        win = check()
        if win:
            print(f'Победа {win}!')
            break

if __name__ == '__main__':
    start()