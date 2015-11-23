import collections, util, copy, minesweeper

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

def create_minesweeper_csp(n = 2):
    def find_neighbors(location, variables, board):
        col, row = location
        neighbors = []
        for variable in variables:
            if (variable[0] == col - 1 or variable[0] == col + 1 or variable[0] == col) \
            and (variable[1] == row - 1 or variable[1] == row + 1 or variable[1] == row):
                if not (variable[0] == col and variable[1] == row):
                    neighbors.append(variable)
        return neighbors
    csp = util.CSP()
    # board = minesweeper.Board(n,[[0,1],[1,2],[2,4],[2,5],[3,5],[5,5]])
    board = minesweeper.Board(n,[[1,1]])
    domain = [0, 1]
    variables = []
    for i in range(n):
        for j in range(n):
            variables.append((i, j))
    for i in range(len(variables)):
        csp.add_variable(variables[i], domain)
    initValue = board.whatsAt((variables[0]))
    neighbors = find_neighbors(variables[0], variables, board)
    print neighbors
    csp.add_unary_factor(get_sum_variable(csp, 'name', neighbors, initValue), lambda x: x == initValue)
    # for i in range(len(variables)):
    #     value = board.whatsAt((variables[i]))
    #     neighbors = find_neighbors(variables[i], variables, board)
    #     csp.add_unary_factor(get_sum_variable(csp, str(i), neighbors, value), lambda x: x == value)
    # END_YOUR_CODE
    return csp

