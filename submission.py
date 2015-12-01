import collections, util, copy, minesweeper, minesweeperAgent

def main():
    n = 2
    mines = 3
    board = minesweeper.Board(5,[(2,2)])
    board.printBoard()
    mineAI = minesweeperAgent.minesweeperAgent()
    mineAI.solve(5, 1, board)
main()
