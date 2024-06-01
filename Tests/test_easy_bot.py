import os
import sys
import unittest
import copy
import random
from unittest.mock import patch


sys.path.insert(1, os.path.join(sys.path[0], '..'))
from board import Board
from easy_bot import EasyBot
from piece import Piece, King, Queen, Rook, Bishop, Knight, Pawn


class TestEasyBot(unittest.TestCase):

    @patch('bot.Bot.connect', return_value=Board())
    def setUp(self, _):
        # Initialize a board and bot
        self.bot = EasyBot("TestBot", ("localhost", 1234))
        self.bot.board.board = [[None for _ in range(8)] for _ in range(8)]
        self.board = self.bot.board

    def test_make_random_move(self):
        # Set up a scenario where bot has only one piece with valid moves
        self.board.board[0][0] = Rook(0, 0, 'b', 'rook')
        self.board.board[0][0].valid_moves = [(0, 1), (1, 0)]

        random_move = self.bot.make_random_move()

        self.assertIn(tuple(random_move), [((0, 0), (0, 1)), ((0, 0), (1, 0))])

    def test_take_piece(self):
        # Set up a scenario where bot can take an opponent's piece
        self.board.board[0][0] = Rook(0, 0, 'b', 'rook')
        self.board.board[1][0] = Pawn(1, 0, 'w', 'pawn')
        self.board.board[0][0].valid_moves = [(1, 0)]

        move = self.bot.take_piece([])

        self.assertEqual(move, [(0, 0), (1, 0)])

    def test_test_one_move_ahead(self):
        self.board.board[0][0] = Rook(0, 0, 'b', 'rook')
        self.board.board[0][1] = Pawn(0, 1, 'w', 'pawn')
        self.board.board[0][0].valid_moves = {(0, 1)}
        initial_board_state = copy.deepcopy(self.board.board)

        new_board = self.bot.test_one_move_ahead(self.board, (0, 0), (0, 1))

        self.assertIsNone(new_board.board[0][0])
        self.assertIsInstance(new_board.board[0][1], Rook)
        self.assertEqual(new_board.board[0][1].color, 'b')

        self.assertNotEqual(self.board.board, initial_board_state)

    def test_take_care(self):
        # Set up a scenario where a bot's piece is under threat
        self.board.board[0][0] = Rook(0, 0, 'b', 'rook')
        self.board.board[1][1] = Pawn(1, 1, 'w', 'pawn')
        self.board.board[1][1].valid_moves = [(0, 0)]
        self.board.board[0][0].valid_moves = [(1, 0)]

        move = self.bot.take_care([])

        self.assertEqual(move, [(0, 0), (1, 0)])

    def test_get_possible_player_moves(self):
        # Set up a scenario with multiple player moves
        self.board.board[0][0] = Rook(0, 0, 'w', 'rook')
        self.board.board[0][0].valid_moves = [(0, 1), (1, 0)]
        self.board.board[1][1] = Pawn(1, 1, 'w', 'pawn')
        self.board.board[1][1].valid_moves = [(2, 1)]

        possible_moves = self.bot.get_possible_player_moves()

        self.assertCountEqual(possible_moves, [(0, 1), (1, 0), (2, 1)])


if __name__ == '__main__':
    unittest.main()
