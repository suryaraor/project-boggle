"""Extra checks for behavior the provided tests do not cover."""

import random
from pathlib import Path

import pytest
from py_boggle.trie_dictionary import TrieDictionary
from py_boggle.my_game_manager import MyGameManager, SHORT

# Resolved from this file so the tests also run from outside the repo folder.
ROOT = Path(__file__).resolve().parents[1]
CUBE_FILE = str(ROOT / "cubes.txt")
WORDS_FILE = str(ROOT / "words.txt")

example_board = [
    ["E", "E", "C", "A"],
    ["A", "L", "E", "P"],
    ["H", "N", "B", "O"],
    ["Q", "T", "T", "Y"],
]
LEAN_PATH = [(1, 1), (0, 0), (1, 0), (2, 1)]


@pytest.fixture(scope="module")
def full_dict():
    d = TrieDictionary()
    d.load_dictionary(WORDS_FILE)
    return d


@pytest.fixture
def game(full_dict):
    g = MyGameManager()
    g.new_game(4, CUBE_FILE, full_dict)
    g.set_game(example_board)
    return g


@pytest.fixture
def blank_game(full_dict):
    """A game with the dictionary attached. Each test sets its own board,
    which may be a different size from the 4x4 new_game rolls."""
    g = MyGameManager()
    g.new_game(4, CUBE_FILE, full_dict)
    return g


def small_dict(tmp_path, lines):
    path = tmp_path / "small.txt"
    path.write_text("\n".join(lines) + "\n")
    d = TrieDictionary()
    d.load_dictionary(str(path))
    return d


# ---- dictionary ----

def test_iterator_matches_sorted_file(full_dict):
    with open(WORDS_FILE) as fin:
        expected = [line.strip().lower() for line in fin if line.strip()]
    assert list(full_dict) == sorted(expected)


def test_iterators_are_independent(tmp_path):
    d = small_dict(tmp_path, ["pot", "potato", "pots", "zoo"])
    first, second = iter(d), iter(d)
    assert next(first) == "pot"
    assert next(first) == "potato"
    assert next(second) == "pot"
    assert list(first) == ["pots", "zoo"]
    assert list(second) == ["potato", "pots", "zoo"]


def test_word_is_also_prefix_and_case_insensitive(tmp_path):
    d = small_dict(tmp_path, ["pot", "potato"])
    assert d.contains("POT") and d.contains("Potato")
    assert d.is_prefix("pot") and d.is_prefix("POTA")
    # a leaf word is still a prefix of itself
    assert d.is_prefix("potato") and d.is_prefix("POTATO")
    assert not d.contains("pota")
    assert not d.is_prefix("potatoes")
    assert d.is_prefix("")


def test_load_cleans_case_whitespace_and_blank_lines(tmp_path):
    d = small_dict(tmp_path, ["  POT  ", "", "Potato\t", "   "])
    assert list(d) == ["pot", "potato"]
    assert not d.contains("")


def test_empty_dictionary():
    d = TrieDictionary()
    assert not d.contains("")
    assert not d.is_prefix("")
    assert not d.is_prefix("a")
    assert list(d) == []


def test_insert_ignores_empty_word():
    d = TrieDictionary()
    d._insert_word("")
    assert not d.contains("") and list(d) == []


# ---- game: human turn ----

def test_add_word_scoring_and_duplicates(game):
    assert game.add_word("PEACE") == 2
    assert game.get_last_added_word() == [(1, 3), (1, 2), (0, 3), (0, 2), (0, 1)]
    assert game.add_word("peace") == 0          # already guessed
    assert game.add_word("lean") == 1
    assert game.get_last_added_word() == LEAN_PATH
    assert game.get_score() == 3
    assert game.add_word("ace") == 0            # on the board but too short
    assert game.add_word("eecl") == 0           # on the board but not a word
    assert game.add_word("place") == 0          # word, but L and P are not adjacent
    assert game.add_word("pope") == 0           # word, but needs the single P twice
    assert game.get_score() == 3
    assert game.get_last_added_word() == LEAN_PATH


def test_last_added_word_is_a_copy(game):
    game.add_word("lean")
    game.get_last_added_word().append((9, 9))
    assert game.get_last_added_word() == LEAN_PATH


def test_handout_human_words_score_nine(game):
    # the human's eight words from handout section 2
    human = "lean pace bent peel pent clan clean lent".split()
    assert sum(game.add_word(w) for w in human) == 9
    assert game.get_score() == 9


def test_computer_words_score_53(game):
    # handout section 2: the computer's leftover words score 53
    human = set("lean pace bent peel pent clan clean lent".split())
    rest = game.board_driven_search() - human
    assert sum(len(w) - SHORT for w in rest) == 53


def test_find_word_backtracks_past_dead_end(blank_game):
    # The first b reached from a (row-major neighbor order) is (0, 1), which
    # has no c next to it. The search must back up and use the b at (2, 1).
    blank_game.set_game([
        ["a", "b", "x"],
        ["x", "x", "x"],
        ["x", "b", "c"],
    ])
    assert blank_game.find_word_in_board("abc") is None  # a is not next to (2, 1)
    blank_game.set_game([
        ["x", "b", "x"],
        ["x", "a", "x"],
        ["x", "b", "c"],
    ])
    assert blank_game.find_word_in_board("abc") == [(1, 1), (2, 1), (2, 2)]


