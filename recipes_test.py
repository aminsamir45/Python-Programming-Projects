#!/usr/bin/env python3
import os
import sys
import copy
import json
import pickle
import lab
import pytest

TEST_DIRECTORY = os.path.dirname(__file__)


example_recipes = [
    ('compound', 'chili', [('beans', 3), ('cheese', 10), ('chili powder', 1), ('cornbread', 2), ('protein', 1)]),
    ('atomic', 'beans', 5),
    ('compound', 'cornbread', [('cornmeal', 3), ('milk', 1), ('butter', 5), ('salt', 1), ('flour', 2)]),
    ('atomic', 'cornmeal', 7.5),
    ('compound', 'burger', [('bread', 2), ('cheese', 1), ('lettuce', 1), ('protein', 1), ('ketchup', 1)]),
    ('compound', 'burger', [('bread', 2), ('cheese', 2), ('lettuce', 1), ('protein', 2),]),
    ('atomic', 'lettuce', 2),
    ('compound', 'butter', [('milk', 1), ('butter churn', 1)]),
    ('atomic', 'butter churn', 50),
    ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
    ('compound', 'cheese', [('milk', 1), ('time', 1)]),
    ('compound', 'cheese', [('cutting-edge laboratory', 11)]),
    ('atomic', 'salt', 1),
    ('compound', 'bread', [('yeast', 1), ('salt', 1), ('flour', 2)]),
    ('compound', 'protein', [('cow', 1)]),
    ('atomic', 'flour', 3),
    ('compound', 'ketchup', [('tomato', 30), ('vinegar', 5)]),
    ('atomic', 'chili powder', 1),
    ('compound', 'ketchup', [('tomato', 30), ('vinegar', 3), ('salt', 1), ('sugar', 2), ('cinnamon', 1)]),  # the fancy ketchup
    ('atomic', 'cow', 100),
    ('atomic', 'milking stool', 5),
    ('atomic', 'cutting-edge laboratory', 1000),
    ('atomic', 'yeast', 2),
    ('atomic', 'time', 10000),
    ('atomic', 'vinegar', 20),
    ('atomic', 'sugar', 1),
    ('atomic', 'cinnamon', 7),
    ('atomic', 'tomato', 13),
]

def compare_recipe_list(expected, result):
    assert len(expected) == len(result), f'Expected recipes list of length {len(expected)} but got {len(result)}'
    assert type(expected) == type(result), f'Expected recipes list to be of type {type(expected)} but got {type(result)}'
    for item in result:
        assert isinstance(item, tuple), f'Expected all items in recipes to be a tuple but got {item}'
        assert len(item) == 3, f'Expected all items in recipes to have length 3 but got {len(item)} \n for {item}'
        a, b, c = item
        assert isinstance(a, str) and a in {'atomic', 'compound'}, f'Expected first item in recipe tuple to be atomic or compound but got {a} in {item}'
        assert isinstance(b, str), f'Expected second item in recipe tuple to be a string but got {type(b)} for {b} in {item}'
        expected_type = (list, ) if a == 'compound' else (int, float)
        assert isinstance(c, expected_type), f'Expected third item in recipe to be of type {expected_type} but got {type(c)} for {c} in {item}'

    exp = set((a, b, tuple(c) if a =='compound' else c) for a,b,c in expected)
    res = set((a, b, tuple(c) if a =='compound' else c) for a,b,c in result)
    assert res == exp, f'Found {len(res.intersection(exp))} matching recipes. Additional recipes: {len(res-exp)} \n {res-exp} \n Missing Recipes: {len(exp-res)} \n {exp-res}'


def canonize_flat_recipe(recipe):
    """
    Produce a nice immutable representation good for sorting and comparison.
    """
    if recipe is None:
        return None
    assert isinstance(recipe, dict), "Each recipe should be flat, e.g. a dictionary!"
    return frozenset(recipe.items())


