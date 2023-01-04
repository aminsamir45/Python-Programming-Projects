# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'

class PrefixTree:
    def __init__(self):
        self.value = None
        self.children = {}

    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree, or reassign the
        associated value if it is already present.  Assume that key is an
        immutable ordered sequence.  Raise a TypeError if the given key is not
        a string.
        """
        if type(key) != str:
            raise TypeError
        if key == '':
            self.value = value
        else:
            if key[0] not in self.children:
                self.children[key[0]] = PrefixTree()
            self.children[key[0]].__setitem__(key[1:], value)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.  If the given key is not in
        the prefix tree, raise a KeyError.  If the given key is not a string,
        raise a TypeError.
        """
        if type(key) != str:
            raise TypeError
        if key == '':
            return self.value
        else:
            if key[0] not in self.children:
                raise KeyError
            return self.children[key[0]].__getitem__(key[1:])

    def __delitem__(self, key):
        """
        Delete the given key from the prefix tree if it exists. If the given
        key is not in the prefix tree, raise a KeyError.  If the given key is
        not a string, raise a TypeError.
        """
        if type(key) != str:
            raise TypeError
        if key == '':
            self.value = None
        else:
            if key[0] not in self.children:
                raise KeyError
            self.children[key[0]].__delitem__(key[1:])
            if self.children[key[0]].value is None and self.children[key[0]].children == {}: 
                del self.children[key[0]]

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.  If the given
        key is not a string, raise a TypeError.
        """
        if type(key) != str:
            raise TypeError
        if key == '':
            return self.value is not None
        else:
            if key[0] not in self.children:
                return False
            return self.children[key[0]].__contains__(key[1:])

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        #generator = yield
        if self.value is not None:
            yield '', self.value
        for k, v in self.children.items():
            for key, value in v:
                yield k + key, value
    def get_subtree(self, key):
        """
        Return a new prefix tree containing all the keys/values in this prefix
        tree and its children.
        """
        if type(key) != str:
            raise TypeError
        if key == '':
            return self
        else:
            if key[0] not in self.children:
                raise KeyError
            return self.children[key[0]].get_subtree(key[1:])

    def get_value(self):
        return self.value



def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    tree = PrefixTree()
    for sentence in tokenize_sentences(text):
        for word in sentence.split():
            if word in tree:
                tree[word] += 1
            else:
                tree[word] = 1
    return tree

def autocomplete(tree, prefix, max_count=None):
    """
    tree is an instance of PrefixTree, prefix is a string, max_count is an integer or None. 
    Return a list of the max_count most-frequently-occurring keys that start with prefix. 
    In the case of a tie, you may output any of the most-frequently-occurring keys. If there 
    are fewer than max_count valid keys available starting with prefix, return only as many 
    s there are. The returned list may be in any order. If max_count is not specified, your 
    list should contain all keys that start with prefix.

    Return [] if prefix is not in the prefix tree. Raise a TypeError if the given prefix is not a string.
    """
    subtree = tree
    try:
        subtree = tree.get_subtree(prefix)
    except KeyError:
        return []
    value = subtree.get_value()    
    dictionary = {}
    keys = set()
    for k, v in subtree:
        word, dictionary[word] = prefix + k,  v
        keys.add(word)
    if subtree.get_value() is not None:
        dictionary[prefix] = value
        keys.add(prefix)
    return sorted(keys, key=lambda x: dictionary[x], reverse=True)[:max_count]

def edits(word):
    """
    Given a word, return a list of all valid edits of the word. The four edits are:
    1. Insert a character
    2. Delete a character
    3. Replace a character
    4. Transpose two adjacent characters
    """
    edit1 = {word[:i] + c + word[i:] for i in range(len(word) + 1) for c in ALPHABET}
    edit2 = {word[:i] + word[i+1:] for i in range(len(word))}
    edit3 = {word[:i] + c + word[i+1:] for i in range(len(word)) for c in ALPHABET}
    edit4 = {word[:i] + word[i+1] + word[i] + word[i+2:] for i in range(len(word) - 1)}
    return edit1 | edit2 | edit3 | edit4


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    autocompletion = autocomplete(tree, prefix, max_count)
    if max_count is None:
        max_count = len(autocompletion)
    if len(autocompletion) == max_count:
        return autocompletion
    else:
        edit = [word for word in edits(prefix) if word in tree]
        autocompletion.extend(sorted(edit, key=lambda x: tree[x], reverse=True)[:max_count - len(autocompletion)])
        return autocompletion


def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    ans = []
    def recurse(tree, pattern, word=''):
        if pattern == '':
            if isinstance(tree.value, int):
                ans.append((word, tree.value))
        elif pattern[:1] != '?' and pattern[:1] != '*':
            if pattern[:1] in tree.children:
                recurse(tree.children[pattern[:1]], pattern[1:], word+pattern[:1])
        elif pattern[:1] == '?':
            #
            for key in tree.children:
                recurse(tree.children[key], pattern[1:], word+key)
        elif pattern[:1] == '*':
            recurse(tree, pattern[1:], word)
            for key in tree.children:
                recurse(tree.children[key], pattern, word+key)
    recurse(tree, pattern)
    return ans



# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
