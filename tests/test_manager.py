import copy
import random
import string
from typing import List, Optional, Set, Tuple

import pytest
from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.trie_dictionary import TrieDictionary
from py_boggle.boggle_game import BoggleGame
from py_boggle.my_game_manager import MyGameManager


# read words file
CUBE_FILE = "cubes.txt"
WORDS_FILE = "words.txt"
words: Set[str] = set()
with open(WORDS_FILE, "r") as fin:
    for line in fin:
        line = line.strip().upper()
        words.add(line)

# handout
example_board = [
    ["E", "E", "C", "A"],
    ["A", "L", "E", "P"],
    ["H", "N", "B", "O"],
    ["Q", "T", "T", "Y"],
]
example_words = set("""
alec alee anele becap bent benthal blae blah blent bott cape capelan capo celeb cent
cento clan clean elan hale hant lane lean leant leap lent lento neap open pace peace
peel pele penal pent thae than thane toby toecap tope topee
""".upper().strip().split())

def test_word_search():
    """Tests a simple .find_word_in_board()
    """

    game_dict = TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    game = MyGameManager()
    game.new_game(len(example_board), CUBE_FILE, game_dict)
    game.set_game(example_board)

    assert game.find_word_in_board("asdf") is None
    assert game.find_word_in_board("O") == [(2,3)]
    assert game.find_word_in_board("blah") == [(2,2), (1,1), (1,0), (2,0)]
    assert game.find_word_in_board("pope") is None


def _check_all_words(game: BoggleGame, expected: Set[str], tactic: str) -> Tuple[bool, str]:
    """Test the words returned by get_all_words against our word set.

    Args:
        game: a game with the appropriate search tactic set
        expected: the expected set of words
        tactic: "board" or "dict"
    Returns:
        Tuple[bool, str]
        The bool indicates whether this check passed.
        The str is a comment for an assertion failure
    """
    game_word_set: Set[str] = set()
    if tactic == "board":
        all_words = game.board_driven_search()
    elif tactic == "dict":
        all_words = game.dictionary_driven_search()
    else:
        assert False, f"Invalid tactic: {tactic}"

    for word in all_words:
        if len(word) < 4:
            return (False, "returns words with length <4")
        game_word_set.add(word.upper())

    if game_word_set == expected:
        return (True, "")
    elif game_word_set < expected:
        # proper subset
        return (False, "fails to find all words")
    else:
        # if `game_word_set` is not a subset of `expected`,
        # then it must contain words that are not in `expected`
        return (False, "finds extraneous words")


def test_board_tactic_example():
    """Tests the board driven search on the example board.
    """
    game_dict = TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    game = MyGameManager()
    game.new_game(len(example_board), CUBE_FILE, game_dict)
    game.set_game(example_board)

    result = _check_all_words(game, example_words, "board")
    comment = f"Your board search {result[1]} when using our game board"

    assert result[0], comment


def test_dictionary_tactic_example():
    """Tests the dictionary driven search on the example board.
    """
    game_dict = TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    game = MyGameManager()
    game.new_game(len(example_board), CUBE_FILE, game_dict)
    game.set_game(example_board)

    result = _check_all_words(game, example_words, "dict")
    comment = f"Your dictionary search {result[1]} when using our game board"

    assert result[0], comment

def test_non_4x4_board():
    """Test a 3x3 board
    """

    game_dict = TrieDictionary()
    game_dict.load_dictionary(WORDS_FILE)

    game = MyGameManager()

    for _ in range(10):
        game.new_game(3, CUBE_FILE, game_dict)
        game.set_game([["Z", "Z", "Z"], ["Z", "Z", "Z"], ["Z", "Z", "Z"]])

        result = _check_all_words(game, set(), "board")
        comment = f"Your board search {result[1]} when using our game board"

        assert result[0], comment