def canonize_flat_recipes(recipes):
    """
    Like above, for lists of recipes
    """
    assert isinstance(recipes, list) and all(isinstance(i, dict) for i in recipes), "Recipes should be represented as a list of dictionaries!"
    return frozenset((canonize_flat_recipe(recipe) for recipe in recipes))

def _load_test(n):
    with open(os.path.join(TEST_DIRECTORY, 'test_recipes', f'big_recipes_{n:02d}.pickle'), 'rb') as f:
        return pickle.load(f)

def _filter_graph(graph, elts):
    elts = set(elts)
    return [i for i in graph if i[1] not in elts]


def test_replace_item_small():
    smaller_recipes = [
        ('compound', 'chili', [('cheese', 2), ('protein', 3), ('tomato', 2)]),
        ('compound', 'milk', [('cow', 1), ('milking stool', 1)]),
        ('compound', 'cheese', [('milk', 1), ('time', 1)]),
        ('compound', 'protein', [('cow', 1)]),
        ('atomic', 'cow', 100),
        ('atomic', 'tomato', 10),
        ('atomic', 'milking stool', 5),
        ('atomic', 'time', 10000),
    ]

    orig = copy.deepcopy(smaller_recipes)
    result = lab.replace_item(smaller_recipes, 'cow', 'soy')
    assert smaller_recipes == orig, "be careful not to mutate the input!"

    expected = [
        ('compound', 'chili', [('cheese', 2), ('protein', 3), ('tomato', 2)]),
        ('compound', 'milk', [('soy', 1), ('milking stool', 1)]),
        ('compound', 'cheese', [('milk', 1), ('time', 1)]),
        ('compound', 'protein', [('soy', 1)]),
        ('atomic', 'soy', 100),
        ('atomic', 'tomato', 10),
        ('atomic', 'milking stool', 5),
        ('atomic', 'time', 10000),
    ]

    compare_recipe_list(expected, result)

    # compare missing ingredient
    result = lab.replace_item(smaller_recipes, 'chocolate', 'soy')
    assert smaller_recipes == orig, "be careful not to mutate the input!"
    compare_recipe_list(smaller_recipes, result)


@pytest.mark.parametrize('testnum', range(5))
def test_replace_item_big(testnum):
    dbs = {}
    for k in ('in', 'out'):
        test_filename = os.path.join(TEST_DIRECTORY, 'test_recipes', f'replace_{k}_tests.pickle')
        with open(test_filename, 'rb') as f:
            dbs[k] = pickle.load(f)['replace_item']
    for i in range(testnum*9, (testnum+1)*9):
        inp = dbs['in'][i]
        orig = copy.deepcopy(inp)
        result = lab.replace_item(*inp)
        assert inp == orig, 'be careful not to mutate the input!'
        exp = dbs['out'][i]
        compare_recipe_list(exp, result)


def test_lowest_cost_examples_all_included():
    orig = copy.deepcopy(example_recipes)

    # atomic food items, should just return their costs
    assert lab.lowest_cost(example_recipes, 'time') == 10000
    assert lab.lowest_cost(example_recipes, 'salt') == 1
    assert abs(lab.lowest_cost(example_recipes, 'cornmeal') - 7.5) <= 1e-6

    # compound food items, only one layer deep
    assert lab.lowest_cost(example_recipes, 'protein') == 100
    assert lab.lowest_cost(example_recipes, 'milk') == 105
    assert lab.lowest_cost(example_recipes, 'bread') == 9

    # two layers
    assert lab.lowest_cost(example_recipes, 'cheese') == 10105

    # more complex
    assert lab.lowest_cost(example_recipes, 'burger') == 10685
    assert lab.lowest_cost(example_recipes, 'chili') == 102985

    assert example_recipes == orig, 'be careful not to mutate the input!'


