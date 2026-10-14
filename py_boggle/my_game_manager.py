import random
from collections import Counter
from typing import Iterator, List, Optional, Set, Tuple

from py_boggle.boggle_dictionary import BoggleDictionary
from py_boggle.boggle_game import BoggleGame

"""
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************
************** READ THIS ***************

If you worked in a group on this project, please type the EIDs of your groupmates below (do not include yourself).
Leave it as TODO otherwise.
Groupmate 1: TODO
Groupmate 2: TODO
"""

SHORT = 3
CUBE_SIDES = 6

# listing the eight (row, col) steps to every horizontal, vertical and diagonal neighbor
DIRECTIONS = [(row_step, col_step) for row_step in (-1, 0, 1) for col_step in (-1, 0, 1)
              if (row_step, col_step) != (0, 0)]

CellPath = List[Tuple[int, int]]

class MyGameManager(BoggleGame):
    """Your implementation of `BoggleGame`
    """

    def __init__(self):
        """Constructs an empty Boggle Game.

        A newly-constructed game is unplayable.
        The `new_game` method will be called to initialize a playable game.
        Do not call `new_game` here.
        """

        self.board: List[List[str]] # current game board
        self.size: int # number of rows (boards may be rectangular)
        self.words: List[str] # player's current words
        self.dictionary: BoggleDictionary # the dictionary to use
        self.last_added_word: Optional[CellPath] # the position of the last added word, or None

    def new_game(self, size: int, cubefile: str, dictionary: BoggleDictionary) -> None:
        """Take the first size*size cubes in `cubefile`, shuffle them onto a
        fresh board, roll each one, and start a new game that checks words
        against `dictionary`. Raises ValueError if size < 2 or there are too
        few cubes.
        """
        # reading every cube line from the file
        with open(cubefile, 'r') as cube_file:
            cube_lines = [line.strip() for line in cube_file]
        all_cubes = [line.lower() for line in cube_lines if len(line) == CUBE_SIDES]
        # checking that the board size is playable with the cubes we have
        if size < 2 or len(all_cubes) < size*size:
            raise ValueError('ERROR: Invalid Dimensions (size, cubes)')
        # keeping only the first n*n cubes, as handout 2.1 asks
        chosen_cubes = all_cubes[:size*size]
        random.shuffle(chosen_cubes)
        self.dictionary = dictionary
        # rolling each cube and laying the board out row by row
        self.set_game([[random.choice(chosen_cubes[row*size + col])
                        for col in range(size)] for row in range(size)])

    def get_board(self) -> List[List[str]]:
        """Return the board as a list of rows of lowercase letters.

        This is the game's own board, not a copy, so edits to it change
        the game. The searches read the board fresh each time and stay
        correct after such an edit.
        """
        return self.board

    def find_word_in_board(self, word: str) -> Optional[CellPath]:
        """Return the (row, col) of each letter of `word` along one legal
        path on the board, or None if there is no such path.

        Does not check the dictionary or the minimum length; add_word does.
        """
        word = word.lower()
        # ruling the word out early when the board is missing letters for it
        if not self._has_enough_letters(word, self._count_board_letters()):
            return None
        return self._find_path(word)[0]

    def add_word(self, word: str) -> int:
        """Credit the player for `word` and return its points, or return 0
        without changing anything if the word is too short, already
        guessed, not in the dictionary, or not on the board.
        """
        word = word.lower()
        # checking length, repeats and the dictionary before touching the board
        if len(word) > SHORT and word not in self.words and self.dictionary.contains(word):
            word_path = self.find_word_in_board(word)
            if word_path is not None:
                # recording the accepted word and its path
                self.last_added_word = word_path
                self.words.append(word)
                return len(word) - SHORT
        return 0

    def get_last_added_word(self) -> Optional[CellPath]:
        """Return the path of the last word credited, or None if none yet."""
        # handing back a copy so a caller editing the list cannot change the game
        if self.last_added_word is None:
            return None
        return list(self.last_added_word)

    def set_game(self, board: List[List[str]]) -> None:
        """Replace the board (stored lowercase) and start scoring over.

        The guessed list, score and last word are cleared. The size comes
        from the new board, so it does not have to match new_game's size.
        The dictionary is left as it is.
        """
        # storing the new board in lowercase
        self.board = [[letter.lower() for letter in board_row] for board_row in board]
        self.size = len(self.board)
        # resetting the player's progress
        self.words = []
        self.last_added_word = None

    def get_score(self) -> int:
        """Return the player's total points so far."""
        # adding up the points for every accepted word
        return sum([len(word) - SHORT for word in self.words])

    def dictionary_driven_search(self) -> Set[str]:
        """Find all words using a dictionary-driven search.

        The dictionary-driven search attempts to find every word in the
        dictionary on the board.

        Returns:
            A set containing all words found on the board, in lowercase.
            Only words long enough to score (four or more letters) are kept.
        """
        found_words: Set[str] = set()
        letter_counts = self._count_board_letters()
        blocked_prefix: Optional[str] = None
        for dict_word in self.dictionary:
            dict_word = dict_word.lower()
            # skipping words too short to score
            if len(dict_word) <= SHORT:
                continue
            # skipping words that extend a prefix no path can spell. This is
            # correct in any order; because BoggleDictionary.__iter__ yields
            # words in sorted order, words sharing a blocked prefix arrive
            # together, so remembering only the latest one is enough.
            if blocked_prefix is not None and dict_word.startswith(blocked_prefix):
                continue
            # skipping words the board does not have the letters for
            if not self._has_enough_letters(dict_word, letter_counts):
                continue
            word_path, best_depth = self._find_path(dict_word)
            if word_path is not None:
                found_words.add(dict_word)
            else:
                # remembering the shortest prefix that no path spells
                blocked_prefix = dict_word[:best_depth + 1]
        return found_words

    def board_driven_search(self) -> Set[str]:
        """Find all words using a board-driven search.

        The board-driven search constructs a string using every path on
        the board and checks whether each string is a valid word in the
        dictionary.

        Returns:
            A set containing all words found on the board, in lowercase.
            Only words long enough to score (four or more letters) are kept.
        """
        found_words: Set[str] = set()
        visited_grid = [[False] * len(board_row) for board_row in self.board]
        # starting a path from every cell on the board
        for row, board_row in enumerate(self.board):
            for col in range(len(board_row)):
                self._gather_words(row, col, "", visited_grid, found_words)
        return found_words

    # Helpers below are not part of the BoggleGame interface.
    # _find_path/_extend_path find ONE path for a given word (human's turn and
    # dictionary search); _gather_words finds EVERY word (board search).

    def _adjacent_cells(self, row: int, col: int) -> Iterator[Tuple[int, int]]:
        """Yield the in-bounds cells adjacent to (row, col)."""
        for row_step, col_step in DIRECTIONS:
            next_row, next_col = row + row_step, col + col_step
            # bounding each column check by that row's own length
            if 0 <= next_row < len(self.board) and 0 <= next_col < len(self.board[next_row]):
                yield next_row, next_col

    def _count_board_letters(self) -> Counter:
        """Count how many cubes on the board show each letter.

        Rebuilt on every call instead of cached, so it is never out of date
        when the board is changed without going through set_game.
        """
        return Counter(letter for board_row in self.board for letter in board_row)

    def _has_enough_letters(self, word: str, letter_counts: Counter) -> bool:
        """Cheap test that runs before any path search: the board must have
        at least as many cubes showing each letter as `word` uses.

        The empty word is rejected here on purpose: the path search indexes
        word[0] and would raise IndexError on "".
        """
        # subtracting counters, which keeps only the letters the board is short of
        return bool(word) and not (Counter(word) - letter_counts)

    def _find_path(self, word: str) -> Tuple[Optional[CellPath], int]:
        """Look for `word` starting from every cell.

        Returns (path, depth). `path` is the first full path found, or
        None. `depth` is the length of the longest prefix of `word` that
        some path spelled. A failed search only gives up after trying every
        path from every cell, so when path is None, `depth` is the true
        maximum and no path spells word[:depth + 1].
        """
        path_so_far: CellPath = []
        visited_grid = [[False] * len(board_row) for board_row in self.board]
        best_depth = 0
        # trying every cell as the first letter
        for row, board_row in enumerate(self.board):
            for col in range(len(board_row)):
                best_depth = max(best_depth,
                                 self._extend_path(word, row, col, path_so_far, visited_grid))
                if best_depth == len(word):
                    return path_so_far, best_depth
        return None, best_depth

    def _extend_path(self, word: str, row: int, col: int,
                     path_so_far: CellPath, visited_grid: List[List[bool]]) -> int:
        """Try to continue `word` at (row, col), depth first.

        `path_so_far` holds the cells already used, so this cell has to
        show word[len(path_so_far)]. It fails right away if the letter is
        wrong or the cell is already on the path.

        Returns the most letters of `word` placed on any path tried,
        counting the cells already in `path_so_far`. If that equals
        len(word), `path_so_far` now holds the full path. Otherwise
        `path_so_far` and `visited_grid` are back to how they were on entry.
        """
        if visited_grid[row][col] or self.board[row][col] != word[len(path_so_far)]:
            # placing nothing new here, so the depth is what was matched before
            return len(path_so_far)
        path_so_far.append((row, col))
        best_depth = len(path_so_far)
        if best_depth == len(word):
            return best_depth
        visited_grid[row][col] = True
        # exploring each neighbor for the next letter
        for next_row, next_col in self._adjacent_cells(row, col):
            best_depth = max(best_depth,
                             self._extend_path(word, next_row, next_col, path_so_far, visited_grid))
            if best_depth == len(word):
                # leaving visited_grid dirty, since _find_path throws it away
                return best_depth
        # backtracking: freeing this cell so other paths can use it
        visited_grid[row][col] = False
        path_so_far.pop()
        return best_depth

    def _gather_words(self, row: int, col: int, prefix: str,
                      visited_grid: List[List[bool]], found_words: Set[str]) -> None:
        """Add the letter at (row, col) to `prefix` and record every word
        reachable from there into `found_words`.

        Stops as soon as the letters so far start no dictionary word. The
        cell is marked only after that check passes and is unmarked before
        returning, because one `visited_grid` is shared by the whole search.
        """
        current_string = prefix + self.board[row][col]
        # pruning this path when no dictionary word starts with it. is_prefix
        # and contains each walk from the dictionary root, which repeats work
        # but keeps the game working with any BoggleDictionary.
        if not self.dictionary.is_prefix(current_string):
            return
        # recording the string if it is a scoring word
        if len(current_string) > SHORT and self.dictionary.contains(current_string):
            found_words.add(current_string)
        visited_grid[row][col] = True
        # extending the path through every unused neighbor
        for next_row, next_col in self._adjacent_cells(row, col):
            if not visited_grid[next_row][next_col]:
                self._gather_words(next_row, next_col, current_string, visited_grid, found_words)
        # backtracking: freeing this cell so other paths can use it
        visited_grid[row][col] = False
