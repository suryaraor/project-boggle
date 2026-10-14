"""
Main module for the Boggle UI.

The program will fail to run if the implementations for `TrieDictionary`
or `MyGameManager` are incomplete.

You can view the full list of command-line arguments by adding `-h` to
the end of the command. e.g:
    python3 boggle.py -h
"""

import argparse
import math
from py_boggle import trie_dictionary, my_game_manager
from typing import List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-w", "--words", type=str, default="words.txt", help="Path to the words file."
    )
    parser.add_argument(
        "-c", "--cubes", type=str, default="cubes.txt", help="Path to the cubes file."
    )
    parser.add_argument(
        "-s", "--size", type=str, default=4, help="Size of board."
    )
    parser.add_argument(
        "-b", "--board", type=str, default="", help="Board given by a string of letters"
    )

    return parser.parse_args()


def run_boggle(args):
    mydict = trie_dictionary.TrieDictionary()
    mydict.load_dictionary(args.words)

    mygame = my_game_manager.MyGameManager()
    if args.board:
        d = math.sqrt(len(args.board))
        if not d.is_integer():
            print("Your custom board is not square. Please try again")
        else:
            board = print_board(args.board, d)
    else:
        d = args.size
    mygame.new_game(int(d), args.cubes, mydict)
    if args.board:
        mygame.set_game(board)
    else:
        board = print_board(transform_board(mygame.get_board()), mygame.size)

    choice = ''
    word_list = []
    while choice != 'q':
        again = 'neutral'
        print("Play by typing a word, or type q to quit")
        choice = input("Type your word (or q to quit): ")
        print()
        if choice == "q":
            print("Your final score: ", mygame.get_score())

            all_words = mygame.board_driven_search()
            comp_words = []
            comp_score = 0
            print("Remaining available words: ")
            for w in all_words:
                if w.upper() not in word_list:
                    comp_words.append(w.upper())
                    comp_score += len(w) - 3
                    print(w, "\t Score: ", comp_score)
            print("Computer total score: ", comp_score)
            if comp_score > mygame.get_score():
                print("You Lose!")
            elif comp_score == mygame.get_score():
                print("Tie!")
            else:
                print("You Win!")

            again = input("Type y to play again or n to exit: ")
            if again == "y":
                word_list = []
                choice = ''
                mygame.new_game(int(d), args.cubes, mydict)
                if args.board:
                    mygame.set_game(board)
                else:
                    board = print_board(transform_board(mygame.get_board()), mygame.size)

        if again == 'neutral': # We are not quitting the game, add the word
            score = mygame.add_word(choice)
            if score == 0:
                print("Word not added. Invalid or already guessed.")
                print("Score: ", mygame.get_score())
                print_board(transform_board(board), len(board))
            else:
                word_list.append(choice.upper())
                print("New score: ", mygame.get_score())
                word_coords = mygame.get_last_added_word()
                print_board(transform_board(board), len(board), word_coords)


def print_board(my_board, side_len, coords=[[]]):
    di = int(side_len)
    board = [[] for i in range(0, di)]
    r = 0
    while r < di:
        for i in range(di):
            board[r].append(my_board[r*di + i])
            if (r, i) in coords:
                print(board[r][i].upper(), end=" ")
            else:
                print(board[r][i].lower(), end=" ")
        print()
        r += 1
    return board


def transform_board(list_board: List[List[str]]):
    return ''.join([''.join(list_board[i]) for i in range(0, len(list_board))])


if __name__ == "__main__":
    cfg = parse_args()
    run_boggle(cfg)

