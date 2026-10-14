import typing
from typing import Optional, Dict

from py_boggle.boggle_dictionary import BoggleDictionary


class TrieNode:
    """
    Our TrieNode class. Feel free to add new properties/functions, but
    DO NOT edit the names of the given properties (children and is_word).
    """
    def __init__(self):
        self.children : Dict[str, TrieNode] = {} # maps a child letter to its TrieNode class
        self.is_word = False # whether or not this Node is a valid word ending


class TrieDictionary(BoggleDictionary):
    """
    BoggleDictionary backed by a trie. Words are stored lowercase, one
    letter per level, so lookups cost the length of the word, not the
    size of the dictionary.
    Do NOT change the name of self.root, as our autograder will manually traverse using self.root
    """

    def __init__(self):
        self.root : TrieNode = TrieNode()

    def load_dictionary(self, filename: str) -> None:
        # adding every word whatever its length; _insert_word lowercases and skips blanks
        with open(filename) as words_file:
            for raw_line in words_file:
                self._insert_word(raw_line.strip())

    def _insert_word(self, word: str) -> None:
        """Add a single word to the trie, creating any missing nodes."""
        # skipping the empty word, which would mark the root itself as a word
        if not word:
            return
        current_node = self.root
        # walking down one letter at a time, creating nodes as needed
        for letter in word.lower():
            if letter not in current_node.children:
                current_node.children[letter] = TrieNode()
            current_node = current_node.children[letter]
        # marking the last node as a word ending
        current_node.is_word = True

    def traverse(self, prefix: str) -> Optional[TrieNode]:
        """
        Traverse will traverse the Trie down a given path of letters `prefix`.
        If there is ever a missing child node, then returns None.
        Otherwise, returns the TrieNode referenced by `prefix`.
        """
        current_node = self.root
        # following the child for each letter until one is missing
        for letter in prefix.lower():
            current_node = current_node.children.get(letter)
            if current_node is None:
                return None
        return current_node

    def is_prefix(self, prefix: str) -> bool:
        end_node = self.traverse(prefix)
        # checking the node leads somewhere: every node below the root lies on
        # the way to some word, but the root of an empty trie does not
        return end_node is not None and (end_node.is_word or bool(end_node.children))

    def contains(self, word: str) -> bool:
        end_node = self.traverse(word)
        return end_node is not None and end_node.is_word

    def __iter__(self) -> typing.Iterator[str]:
        # returning a fresh generator, so each caller gets its own state and
        # StopIteration is raised on its own once the walk is done
        return self._iterate_words(self.root, "")

    def _iterate_words(self, node: TrieNode, spelled: str) -> typing.Iterator[str]:
        """Yield every word at or below `node` in lexicographic order."""
        # yielding this node's word before its children's, which puts "pot" ahead of "potato"
        if node.is_word:
            yield spelled
        # visiting children in sorted letter order
        for letter in sorted(node.children):
            yield from self._iterate_words(node.children[letter], spelled + letter)
