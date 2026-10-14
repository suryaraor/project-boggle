"""
This module contains the definition of an abstract game class.
Your concrete implementation inherits from the abstract class.
"""

from __future__ import annotations
import enum
from abc import ABC, abstractmethod
from typing import Collection, List, Optional, Tuple

from py_boggle.boggle_dictionary import BoggleDictionary


class BoggleGame(ABC):
    """
    This abstract class defines the game logic for Boggle.
    """

    @abstractmethod
    def new_game(self, size: int, cubefile: str, dictionary: BoggleDictionary) -> None:
        """Create a new Boggle game using a `size` x `size` board and
        the cubes specified in the file `cubefile`.

        Args:
            size: The size of the Boggle Board.
            cubefile: Name of a file containing the cubes.
            dict: A `BoggleDictionary` of valid words.

        Raises:
            OSError: The `cubefile` cannot be opened or read.

        Note:
            This is NOT the constructor for the class.
            Instead, it sets the internal state of the class to a new, playable game.
            Your `MyGameManager` constructor must not take any parameters.

        Example Usage
        -------
        dictionary = MyGameDictionary()
        dictionary.load_dictionary("words.txt")
        game = MyGameManager()
        game.new_game(4, "cubes.txt", dictionary)
        """
        raise NotImplementedError("abstract method `new_game`")

    @abstractmethod
    def get_board(self) -> List[List[str]]:
        """Return a `size` x `size` character matrix representing the
        Boggle board, in row-major order.
        """
        raise NotImplementedError("abstract method `get_board`")

    @abstractmethod
    def add_word(self, word: str) -> int:
        """Add a word to a list of guessed words.

        Each word can only be added once throughout the entirety of the
        game. This method should be case-insensitive.

        Args:
            word: The word to add.

        Returns:
            The point value of the word.

        If the word is invalid or the player cannot add the word, it
        is worth zero points and is not actually added to the guessed list.
        """
        raise NotImplementedError("abstract method `add_word`")

    @abstractmethod
    def get_last_added_word(self) -> Optional[List[Tuple[int, int]]]:
        """Return a list of coordinates showing the previous
        successfully added word.

        If there is no previous word, return `None`.

        The coordinates are listed by letter, then row, then column.
        That is, if `coords` is the return value, then:
        - `len(coords)` is the length of the last word added
        - `coords[0]` is the position of the first letter of the word
          - `coords[0][0]` is the row of the first letter of the word
          - `coords[0][1]` is the column of the first letter of the word
        - `coords[1]` is the position of the second letter...
        ... and so on
        """
        raise NotImplementedError("abstract method `get_last_added_word`")

    @abstractmethod
    def set_game(self, board: List[List[str]]) -> None:
        """Set the game board to the given board.

        The `board` should be in row-major order and must be square.

        Sets the current score to zero and resets guessed list.
        Other game-related parameters (like the dictionary) should be left as-is.
        """
        raise NotImplementedError("abstract method `set_game`")

    @abstractmethod
    def dictionary_driven_search(self) -> Set[str]:
        """Find all words using a dictionary-driven search.

        The dictionary-driven search attempts to find every word in the
        dictionary on the board.

        Returns:
            A set containing all words found on the board with no particular capitalization.
            Each returned word must be long enough to give points.
        """
        raise NotImplementedError("abstract method `dictionary_driven_search`")

    @abstractmethod
    def board_driven_search(self) -> Set[str]:
        """Find all words using a board-driven search.

        The board-driven search constructs a string using every path on
        the board and checks whether each string is a valid word in the
        dictionary.

        Returns:
            A set containing all words found on the board with no particular capitalization.
            Each returned word must be long enough to give points.
        """
        raise NotImplementedError("abstract method `board_driven_search`")


    @abstractmethod
    def get_score(self) -> int:
        """Returns the current player score"""
        raise NotImplementedError("abstract method `get_score`")
