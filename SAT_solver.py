#!/usr/bin/env python3

import sys
import typing
import doctest

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS
def reduced_formula(formula, constraints):
    """
    Given a formula and a constraint, return a new formula that is equivalent to
    the original formula, but with the constraint added to it.
    """
    reduced = []
    check = True
    for clause in formula:
        if constraints not in clause:
            reduction = [boolean for boolean in clause if (boolean != (constraints[0], not constraints[1]))]
            reduced.append(reduction)
            if reduction == []:
                check = False
             # if what i jsut added is []. check = False
    return reduced, check

def validity_test(constraints):
    """
    Given a list of constraints, return True if the constraints are valid,
    and False otherwise.
    """
    for constraint in constraints:
        if (constraint[0], not constraint[1]) in constraints:
            return True
    return False

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    
    #if initial formula is empty, return empty dictionary
    if formula == []:
        return {}
    #if formula is not empty, reduce the formula
    formula_reduced = formula 
    constraints = []
    while formula_reduced:
        for clause in formula_reduced:
            if len(clause) == 1:
                #Fformula_reduced, check = 
                formula_reduced, check = reduced_formula(formula_reduced, clause[0])
                constraints.append(clause[0])
                if not check:
                    return None
                break
        else:
            break
    #if the reduced formula is empty, return the constraints
    if formula_reduced == []:
        return {constraint[0]: constraint[1] for constraint in constraints}
    # if the simplified formula is not empty, pick a literal and try to solve it
    for clause in formula_reduced:
        for literal in clause:
            formula_reduced, check = reduced_formula(formula_reduced, literal)
            constraints.append(literal)
            assignment = satisfying_assignment(formula_reduced)
            if assignment is not None:
                return {**assignment, **{constraint[0]: constraint[1] for constraint in constraints}}
            else:
                formula_reduced = formula
                constraints = []
        return None 


def get_combos(list, n):
    """
    Return a list of all possible combinations of n items from a list

    """
    if n == 0:
        return [[]]
    if not list:
        return []
    return [[list[0]] + rest for rest in get_combos(list[1:], n-1)] + get_combos(list[1:], n)

def rule0(sudoku_board):
    """
    Adds already existing elements to the formula
    """
    sat = []
    n = len(sudoku_board)
    for r in range(n):
        for c in range(n):
            if sudoku_board[r][c] != 0:
                sat.append([((sudoku_board[r][c], (r,c)), True)])
    return sat

def rule1(sudoku_board):
    """
    Function to ensure that each row and column contains each value exactly once

    A sat clause will come in the form [(value, (r,c)), True)] or [(value, (r,c)), False)]
    """
    
    sat = []
    n = len(sudoku_board)
    for r in range(n):
        for c in range(n):
            sat.append([((value, (r, c)), True) for value in range(1, n+1)])
            sat.append([((value, (c, r)), True) for value in range(1, n+1)])
    for r in range(n): 
        for value in range(1, n+1):
            combos = get_combos(range(n), 2)
            for combo in combos:
                sat.append([((value, (r, combo[0])), False), ((value, (r, combo[1])), False)])
                sat.append([((value, (combo[0], r)), False), ((value, (combo[1], r)), False)])
    return sat

        
# def rule2(sudoku_board):
#     """
#     Function to ensure that each column contains each value exactly once

#     A sat clause will come in the form [(value, (r,c)), True)] or [(value, (r,c)), False)]
#     """
#     sat = []
#     n = len(sudoku_board)
#     #iterate through each column
#     for c in range(n):
#         for r in range(n):
#             sat.append([((value, (r, c)), True) for value in range(1, n+1)])
#     # for r in range(n):
#     #     for value in range(1, n+1):
#     #         combos = get_combos(range(n), 2)
#     #         for combo in combos:
#     #             sat.append([((value, (combo[0], r)), False), ((value, (combo[1], r)), False)])
#     return sat

def rule2(sudoku_board):
    """
    Function to ensure that each subgrid contains each value exactly once
    """
    sat = []
    n = len(sudoku_board)
    subgrid_size = int(n**0.5)
    for r in range(0, n, subgrid_size):
        for c in range(0, n, subgrid_size):
            for i in range(subgrid_size):
                for j in range(subgrid_size):
                    sat.append([((value, (r+i, c+j)), True) for value in range(1, n+1)])
            for value in range(1, n+1):
                combos = get_combos([(r+i, c+j) for i in range(subgrid_size) for j in range(subgrid_size)], 2)
                for combo in combos:
                    sat.append([((value, combo[0]), False), ((value, combo[1]), False)])
    return sat

def rule3(sudoku_board):
    """
    Function to ensure that each cell contains exactly one value
    """
    sat = []
    n = len(sudoku_board)
    #iterate through each cell
    for r in range(n):
        for c in range(n):  
            #if the cell is not empty, create a clause in the form [(value, (r,c)), True)] where the value is the value in the cell
            sat += ([((value1, (r, c)), False), ((value2, (r, c)), False)] for value1, value2 in get_combos(range(1, n+1), 2))
    return sat


def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    
    A board in the form of a list of lists is passed in.  Each list represents
    a row of the board.  Each item in the list is either 0 (if the cell is
    empty) or a value from 1 to n (if the cell is filled in).

    A sat clause will come in the form [(value, (r,c), True)] or [(value, (r,c), False)]
    """

    sat = []
    sat += rule0(sudoku_board)
    sat += rule1(sudoku_board)
    sat += rule2(sudoku_board)
    sat += rule3(sudoku_board)
    return sat


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolveable board, return None
    instead.

    assignments is a dictionary mapping variable names to True or False.
    """
    sudoku_board = [[0 for i in range(n)] for j in range(n)]
    if assignments == None:
        return None
    for key, value in assignments.items():
        if value:
            sudoku_board[key[1][0]][key[1][1]] = key[0]
    return sudoku_board


if __name__ == "__main__":
    import doctest

    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)
    board =  [
            [1, 0, 0, 0],
            [0, 0, 0, 4],
            [3, 0, 0, 0],
            [0, 0, 0, 2],
        ]
    board2 =[   [0, 8, 0, 0, 0, 0, 0, 9, 0], 
                [0, 1, 0, 0, 8, 6, 3, 0, 2],
                [0, 0, 0, 3, 1, 0, 0, 0, 0],
                [0, 0, 4, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 5],
                [0, 0, 0, 2, 6, 1, 0, 0, 4],
                [0, 0, 0, 5, 4, 0, 0, 0, 6],
                [3, 0, 9, 0, 0, 0, 8, 0, 0],
                [2, 0, 0, 0, 0, 0, 0, 0, 0],
            ]
    # print(rule1(board))
    # print(len(rule1(board2)))
    # print(len(rule2(board2)))
    # print(len(rule3(board2)))
    # print(len(rule4(board2)))
    # print(get_combos(range(1, 4+1), 2))
    # print(sudoku_board_to_sat_formula(board))
    # print(satisfying_assignment(sudoku_board_to_sat_formula(board)))
    print(assignments_to_sudoku_board(satisfying_assignment(sudoku_board_to_sat_formula(board)), 4))
    result = [  [1, 2, 2, 3], 
                [2, 2, 1, 4], 
                [3, 1, 1, 1], 
                [4, 1, 1, 2]    ]