@pytest.mark.parametrize('testnum', range(11))
def test_lowest_cost_big_all_included(testnum):
    for i in range(testnum*5, (testnum+1)*5):
        test_data = _load_test(i)
        graph = test_data['graph']
        target = test_data['target']
        orig_graph = copy.deepcopy(graph)
        result = lab.lowest_cost(graph, target)
        assert graph == orig_graph, "be careful not the change the input!"
        assert result == test_data['orig_min']


def test_lowest_cost_examples_excluded():
    graph = _filter_graph(example_recipes, ('cow',))
    orig = copy.deepcopy(graph)

    # atomic food items, should just return their costs
    assert lab.lowest_cost(graph, 'time') == 10000
    assert lab.lowest_cost(graph, 'salt') == 1
    assert abs(lab.lowest_cost(graph, 'cornmeal') - 7.5) <= 1e-6

    # compound food items, only one layer deep
    assert lab.lowest_cost(graph, 'protein') is None
    assert lab.lowest_cost(graph, 'milk') is None
    assert lab.lowest_cost(graph, 'bread') == 9

    # two layers
    assert lab.lowest_cost(graph, 'cheese') == 11000

    # more complex
    assert lab.lowest_cost(graph, 'burger') == None
    assert lab.lowest_cost(graph, 'chili') == None

    assert graph == orig, 'be careful not to mutate the input!'



def test_lowest_cost_more_examples_excluded():
    with open(os.path.join(TEST_DIRECTORY, 'test_recipes', 'examples_filter.pickle'), 'rb') as f:
        test_data = pickle.load(f)

    for (target, filt) in test_data:
        graph = _filter_graph(example_recipes, filt)
        orig = copy.deepcopy(graph)
        result = lab.lowest_cost(graph, target)
        assert graph == orig, 'be careful not to mutate the input!'
        assert result == test_data[(target, filt)][1]


@pytest.mark.parametrize('testnum', range(11))
def test_lowest_cost_big_excluded(testnum):
    for i in range(testnum*5, (testnum+1)*5):
        test_data = _load_test(i)
        target = test_data['target']
        for filt, expected in [
                ('change_filter', test_data['change_min']),
                ('none_filter', None),
                ('same_filter', test_data['orig_min']),
        ]:
            graph = _filter_graph(test_data['graph'], test_data[filt])
            orig_graph = copy.deepcopy(graph)
            result = lab.lowest_cost(graph, target)
            assert graph == orig_graph, "be careful not the change the input!"
            assert result == expected


def test_lowest_cost_examples_forbidden():
    orig = copy.deepcopy(example_recipes)

    # atomic food items, should just return their costs
    assert lab.lowest_cost(example_recipes, 'time', ('cow')) == 10000
    assert lab.lowest_cost(example_recipes, 'salt', ('cow')) == 1
    assert abs(lab.lowest_cost(example_recipes, 'cornmeal', ('cow')) - 7.5) <= 1e-6

    # compound food items, only one layer deep
    assert lab.lowest_cost(example_recipes, 'protein', ('cow')) is None
    assert lab.lowest_cost(example_recipes, 'milk', ('cow')) is None
    assert lab.lowest_cost(example_recipes, 'bread', ('cow')) == 9

    # two layers
    assert lab.lowest_cost(example_recipes, 'cheese', ('cow')) == 11000

    # more complex
    assert lab.lowest_cost(example_recipes, 'burger', ('cow')) == None
    assert lab.lowest_cost(example_recipes, 'chili', ('cow')) == None

    assert example_recipes == orig, 'be careful not to mutate the input!'



def test_lowest_cost_more_examples_forbidden():
    with open(os.path.join(TEST_DIRECTORY, 'test_recipes', 'examples_filter.pickle'), 'rb') as f:
        test_data = pickle.load(f)

    for (target, filt) in test_data:
        orig = copy.deepcopy(example_recipes)
        result = lab.lowest_cost(example_recipes, target, filt)
        assert example_recipes == orig, 'be careful not to mutate the input!'
        assert result == test_data[(target, filt)][1]


