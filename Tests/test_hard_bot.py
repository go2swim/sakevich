import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))
import unittest
import copy
from unittest.mock import MagicMock, patch
from hard_bot import HardBot, get_child_positions, evaluate_position
from board import Board
from piece import Piece, Pawn
from constants import DEPTH_FOR_HARD_BOT

class TestHardBot(unittest.TestCase):

    @patch('bot.Bot.connect', return_value=Board())
    def setUp(self, _):
        self.bot = HardBot("TestBot", ("localhost", 12346))
        self.bot.board.board = [[None for _ in range(8)] for _ in range(8)]
        self.board = self.bot.board

    def test_evaluate_position(self):
        """Тестирование функции оценки позиции."""
        initial_evaluation = evaluate_position(self.bot.board)
        self.assertEqual(initial_evaluation, 0.0, "Начальная позиция должна иметь оценку 0.0")

    def test_get_child_positions(self):
        """Тестирование функции получения дочерних позиций."""
        self.bot.board.board[1][1] = Pawn(1, 0, 'w', 'pawn')
        self.bot.board.board[1][1].valid_moves = {(2, 0)}
        child_positions = get_child_positions(self.bot.board, "w")
        self.assertGreater(len(child_positions), 0)

    def test_minimax_depth_zero(self):
        """Тестирование функции minimax на глубине 0."""
        initial_evaluation = evaluate_position(self.bot.board)
        minimax_evaluation = self.bot.minimax(self.bot.board, 0, -float('inf'), float('inf'), True)
        self.assertEqual(initial_evaluation, minimax_evaluation, "Оценка на глубине 0 должна совпадать с начальной оценкой")

    def test_minimax_maximizing(self):
        """Тестирование функции minimax для максимизирующего игрока."""
        self.bot.board.move(self.bot.name, (6, 4), (4, 4))  # белые делают ход
        evaluation = self.bot.minimax(self.bot.board, DEPTH_FOR_HARD_BOT, -float('inf'), float('inf'), True)
        self.assertIsInstance(evaluation, float, "Результат minimax должен быть числом")

    def test_make_random_move(self):
        """Тестирование функции случайного хода."""
        self.bot.board.board[1][1] = Pawn(1, 0, 'b', 'pawn')
        self.bot.board.board[1][1].valid_moves = {(2, 0)}
        random_move = self.bot.make_random_move()
        self.assertIsInstance(random_move, list, "Случайный ход должен быть списком")
        self.assertEqual(len(random_move), 2, "Случайный ход должен содержать две позиции")


if __name__ == "__main__":
    unittest.main()