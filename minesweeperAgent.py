__author__ = 'Alex'
import collections, util, copy, minesweeper, random
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
            for i in [-1,0,1]:
                for j in [-1,0,1]:

                    if inBounds((node[0]+i,node[1] + j)) and (node[0]+i,node[1] + j) != node and self.board.whatsAt((node[0]+i,node[1] + j)) != None and (node[0]+i,node[1]+j) not in self.probed:
                        print self.board.whatsAt((node[0]+i,node[1] + j))
                        unprobedNeighbors.append((node[0]+i,node[1]+j))
            return unprobedNeighbors
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



        random.seed()
        for i in range(size):
            for j in range(size):
                self.unprobed.append((i,j))
        self.size = size
        self.minesRemaining = mines
        self.board = board
        constraints = []
        currentNode = (0,0)
        toProbe = []
        toProbe.append(currentNode)
        while self.solved == False and self.lose == False:
            if len(toProbe) > 0:
                nodeValue = board.whatsAt(toProbe[0])
            else:
                nodeValue = board.whatsAt(random.choice(self.unprobed))
            if nodeValue == 'x':
                self.lose = True
                break
            neighbors = getUnprobedNeighbors(self, toProbe[0])
            print neighbors
            print nodeValue

            if nodeValue == 0:
                for neighbor in neighbors:
                    toProbe.append(neighbor)
            elif nodeValue == len(neighbors):
                for neighbor in neighbors:
                    self.mineLocs.append(neighbor)
                    self.minesRemaining -= 1
                if self.minesRemaining <= 0:
                    print self.mineLocs
                    self.solved = True
                    break
        if self.solved == True:
            solution = minesweeper.Board(self.size, [self.mineLocs[i] for i in range(len(self.mineLocs))])
            solution.printBoard()
