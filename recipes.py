# Recipes Database
# NO ADDITIONAL IMPORTS!
import re
import sys


sys.setrecursionlimit(20_000)
def dictionary_adder(d1, d2):
    """
    Adds two dictionaries together. Shared keys will have added values
"""
    return {i: d1.get(i, 0) + d2.get(i, 0) for i in set(d1).union(d2)}

def tuple_converter(old_tuple, new_tuple):
    """
    Converts a tuple to a list, changes the elements of the list,
    and returns a tuple of the list
    """
    new_list = list(old_tuple)
    if len(new_list) == 2:
        new_list[0] = new_tuple[0]
        new_list[1] = new_tuple[1]
    if len(new_list) == 3:
        new_list[0] = new_tuple[0]
        new_list[1] = new_tuple[1]
        new_list[2] = new_tuple[2]
    return tuple(new_list)

def copy_recipes(recipes):
    """
    Returns a deep copy of the recipes list.
    """
    #given a recipe, return a deep copy of the recipe
    new_recipes = []
    for item in recipes:
        if item[0] == 'compound':
            new_item = tuple_converter(item, (item[0], item[1], item[2][:]))
            new_recipes.append(new_item)
        if item[0] == 'atomic':
            new_item = tuple_converter(item, (item[0], item[1], item[2]))
            new_recipes.append(new_item)
    return new_recipes
def atomic_compound_recipes(recipes):
    """
    Given a list of recipes, produce a dictionary mapping food items to
    their full recipes.
    """
    compound = {}
    atomic = {}
    #create two new dictionaries for atomic and compound recipes
    for item in recipes:
        if item[0] == 'atomic':
            atomic[item[1]] = item[2]
 
        if item[0] == 'compound':
            #if the key is not in the dictionary, make a new key
            if item[1] not in compound:
                compound[item[1]] = [item[2]]
            #if the key is in the dictionary, append the value to the key
            else:
                compound[item[1]].append(item[2])
        else:
            atomic[item[1]] = item[2]
    return atomic, compound


def replace_item(recipes, old_name, new_name):
    """
    Returns a new recipes list based on the input list, where all mentions of
    the food item given by old_name are replaced with new_name.
    """
    new_recipes = copy_recipes(recipes)
    #iterate through the recipes list and replace the old_name with new_name
    for item in new_recipes:
        if item[1] == old_name:
            new_item = tuple_converter(item, (item[0], new_name, item[2]))
            new_recipes[new_recipes.index(item)] = new_item
        if item[0] == 'compound':
            for ingredient in item[2]:
                if ingredient[0] == old_name:
                    new_ingredient = tuple_converter(ingredient, (new_name, ingredient[1]))
                    new_recipes[new_recipes.index(item)][2][item[2].index(ingredient)] = new_ingredient
    return new_recipes

def lowest_cost(recipes, food_item, forbidden = []):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item. 
    """

    new_recipes = copy_recipes(recipes)
    atomic, compound = atomic_compound_recipes(new_recipes)
    results, temp_dict  = recurse_recipe_cost(new_recipes, food_item, atomic, compound, forbidden)
    return results if results != float('inf') else None

def scale(dictionary, scaler):
    for i in dictionary.keys():
        dictionary[i] *= scaler
    return dictionary

def recurse_recipe_cost(new_recipes, food_item, atomic, compound, forbidden = []):
    """
    Recurses through the recipes list and returns the lowest cost of a full recipe for the given food item.
    """
    if food_item in forbidden:
        return float('inf'), {}
    cost = []
    all_recipes = {}
    if food_item not in atomic and food_item not in compound:
        return float('inf'), {}
    #iterate through the recipes list and recursively find the price of an item
    for item in new_recipes:
        if item[1] == food_item:
            total_cost = 0
            recipe_dict = {}
            if item[0] == 'compound':
                for ingredient in item[2]:
                    if ingredient[0] in compound or ingredient[0] in atomic:
                        temp_cost, temp_dict = recurse_recipe_cost(new_recipes, ingredient[0], atomic, compound, forbidden)
                        total_cost += temp_cost * ingredient[1]
                        if temp_dict != {}:
                            recipe_dict = dictionary_adder(recipe_dict, scale(temp_dict[min(temp_dict.keys())], ingredient[1]))
                    else:
                        total_cost = float('inf')
                cost.append(total_cost)
                all_recipes[total_cost] = recipe_dict
            if item[0] == 'atomic':
                total_cost += item[2]
                cost.append(total_cost)
                if item[1] not in recipe_dict:
                    recipe_dict[item[1]] = 1
                else:
                    recipe_dict[item[1]] += 1
                all_recipes[total_cost] = recipe_dict
    return min(cost), all_recipes


def cheapest_flat_recipe(recipes, food_item, forbidden = []):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing a full recipe for
    the given food item.
    """
    new_recipes = copy_recipes(recipes)
    atomic, compound = atomic_compound_recipes(new_recipes)
    results, dictionary  = recurse_recipe_cost(new_recipes, food_item, atomic, compound, forbidden)
    if float('inf') in dictionary:
        del dictionary[float('inf')]
    # print(results, dictionary)
    if dictionary == {}:
        return None
    else: 
        return dictionary[results]