def test_find_word_skips_path_search_when_letters_missing(blank_game, monkeypatch):
    # Without the letter-count check these calls would search for hours.
    blank_game.set_game([["e"] * 5 for _ in range(5)])
    monkeypatch.setattr(blank_game, "_find_path", lambda word: pytest.fail("path search ran"))
    assert blank_game.find_word_in_board("e" * 12 + "x") is None
    assert blank_game.find_word_in_board("e" * 26) is None  # more letters than cubes


def test_find_path_reports_deepest_prefix(blank_game):
    blank_game.set_game([["c", "a"], ["x", "x"]])
    assert blank_game._find_path("cat") == (None, 2)   # "ca" fits, "cat" does not
    assert blank_game._find_path("ca") == ([(0, 0), (0, 1)], 2)


def test_board_changed_without_set_game(blank_game):
    # The game must read the board as it is now, not a copy saved earlier.
    blank_game.set_game([["a", "b", "c", "d"], ["e", "f", "g", "h"],
                         ["i", "j", "k", "l"], ["m", "n", "o", "p"]])
    blank_game.board = [[c.lower() for c in row] for row in example_board]
    assert blank_game.find_word_in_board("peace") is not None
    assert blank_game.add_word("peace") == 2
    assert blank_game.dictionary_driven_search() == blank_game.board_driven_search()
    # get_board returns the live board (not a copy), so this edit reaches the game.
    blank_game.get_board()[0][0] = "z"
    assert blank_game.find_word_in_board("ze") == [(0, 0), (0, 1)]


def test_set_game_resets_score_and_last_word(game):
    game.add_word("peace")
    game.set_game(example_board)
    assert game.get_score() == 0
    assert game.get_last_added_word() is None
    assert game.add_word("peace") == 2


# ---- game: board setup ----

def test_new_game_board_shape(full_dict):
    g = MyGameManager()
    for size in (2, 3, 4):
        g.new_game(size, CUBE_FILE, full_dict)
        board = g.get_board()
        assert len(board) == size and all(len(row) == size for row in board)
        assert g.get_score() == 0 and g.get_last_added_word() is None


def test_new_game_rejects_too_few_cubes(full_dict):
    g = MyGameManager()
    with pytest.raises(ValueError):
        g.new_game(5, CUBE_FILE, full_dict)  # cubes.txt has only 16 cubes


def test_new_game_uses_first_n_squared_cubes(tmp_path, full_dict):
    # Handout 2.1: only the first n*n cubes in the file go on the board.
    path = tmp_path / "cubes.txt"
    path.write_text("AAAAAA\n" * 4 + "ZZZZZZ\n" * 12)
    g = MyGameManager()
    for _ in range(20):
        g.new_game(2, str(path), full_dict)
        assert g.get_board() == [["a", "a"], ["a", "a"]]


def test_empty_word_is_rejected(game):
    assert game.find_word_in_board("") is None
    assert game.add_word("") == 0
    assert game.get_score() == 0


def test_set_game_with_different_size(blank_game):
    blank_game.set_game([
        ["s", "t", "a", "r", "e"],
        ["x", "x", "x", "x", "s"],
        ["x", "x", "x", "x", "x"],
        ["x", "x", "x", "x", "x"],
        ["x", "x", "x", "x", "x"],
    ])
    assert blank_game.find_word_in_board("stares") == [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4)]
    assert "stares" in blank_game.board_driven_search()
    assert "stares" in blank_game.dictionary_driven_search()

    blank_game.set_game([["c", "a"], ["t", "s"]])
    found = blank_game.board_driven_search()
    assert found == blank_game.dictionary_driven_search()
    assert {"cats", "scat", "acts", "cast"} <= found
    assert blank_game.find_word_in_board("stares") is None


def test_rectangular_board(blank_game):
    blank_game.set_game([["c", "a", "t"], ["x", "x", "s"]])
    assert blank_game.find_word_in_board("cats") == [(0, 0), (0, 1), (0, 2), (1, 2)]
    blank_game.set_game([["c", "a"], ["x", "t"], ["x", "s"]])
    assert blank_game.find_word_in_board("cats") == [(0, 0), (0, 1), (1, 1), (2, 1)]
    assert "cats" in blank_game.board_driven_search()
    assert "cats" in blank_game.dictionary_driven_search()


# ---- game: computer turn ----

def check_found_words(game, found, dictionary):
    for w in found:
        assert len(w) > SHORT and dictionary.contains(w)
        path = game.find_word_in_board(w)
        assert path is not None, w
        assert len(path) == len(w) == len(set(path))
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            assert max(abs(r1 - r2), abs(c1 - c2)) == 1
        assert "".join(game.get_board()[r][c] for r, c in path) == w


def test_searches_agree_on_random_boards(blank_game, full_dict):
    rng = random.Random(395)
    for size in (2, 3, 4, 5, 8):
        for _ in range(2):
            board = [[rng.choice("etaoinshrdlucmpbgy") for _ in range(size)] for _ in range(size)]
            blank_game.set_game(board)
            by_board = blank_game.board_driven_search()
            assert by_board == blank_game.dictionary_driven_search()
            check_found_words(blank_game, by_board, full_dict)
