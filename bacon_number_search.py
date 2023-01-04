#!/usr/bin/env python3

import pickle
from shutil import move
from types import new_class

# NO ADDITIONAL IMPORTS ALLOWED!

bacon = 4724

def transform_data(raw_data):
    """
    Using the provided database, returns a dictionary of """
    #gather a dictionary with every actor as a key and every actor that the key actor has acted with as a value
    acted_together = {}
    #gather a dictionary with movies as a key and every actor in the movie as a value
    movies = {}
    for i in range(len(raw_data)):
        actor1 = raw_data[i][0]
        actor2 = raw_data[i][1]
        movie = raw_data[i][2]
        actor_list = [actor1, actor2]
        if actor1 not in acted_together:  
            acted_together[actor1] = {actor2}
        else:
            acted_together[actor1].add(actor2)
        if actor2 not in acted_together:  
            acted_together[actor2] = {actor1}
        else:
            acted_together[actor2].add(actor1)
        if movie not in movies:
            movies[movie] = {actor1, actor2}
        else:
            movies[movie].update(actor_list)
       
    #return set with set of actors who acted together and set of actors in a given movie
    return {'acted_together': acted_together,
            'movies': movies }


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Returns whether two actors have acted_together as either True or False 
    """
    #True if both actors are the same person
    if actor_id_1 == actor_id_2:
        return True
    #check database for tuple containing both actors
    #return True if tuple exists, else False
    else:
        return actor_id_1 in transformed_data['acted_together'][actor_id_2]


def actors_with_bacon_number(transformed_data, n):
    """
    Returns the set of people who have the same Bacon number
     """
    acted_together = transformed_data.get('acted_together')
    return bacon_number_search(acted_together, bacon, n)        

def bacon_number_search(transformed_data, actor, n):
    curr = {actor}
    cumulative = set()
    count = 0
    #base case - bacon number of 0
    if n == 0:
        if actor in transformed_data:
            return curr
        else:
            return set()
    #iterate through len(bacon number) and find all unique actors who are connected previous actors. Stop when len(bacon number) is reached.
    elif n>0:
        while count < n:
            new = set()
            if curr == set():
                return set()
            for actor in curr:
                for actedwith in find_acted_together(transformed_data, actor):
                    if actedwith not in cumulative:
                        cumulative.add(actedwith)
                        new.add(actedwith)
            curr = new
            count += 1
        if bacon in new:
            new.remove(bacon)
    
        return new
    else:
        return set()
    
    
            
def find_acted_together(transformed_data, actor):
    return transformed_data[actor]



def bacon_path(transformed_data, actor_id):
    """
    Returns list of connecting actors from bacon to any given actor. Returns none if such list DNE
    """
    return actor_to_actor_path(transformed_data, bacon, actor_id)
            

def path_finder(path_dict, initial_actor):

    actor_list = []
    curr = initial_actor
    while curr is not None:
        actor_list.append(curr)
        curr = path_dict[curr]
    return actor_list[::-1]



def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Returns list of connecting actors from any actor to another given actor. Returns none if such list DNE
    """
    return actor_path(transformed_data, actor_id_1, lambda search: search == actor_id_2)


def actor_path(transformed_data, actor_id_1, goal_test_function):
    """
    Returns shortest list of actors between an actor and another general datapoint
    """
    acted_together = transformed_data.get('acted_together')
    curr = {actor_id_1}
    paths = {actor_id_1: None}
    if goal_test_function(actor_id_1):
        return [actor_id_1]
    while curr:
        new = set()
        for actor in curr:
            for actedwith in acted_together[actor]:
                if actedwith not in paths:
                    paths[actedwith] = actor
                    new.add(actedwith)
                    if goal_test_function(actedwith):
                        paths[actedwith] = actor
                        return path_finder(paths, actedwith)
        curr = new
    return None



def movie_path(transformed_data, actor_id_1, actor_id_2):
    oactor_list = actor_path(transformed_data, actor_id_1, lambda search: search == actor_id_2)
    actor_list = oactor_list[::-1]
    movies = transformed_data.get('movies')
    acted_together = transformed_data.get('acted_together')
    movie_path = []
    for i in range(len(actor_list)-1):
        for movie in movies:
            if actor_list[i] and actor_list[i+1] in movies[movie] and movie not in movie_path:
                movie_path.append(movie)
                break
    return movie_path[::-1]

            
def actors_connecting_films(transformed_data, film1, film2):
    movies = transformed_data.get('movies')
    initial_actors = movies.get(film1)
    target_actors = set()
    target_actors.update(movies[film2])
    all_paths = []
    for i in initial_actors:
        new_path = actor_path(transformed_data, i, lambda search: search in target_actors)
        all_paths.append(new_path)
    return min(all_paths, key=len)
   
            


def get_keys_from_value(d, val):
    return [k for k, v in d.items() if v == val]


if __name__ == "__main__":
    with open("resources/names.pickle", "rb") as f:
        large = pickle.load(f)
    # print(large)
    print(large['Michael Yarmush'])
    print(large['Iva Ilakovac'])
    # # print(large['Kamatari Fujiwara'])
    # # print(actors_with_bacon_number(transform_data(large), 6))
    # # print(movie_path(transform_data(large), 1217850, 1345462))
    # list = [109614, 337339, 11908, 44909, 29938, 256690]
    # new_list = []
    # for i in list:
    #     new_list.append(get_keys_from_value(large, i))
    # print(new_list)