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
    #
    # def checkConsistency():
    #     for i in range(size):
    #         for j in range(size):
    #             freeSquares = countFreeSquaresAround(i, j)
    #             numFlags = ound(i , j)
    #             if self.onScreen[(i,j)] == 0 and freeSquares > 0:
    #                 return False
    #             if (self.onScreen[(i,j)] - numFlags) > 0 and freeSquares == 0:
    #                 return False
    #     return True

    def solve(self, size, mines, board):
        def stillAlive(status):
            if status == 'x':
                return False
            else:
                return True

        def flagOn(i, j):
            self.flags[(i, j)] = True
            self.minesRemaining -= 1
            return self.flags[(i, j)]

        def clickOn(i, j):
            self.onScreen[(i,j)] = self.board.whatsAt((i, j))
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
            if self.onScreen[(i-1, j)] == -1:
                freeSquares += 1
            if self.onScreen[(i+1, j)] == -1:
                freeSquares += 1
            if self.onScreen[(i, j-1)] == -1:
                freeSquares += 1
            if self.onScreen[(i, j+1)] == -1:
                freeSquares += 1
            if self.onScreen[(i-1, j-1)] == -1:
                freeSquares += 1
            if self.onScreen[(i-1, j+1)] == -1:
                freeSquares += 1
            if self.onScreen[(i+1, j-1)] == -1:
                freeSquares += 1
            if self.onScreen[(i+1, j+1)] == -1:
                freeSquares += 1
            return freeSquares

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
                    num = self.tank_board[(i, j)] if self.tank_board[(i, j)] != None else -1
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
                    print borderTiles, len(borderTiles)
                    for i in range(len(borderTiles)):
                        s = borderTiles[i]
                        si, sj = s
                        solution.append(self.knownMine[(si, sj)])
                        print solution, i
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
                    if not covered.contains(firstT):
                        queue.append(firstT)
                        break
                if len(queue) == 0:
                    break

                while not len(queue) == 0:
                    curTile = queue.poll()
                    ci, cj = curTile
                    finishedRegion.append(curTile)
                    covered.append(curTile)

                    for tile in borderTiles:
                        ti, tj = tile
                        if abs(ci - ti) > 2 or abs(cj - tj) > 2:
                            isConnected = False
                        else:
                            for i in len(self.size):
                                for j in len(self.size):
                                    if self.onScreen[(i,j)] > 0:
                                        if abs(ci - i) <= 1 and abs(cj - j) <= 1 and abs(ti - i) <= 1 and abs(tj - j) <= 1:
                                            isConnected = True
                                            break

                        if not isConnected:
                            continue
                        if not queue.contains(tile):
                            queue.add(tile)
            return allRegions


        def tankSolver():
            borderTiles = []
            allEmptyTiles = []
            self.borderOptimization = False
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i,j)] == None and not self.flags[(i, j)]:
                        allEmptyTiles.append((i,j))
            for i in range(self.size):
                for j in range(self.size):
                    if isBoundary(i, j) and not self.flags[(i, j)]:
                        borderTiles.append((i,j))
            numOutSquares = len(allEmptyTiles) - len(borderTiles)
            if numOutSquares > self.BF_LIMIT:
                self.borderOptimization = True
            else:
                borderTiles = allEmptyTiles

            if len(borderTiles) == 0:
                print "borderTiles error"
                return

            segregated = []
            if not self.borderOptimization:
                segregated = []
                segregated.append(borderTiles)
            else:
                segregated = tankSegregate(borderTiles)

            totalMultCases = 1
            success = False
            prob_best = 0
            prob_besttile = -1
            prob_best_s = -1
            for s in range(len(segregated)):
                self.tank_solutions = []
                self.tank_board = self.onScreen.copy()
                self.knownMine = self.flags.copy()
                self.knownEmpty = collections.Counter()
                for i in range(self.size):
                    for j in range(self.size):
                        if self.tank_board[(i, j)] >= 0:
                            self.knownEmpty[(i, j)] = True
                        else:
                            self.knownEmpty[(i, j)] = False
                tankRecurse(segregated[s], 0)
                if len(self.tank_solutions) == 0:
                    print "tank_solutions error"
                    return
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
                print "TANK Solver successfully invoked at step %d (%d cases)%s\n" % (self.TOT_MINES - self.minesRemaining, totalMultCases, self.borderOptimization)
                return

            print "TANK Solver guessing with probability %1.2f at step %d (%d cases)%s\n" % (prob_best, self.TOT_MINES - self.minesRemaining, totalMultCases, self.borderOptimization)
            q = segregated[prob_best_s][prob_besttile]
            qi, qj = q
            clickOn(qi, qj)

        def attemptFlagMine():
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i,j)] >= 1:
                        curNum = self.onScreen[(i,j)]
                        if curNum == countFreeSquaresAround(i, j):
                            for ii in range(size):
                                for jj in range(size):
                                    if abs(ii - i) <= 1 and abs(jj - j) <= 1:
                                        if self.onScreen[(ii, jj)] == None and not flags[(ii, jj)]:
                                            flagOn(ii, jj)

        def attemptMove():
            success = False
            for i in range(self.size):
                for j in range(self.size):
                    if self.onScreen[(i, j)] >= 1:
                        curNum = self.onScreen[(i, j)]
                        mines = countFlagsAround(self.onScreen, i, j)
                        freeSquares = countFreeSquaresAround(i, j)
                        if curNum == mines and freeSquares > mines:
                            success = True
                            if freeSquares - mines > 1:
                                self.onScreen[(i, j)] = 0
                                continue
                            for ii in range(size):
                                for jj in range(size):
                                    if abs(ii - i) <= 1 and abs(jj - j) <= 1:
                                        if self.onScreen[(ii, jj)] == None and not flags[(ii, jj)]:
                                            clickOn(ii, jj)
            if success:
                return
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
        for c in range(1000000):
            if not stillAlive(currentNode):
                self.lose = True
                break
            attemptFlagMine()
            attemptMove()