@pytest.mark.parametrize('testnum', range(11))
def test_lowest_cost_big_forbidden(testnum):
    for i in range(testnum*5, (testnum+1)*5):
        test_data = _load_test(i)
        target = test_data['target']
        for filt, expected in [
                ('change_filter', test_data['change_min']),
                ('none_filter', None),
                ('same_filter', test_data['orig_min']),
        ]:
            graph = test_data['graph']
            orig_graph = copy.deepcopy(graph)
            result = lab.lowest_cost(graph, target, test_data[filt])
            assert graph == orig_graph, "be careful not the change the input!"
            assert result == expected


@pytest.mark.parametrize('testnum', range(5))
def test_lowest_cost_big_excluded_forbidden(testnum):
    for i in range(testnum*11, (testnum+1)*11):
        test_data = _load_test(i)
        target = test_data['target']
        for filt, expected in [
                ('change_filter', test_data['change_min']),
                ('none_filter', None),
                ('same_filter', test_data['orig_min']),
        ]:
            graph = _filter_graph(test_data['graph'], test_data[filt][::2])
            orig_graph = copy.deepcopy(graph)
            result = lab.lowest_cost(graph, target, test_data[filt][1::2])
            assert graph == orig_graph, "be careful not the change the input!"
            assert result == expected


def test_recipe_examples():
    orig = copy.deepcopy(example_recipes)

    # atomic food items, should just return their costs
    assert lab.cheapest_flat_recipe(example_recipes, 'time') == {'time': 1}
    assert lab.cheapest_flat_recipe(example_recipes, 'salt') == {'salt': 1}

    # compound food items, only one layer deep
    assert lab.cheapest_flat_recipe(example_recipes, 'protein') == {'cow': 1}
    assert lab.cheapest_flat_recipe(example_recipes, 'protein', ('cow',)) is None

    assert lab.cheapest_flat_recipe(example_recipes, 'milk') == {'cow': 1, 'milking stool': 1}
    assert lab.cheapest_flat_recipe(example_recipes, 'bread') == {'flour': 2, 'salt': 1, 'yeast': 1}

    # two layers
    assert lab.cheapest_flat_recipe(example_recipes, 'cheese') == {'cow': 1, 'milking stool': 1, 'time': 1}
    assert lab.cheapest_flat_recipe(example_recipes, 'cheese', ('milking stool',)) == {'cutting-edge laboratory': 11}
    assert lab.cheapest_flat_recipe(example_recipes, 'cheese', ('milking stool', 'cutting-edge laboratory')) is None

    # more complex
    assert lab.cheapest_flat_recipe(example_recipes, 'burger') == {'yeast': 2, 'salt': 3, 'flour': 4, 'cow': 2, 'milking stool': 1, 'time': 1, 'lettuce': 1, 'tomato': 30, 'vinegar': 3, 'sugar': 2, 'cinnamon': 1}
    assert lab.cheapest_flat_recipe(example_recipes, 'burger', ('vinegar',)) == {'yeast': 2, 'salt': 2, 'flour': 4, 'cow': 4, 'milking stool': 2, 'time': 2, 'lettuce': 1}
    assert lab.cheapest_flat_recipe(example_recipes, 'burger', ('vinegar','milk')) == {'yeast': 2, 'salt': 2, 'flour': 4, 'cutting-edge laboratory': 22, 'lettuce': 1, 'cow': 2}


    assert example_recipes == orig, 'be careful not to mutate the input!'



@pytest.mark.parametrize('testnum', range(5))
def test_recipe_big_all_included(testnum):
    for i in range(testnum*11, (testnum+1)*11):
        test_data = _load_test(i)
        target = test_data['target']
        graph = test_data['graph']
        orig_graph = copy.deepcopy(graph)
        result = lab.cheapest_flat_recipe(graph, target)
        assert graph == orig_graph, "be careful not the change the input!"
        assert canonize_flat_recipe(result) == canonize_flat_recipe(test_data['orig_min_recipe'])