def all_flat_recurse(new_recipes, food_item, atomic, compound, forbidden = []):
    """
    Recurses through the recipes list and returns the lowest cost of a full recipe for the given food item.
    """
    combos = []
    def permutation_creator(combo, final):
        """
        Returns all the posssible permutations of elements
        """
        last = (len(combo) == 1)
        n = len(combo[0])
        for i in range(n):
            item = final + combo[0][i]
            if last:
                combos.append(item)
            else:
                permutation_creator(combo[1:], item)

    if food_item in forbidden:
        return {}
    if food_item not in atomic and food_item not in compound:
        return {}
    if food_item in atomic:
        return [{food_item: 1}]
    if food_item in compound:
        all_recipes = []
        for recipe in compound['food_item']:
            occurrence_list = []
            for ingredient in recipe:
                if ingredient in atomic:
                    all_recipes += {ingredient: 1}
                if ingredient in compound:
                    occurrences = len(compound[ingredient]) -1
                    occurrence_list.append(occurrences)
                for recipe in compound['food_item']:
                    for ingredient in recipe:
                        if ingredient in compound:
                            all_recipes += all_flat_recurse(new_recipes, ingredient, atomic, compound, forbidden)

    return all_recipes
   

def all_flat_recipes(recipes, food_item, forbidden = []):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.
    """
    new_recipes = copy_recipes(recipes)
    atomic, compound = atomic_compound_recipes(new_recipes)
    dictionary = all_flat_recurse(new_recipes, food_item, atomic, compound, forbidden)
    final_recipe_list = []
    for value in dictionary:
        final_recipe_list.append(dictionary[value])
    if final_recipe_list == []:
        return None
    else: 
        return final_recipe_list


if __name__ == "__main__":
    # you are free to add additional testing code here!
    pass
#     recipes = [
#     ('compound', 'milk', [('cow', 2), ('milking stool', 1)]),
#     ('compound', 'cheese', [('milk', 1), ('time', 1)]),
#     ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
#     ('atomic', 'milking stool', 5),
#     ('atomic', 'cutting-edge laboratory', 1000),
#     ('atomic', 'time', 10000),
#     ('atomic', 'cow', 100),
#     ]



#     example_recipes = [
#     ('compound', 'chili', [('beans', 3), ('cheese', 10), ('chili powder', 1), ('cornbread', 2), ('protein', 1)]),
#     ('atomic', 'beans', 5),
#     ('compound', 'cornbread', [('cornmeal', 3), ('milk', 1), ('butter', 5), ('salt', 1), ('flour', 2)]),
#     ('atomic', 'cornmeal', 7.5),
#     ('compound', 'burger', [('bread', 2), ('cheese', 1), ('lettuce', 1), ('protein', 1), ('ketchup', 1)]),
#     ('compound', 'burger', [('bread', 2), ('cheese', 2), ('lettuce', 1), ('protein', 2),]),
#     ('atomic', 'lettuce', 2),
#     ('compound', 'butter', [('milk', 1), ('butter churn', 1)]),
#     ('atomic', 'butter churn', 50),
#     ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
#     ('compound', 'cheese', [('milk', 1), ('time', 1)]),
#     ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
#     ('atomic', 'salt', 1),
#     ('compound', 'bread', [('yeast', 1), ('salt', 1), ('flour', 2)]),
#     ('compound', 'protein', [('cow', 1)]),
#     ('atomic', 'flour', 3),
#     ('compound', 'ketchup', [('tomato', 30), ('vinegar', 5)]),
#     ('atomic', 'chili powder', 1),
#     ('compound', 'ketchup', [('tomato', 30), ('vinegar', 3), ('salt', 1), ('sugar', 2), ('cinnamon', 1)]),  # the fancy ketchup
#     ('atomic', 'cow', 100),
#     ('atomic', 'milking stool', 5),
#     ('atomic', 'cutting-edge laboratory', 1000),
#     ('atomic', 'yeast', 2),
#     ('atomic', 'time', 10000),
#     ('atomic', 'vinegar', 20),
#     ('atomic', 'sugar', 1),
#     ('atomic', 'cinnamon', 7),
#     ('atomic', 'tomato', 13),
# ]   
