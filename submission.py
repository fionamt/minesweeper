import collections, util, copy, minesweeper, minesweeperAgent

def main():
    n = 2
    mines = 3
    board = minesweeper.Board(n,[(0,1),(1,0),(1,1)])
    board.printBoard()
    mineAI = minesweeperAgent.minesweeperAgent()
    mineAI.solve(n, mines, board)
main()
