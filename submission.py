import collections, util, copy, minesweeper, minesweeperAgent

def main():
    n = 2
    mines = 3
    board = minesweeper.Board(5,[(2,2),(2,3),(1,4),(0,3)])
    board.printBoard()
    mineAI = minesweeperAgent.minesweeperAgent()
    mineAI.solve(5, 4, board)
main()
