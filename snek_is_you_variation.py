# Snekoban Game

import json
import typing

# NO ADDITIONAL IMPORTS!

direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    h = len(level_description)
    w = len(level_description[0])
    target_loc = set()
    wall_loc = set()
    computer_loc = set()
    for row, val1 in enumerate(level_description):
        for column, val2 in enumerate(val1):
            for element in val2:
                if element == 'player':
                    player_loc = (row, column)
                elif element == 'target':
                    target_loc.add((row, column))
                elif element == 'wall':
                    wall_loc.add((row, column))
                elif element == 'computer':
                    computer_loc.add((row, column))
                    
    return {'player': player_loc, 
            'target': target_loc, 
            'wall': wall_loc,
            'computer': computer_loc,
            'height': h,
            "width": w }


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    if game['target'] == set() or game['computer'] == set():
        return False
    if game['target'] == game['computer']:
        return True
    else:
        return False


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    return helper_step(game, direction)

def helper_step(game, direction):
    """
    Breaks the step function into the new position and a newer position 
    (the position following the new position) after a direction is input
    """
    new_pos = (game.get('player')[0] + direction_vector[direction][0], game.get('player')[1] + direction_vector[direction][1])
    newer_pos = (new_pos[0]+ direction_vector[direction][0], new_pos[1] + direction_vector[direction][1])
    return helper_step2(game, new_pos, newer_pos)

def helper_step2(game, new_pos, newer_pos):
    """
    Creates the conditions for object movement after a direction
    has been input """
    new_state = {'player': None, 
                'target': game.get('target').copy(), 
                'wall': game.get('wall').copy(),
                'computer': game.get('computer').copy(),
                'height': game.get('height'),
                'width': game.get('width') }
    if new_pos in game.get('wall'):
        new_state['player'] = game.get('player')
    elif new_pos in game.get('computer'):
        if newer_pos in game.get('computer') or newer_pos in game.get('wall'):
            new_state['player'] = game.get('player')
        else:
            new_state['player'] = new_pos
            new_state.get('computer').remove(new_pos)
            new_state.get('computer').add(newer_pos)   
    else:
        new_state['player'] = new_pos
    return new_state

    
    
def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    #create an empty board the same size as the original
    board = []
    for row in range(0, game['height']):
        board.append([])
        for column in range(0, game['width']):
            board[row].append([])
    board[game['player'][0]][game['player'][1]].append('player')
    object = ['target', 'wall', 'computer']
    for i in object:
        for j in game.get(i):
            board[j[0]][j[1]].append(i)
    return board
            


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
#     start = game['player']
#     curr = {game['player']}
#     paths = {game['player']: None}

#     while curr:
#         new = set()
#         for pos in curr:
#             for actedwith in acted_together[actor]:
#                 if actedwith not in paths:
#                     paths[actedwith] = actor
#                     new.add(actedwith)
#                     if goal_test_function(actedwith):
#                         paths[actedwith] = actor
#                         return path_finder(paths, actedwith)
#         curr = new
#     return None
# def path_finder(path_dict, initial_start):

#     path = []
#     curr = initial_start
#     while curr is not None:
#         path.append(curr)
#         curr = path_dict[curr]
#     return path[::-1]


def find_path(game, neighbors_function, victory_check):
    data = ((game['player']), tuple(i for i in game['computer']))
    if victory_check(game):
        return []
    agenda = [data]
    visited = {data}
    print(visited)
    while agenda:
        this_path = agenda.pop(0)
        # terminal_state = this_path[-1]
        # print(terminal_state)
        for neighbor in neighbors_function(game_state_creator(game, this_path)):
            
            if neighbor not in visited:
                # print(neighbor)
                new_path = this_path + (neighbor, )
                # print(new_path)
                # print(game_state_creator(game, neighbo))
                if victory_check(game_state_creator(game, neighbor)):
                    return direction_list(new_path)

                agenda.append(new_path)
                # print(agenda)
                visited.add(neighbor)
                
    return None
        
def neighbors_function(game):
    """
    Finds all possible neighbors
    """
    neighbors = []
    for direction in direction_vector:
        if game.get('player')[0]+ direction_vector[direction][0] in range(0, game['height']) and game.get('player')[1]+ direction_vector[direction][1] in range(0, game['width']):
            neighbors.append((helper_step(game, direction)['player'], tuple(i for i in (helper_step(game, direction)['computer']))))
    return neighbors

def game_state_creator(game, player_comp_tuple):
    return  {'player': player_comp_tuple[0], 
            'target': game['target'], 
            'wall': game['wall'],
            'computer': set(player_comp_tuple[1]),
            'height': game['height'],
            "width": game['width'] }

def direction_list(path):
    """
    Converts a list of tuples of player locations to directions
    """
    new_list = []
    for i in range(len(path)-1):
        change = tuple(zip(path[i], path[i+1]))
        new_list.append(direction_vector.keys()[direction_vector.values().index(change)])
    return new_list



if __name__ == "__main__":
    level =   [
   [['player'], ['computer'], ['target']],
   [[], ['computer'], ['target']],
   [[], ['computer'], ['target']]
]
    game = {'player': (0, 0), 
            'target': {(4,4)}, 
            'wall': set(),
            'computer': {(5,5)},
            'height': 6,
            "width": 6 }
    print(find_path(new_game(level), neighbors_function, victory_check))
    # print(neighbors_function(game))
    # print(new_game(level))
    # print(level)
    # print(dump_game(new_game(level)))