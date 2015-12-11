__author__ = 'Alex'

import collections, util, copy, minesweeper, random, time
from constraint import *
class oracleAgent:
    def __init__(self):
        self.minesRemaining = 0
        # self.mineLocs = []
        self.board = None
        # self.solved = False
        self.lose = False
        # self.probed = []
        self.size = 0
        # self.unprobed = []
        self.onScreen = collections.Counter()
        self.flags = collections.Counter()
        self.knownMine = None
        self.knownEmpty = None
        self.tank_solutions = None
        self.BF_LIMIT = 8
        self.tank_board = None
        self.TOT_MINES = 99
        self.borderOptimization = None
        self.solved = False
    #
    # def checkConsistency():
    #     for i in range(size):
    #         for j in range(size):
    #             freeSquares = SquaresAround(i, j)
    #             numFlags = ound(i , j)
    #             if self.onScreen[(i,j)] == 0 and freeSquares > 0:
    #                 return False
    #             if (self.onScreen[(i,j)] - numFlags) > 0 and freeSquares == 0:
    #                 return False
    #     return True

    def solve(self, size, mines, board):
        def printBoard():
            "Current status: "
            for i in range(self.size):
                for j in range(self.size):
                    loc = self.onScreen[(i, j)]
                    if self.onScreen[(i, j)] == None:
                        loc = 'u'
                    print loc,
                print
            print

        def checkGameOutcome():
            if self.solved == True:
                # print 'You win!'
                solution = []
                for flag in self.flags:
                    if self.flags[flag]:
                        solution.append(flag)
                if set(solution) == set(board._bomblocations):
                    return True
                return False

            #if self.lose== True:
                #print 'You lose'
            return False

        def stillAlive():
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i, j)] == -10:
                        return False
            return True

        def solved():
            flags = 0
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i, j)] == None:
                        return False
                    if self.flags[(i, j)]:
                        flags += 1
            if flags == self.TOT_MINES:
                return True
            return False

        def flagOn(i, j):
            self.flags[(i, j)] = True
            self.onScreen[(i, j)] = -1
            self.minesRemaining -= 1
            return self.flags[(i, j)]

        def clickOn(i, j):
            self.onScreen[(i,j)] = self.board.whatsAt((i, j)) if self.board.whatsAt((i, j)) != 'x' else -10
            if self.onScreen[(i,j)] == -10:
                print "clicked: ", (i, j), self.onScreen[(i,j)]
                self.lose = True
            return self.onScreen[(i,j)]

        def firstSquare():
            isUntouched = True
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i,j)] != None:
                        isUntouched = False
                if not isUntouched:
                    break
            return clickOn(size/2-1, size/2-1)

        def countFreeSquaresAround(i, j):
            freeSquares = 0
            freeSquareOptions = []
            if self.onScreen[(i-1, j)] == None and not self.flags[(i-1, j)]:
                freeSquareOptions.append((i-1, j))
                freeSquares += 1
            if self.onScreen[(i+1, j)] == None and not self.flags[(i+1, j)]:
                freeSquareOptions.append((i+1, j))
                freeSquares += 1
            if self.onScreen[(i, j-1)] == None and not self.flags[(i, j-1)]:
                freeSquareOptions.append((i, j-1))
                freeSquares += 1
            if self.onScreen[(i, j+1)] == None and not self.flags[(i, j+1)]:
                freeSquareOptions.append((i, j+1))
                freeSquares += 1
            if self.onScreen[(i-1, j-1)] == None and not self.flags[(i-1, j-1)]:
                freeSquareOptions.append((i-1, j-1))
                freeSquares += 1
            if self.onScreen[(i-1, j+1)] == None and not self.flags[(i-1, j+1)]:
                freeSquareOptions.append((i-1, j+1))
                freeSquares += 1
            if self.onScreen[(i+1, j-1)] == None and not self.flags[(i+1, j-1)]:
                freeSquareOptions.append((i+1, j-1))
                freeSquares += 1
            if self.onScreen[(i+1, j+1)] == None and not self.flags[(i+1, j+1)]:
                freeSquareOptions.append((i+1, j+1))
                freeSquares += 1
            return freeSquares, freeSquareOptions

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
            if self.onScreen[(i, j)] != None:
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
            if not oU and self.onScreen[(i-1, j)] != None:
                isBoundary = True
            if not oL and self.onScreen[(i, j-1)] != None:
                isBoundary = True
            if not oD and self.onScreen[(i+1, j)] != None:
                isBoundary = True
            if not oR and self.onScreen[(i, j+1)] != None:
                isBoundary = True
            if not oU and not oL and self.onScreen[(i-1, j-1)] != None:
                isBoundary = True
            if not oR and not oU and self.onScreen[(i-1, j+1)] != None:
                isBoundary = True
            if not oD and not oL and self.onScreen[(i+1, j-1)] != None:
                isBoundary = True
            if not oD and not oR and self.onScreen[(i+1, j+1)] != None:
                isBoundary = True
            return isBoundary

        def tankRecurse(borderTiles, k):
            flagCount = 0
            for i in range(self.size):
                for j in range(self.size):
                    if self.knownMine[(i,j)]:
                        flagCount += 1
                    num = self.tank_board[(i, j)] if self.tank_board[(i, j)] != None else -10
                    if num < 0:
                        continue
                    surround = 0
                    if (i == 0 and j == 0) or (i == self.size-1 and j == self.size-1):
                        surround = 3
                    elif (i == 0 or j == 0 or i == self.size-1 or j == self.size-1):
                        surround = 5
                    else:
                        surround = 8
                    numFlags = countFlagsAround(self.knownMine, i, j)
                    numFree = countFlagsAround(self.knownEmpty, i, j)
                    if numFlags > num:
                        return

                    if surround - numFree < num:
                        return

            if flagCount > self.TOT_MINES:
                return
            if k == len(borderTiles):
                if not self.borderOptimization and flagCount < self.TOT_MINES:
                # if flagCount < self.TOT_MINES:
                    return
                solution = []
                for i in range(len(borderTiles)):
                    s = borderTiles[i]
                    si, sj = s
                    solution.append(self.knownMine[(si, sj)])
                self.tank_solutions.append(solution)
                return
            q = borderTiles[k]
            qi, qj = q
            self.knownMine[(qi, qj)] = True
            tankRecurse(borderTiles, k+1)
            self.knownMine[(qi, qj)] = False

            self.knownEmpty[(qi, qj)] = True
            tankRecurse(borderTiles, k+1)
            self.knownEmpty[(qi, qj)] = False

        def tankSegregate(borderTiles):
            allRegions = []
            covered = []
            while True:
                queue = []
                finishedRegion = []
                for firstT in borderTiles:
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
                    for tile in borderTiles:
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
                                    if self.onScreen[(i,j)] > 0 and self.onScreen[(i,j)] != None:
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
                # print allRegions
            return allRegions


        def tankSolver():
            borderTiles = []
            allEmptyTiles = []
            self.borderOptimization = False
            allFlags = 0
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i,j)] == None and not self.flags[(i, j)]:
                        allEmptyTiles.append((i,j))
                    if self.flags[(i, j)]:
                        allFlags += 1
            if allFlags > self.TOT_MINES:
                return
            for i in range(self.size):
                for j in range(self.size):
                    if isBoundary(i, j) and not self.flags[(i, j)]:
                        borderTiles.append((i,j))
            # num squares in knowable range
            numOutSquares = len(allEmptyTiles) - len(borderTiles)
            if numOutSquares > self.BF_LIMIT:
                self.borderOptimization = True
            else:
                borderTiles = allEmptyTiles
            if len(borderTiles) == 0:
                # print "borderTiles error: ", borderTiles
                return

            segregated = None
            if not self.borderOptimization:
                segregated = []
                segregated.append(borderTiles)
            else:
                # print "tank segregate"
                segregated = tankSegregate(borderTiles)
                # print "finished"

            totalMultCases = 1
            success = False
            prob_best = 0
            prob_besttile = -1
            prob_best_s = -1
            for s in range(len(segregated)):
                self.tank_solutions = []
                self.tank_board = collections.Counter()
                self.knownMine = collections.Counter()
                for o in self.onScreen:
                    self.tank_board[o] = self.onScreen[o]
                for f in self.flags:
                    self.knownMine[f] = self.flags[f]
                self.knownEmpty = collections.Counter()
                for i in range(self.size):
                    for j in range(self.size):
                        if self.tank_board[(i, j)] != None:
                            self.knownEmpty[(i, j)] = True
                        else:
                            self.knownEmpty[(i, j)] = False
                tankRecurse(segregated[s], 0)
                solution = False
                if len(self.tank_solutions) == 0:
                    if solved():
                        # print "SOLVED"
                        self.tank_solutions.append(self.flags)
                        solution = True
                    else:
                        # print "tank_solutions error"
                        return
                if not solution:
                    for i in range(len(segregated[s])):
                        allMine = True
                        allEmpty = True
                        for sln in self.tank_solutions:
                            if not sln[i]:
                                allMine = False
                            if sln[i]:
                                allEmpty = False
                        q = segregated[s][i]
                        qi, qj = q
                        if allMine:
                            # print "all Mine"
                            flagOn(qi, qj)
                        if allEmpty:
                            success = True
                            clickOn(qi, qj)
                totalMultCases *= len(self.tank_solutions)

                if success:
                    continue
                maxEmpty = -10000
                iEmpty = -1
                for i in range(len(segregated[s])):
                    nEmpty = 0
                    for sln in self.tank_solutions:
                        if not sln[i]:
                            nEmpty += 1
                    if nEmpty > maxEmpty:
                        maxEmpty = nEmpty
                        iEmpty = i
                probability = float(maxEmpty)/len(self.tank_solutions)

                if probability > prob_best:
                    prob_best = probability
                    prob_besttile = iEmpty
                    prob_best_s = s

            if self.BF_LIMIT == 8 and numOutSquares > 8 and numOutSquares <= 13:
                print "Extending bruteforce horizon"
                self.BF_LIMIT = 13
                tankSolver()
                self.BF_LIMIT = 8
                return

            if success:
                print "TANK Solver successfully invoked at step %d (%d cases) %s\n" % (self.TOT_MINES - self.minesRemaining, totalMultCases, self.borderOptimization)
                return

            print "TANK Solver guessing with probability %1.2f at step %d (%d cases) %s\n" % (prob_best, self.TOT_MINES - self.minesRemaining, totalMultCases, self.borderOptimization)
            q = segregated[prob_best_s][prob_besttile]
            qi, qj = q
            clickOn(qi, qj)

        def attemptFlagMine():
            # print "attempt Flag Mine"
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i,j)] >= 1 and self.onScreen[(i, j)] != None:
                        curNum = self.onScreen[(i,j)]
                        if curNum == countFreeSquaresAround(i, j):
                            for ii in range(size):
                                for jj in range(size):
                                    if abs(ii - i) <= 1 and abs(jj - j) <= 1:
                                        if self.onScreen[(ii, jj)] == None and not self.flags[(ii, jj)]:
                                            flagOn(ii, jj)

        def attemptMove():
            success = False
            # print
            # print "attempt Move: "
            # printBoard()
            # self.board.printBoard()
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i, j)] >= 0:
                        curNum = self.onScreen[(i, j)]
                        mines = countFlagsAround(self.flags, i, j)
                        freeSquares, freeSquareOptions = countFreeSquaresAround(i, j)
                        # print "squares ", (i, j), freeSquares, curNum, mines, curNum == mines and freeSquares > 0, freeSquareOptions
                        if curNum == mines and freeSquares > 0:
                            success = True
                            # if freeSquares - mines > 1:
                            #     self.onScreen[(i, j)] = 0
                            #     continue
                            for square in freeSquareOptions:
                                si, sj = square
                                clickOn(si, sj)
            if success:
                return
            else:
                tankSolver()


        self.board = board
        self.size = size
        self.minesRemaining = mines
        self.TOT_MINES = mines
        for i in range(size):
            for j in range(size):
                self.flags[(i, j)] = False
                self.onScreen[(i, j)] = None
        currentNode = firstSquare()
        for c in range(100000):
            # print "flags ", self.flags
            # print "board ", self.onScreen
            if not stillAlive():
                self.lose = True
                break
            if solved():
                self.solved = True
                break
            attemptFlagMine()
            if solved():
                self.solved = True
                break
            attemptMove()
        return checkGameOutcome()
