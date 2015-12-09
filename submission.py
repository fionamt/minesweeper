import collections, util, copy, minesweeper, minesweeperAgent, random

def main():
    random.seed()
    numGames = 5
    n = 16
    mines = 40
    gamesWon = 0
    boardLocs = []
    for i in range(n):
        for j in range(n):
            if (i,j) != (0,0):
                boardLocs.append((i,j))
    for game in range(numGames):
        mineLocs = random.sample(boardLocs, mines)
        board = minesweeper.Board(n,mineLocs)
        mineAI = minesweeperAgent.minesweeperAgent()
        result = mineAI.solve(n, mines, board)
        if result:
            gamesWon += 1
        if game % 100 == 0:
            print game
    winRate =float(gamesWon)/numGames
    print 'You won %d games out of %d with a win rate of %.4s'%(gamesWon,numGames,winRate)
main()
exit(0)