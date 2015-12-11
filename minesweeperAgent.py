__author__ = 'Alex'

import collections, util, copy, minesweeper, random, time
from constraint import *
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

        def combineConstraints(newConstraint):
            hasChanged = False
            for i in range(len(constraints)):
                if i < len(constraints):
                    constraintSet = set(constraints[i][0])
                    newConstraintSet = set(newConstraint[0])
                    if len(constraintSet) > 0 and len(newConstraintSet) > 0:
                        if constraintSet.issubset(newConstraintSet) and constraintSet != newConstraintSet:
                            combineConstraints(([node for node in newConstraintSet-constraintSet], newConstraint[1]-constraints[i][1]))
                            hasChanged = True
                        elif newConstraintSet.issubset(constraintSet) and constraintSet != newConstraintSet:
                            constraintValue = constraints[i][1]
                            constraints.remove(constraints[i])
                            combineConstraints(([node for node in constraintSet-newConstraintSet], constraintValue-newConstraint[1]))

            if (hasChanged != True or len(constraints) ==0) and newConstraint not in constraints:
                constraints.append(newConstraint)

        def checkForTrivialConstraints():
            for constraint in constraints:
                if len(constraint[0]) == constraint[1]:
                    for mine in constraint[0]:
                        if mine not in self.mineLocs:
                            addMine(mine)
                    if self.minesRemaining <= 0:
                        self.solved = True

                if constraint[1] == 0 and len(constraint[0]) > 1:
                    for node in constraint[0]:
                        constraints.append(([node], 0))
                        toProbe.append(node)
                    constraints.remove(constraint)

        def checkGameOutcome():
            if self.solved == True:
                #print 'You win!'
                solution = minesweeper.Board(self.size, [self.mineLocs[i] for i in range(len(self.mineLocs))])
                if set(solution._bomblocations) == set(board._bomblocations):
                    return True
                return False

            #if self.lose== True:
                #print 'You lose'
            return False

        def getSortedMCVVars():
            return sorted(mostConstrainedDict, key=mostConstrainedDict.get, reverse=True)

        def getDependentVariablesandConstraints(mcv):
            dependentVariables = []
            dependentConstraints = []
            for constraint in constraints:
                if mcv in constraint[0]:
                    dependentConstraints.append(constraint)
                    for variable in constraint[0]:
                        if variable != mcv and variable not in dependentVariables:
                          dependentVariables.append(variable)
            return dependentVariables, dependentConstraints

        def updateMCVDict():
            mostConstrainedDict.clear()
            for constraint in constraints:
                for variable in constraint[0]:
                    mostConstrainedDict[variable] += 1

        def satisfiesConstraints(consts, testAssignment):
            for constraint in consts:
                varSum = 0
                varsAssigned = 0
                for var in constraint[0]:
                    if var in testAssignment:
                        varSum += testAssignment[var]
                        varsAssigned += 1
                if varSum > constraint[1] or (varsAssigned == len(constraint[0]) and varSum != constraint[1]):
                    return False
            return True

        def findSolutions(vars, consts, varIndex, currAssignment, assignments):
            if len(vars) == len(currAssignment):
                mineCount = 0
                for var in currAssignment:
                    mineCount += currAssignment[var]
                if satisfiesConstraints(consts, currAssignment) and mineCount <= self.minesRemaining and currAssignment not in assignments and len(consts) > 1:
                    assignments.append(copy.deepcopy(currAssignment))
                return
            for i in [0,1]:
                currAssignment[vars[varIndex]] = i
                if satisfiesConstraints(consts,currAssignment):
                    findSolutions(vars, consts, varIndex + 1, copy.deepcopy(currAssignment), assignments)
            return
        def addMine(mine):
            if mine is not None:
                self.mineLocs.append(mine)
                self.minesRemaining -= 1
                if mine in self.unprobed:
                    self.unprobed.remove(mine)
                combineConstraints(([mine], 1))

        def computeMCVSolution(toProbe, MCV):

            depVars, depConst = getDependentVariablesandConstraints(MCV)
            depVars.append(MCV)
            if len(depVars) > 1 and len(depConst) > 1:
                assignments = []
                currAssignment = {}
                findSolutions(depVars,depConst, 0,currAssignment, assignments)
                varValues = collections.Counter()
                prevNumMines = -1
                for assignment in assignments:
                    numMines = 0
                    for var in assignment:
                        varValues[var]+= assignment[var]
                        numMines += assignment[var]
                    else:
                        prevNumMines = numMines
                mineProbs = {}
                changed = False
                for varValue in varValues:
                    prob = float(varValues[varValue])/len(assignments)
                    if prob == 1:
                        addMine(varValue)
                        changed = True
                        if self.minesRemaining == 0:
                            self.solved = True
                            return
                    elif prob == 0:
                        toProbe.append(varValue)
                        changed = True
                    else:
                        mineProbs[varValue] = prob
                else:
                    if changed is False and len(mineProbs) > 0:
                        lowestProbMineVar = min(mineProbs, key = mineProbs.get)

                        if mineProbs[lowestProbMineVar] < self.minesRemaining/float(len(self.unprobed)):
                            toProbe.append(lowestProbMineVar)
                        
        random.seed()
        for i in range(size):
            for j in range(size):
                self.unprobed.append((i,j))
        self.size = size
        self.minesRemaining = mines
        self.board = board
        self.constrainedNodes = []
        constraints = []
        startNode = (0,0)
        toProbe = []
        toProbe.append(startNode)
        mostConstrainedDict = collections.Counter()
        oldMCDict = None
        while self.solved == False and self.lose == False:

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
                updateMCVDict()
                MCVList = getSortedMCVVars()
                if len(MCVList) > 0:
                    if mostConstrainedDict[MCVList[0]] > 1 and oldMCDict != mostConstrainedDict:
                        computeMCVSolution(toProbe, MCVList[0])
                        if self.solved is True:
                            break
                        oldMCDict = mostConstrainedDict
                if len(toProbe) > 0:
                    currentNode = toProbe[0]
                    nodeValue = board.whatsAt(currentNode)
                    toProbe.remove(currentNode)
                if currentNode is None:
                    corners=[(0,self.size - 1), (self.size-1, 0), (self.size-1, self.size-1)]
                    for corner in corners:
                        if corner in self.unprobed and corner not in self.constrainedNodes:
                            currentNode = corner
                    if len(set(self.unprobed)-set(self.constrainedNodes)) > 0 and currentNode is None:
                        currentNode= random.choice(list(set(self.unprobed)-set(self.constrainedNodes)))

                    else:
                        currentNode = random.choice(self.unprobed)
                    nodeValue = board.whatsAt(currentNode)
            if nodeValue == 'x':
                self.lose = True
                break
            combineConstraints(([currentNode], 0))
            neighbors, numMineNeighbors = getUnprobedNeighbors(currentNode)
            nodeValue-=numMineNeighbors
            if nodeValue == 0:
                for neighbor in neighbors:
                    if neighbor not in toProbe:
                        toProbe.append(neighbor)
                    combineConstraints(([neighbor],0))
                    self.constrainedNodes.append(neighbor)
                    checkForTrivialConstraints()
            elif nodeValue == len(neighbors):
                for neighbor in neighbors:
                    addMine(neighbor)
                if self.minesRemaining <= 0:
                    self.solved = True
                    break
            else:
                combineConstraints(([neighbor for neighbor in neighbors],nodeValue))
                for neighbor in neighbors:
                    self.constrainedNodes.append(neighbor)
                checkForTrivialConstraints()
                if self.solved == True:
                    break
            if currentNode in self.unprobed:
                self.unprobed.remove(currentNode)
        return checkGameOutcome()
