__author__ = 'Alex'

import collections, util, copy, minesweeper, random, time
from constraint import *
class baselineAgent:
    def __init__(self):
        self.minesRemaining = 0
        self.mineLocs = []
        self.board = None
        self.solved = False
        self.lose = False
        self.probed = []
        self.size = 0
        self.unprobed = []


    def solve(self, size, mines, board):
        def inBounds(node):
            if node[0] < size and node[1] <size and node[0] >= 0 and node[1] >=0:
                return True
            return False

        def getUnprobedNeighbors(node):
            unprobedNeighbors = []
            numMineNeighbors = 0
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if (node[0]+i,node[1]+j) in self.mineLocs:
                        numMineNeighbors +=1
                    elif inBounds((node[0]+i,node[1] + j)) and (node[0]+i,node[1] + j) != node and self.board.whatsAt((node[0]+i,node[1] + j)) != None and (node[0]+i,node[1]+j) in self.unprobed:
                        unprobedNeighbors.append((node[0]+i,node[1]+j))
            return unprobedNeighbors, numMineNeighbors

        def addMine(mine):
            if mine is not None:
                self.mineLocs.append(mine)
                self.minesRemaining -= 1
                if mine in self.unprobed:
                    self.unprobed.remove(mine)

        def checkGameOutcome():
            if self.solved == True:
                # print 'You win!'
                solution = minesweeper.Board(self.size, [self.mineLocs[i] for i in range(len(self.mineLocs))])
                if set(solution._bomblocations) == set(board._bomblocations):
                    return True
                return False

            #if self.lose== True:
                #print 'You lose'
            return False

        random.seed()
        for i in range(size):
            for j in range(size):
                self.unprobed.append((i,j))
        self.size = size
        self.minesRemaining = mines
        self.board = board
        startNode = (0,0)
        toProbe = []
        toProbe.append(startNode)
        while self.solved == False and self.lose == False:
            # print "remaining: ", self.minesRemaining, toProbe, self.mineLocs
            currentNode = None
            nodeValue =-1
            if len(self.unprobed) == 0:
                self.solved = True
                break
            if len(self.unprobed) == self.minesRemaining:
                for node in self.unprobed:
                    addMine(node)
                break
            if len(toProbe) > 0:
                currentNode = toProbe[0]
                nodeValue = board.whatsAt(currentNode)
                toProbe.remove(currentNode)
            else:
                rand = random.randint(0, len(self.unprobed)-1)
                currentNode = self.unprobed[rand]
                nodeValue = board.whatsAt(currentNode)
            # print currentNode, nodeValue
            if nodeValue == 'x':
                self.lose = True
                break
            neighbors, numMineNeighbors = getUnprobedNeighbors(currentNode)
            nodeValue -= numMineNeighbors
            if nodeValue == 0:
                for neighbor in neighbors:
                    if neighbor not in toProbe:
                        toProbe.append(neighbor)
            elif nodeValue == len(neighbors):
                for neighbor in neighbors:
                    addMine(neighbor)
                if self.minesRemaining <= 0:
                    self.solved = True
                    break
            if currentNode in self.unprobed:
                self.unprobed.remove(currentNode)
        return checkGameOutcome()
