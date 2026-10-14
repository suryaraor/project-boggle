import copy
import random
import string
from typing import List, Optional, Set, Tuple

import pytest
from py_boggle import trie_dictionary


# read words file
WORDS_FILE = "words.txt"
words: Set[str] = set()
with open(WORDS_FILE, "r") as fin:
    for line in fin:
        line = line.strip().upper()
        words.add(line)


def test_contains_all_example():
    """Test that the contains() returns True for all of the words specified
    in the dictionary file.
    """

    # make dictionary
    game_dict = trie_dictionary.TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    for s in words:
        assert game_dict.contains(s)


def test_prefixes_example():
    """Test that is_prefix returns True for random prefixes of words
    in the dictionary file.
    """
    game_dict = trie_dictionary.TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    random.seed(12345)
    for s in words:
        idx = random.randint(0, len(s) - 1)
        pfx = s[:idx]
        assert game_dict.is_prefix(pfx)

def test_iterator_exception_example():
    """Tests that the GameDictionary iterator raises a StopIteration
    when all elements have been returned.

    Python iterators do not have a `hasNext()` method and only terminate
    when a StopIteration is raised. Many dictionary tests use the
    iterator and will hang if the exception is not raised.

    The iterator specification is provided in the handout.

    This function also tests that the empty dictionary is a valid state
    for the iterator.
    """

    game_dict = trie_dictionary.TrieDictionary()
    iterator = game_dict.__iter__()

    with pytest.raises(StopIteration):
        iterator.__next__()


def test_iterator_first_ten():
    """Tests that the iterator correctly returns the first 10 elements of the
    given dictionary.
    """
    
    game_dict = trie_dictionary.TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)
    iterator = game_dict.__iter__()

    word_list = []
    for s in iterator:
        if len(word_list) < 10:
            word_list.append(s.lower())
        else:
            break

    assert word_list == ['aa', 'aah', 'aahed', 'aahing', 'aahs', 'aal',
                         'aalii', 'aaliis', 'aals', 'aardvark']

def test_traversal():
    """Tests that a simple traversal works
    """

    game_dict = trie_dictionary.TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    tn1 = game_dict.traverse("potato")
    assert tn1.is_word

    tn2 = game_dict.traverse("potat")
    assert not tn2.is_word

    tn3 = game_dict.traverse("asdfkljsakldfj")
    assert tn3 is None

def test_root():
    """Tests that your root node obeys certain properties.
    """
    game_dict = trie_dictionary.TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    root = game_dict.root
    assert not root.is_word

    children_keys = set(root.children.keys())
    alphabet = set(string.ascii_lowercase)
    ALPHABET = set(string.ascii_uppercase)

    assert children_keys == alphabet or children_keys == ALPHABET
    

