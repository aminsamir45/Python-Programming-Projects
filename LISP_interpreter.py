#!/usr/bin/env python3
import sys
import doctest

sys.setrecursionlimit(10_000)

# NO ADDITIONAL IMPORTS!
########
# REPL #
########


def repl(raise_all=False):
    global_frame = None
    while True:
        # read the input.  pressing ctrl+d exits, as does typing "EXIT" at the
        # prompt.  pressing ctrl+c moves on to the next prompt, ignoring
        # current input
        try:
            inp = input("in> ")
            if inp.strip().lower() == "exit":
                print("  bye bye!")
                return
        except EOFError:
            print()
            print("  bye bye!")
            return
        except KeyboardInterrupt:
            print()
            continue

        try:
            # tokenize and parse the input
            tokens = tokenize(inp)
            ast = parse(tokens)
            # if global_frame has not been set, we want to call
            # result_and_frame without it (which will give us our new frame).
            # if it has been set, though, we want to provide that value
            # explicitly.
            args = [ast]
            if global_frame is not None:
                args.append(global_frame)
            result, global_frame = result_and_frame(*args)
            # finally, print the result
            print("  out> ", result)
        except SchemeError as e:
            # if raise_all was given as True, then we want to raise the
            # exception so we see a full traceback.  if not, just print some
            # information about it and move on to the next step.
            #
            # regardless, all Python exceptions will be raised.
            if raise_all:
                raise
            print(f"{e.__class__.__name__}:", *e.args)
        print()

#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """
    pass

############################
# Tokenization and Parsing #
############################


