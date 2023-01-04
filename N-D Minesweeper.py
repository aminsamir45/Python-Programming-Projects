
import typing
import doctest


# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)

# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, True, True, True]
        [True, True, True, True]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)
    

def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['hidden'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is revealed on the board after digging (i.e. game['hidden'][bomb_location]
    == False), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    hidden:
        [True, False, False, False]
        [True, True, False, False]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden': [[True, False, True, True],
    ...                  [True, True, True, True]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    hidden:
        [False, False, True, True]
        [True, True, True, True]
    state: defeat
    """

    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['hidden'] indicates which squares should be hidden.  If
    xray is True (the default is False), game['hidden'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the that are not
                    game['hidden']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, False, True],
    ...                   [True, True, False, True]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'hidden':  [[True, False, True, False],
    ...                   [True, True, True, False]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """

    return render_nd(game, xray)
    

def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'hidden':  [[False, False, False, True],
    ...                            [True, True, False, True]]})
    '.31_\\n__1_'
    """
    #call render_2d_locations
    new_board = render_2d_locations(game, xray)
    #iterate through new_board and append values to string
    #separate rows with \n function
    string = '' 
    for y in range(game['dimensions'][0]):
        for x in range(game['dimensions'][1]):
            string += new_board[y][x]
        string += '\n'
    return string[:-1]
    

# N-D IMPLEMENTATION


def victory_check_ND(board, hidden):
    """
    Given a board and a hidden board, returns if the game has been won
    """
    #given a game state, return True if the game has been won
    if not isinstance(board[0], list):
        for i in range(len(board)):
            if board[i] != '.' and hidden[i]:
                return False
        return True
    else:
        for i in range(len(board)):
            if not victory_check_ND(board[i], hidden[i]):
                return False
        return True

def all_coordinates(dimensions):
    """
    Given game dimensions, returns a list of all coordinates in the game.
    """
    if len(dimensions) == 1:
        return {(i,) for i in range(dimensions[0])}
    coordinate_list = set()
    previous = all_coordinates(dimensions[:-1])
    for coord in previous:
        coordinate_list.update((coord) + (j,) for j in range(dimensions[-1]))
    return coordinate_list

def recurse_neighbors(coordinates):
    """
    Recursively finds all neighbors of a coordinate
    """
    if len(coordinates) == 1:
        return {(coordinates[0]-1,), (coordinates[0],), (coordinates[0] + 1,)}
    coordinate_list = set()
    previous = recurse_neighbors(coordinates[:-1])
    for coord in previous:
        coordinate_list.update((coord) + (j, ) for j in range(coordinates[-1] - 1, coordinates[-1] + 2))
    return coordinate_list

def get_neighbors(coordinates, dimensions):
    """
    Given a single coordinate tuple, returns a set of all neighbors
    """
    neighbors = recurse_neighbors(coordinates)
    neighbors.remove(coordinates)
    neighbors = {coord for coord in neighbors if all(0 <= i < j for i, j in zip(coord, dimensions))}
    return neighbors


def get_value(board, coordinates):
    """
    Given a board and a coordinate tuple, recursively returns the value at that coordinate
    """
    if len(coordinates) == 1:
        return board[coordinates[0]]
    return get_value(board[coordinates[0]], coordinates[1:])


def change_value(board, coordinates, value):
    """
    Given a board, a coordinate tuple, and a value, recursively replaces the value at the coordinate
    """
    if len(coordinates) == 1:
        board[coordinates[0]] = value
        return board
    return change_value(board[coordinates[0]], coordinates[1:], value)


def get_array(dimensions, value):
    """
    Given dimensions and a value, recursively creates an array of that value
    """
    if len(dimensions) == 1:
        return [value] * dimensions[0]
    return [get_array(dimensions[1:], value) for i in range(dimensions[0])]

def get_board_copy(board):
    """
    Given a board, recursively return a copy of the board
    """
    copy = [get_board_copy(row) for row in board] if isinstance(board, list) else board
    #make all integers in copy into strings
    if isinstance(copy, int):
        copy = str(copy)
    return zero_to_blank(copy)
    
def zero_to_blank(board):
    """
    Given a board, recursively replaces all 0s with blanks
    """
    if isinstance(board, list):
        return [zero_to_blank(row) for row in board]
    if board == '0':
        return ' '
    return board

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'hidden' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, True], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: ongoing
    """
    #create new board
    new_game = {'board': get_array(dimensions, 0), 'dimensions': dimensions, 'state': 'ongoing', 'hidden': get_array(dimensions, True)}
    #iterate through bombs and add 1 to all neighbors
    for bomb in bombs:
        for neighbor in get_neighbors(bomb, dimensions):
            if get_value(new_game['board'], neighbor) != '.':
                change_value(new_game['board'], neighbor, get_value(new_game['board'], neighbor) + 1)
        change_value(new_game['board'], bomb, '.')
    return new_game
    


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the hidden to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is revealed on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are revealed, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, True], [True, False], [False, False], [False, False]]
        [[True, True], [True, True], [False, False], [False, False]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [True, True],
    ...                [True, True]],
    ...               [[True, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    hidden:
        [[True, False], [True, False], [True, True], [True, True]]
        [[True, True], [True, True], [True, True], [True, True]]
    state: defeat
    """
    #change hidden value to False
    if get_value(game['hidden'], coordinates):
        change_value(game['hidden'], coordinates, False)
        #victory check
        if victory_check_ND(game['board'], game['hidden']):
            game['state'] = 'victory'
            return 1
        #if 0, recursively dig neighbors
        elif get_value(game['board'], coordinates) == 0:
            revealed = 1
            for neighbor in get_neighbors(coordinates, game['dimensions']):
                revealed += dig_nd(game, neighbor)
            return revealed
        #if bomb, change state to defeat
        elif get_value(game['board'], coordinates) == '.':
            game['state'] = 'defeat'
            return 1
        else:
            return 1
    else: 
        return 0
    


    


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['hidden'] array indicates which squares should be
    hidden.  If xray is True (the default is False), the game['hidden'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['hidden']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'hidden': [[[True, True], [True, False], [False, False],
    ...                [False, False]],
    ...               [[True, True], [True, True], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    
    def recurse_nd(board, hidden):
        """
        Given a board and a list of hidden booleans, 
        returns the n-dimensional board representation
        """
        nd_state = []
        #base case
        if not isinstance(board[0], list):
            for i in range(len(board)):
                if hidden[i] == False:
                    nd_state.append(str(board[i]))
                else:
                    nd_state.append('_')
            return nd_state

        #recursive step
        else:
            for bored, hiden in zip(board, hidden): #thought names were funny, couldn't think of anything else :)
                nd_state.append(recurse_nd(bored, hiden))
            return nd_state

    copy = get_board_copy(game['board'])
    #if xray is true, return the board
    if xray:
        return copy
    #if xray is false, replace hidden squares with _
    else:
        return recurse_nd(copy, game['hidden'])


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests


    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    #doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # print(get_neighbors((5, 13, 0), (10,20, 3)))
    # print(get_array((2,2, 2), 1))
    # g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    # print(g)
    # board = [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    # print(get_board_copy(board))
    # g = {'dimensions': (2, 4, 2),
    #   'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    #             [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    #     'hidden': [[[False, True], [False, False], [False, False], [False, False]],
    #               [[True, False], [False, True], [False, False], [False, False]]],
    #       'state': 'ongoing'}
    # render_nd(g, False)
    # game = {'dimensions': [2, 4],
    #          'board': [['.', 3, 1, 0],
    #                    ['.', '.', 1, 0]],
    #          'hidden': [[True, False, False, False],
    #                   [True, True, False, False]],
    #          'state': 'ongoing'}
    # print(victory_check_ND(game['board'], game['hidden']))

    # print(dig_2d(game, 0, 0))
