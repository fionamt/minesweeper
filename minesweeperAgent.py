__author__ = 'Alex Engel and Fiona Meyer Teruel'

import collections, copy, minesweeper, random
class minesweeperAgent:
    def __init__(self):
        # Mines left on board
        self.minesRemaining = 0
        # Known mines
        self.mineLocs = []
        # original board
        self.board = None
        # endgame variables
        self.solved = False
        self.lose = False
        # board size
        self.size = 0
        # mines not yet examined
        self.unprobed = []

    # Find the solution to a size*size Minesweeper board with 'mines' mines.
    def solve(self, size, mines, board):
        # Return true if a variable is within the bounds of the board
        def inBounds(node):
            if node[0] < size and node[1] <size and node[0] >= 0 and node[1] >=0:
                return True
            return False

        # return a list of all neighboring variables that have not been probed already and are not mines.
        # Also return an integer number of mines touching the node being examined
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

        # Combine subsets of constraints to make them as trivial as possible. For example, if we have a constraint
        #  ([x1, x2], 1) which means x1 + x2 = 1 and we add a constraint ([x1], 1) which means x1 = 1, we can
        # trivialize the first constraint to be ([x2], 0) or x2 = 0.
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

        # If we have any constraints that can be immediately trivialized to say whether variables contain mines or not,
        # find them and add them to the solution.
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
        # Return true if the game has been correctly solved, false otherwise.
        def checkGameOutcome():
            if self.solved is True:
                print 'You win!'
                solution = minesweeper.Board(self.size, [self.mineLocs[i] for i in range(len(self.mineLocs))])
                print 'AI Solution:\n'
                solution.printBoard()
                if set(solution._bomblocations) == set(board._bomblocations):
                    return True
                return False
            if self.lose is True:
                print 'You lose'
            return False

        # For a certain variable, find all constrained variables that are in the same constraints as the given variable.
        # Return a list of these variables and their constraints
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

        # Update most constrained variable dictionary with latest info
        def updateMCVDict():
            mostConstrainedDict.clear()
            for constraint in constraints:
                for variable in constraint[0]:
                    mostConstrainedDict[variable] += 1

        # For a certain assignment of variables, check to ensure that they satisfy all constraints.
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

        # Recursive method that finds all the solutions that do not violate any constraints for a given group of variables
        def findSolutions(vars, consts, varIndex, currAssignment, assignments):
            # If all variables assigned
            if len(vars) == len(currAssignment):
                mineCount = 0
                for var in currAssignment:
                    mineCount += currAssignment[var]
                # If the assignment is valid with respect to constraints, add it.
                if satisfiesConstraints(consts, currAssignment) and mineCount <= self.minesRemaining \
                        and currAssignment not in assignments and len(consts) > 1:
                    assignments.append(copy.deepcopy(currAssignment))
                return
            # Recurse twice, once with setting the current variable to be a mine and once setting it to be free
            for i in [0,1]:
                currAssignment[vars[varIndex]] = i
                if satisfiesConstraints(consts,currAssignment):
                    findSolutions(vars, consts, varIndex + 1, copy.deepcopy(currAssignment), assignments)
            return

        # Mark a mine on the board and update lists
        def addMine(mine):
            if mine is not None:
                self.mineLocs.append(mine)
                self.minesRemaining -= 1
                if mine in self.unprobed:
                    self.unprobed.remove(mine)
                combineConstraints(([mine], 1))

        # Wrapper method for findSolutions recursive method. After finding all possible solutions, we now have new info.
        # If all solutions say that a certain variable is a mine, we know that to be true. Same goes for if all solutions
        # say the variable is clear. Otherwise, the solutions give us a probability that the variable is free.
        def computeMCVSolution(toProbe, MCV):
            depVars, depConst = getDependentVariablesandConstraints(MCV)
            depVars.append(MCV)
            if len(depVars) > 1 and len(depConst) > 1:
                assignments = []
                currAssignment = {}
                if len(self.unprobed) > 20:
                    findSolutions(depVars,depConst, 0,currAssignment, assignments)
                else:
                    findSolutions(self.unprobed, constraints, 0 , currAssignment, assignments)
                varValues = collections.Counter()
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
        # Take a node value and check if it is a mine. If it isn't add the correct constraints to the csp.
        def evaluateNodeValue(nodeValue):
            if nodeValue == 'x':
                self.lose = True
                return
            else:
                combineConstraints(([currentNode], 0))
                neighbors, numMineNeighbors = getUnprobedNeighbors(currentNode)
                nodeValue -= numMineNeighbors
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
                        return
                else:
                    toConstrain = []
                    for neighbor in neighbors:
                        self.constrainedNodes.append(neighbor)
                        toConstrain.append(neighbor)
                    combineConstraints((toConstrain, nodeValue))
                    checkForTrivialConstraints()
                    if self.solved == True:
                        return

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

        while self.solved is False and self.lose is False:
            currentNode = None
            # if we have probed all mines we are done
            if len(self.unprobed) == 0:
                self.solved = True
                break
            # if the number of remaining variables is the same as the number of remaining mines, they are all mines
            if len(self.unprobed) == self.minesRemaining:
                for node in self.unprobed:
                    addMine(node)
                break
            # if there are mines that we know are safe, probe them
            if len(toProbe) > 0:
                currentNode = toProbe[0]
                toProbe.remove(currentNode)
            else:
                updateMCVDict()
                MCV = max(mostConstrainedDict, key=mostConstrainedDict.get)
                # brute force solution for mcv and surrounding tiles
                if MCV is not None:
                    if mostConstrainedDict[MCV] > 1:
                        computeMCVSolution(toProbe, MCV)
                        if self.solved is True:
                            break
                # if we found safe nodes while brute forcing solutions
                if len(toProbe) > 0:
                    currentNode = toProbe[0]
                    toProbe.remove(currentNode)
                # if a random choice will give us the best hope
                if currentNode is None:
                    corners = [(0,self.size - 1), (self.size-1, 0), (self.size-1, self.size-1)]
                    for corner in corners:
                        if corner not in self.unprobed or corner in self.constrainedNodes:
                            corners.remove(corner)
                    if len(corners) > 0:
                        currentNode = random.choice(corners)
                    if len(set(self.unprobed)-set(self.constrainedNodes)) > 0 and currentNode is None:
                        currentNode= random.choice(list(set(self.unprobed)-set(self.constrainedNodes)))
                    else:
                        currentNode = random.choice(self.unprobed)
            nodeValue = board.whatsAt(currentNode)
            evaluateNodeValue(nodeValue)
            if self.solved is True or self.lose is True:
                break
            if currentNode in self.unprobed:
                self.unprobed.remove(currentNode)
        return checkGameOutcome()