def test_recipe_more_examples_excluded():
    with open(os.path.join(TEST_DIRECTORY, 'test_recipes', 'examples_filter.pickle'), 'rb') as f:
        test_data = pickle.load(f)

    for (target, filt) in test_data:
        graph = _filter_graph(example_recipes, filt)
        orig = copy.deepcopy(graph)
        result = lab.cheapest_flat_recipe(graph, target)
        assert graph == orig, 'be careful not to mutate the input!'
        assert result == test_data[(target, filt)][0]


@pytest.mark.parametrize('testnum', range(5))
def test_recipe_big_excluded(testnum):
    for i in range(testnum*11, (testnum+1)*11):
        test_data = _load_test(i)
        target = test_data['target']
        for filt, expected in [
                ('change_filter', test_data['change_min_recipe']),
                ('none_filter', None),
                ('same_filter', test_data['orig_min_recipe']),
        ]:
            graph = _filter_graph(test_data['graph'], test_data[filt])
            orig_graph = copy.deepcopy(graph)
            result = lab.cheapest_flat_recipe(graph, target)
            assert graph == orig_graph, "be careful not the change the input!"
            assert canonize_flat_recipe(result) == canonize_flat_recipe(expected)


def test_recipe_more_examples_forbidden():
    with open(os.path.join(TEST_DIRECTORY, 'test_recipes', 'examples_filter.pickle'), 'rb') as f:
        test_data = pickle.load(f)

    for (target, filt) in test_data:
        orig = copy.deepcopy(example_recipes)
        result = lab.cheapest_flat_recipe(example_recipes, target, filt)
        assert example_recipes == orig, 'be careful not to mutate the input!'
        assert result == test_data[(target, filt)][0]


@pytest.mark.parametrize('testnum', range(5))
def test_recipe_big_forbidden(testnum):
    for i in range(testnum*11, (testnum+1)*11):
        test_data = _load_test(i)
        target = test_data['target']
        for filt, expected in [
                ('change_filter', test_data['change_min_recipe']),
                ('none_filter', None),
                ('same_filter', test_data['orig_min_recipe']),
        ]:
            graph = test_data['graph']
            orig_graph = copy.deepcopy(graph)
            result = lab.cheapest_flat_recipe(graph, target, test_data[filt])
            assert graph == orig_graph, "be careful not the change the input!"
            assert canonize_flat_recipe(result) == canonize_flat_recipe(expected)


@pytest.mark.parametrize('testnum', range(5))
def test_recipe_big_excluded_forbidden(testnum):
    for i in range(testnum*11, (testnum+1)*11):
        test_data = _load_test(i)
        target = test_data['target']
        for filt, expected in [
                ('change_filter', test_data['change_min_recipe']),
                ('none_filter', None),
                ('same_filter', test_data['orig_min_recipe']),
        ]:
            graph = _filter_graph(test_data['graph'], test_data[filt][::2])
            orig_graph = copy.deepcopy(graph)
            result = lab.cheapest_flat_recipe(graph, target, test_data[filt][1::2])
            assert graph == orig_graph, "be careful not the change the input!"
            assert canonize_flat_recipe(result) == canonize_flat_recipe(expected)