def number_or_symbol(source):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('source')
    'source'
    """
    try:
        return int(source)
    except ValueError:
        try:
            return float(source)
        except ValueError:
            return source


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    #character by character
    result = ""

    for element in source.splitlines():
        for character in element:
            if character == '(' or character == ')':
                result += f' {character} '
            elif character == ";":
                break
            else:
                result += character
        result += " "
    return result.split()

operations = {
        "+": lambda args: sum(args),
        "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
        "*": lambda args: mult(args),
        "/": lambda args: 1 / args[0] if len(args) == 1 else (args[0] / mult(args[1:])),
        "**": lambda args: args[0] ** args[1],
         }
reverse_operations = {lambda args: sum(args): "+",
                      lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])): "-",  
                      lambda args: mult(args): "*",
                      lambda args: 1 / args[0] if len(args) == 1 else (args[0] / mult(args[1:])): "/",
                      lambda args: args[0] ** args[1]: "**",}
def parse(tokens):
    #if the number of open parenthesis is not equal to the number of closed parenthesis, raise an error
    if tokens.count('(') != tokens.count(')'):
        raise SchemeSyntaxError("Unbalanced parenthesis")
    if tokens[0] != '(' and len(tokens) > 1:
        raise SchemeSyntaxError("Expression must start with an open parenthesis")
    def parse_expression(tokens):
        if tokens[0] == '(':
            tokens.pop(0)
            result = []
            while tokens[0] != ')':
                result.append(parse_expression(tokens))
            tokens.pop(0)
            return result
        elif tokens[0] == ')':
            raise SchemeSyntaxError("Unexpected ')'")
        else:
            return number_or_symbol(tokens.pop(0))
    return parse_expression(tokens)

    #     if tokens[0] == '(':
    #         tokens.pop(0)
    #         expression = []
    #         while tokens[0] != ')':
    #             expression.append(parse_expression(tokens))
    #         tokens.pop(0)
    #         return expression
    #     elif tokens[0] == ')':
    #         raise SchemeSyntaxError("Unexpected ')'")
    #     elif tokens[0] in operations.keys():
    #         return reverse_operations[operations[tokens.pop(0)]]
    #     else:
    #         return number_or_symbol(tokens.pop(0))
    # return parse_expression(tokens)

######################
# Built-in Functions #
######################
class Frames():
    def __init__(self, parent=None):
        self.parent = parent
        if not self.parent:
            self.parent = scheme_builtins
        self.frame = {}
    def __setitem__(self, key, value):
        self.frame[key] = value
    def __getitem__(self, key):
        if key in self.frame:
            return self.frame[key]
        else:
            try:
                return self.parent[key]
            except:
                raise SchemeNameError("Variable not found")
    def __repr__(self):
        return f'{self.frame}'
    def __contains__(self, item):
        return item in self.frame or item in self.parent
    def set_frame(self, item, eval):
        if item not in self:
            raise SchemeNameError
        if item in self.frame:
            self.frame[item] = eval
        else:
            self.parent.set_frame(item, eval)
    def get_frame(self, item):
        if item in self.frame:
            return self.frame[item]
        if self.parent:
            return self.parent.get_frame(item)
        raise SchemeNameError
    def delete_item(self, key):
        if key in self.frame:
            return self.frame.pop(key)
        else:
            return SchemeNameError("Item not in frame")

class Function():
    def __init__(self, args, body, frame):
        self.args = args
        self.body = body
        self.frame = frame
    def __call__(self, items):
        if len(items) != len(self.args):
            raise SchemeEvaluationError("Invalid number of arguments")
        new_frame = Frames(self.frame)
        for i in range(len(items)):
            new_frame[self.args[i]] = items[i]
        return evaluate(self.body, new_frame)
    def __repr__(self):
        return 'function'

class Pair():
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr
    def get_car(self):
        return self.car
    def get_cdr(self):
        return self.cdr
    def index_recurse(self, index):
        if index == 0:
            return self
        try:
            self.cdr.index_recurse(index - 1)
        except:
            raise SchemeEvaluationError("Index out of range")
    def append_recurse(self, values):
        if self.cdr == nil():
            if values:
                return Pair(self.car, values[0].append_recurse(values))
            else:
                return Pair(self.car, values[0])
        try:
            return Pair(self.car, self.cdr.append_recurse(values))
        except:
            raise SchemeEvaluationError('Recursion Error')
    def __len__(self):
        if self.cdr == nil():
            return 1
        return 1 + len(self.cdr)
    def __repr__(self):
        return f'Pair({self.car}, {self.cdr})'

class nil():  
    def append_recursive(self, other):
        if len(other) != 1:
            return other[0].append_recursive(other[1:])
        return other[0]
    def index_recurse(self, index):
        return SchemeEvaluationError("Index out of range")
    def __eq__(self, other):
        return isinstance(other, nil)
    def __repr__(self):
        return 'nil'
    def __len__(self):
        return 0

def define_helper(args, frame):
    if isinstance(args[0], list):
        arg = Function(args[0][1:], args[1], Frames(frame))
        frame[args[0][0]] = arg
    else:
        arg = evaluate(args[1], frame)
        frame[args[0]] = arg 
    return arg
def lambda_helper(args, frame):
    return Function(args[0], args[1], frame)
def mult(args):
    if len(args) == 0:
        return 0
    result = 1
    for arg in args:
        result *= arg
    return result
def and_helper(args, frame):
    if len(args) == 0:
        return '#t'
    for arg in args:
        if evaluate(arg, frame) == '#f':
            return '#f'
    return '#t'
def or_helper(args, frame):
    if len(args) == 0:
        return '#f'
    for arg in args:
        if evaluate(arg, frame) == '#t':
            return '#t'
    return '#f'
def not_helper(args):
    if len(args) != 1:
        raise SchemeEvaluationError("Not takes only one argument")
    if evaluate(args[0]) == '#t':
        return '#f'
    return '#t'
def cons_helper(args):
    if len(args) != 2:
        raise SchemeEvaluationError("Cons takes only two arguments")
    return Pair(args[0], args[1])
def car_helper(args):
    if len(args) != 1 or args[0] == nil() or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].get_car()
def cdr_helper(args):
    if len(args) != 1 or args[0] == nil() or not isinstance(args[0], Pair):
        raise SchemeEvaluationError
    return args[0].get_cdr()
#can consider combining these two
def create_list(args):
    if len(args) == 0 or not args:
        return nil()
    return Pair(args[0], create_list(args[1:]))
def check_list(args):
    if isinstance(args[0], nil):
        return '#t'
    elif isinstance(args[0], Pair):
        return check_list([args[0].get_cdr()])
    return '#f'
def length_helper(args):
    try:
        return args[0].__len__()
    except:
        raise SchemeEvaluationError("Argument must be a linked-list")
def list_ref(args):
    if len(args) != 2:
        raise SchemeEvaluationError("List-ref takes two arguments")
    try:
        return args[0].index_recurse(args[1])
    except:
        raise SchemeEvaluationError("Index out of range")

def append_helper(args):
    for element in args:
        if type(element) != list:
            raise SchemeEvaluationError("Arguments must be lists")
    if len(args) == 0:
        return nil()
    if len(args) == 1:
        return args[0]
    if len(args) == 2:
        return args[0] + args[1]
    else:
        return args[0].append_recursive(args[1:])
def delete_helper(args, frame):
    return frame.delete_item(args[0])
def let_helper(args, frame):
    if len(args) != 2:
        raise SchemeEvaluationError("Let takes only two arguments")
    new_frame = Frames(frame)
    for element in args[0]:
        new_frame[element[0]] = evaluate(element[1], new_frame)
    return evaluate(args[1], new_frame)
def set_helper(args, frame):
    return frame.set_frame(args[0], evaluate(args[1], frame))

scheme_builtins = {
    "+": lambda args: sum(args),
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": lambda args: mult(args),
    "/": lambda args: 1 / args[0] if len(args) == 1 else (args[0] / mult(args[1:])),
    "**": lambda args: args[0] ** args[1],
    "equal?": lambda args: '#t' if all(arg == args[0] for arg in args) else '#f',
    ">": lambda args: '#t' if all(args[i] > args[i+1] for i in range(len(args)-1)) else '#f',
    "<": lambda args: '#t' if all(args[i] < args[i+1] for i in range(len(args)-1)) else '#f',
    ">=": lambda args: '#t' if all(args[i] >= args[i+1] for i in range(len(args)-1)) else '#f',
    "<=": lambda args: '#t' if all(args[i] <= args[i+1] for i in range(len(args)-1)) else '#f',
    "and": and_helper,
    "or": or_helper,
    "not": not_helper,
    "#t": '#t',
    "#f": '#f',
    "cons": cons_helper,
    "car": car_helper,
    "cdr": cdr_helper,
    "if": lambda args, frame: evaluate(args[1], frame) if evaluate(args[0], frame) == '#t' else evaluate(args[2], frame),
    "nil": nil(),
    "list": create_list,
    "list?": check_list,
    "list-ref": list_ref,
    "length": length_helper,
    "append": append_helper,
    "begin": lambda args: args[-1],
    "del": delete_helper,
    "let": let_helper,
    "set!": set_helper, 
    "define": define_helper,
    "lambda": lambda_helper
}

special_forms =  ['lambda', 'define', 'and', 'or', 'if', 'del', 'let', 'set!']

##############
# Evaluation #
##############
    
def result_and_frame(tree, current_frame = None):
    """
    returns a tuple with two elements: the result of the 
    evaluation and the frame in which the expression was evaluated
    """
    if not current_frame:
        current_frame = Frames(scheme_builtins)
    return evaluate(tree, current_frame), current_frame

def evaluate(tree, current_frame = None):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if current_frame is None:
        current_frame = Frames()
        global_frame = Frames(current_frame)
    if tree == []:
        raise SchemeEvaluationError("Empty expression")
    if not isinstance(tree, list):
        return current_frame[tree] if isinstance(tree, str) else tree
    # if isinstance(tree, list) and tree[0] not in current_frame:
    #     return SchemeEvaluationError("Cannot redefine built-in function")
    else:
        car, cdr = tree[0], tree[1:]
        arg = evaluate(car, current_frame)
        if callable(arg):
            if car in special_forms:
                return arg(cdr, current_frame)
            return arg([evaluate(element, current_frame) for element in cdr])
        else:
            raise SchemeEvaluationError("Cannot call non-function")

    # # raise SchemeEvaluationError
    # if current_frame is None:
    #     #if no functions, scheme_builtins is the global environment
    #     current_frame = scheme_builtins
    # #int or float
    # if isinstance(tree, (int, float)):
    #     return tree
    # #string
    # elif isinstance(tree, str):
    #     return current_frame.__getitem__(tree)
    # #list
    # elif isinstance(tree, list):
    #     #first element is a function
    #     if not isinstance(tree[0], str) and not isinstance(tree[0], list):
    #         raise SchemeEvaluationError("Invalid function")
    #     if tree[0] == 'define':
    #         # if len(tree) != 3:
    #         #     raise SchemeEvaluationError("Invalid number of arguments")
    #         if isinstance(tree[1], str):
    #             current_frame[tree[1]] = evaluate(tree[2], current_frame)
    #             return current_frame[tree[1]]
    #         elif isinstance(tree[1], list):
    #             current_frame[tree[1][0]] = Function(tree[1][1:], tree[2], current_frame)
    #             return current_frame[tree[1][0]]
    #     elif tree[0] == 'lambda':
    #         # if len(tree) != 3:
    #         #     raise SchemeEvaluationError("Invalid number of arguments")
    #         return Function(tree[1], tree[2], current_frame)
    #     elif tree[0] == 'if':
    #         if len(tree) != 4:
    #             raise SchemeEvaluationError("Invalid number of arguments")
    #         if evaluate(tree[1], current_frame):
    #             return evaluate(tree[2], current_frame)
    #         else:
    #             return evaluate(tree[3], current_frame)
    #     return evaluate(tree[0], current_frame)([evaluate(item, current_frame) for item in tree[1:]])

def evaluate_file(file_name, current_frame = None):
    """
    Evaluate the given file according to the rules of the Scheme
    language.

    Arguments:
        file_name (str): the name of the file to evaluate
    """
    with open(file_name) as f:
        return evaluate(parse(tokenize(f.read())), current_frame)

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    repl()
    # print(evaluate(3.14))
    # print(evaluate(['*', 3, 7, 2]))
    # print(evaluate(['*', 3, ['*', 7, 5]]))
    # print(evaluate([define, pi, 3.14]))
#     print(evaluate([
#   [
#     "define",
#     "spam",
#     "x"
#   ],
#   "eggs"

# ]))
