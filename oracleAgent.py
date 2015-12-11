__author__ = 'Alex'

import collections, util, copy, minesweeper, random, time
from constraint import *
class oracleAgent:
    def __init__(self):
        self.NORMAL_BRUTE_FORCE_CONSTANT = 8
        self.MAX_BRUTE_FORCE_CONSTANT = 13
        self.MAX_ATTEMPTS_BEFORE_FAILURE = 10000
        self.brute_force_limit = self.NORMAL_BRUTE_FORCE_CONSTANT
        self.totalNumMines = 0
        self.minesRemaining = 0
        self.actualBoard = None
        self.lose = False
        self.solved = False
        self.size = 0
        self.minesweeperBoard = collections.Counter()
        self.flagLocations = collections.Counter()
        self.uncoveredTiles = None
        self.temporaryMinePlacement = None
        self.solutionOptions = None
        self.temporaryBoard = None
        self.borderOptimization = None

        self.verbose = False

    def solve(self, size, mines, board):
        def printBoard():
            "Current status: "
            for i in range(self.size):
                for j in range(self.size):
                    loc = self.minesweeperBoard[(i, j)]
                    if self.minesweeperBoard[(i, j)] == None:
                        loc = 'u'
                    print loc,
                print
            print

        def copyBoard(board):
            newBoard = collections.Counter()
            for b in board:
                newBoard[b] = copy.deepcopy(board[b])
            return newBoard

        def checkGameOutcome():
            if self.solved == True:
                solution = []
                for flag in self.flagLocations:
                    if self.flagLocations[flag]:
                        solution.append(flag)
                if set(solution) == set(board._bomblocations):
                    return True
                return False
            return False

        def stillAlive():
            for i in range(self.size):
                for j in range(self.size):
                    if self.minesweeperBoard[(i, j)] == -1000:
                        return False
            return True

        def isSolved():
            flags = 0
            for i in range(self.size):
                for j in range(self.size):
                    if self.minesweeperBoard[(i, j)] == None:
                        return False
                    if self.flagLocations[(i, j)]:
                        flags += 1
            if flags == self.totalNumMines:
                return True
            return False

        def flagTile(i, j):
            self.flagLocations[(i, j)] = True
            self.minesweeperBoard[(i, j)] = -1
            self.minesRemaining -= 1
            return self.flagLocations[(i, j)]

        def clickTile(i, j):
            self.minesweeperBoard[(i,j)] = self.actualBoard.whatsAt((i, j)) if self.actualBoard.whatsAt((i, j)) != 'x' else -1000
            if self.minesweeperBoard[(i,j)] == -1000:
                self.lose = True
            return self.minesweeperBoard[(i,j)]

        def firstTile():
            return clickTile(0, 0)

        def countFreeTilesAround(i, j):
            freeTiles = 0
            freeTileOptions = []
            if self.minesweeperBoard[(i-1, j)] == None and not self.flagLocations[(i-1, j)]:
                freeTileOptions.append((i-1, j))
                freeTiles += 1
            if self.minesweeperBoard[(i+1, j)] == None and not self.flagLocations[(i+1, j)]:
                freeTileOptions.append((i+1, j))
                freeTiles += 1
            if self.minesweeperBoard[(i, j-1)] == None and not self.flagLocations[(i, j-1)]:
                freeTileOptions.append((i, j-1))
                freeTiles += 1
            if self.minesweeperBoard[(i, j+1)] == None and not self.flagLocations[(i, j+1)]:
                freeTileOptions.append((i, j+1))
                freeTiles += 1
            if self.minesweeperBoard[(i-1, j-1)] == None and not self.flagLocations[(i-1, j-1)]:
                freeTileOptions.append((i-1, j-1))
                freeTiles += 1
            if self.minesweeperBoard[(i-1, j+1)] == None and not self.flagLocations[(i-1, j+1)]:
                freeTileOptions.append((i-1, j+1))
                freeTiles += 1
            if self.minesweeperBoard[(i+1, j-1)] == None and not self.flagLocations[(i+1, j-1)]:
                freeTileOptions.append((i+1, j-1))
                freeTiles += 1
            if self.minesweeperBoard[(i+1, j+1)] == None and not self.flagLocations[(i+1, j+1)]:
                freeTileOptions.append((i+1, j+1))
                freeTiles += 1
            return freeTiles, freeTileOptions

        def countFlagsAround(board, i, j):
            flags = 0
            if board[(i-1, j)] == True:
                flags += 1
            if board[(i+1, j)] == True:
                flags += 1
            if board[(i, j-1)] == True:
                flags += 1
            if board[(i, j+1)] == True:
                flags += 1
            if board[(i-1, j-1)] == True:
                flags += 1
            if board[(i-1, j+1)] == True:
                flags += 1
            if board[(i+1, j-1)] == True:
                flags += 1
            if board[(i+1, j+1)] == True:
                flags += 1
            return flags

        def isBoundary(i, j):
            if self.minesweeperBoard[(i, j)] != None:
                return False
            oU = False
            oD = False
            oL = False
            oR = False
            if i == 0:
                oU = True
            if j == 0:
                oL = True
            if i == self.size-1:
                oD = True
            if j == self.size-1:
                oR = True
            isBoundary = False
            if not oU and self.minesweeperBoard[(i-1, j)] != None:
                isBoundary = True
            if not oL and self.minesweeperBoard[(i, j-1)] != None:
                isBoundary = True
            if not oD and self.minesweeperBoard[(i+1, j)] != None:
                isBoundary = True
            if not oR and self.minesweeperBoard[(i, j+1)] != None:
                isBoundary = True
            if not oU and not oL and self.minesweeperBoard[(i-1, j-1)] != None:
                isBoundary = True
            if not oR and not oU and self.minesweeperBoard[(i-1, j+1)] != None:
                isBoundary = True
            if not oD and not oL and self.minesweeperBoard[(i+1, j-1)] != None:
                isBoundary = True
            if not oD and not oR and self.minesweeperBoard[(i+1, j+1)] != None:
                isBoundary = True
            return isBoundary

        def recurseThroughAreaSolutionOptions(boardBorderTiles, k):
            flagCount = 0
            for i in range(self.size):
                for j in range(self.size):
                    if self.temporaryMinePlacement[(i,j)]:
                        flagCount += 1
                    num = self.temporaryBoard[(i, j)] if self.temporaryBoard[(i, j)] != None else -1000
                    if num < 0:
                        continue
                    numSurroundingTiles = 0
                    # corner tile
                    if (i == 0 and j == 0) or (i == self.size-1 and j == self.size-1):
                        numSurroundingTiles = 3
                    # edge tile
                    elif (i == 0 or j == 0 or i == self.size-1 or j == self.size-1):
                        numSurroundingTiles = 5
                    # center tile
                    else:
                        numSurroundingTiles = 8
                    numFlags = countFlagsAround(self.temporaryMinePlacement, i, j)
                    numFree = countFlagsAround(self.uncoveredTiles, i, j)
                    if numFlags > num:
                        return

                    if numSurroundingTiles - numFree < num:
                        return

            if flagCount > self.totalNumMines:
                return
            if k == len(boardBorderTiles):
                if not self.borderOptimization and flagCount < self.totalNumMines:
                    return
                solution = []
                for i in range(len(boardBorderTiles)):
                    solution.append(self.temporaryMinePlacement[boardBorderTiles[i]])
                self.solutionOptions.append(solution)
                return
            self.temporaryMinePlacement[boardBorderTiles[k]] = True
            recurseThroughAreaSolutionOptions(boardBorderTiles, k+1)
            self.temporaryMinePlacement[boardBorderTiles[k]] = False

            self.uncoveredTiles[boardBorderTiles[k]] = True
            recurseThroughAreaSolutionOptions(boardBorderTiles, k+1)
            self.uncoveredTiles[boardBorderTiles[k]] = False

        def segregateBoardAreas(boardBorderTiles):
            allRegions = []
            covered = []
            while True:
                queue = []
                finishedRegion = []
                for firstT in boardBorderTiles:
                    if firstT not in covered:
                        queue.append(firstT)
                        break
                if len(queue) == 0:
                    break
                while not len(queue) == 0:
                    curTile = queue.pop(0)
                    ci, cj = curTile
                    finishedRegion.append(curTile)
                    covered.append(curTile)

                    # determine bordering tiles
                    for tile in boardBorderTiles:
                        ti, tj = tile
                        isConnected = False
                        if tile in finishedRegion:
                            continue
                        if abs(ci - ti) > 2 or abs(cj - tj) > 2:
                            isConnected = False
                        else:
                            for i in range(self.size):
                                isTrue = False
                                for j in range(self.size):
                                    if self.minesweeperBoard[(i,j)] > 0 and self.minesweeperBoard[(i,j)] != None:
                                        if abs(ci - i) <= 1 and abs(cj - j) <= 1 and abs(ti - i) <= 1 and abs(tj - j) <= 1:
                                            isConnected = True
                                            isTrue = True
                                            break
                                if isTrue:
                                    break

                        if not isConnected:
                            continue
                        elif tile not in queue:
                            queue.append(tile)
                allRegions.append(finishedRegion)
            return allRegions


        def tankSolver():
            boardBorderTiles = []
            allEmptyTiles = []
            self.borderOptimization = False
            for i in range(self.size):
                for j in range(self.size):
                    if self.minesweeperBoard[(i,j)] == None and not self.flagLocations[(i, j)]:
                        allEmptyTiles.append((i,j))
            for i in range(self.size):
                for j in range(self.size):
                    if isBoundary(i, j) and not self.flagLocations[(i, j)]:
                        boardBorderTiles.append((i,j))
            # number of tiles in the knowable range
            numOutTiles = len(allEmptyTiles) - len(boardBorderTiles)
            if numOutTiles > self.brute_force_limit:
                self.borderOptimization = True
            else:
                boardBorderTiles = allEmptyTiles
            if len(boardBorderTiles) == 0:
                return

            segregatedAreas = None
            if not self.borderOptimization:
                segregatedAreas = []
                segregatedAreas.append(boardBorderTiles)
            else:
                segregatedAreas = segregateBoardAreas(boardBorderTiles)

            totalMultCases = 1
            success = False
            bestProbability = 0
            bestTileProbability = -1
            bestProbabilityIndex = -1
            for s in range(len(segregatedAreas)):
                self.solutionOptions = []
                self.temporaryBoard = copyBoard(self.minesweeperBoard)
                self.temporaryMinePlacement = copyBoard(self.flagLocations)
                self.uncoveredTiles = collections.Counter()
                for i in range(self.size):
                    for j in range(self.size):
                        if self.temporaryBoard[(i, j)] != None and self.temporaryBoard[(i, j)] >= 0:
                            self.uncoveredTiles[(i, j)] = True
                        else:
                            self.uncoveredTiles[(i, j)] = False
                recurseThroughAreaSolutionOptions(segregatedAreas[s], 0)
                solution = False
                if len(self.solutionOptions) == 0:
                    return
                for i in range(len(segregatedAreas[s])):
                    allMine = True
                    allEmpty = True
                    for sln in self.solutionOptions:
                        if not sln[i]:
                            allMine = False
                        if sln[i]:
                            allEmpty = False
                    ti, tj = segregatedAreas[s][i]
                    if allMine:
                        flagTile(ti, tj)
                    if allEmpty:
                        success = True
                        clickTile(ti, tj)
                totalMultCases *= len(self.solutionOptions)

                if success:
                    continue
                maxEmpty = -1000000
                iEmpty = -1
                for i in range(len(segregatedAreas[s])):
                    nEmpty = 0
                    for sln in self.solutionOptions:
                        if not sln[i]:
                            nEmpty += 1
                    if nEmpty > maxEmpty:
                        maxEmpty = nEmpty
                        iEmpty = i
                probability = float(maxEmpty)/len(self.solutionOptions)

                if probability > bestProbability:
                    bestProbability = probability
                    bestTileProbability = iEmpty
                    bestProbabilityIndex = s

            if self.brute_force_limit == self.NORMAL_BRUTE_FORCE_CONSTANT and numOutTiles > self.NORMAL_BRUTE_FORCE_CONSTANT and numOutTiles <= self.MAX_BRUTE_FORCE_CONSTANT:
                if self.verbose:
                    print "Extending bruteforce horizon"
                self.brute_force_limit = self.MAX_BRUTE_FORCE_CONSTANT
                tankSolver()
                self.brute_force_limit = self.NORMAL_BRUTE_FORCE_CONSTANT
                return

            if success:
                if self.verbose:
                    print "TANK Solver successfully invoked at step %d (%d cases) %s\n" % (self.totalNumMines - self.minesRemaining, totalMultCases, self.borderOptimization)
                return

            if self.verbose:
                print "TANK Solver guessing with probability %1.2f at step %d (%d cases) %s" % (bestProbability, self.totalNumMines - self.minesRemaining, totalMultCases, self.borderOptimization)
            i, j = segregatedAreas[bestProbabilityIndex][bestTileProbability]
            click = clickTile(i, j)
            if self.verbose:
                if click == -1000:
                    print "You guessed wrong."
                else:
                    print "Got lucky this time! ", click
                print

        def attemptFlagMine():
            # print "attempt Flag Mine"
            for i in range(self.size):
                for j in range(self.size):
                    if self.minesweeperBoard[(i,j)] >= 1 and self.minesweeperBoard[(i, j)] != None:
                        curNum = self.minesweeperBoard[(i,j)]
                        if curNum == countFreeTilesAround(i, j):
                            for ii in range(size):
                                for jj in range(size):
                                    if abs(ii - i) <= 1 and abs(jj - j) <= 1:
                                        if self.minesweeperBoard[(ii, jj)] == None and not self.flagLocations[(ii, jj)]:
                                            flagTile(ii, jj)

        def attemptMove():
            success = False
            # print
            # print "attempt Move: "
            # printBoard()
            # self.actualBoard.printBoard()
            for i in range(self.size):
                for j in range(self.size):
                    if self.minesweeperBoard[(i, j)] >= 0:
                        curNum = self.minesweeperBoard[(i, j)]
                        mines = countFlagsAround(self.flagLocations, i, j)
                        freeTiles, freeTileOptions = countFreeTilesAround(i, j)
                        if curNum == mines and freeTiles > 0:
                            success = True
                            for tile in freeTileOptions:
                                si, sj = tile
                                clickTile(si, sj)
                        if freeTiles == curNum - mines and freeTiles > 0:
                            success = True
                            for tile in freeTileOptions:
                                si, sj = tile
                                flagTile(si, sj)
            if success:
                return
            else:
                tankSolver()


        self.actualBoard = board
        self.size = size
        self.minesRemaining = mines
        self.totalNumMines = mines
        for i in range(size):
            for j in range(size):
                self.flagLocations[(i, j)] = False
                self.minesweeperBoard[(i, j)] = None
        currentNode = firstTile()
        for attempt in range(self.MAX_ATTEMPTS_BEFORE_FAILURE):
            if not stillAlive():
                self.lose = True
                break
            if isSolved():
                self.solved = True
                break
            attemptFlagMine()
            if isSolved():
                self.solved = True
                break
            attemptMove()
        return checkGameOutcome()