def test_all_recipes_examples():
    orig = copy.deepcopy(example_recipes)

    # atomic food items, should just return their costs
    assert lab.all_flat_recipes(example_recipes, 'time') == [{'time': 1}]
    assert lab.all_flat_recipes(example_recipes, 'salt') == [{'salt': 1}]

    # compound food items, only one layer deep
    assert lab.all_flat_recipes(example_recipes, 'protein') == [{'cow': 1}]
    assert lab.all_flat_recipes(example_recipes, 'protein', ('cow',)) == []

    assert lab.all_flat_recipes(example_recipes, 'milk') == [{'cow': 1, 'milking stool': 1}]
    assert lab.all_flat_recipes(example_recipes, 'bread') == [{'flour': 2, 'salt': 1, 'yeast': 1}]

    # two layers
    assert canonize_flat_recipes(lab.all_flat_recipes(example_recipes, 'cheese')) == canonize_flat_recipes([{'cow': 1, 'milking stool': 1, 'time': 1}, {'cutting-edge laboratory': 11}])
    assert lab.all_flat_recipes(example_recipes, 'cheese', ('milking stool',)) == [{'cutting-edge laboratory': 11}]
    assert lab.all_flat_recipes(example_recipes, 'cheese', ('milking stool', 'cutting-edge laboratory')) == []

    # more complex
    burgers = [
        {'yeast': 2, 'salt': 2, 'flour': 4, 'cow': 4, 'milking stool': 2, 'time': 2, 'lettuce': 1},
        {'yeast': 2, 'salt': 2, 'flour': 4, 'cutting-edge laboratory': 22, 'lettuce': 1, 'cow': 2},
        {'yeast': 2, 'salt': 3, 'flour': 4, 'cow': 2, 'milking stool': 1, 'time': 1, 'lettuce': 1, 'tomato': 30, 'vinegar': 3, 'sugar': 2, 'cinnamon': 1},
        {'yeast': 2, 'salt': 2, 'flour': 4, 'cow': 2, 'milking stool': 1, 'time': 1, 'lettuce': 1, 'tomato': 30, 'vinegar': 5},
        {'yeast': 2, 'salt': 3, 'flour': 4, 'cutting-edge laboratory': 11, 'lettuce': 1, 'cow': 1, 'tomato': 30, 'vinegar': 3, 'sugar': 2, 'cinnamon': 1},
        {'yeast': 2, 'salt': 2, 'flour': 4, 'cutting-edge laboratory': 11, 'lettuce': 1, 'cow': 1, 'tomato': 30, 'vinegar': 5}
    ]

    assert canonize_flat_recipes(lab.all_flat_recipes(example_recipes, 'burger')) == canonize_flat_recipes(burgers)

    burgers2 = [
        {'yeast': 2, 'salt': 3, 'flour': 4, 'cutting-edge laboratory': 11, 'lettuce': 1, 'cow': 1, 'tomato': 30, 'vinegar': 3, 'sugar': 2, 'cinnamon': 1},
        {'yeast': 2, 'salt': 2, 'flour': 4, 'cutting-edge laboratory': 11, 'lettuce': 1, 'cow': 1, 'tomato': 30, 'vinegar': 5},
        {'yeast': 2, 'salt': 2, 'flour': 4, 'cutting-edge laboratory': 22, 'lettuce': 1, 'cow': 2}
    ]
    assert canonize_flat_recipes(lab.all_flat_recipes(example_recipes, 'burger', ('milk',))) == canonize_flat_recipes(burgers2)

    assert example_recipes == orig, 'be careful not to mutate the input!'


@pytest.mark.parametrize('testnum', range(11))
def test_all_recipes_big(testnum):
    for i in range(testnum*5, (testnum+1)*5):
        test_data = _load_test(i)
        target = test_data['target']
        test_data['identity_filter'] = ()
        for filt, expected in [
                ('identity_filter', test_data['orig_all']),
                ('change_filter', test_data['change_all']),
                ('none_filter', []),
                ('same_filter', test_data['same_all']),
        ]:
            for graph, filter_ in [(_filter_graph(test_data['graph'], test_data[filt]), ()),
                                   (test_data['graph'], test_data[filt]),
                                   (_filter_graph(test_data['graph'], test_data[filt][1::2]), test_data[filt][::2])]:
                orig_graph = copy.deepcopy(graph)
                result = lab.all_flat_recipes(graph, target, filter_)
                print(result)
                assert graph == orig_graph, "be careful not the change the input!"
                assert canonize_flat_recipes(result) == canonize_flat_recipes(expected)



if __name__ == "__main__":
    import sys
    res = pytest.main(["-k", " or ".join(sys.argv[1:]), "-v", __file__])