class BacktrackingSearch():

    def reset_results(self):
        """
        This function resets the statistics of the different aspects of the
        CSP solver. We will be using the values here for grading, so please
        do not make any modification to these variables.
        """
        # Keep track of the best assignment and weight found.
        self.optimalAssignment = {}
        self.optimalWeight = 0

        # Keep track of the number of optimal assignments and assignments. These
        # two values should be identical when the CSP is unweighted or only has binary
        # weights.
        self.numOptimalAssignments = 0
        self.numAssignments = 0

        # Keep track of the number of times backtrack() gets called.
        self.numOperations = 0

        # Keep track of the number of operations to get to the very first successful
        # assignment (doesn't have to be optimal).
        self.firstAssignmentNumOperations = 0

        # List of all solutions found.
        self.allAssignments = []

    def print_stats(self):
        """
        Prints a message summarizing the outcome of the solver.
        """
        if self.optimalAssignment:
            print "Found %d optimal assignments with weight %f in %d operations" % \
                (self.numOptimalAssignments, self.optimalWeight, self.numOperations)
            print "First assignment took %d operations" % self.firstAssignmentNumOperations
        else:
            print "No solution was found."

    def get_delta_weight(self, assignment, var, val):
        """
        Given a CSP, a partial assignment, and a proposed new value for a variable,
        return the change of weights after assigning the variable with the proposed
        value.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param var: name of an unassigned variable.
        @param val: the proposed value.

        @return w: Change in weights as a result of the proposed assignment. This
            will be used as a multiplier on the current weight.
        """
        assert var not in assignment
        w = 1.0
        if self.csp.unaryFactors[var]:
            w *= self.csp.unaryFactors[var][val]
            if w == 0: return w
        for var2, factor in self.csp.binaryFactors[var].iteritems():
            if var2 not in assignment: continue  # Not assigned yet
            w *= factor[val][assignment[var2]]
            if w == 0: return w
        return w

    def solve(self, csp, mcv = False, ac3 = False):
        """
        Solves the given weighted CSP using heuristics as specified in the
        parameter. Note that unlike a typical unweighted CSP where the search
        terminates when one solution is found, we want this function to find
        all possible assignments. The results are stored in the variables
        described in reset_result().

        @param csp: A weighted CSP.
        @param mcv: When enabled, Most Constrained Variable heuristics is used.
        @param ac3: When enabled, AC-3 will be used after each assignment of an
            variable is made.
        """
        # CSP to be solved.
        self.csp = csp

        # Set the search heuristics requested asked.
        self.mcv = mcv
        self.ac3 = ac3

        # Reset solutions from previous search.
        self.reset_results()

        # The dictionary of domains of every variable in the CSP.
        self.domains = {var: list(self.csp.values[var]) for var in self.csp.variables}

        # Perform backtracking search.
        self.backtrack({}, 0, 1)
        # Print summary of solutions.
        self.print_stats()

    def backtrack(self, assignment, numAssigned, weight):
        """
        Perform the back-tracking algorithms to find all possible solutions to
        the CSP.

        @param assignment: A dictionary of current assignment. Unassigned variables
            do not have entries, while an assigned variable has the assigned value
            as value in dictionary. e.g. if the domain of the variable A is [5,6],
            and 6 was assigned to it, then assignment[A] == 6.
        @param numAssigned: Number of currently assigned variables
        @param weight: The weight of the current partial assignment.
        """

        self.numOperations += 1
        assert weight > 0
        if numAssigned == self.csp.numVars:
            # A satisfiable solution have been found. Update the statistics.
            self.numAssignments += 1
            newAssignment = {}
            for var in self.csp.variables:
                newAssignment[var] = assignment[var]
            self.allAssignments.append(newAssignment)

            if len(self.optimalAssignment) == 0 or weight >= self.optimalWeight:
                if weight == self.optimalWeight:
                    self.numOptimalAssignments += 1
                else:
                    self.numOptimalAssignments = 1
                self.optimalWeight = weight

                self.optimalAssignment = newAssignment
                if self.firstAssignmentNumOperations == 0:
                    self.firstAssignmentNumOperations = self.numOperations
            return

        # Select the next variable to be assigned.
        var = self.get_unassigned_variable(assignment)
        # Get an ordering of the values.
        ordered_values = self.domains[var]

        # Continue the backtracking recursion using |var| and |ordered_values|.
        if not self.ac3:
            # When arc consistency check is not enabled.
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    del assignment[var]
        else:
            # Arc consistency check is enabled.
            # Problem 1c: skeleton code for AC-3
            # You need to implement arc_consistency_check().
            for val in ordered_values:
                deltaWeight = self.get_delta_weight(assignment, var, val)
                if deltaWeight > 0:
                    assignment[var] = val
                    # create a deep copy of domains as we are going to look
                    # ahead and change domain values
                    localCopy = copy.deepcopy(self.domains)
                    # fix value for the selected variable so that hopefully we
                    # can eliminate values for other variables
                    self.domains[var] = [val]

                    # enforce arc consistency
                    self.arc_consistency_check(var)

                    self.backtrack(assignment, numAssigned + 1, weight * deltaWeight)
                    # restore the previous domains
                    self.domains = localCopy
                    del assignment[var]

    def get_unassigned_variable(self, assignment):
        """
        Given a partial assignment, return a currently unassigned variable.

        @param assignment: A dictionary of current assignment. This is the same as
            what you've seen so far.

        @return var: a currently unassigned variable.
        """

        if not self.mcv:
            # Select a variable without any heuristics.
            for var in self.csp.variables:
                if var not in assignment: return var
        else:
            # Problem 1b
            # Heuristic: most constrained variable (MCV)
            # Select a variable with the least number of remaining domain values.
            # Hint: given var, self.domains[var] gives you all the possible values
            # Hint: get_delta_weight gives the change in weights given a partial
            #       assignment, a variable, and a proposed value to this variable
            # BEGIN_YOUR_CODE (around 10 lines of code expected)
            minDomain = float('inf')
            minVar = None
            for var in self.csp.variables:
                if var not in assignment:
                    inDomain = 0
                    for option in self.domains[var]:
                        if self.get_delta_weight(assignment, var, option) > 0:
                            inDomain += 1
                    if inDomain < minDomain:
                        minDomain = inDomain
                        minVar = var
            return minVar
            # END_YOUR_CODE

    def arc_consistency_check(self, var):
        """
        Perform the AC-3 algorithm. The goal is to reduce the size of the
        domain values for the unassigned variables based on arc consistency.

        @param var: The variable whose value has just been set.
        """
        # Problem 1c
        # Hint: How to get variables neighboring variable |var|?
        # => for var2 in self.csp.get_neighbor_vars(var):
        #       # use var2
        #
        # Hint: How to check if two values are inconsistent?
        # For unary factors
        #   => self.csp.unaryFactors[var1][val1] == 0
        #
        # For binary factors
        #   => self.csp.binaryFactors[var1][var2][val1][val2] == 0
        #   (self.csp.binaryFactors[var1][var2] returns a nested dict of all assignments)

        # BEGIN_YOUR_CODE (around 20 lines of code expected)
        queue = list([var])
        while queue:
            currVar = queue.pop(0)
            for neighbor in self.csp.get_neighbor_vars(currVar):
                delete = []
                for value in self.domains[neighbor]:
                    remove = True
                    if self.csp.unaryFactors[neighbor] != None and self.csp.unaryFactors[neighbor][value] != 0:
                        remove = False
                    else:
                        for currValue in self.domains[currVar]:
                            if self.csp.binaryFactors[currVar][neighbor] != None and self.csp.binaryFactors[currVar][neighbor][currValue][value] != 0:
                                remove = False
                    if remove:
                        delete.append(value)
                if len(delete) > 0:
                    queue.append(neighbor)
                for value in delete:
                    self.domains[neighbor].remove(value)
        # END_YOUR_CODE

solver = BacktrackingSearch()
solver.solve(create_minesweeper_csp(15))
