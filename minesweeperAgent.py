__author__ = 'Alex'

import collections, util, copy, minesweeper, random, sys
class minesweeperAgent:
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
        def getUnprobedNeighbors(self, node):
            unprobedNeighbors = []
            numMineNeighbors = 0
            for i in [-1,0,1]:
                for j in [-1,0,1]:
                    if (node[0]+i,node[1]+j) in self.mineLocs:
                        numMineNeighbors +=1
                    elif inBounds((node[0]+i,node[1] + j)) and (node[0]+i,node[1] + j) != node and self.board.whatsAt((node[0]+i,node[1] + j)) != None and (node[0]+i,node[1]+j) in self.unprobed:
                        unprobedNeighbors.append((node[0]+i,node[1]+j))
            return unprobedNeighbors, numMineNeighbors
        def get_sum_variable(csp, name, variables, maxSum):
            domain = []
            for i in range(0, maxSum+1):
                for j in range(i, maxSum+1):
                    domain.append((i, j))
            result = ('sum', name, 'aggregated')
            finalDomain = [i for i in range(0, maxSum+1)]
            csp.add_variable(result, finalDomain)
            if len(variables) == 0:
                csp.add_unary_factor(result, lambda val: not val)
                return result
            for i in range(0, len(variables)-1):
                var1 = variables[i]
                if i == 0:
                    auxVar = ('sum', name, var1)
                    csp.add_variable(auxVar, domain)
                    csp.add_unary_factor(auxVar, lambda x : x[0] == 0)
                var2 = variables[i+1]
                auxVar1 = ('sum', name, var1)
                auxVar2 = ('sum', name, var2)
                csp.add_variable(auxVar2, domain)
                csp.add_binary_factor(auxVar1, var1, lambda x, y: x[1] == x[0] + y)
                csp.add_binary_factor(auxVar1, auxVar2, lambda x, y: x[1] == y[0])
            beforeFinal = ('sum', name, variables[len(variables)-1])
            csp.add_binary_factor(beforeFinal, variables[len(variables)-1], lambda x, y: x[1] == x[0] + y)
            csp.add_binary_factor(result, beforeFinal, lambda x, y : x == y[1])
            return result

        def combineConstraints(newConstraint):
                hasChanged = False
                for i in range(len(constraints)):
                    constraintSet = set(constraints[i][0])
                    newConstraintSet = set(newConstraint[0])
                    if len(constraintSet) > 0 and len(newConstraintSet) > 0:
                        if constraintSet.issubset(newConstraintSet) and constraintSet != newConstraintSet :
                            combineConstraints(([node for node in newConstraintSet-constraintSet], newConstraint[1]-constraints[i][1]))
                            hasChanged = True
                        elif newConstraintSet.issubset(constraintSet) and constraintSet != newConstraintSet:
                            constraintValue = constraints[i][1]
                            constraints.remove(constraints[i])
                            combineConstraints(([node for node in constraintSet-newConstraintSet], constraintValue-newConstraint[1]))

                if (hasChanged != True or len(constraints) ==0) and newConstraint not in constraints:
                    constraints.append(newConstraint)
                    for variable in newConstraint[0]:
                        mostConstrainedDict[variable] += 1


        def checkForTrivialConstraints(self):
            for constraint in constraints:
                    if len(constraint[0]) == constraint[1]:
                        for mine in constraint[0]:
                            if mine not in self.mineLocs:
                                self.mineLocs.append(mine)
                                self.minesRemaining -=1
                            if mine in self.unprobed:
                                self.unprobed.remove(mine)
                        if self.minesRemaining <= 0:
                            self.solved = True

                    if constraint[1] == 0 and len(constraint[0]) > 1:
                        for node in constraint[0]:
                            constraints.append(([node], 0))
                            toProbe.append(node)
                        constraints.remove(constraint)
        def checkGameOutcome(self):
            if self.solved == True:
                print 'Solution:'
                solution = minesweeper.Board(self.size, [self.mineLocs[i] for i in range(len(self.mineLocs))])
                solution.printBoard()
            if self.lose== True:
                print 'You lose'
        def getMCV():
            return max(mostConstrainedDict.iteritems(), key=lambda x: x[1])

        random.seed()
        for i in range(size):
            for j in range(size):
                self.unprobed.append((i,j))
        self.size = size
        self.minesRemaining = mines
        self.board = board
        constraints = []
        startNode = (0,0)
        toProbe = []
        toProbe.append(startNode)
        mostConstrainedDict = collections.Counter()
        while self.solved == False and self.lose == False:
            currentNode = None
            if len(self.unprobed) == 0:
                self.solved = True
                break
            if len(self.unprobed) == self.minesRemaining:
                for node in self.unprobed:
                    self.mineLocs.append(node)
                    self.solved=True
                break
            if len(toProbe) > 0:
                currentNode = toProbe[0]
                nodeValue = board.whatsAt(currentNode)
                toProbe.remove(currentNode)
            #elif len(mostConstrainedDict) > 0:
            #    currentNode = getMCV()[0]

            else:
                currentNode= random.choice(self.unprobed)
                nodeValue = board.whatsAt(currentNode)
                print nodeValue
            if nodeValue == 'x':
                self.lose = True
                break
            neighbors, numMineNeighbors = getUnprobedNeighbors(self, currentNode)
            nodeValue-=numMineNeighbors
            if nodeValue == 0:
                for neighbor in neighbors:
                    if neighbor not in toProbe:
                        toProbe.append(neighbor)
                    combineConstraints(([neighbor],0))
            elif nodeValue == len(neighbors):
                for neighbor in neighbors:
                    self.mineLocs.append(neighbor)
                    self.minesRemaining -= 1
                    self.unprobed.remove(neighbor)
                if self.minesRemaining <= 0:
                    self.solved = True
                    break
            else:
                combineConstraints(([neighbor for neighbor in neighbors],nodeValue))
                checkForTrivialConstraints(self)
                if self.solved == True:
                    break
            if currentNode in self.unprobed:
                self.unprobed.remove(currentNode)
        checkGameOutcome(self)

