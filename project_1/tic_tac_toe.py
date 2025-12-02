"""Tic-tac-toe in console
"""
import numpy as np
import os

clear = lambda: os.system('cls')

PlayingField = []
WinLines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]

def clearPlayingField():
    """Clear playing feild
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
    """Print playing feild
    Args:
        None
    Returns:
        None
    """
    
    strNum = 0
    clear()
    print('  |',0,1,2)
    print('__|_______')
    for string in PlayingField:
        print(strNum,'|',*string)
        strNum += 1
        
def setXO(sym:str, x:int, y:int) -> bool:
    """Set Х or О to playing field
    Args:
        sym (str): Symbol (X or O)
        x (int): coord by horizon
        y (int): coord by vertical
    Returns:
        Boolean
    """
    if PlayingField[int(x)][int(y)] not in ['X', 'O']:
        PlayingField[int(x)][int(y)] = sym
        return True
    return False

def checkForWin(sym: str) -> bool:
    """Check for win
    Args:
        sym (str): 'X' or 'O'
    Returns:
        Boolean
    """
    PlayingLine = np.array(sum(PlayingField, []))
    for i in WinLines:
        if PlayingLine[i[0]] == PlayingLine[i[1]] == PlayingLine[i[2]] == sym:
            print(f'Победа {sym}!')
            return True
    if len(np.where(PlayingLine == '-')[0]) == 0:
        print('Ничья!')
        return True
    return False

def doTurn(sym: str):
    """Do turn by "AI"
    Args:
        sym (str): 'X' or 'O'
    Returns:
        None
    """
    Antysym = 'O' if sym == 'X' else 'X'
    PlayingLine = np.array(sum(PlayingField, []))
    Pos = int(np.random.choice(np.where(PlayingLine == '-')[0]))
    Result = [Pos // 3, Pos % 3]
    for WinLine in WinLines:
        rowSym = list(filter(lambda item: item == sym, PlayingLine[WinLine]))
        rowAntysym = list(filter(lambda item: item == Antysym, PlayingLine[WinLine]))
        Index = np.where(PlayingLine[WinLine] == '-')[0]
        if len(rowAntysym) == 2 and len(Index) == 1:
            Pos = WinLine[Index[0]]
            Result = [Pos // 3, Pos % 3]
        if len(rowSym) == 2 and len(Index) == 1:
            Pos = WinLine[Index[0]]
            Result = [Pos // 3, Pos % 3]
    setXO(sym, *Result)
    printPlayingField()
                
def start():
    """Perform main cycle
    Args:
        None
    Returns:
        None
    """
    sym = 'X'
    playerSym = 'X'
    players = int(input('1 или 2 игрока? ')) or 1
    if players == 1: 
        if input('X или O? ') in ['O','o','0','О','о']: 
            playerSym = 'O'
        else: 
            playerSym = 'X' 
    clearPlayingField()    
    printPlayingField()
    while True:    
        if sym == playerSym or players > 1:
            try:
                if setXO(sym, *str(input(f'Куда поставить {sym} (x y): ')).split()):
                    printPlayingField()
                    winer = checkForWin(sym)
                    if winer: break
                    sym = 'O' if sym == 'X' else 'X'
                else:
                    print('Клетка занята.')
                    continue
            except Exception as e:
                print('Не удалось распознать координаты.', e)
                continue
        if players == 1:
            doTurn(sym)
            winer = checkForWin(sym)
            if winer: break
            sym = 'O' if sym == 'X' else 'X'
        

if __name__ == '__main__':
    start()