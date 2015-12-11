import minesweeper, minesweeperAgent, random

def main():
    random.seed()
    numGames = 10
    boardSize = 10
    mines = 10
    gamesWon = 0
    boardLocs = []
    for i in range(boardSize):
        for j in range(boardSize):
            if (i,j) != (0,0):
                boardLocs.append((i,j))
    for game in range(numGames):
        mineLocs = random.sample(boardLocs, mines)
        board = minesweeper.Board(boardSize,mineLocs)
        print 'The solution should look like this:\n'
        board.printBoard()
        mineAI = minesweeperAgent.minesweeperAgent()
        result = mineAI.solve(boardSize, mines, board)
        if result:
            gamesWon += 1
        if game % 100 == 0:
            print game
    winRate =float(gamesWon)/numGames
    print 'You won %d games out of %d with a win rate of %.4s'%(gamesWon,numGames,winRate)
main()
exit(0)