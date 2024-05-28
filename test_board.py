import unittest
import pygame
from unittest.mock import patch, MagicMock
from board import Board, Pawn, King, Piece


class TestBoard(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.board = Board()

    def test_set_name(self):
        """Проверка установки имени игрока"""
        self.board.set_name("Player1")
        self.assertEqual(self.board.wp_name, "Player1")
        self.assertEqual(self.board.turn, "Player1")

        self.board.set_name("Player2")
        self.assertEqual(self.board.bp_name, "Player2")
        self.assertTrue(self.board.is_ready)

    def test_update_is_ready(self):
        """Проверка обновления состояния готовности доски"""
        self.assertFalse(self.board.is_ready)
        self.board.set_name("Player1")
        self.assertFalse(self.board.is_ready)
        self.board.set_name("Player2")
        self.assertTrue(self.board.is_ready)

    def test_command(self):
        """Проверка выполнения команд"""
        self.board.set_name("Player1")
        self.board.set_name("Player2")

        command = {"command": "move", "p_name": "Player1", "pos_before": (6, 0), "pos_after": (5, 0)}
        window = pygame.Surface((800, 600))

        self.board.command(command, window)
        self.assertIsNone(self.board.board[6][0])
        self.assertIsInstance(self.board.board[5][0], Pawn)

    def test_click(self):
        """Проверка обработки кликов и выполнения хода"""
        self.board.set_name("Player1")
        self.board.set_name("Player2")

        self.board.click("Player1", 6, 0)
        self.assertTrue(self.board.click("Player1", 5, 0))
        self.assertIsNone(self.board.board[6][0])
        self.assertIsInstance(self.board.board[5][0], Pawn)

    def test_update_winner(self):
        """Проверка обновления победителя"""
        self.board.update_winner("Player1")
        self.assertEqual(self.board.winner, "Player1")

    def test_update_log(self):
        """Проверка обновления лога"""
        piece = Pawn(6, 0, "w", "pawn")
        self.board.update_log(piece, None, (6, 0), (5, 0), set())
        self.assertIn('wa4', self.board.log[0])

    def test_move(self):
        """Проверка выполнения хода"""
        self.board.set_name("Player1")
        self.board.set_name("Player2")

        initial_piece = self.board.board[6][0]  # Pawn
        self.board.update_valid_moves()
        self.assertTrue(self.board.move("Player1", (6, 0), (5, 0)))
        self.assertIsNone(self.board.board[6][0])
        self.assertEqual(self.board.board[5][0], initial_piece)

    def test_click_valid_move(self):
        """Проверка обработки кликов и выполнения хода"""
        self.board.set_name("Player1")
        self.board.set_name("Player2")

        self.board.click("Player1", 6, 0)
        self.assertTrue(self.board.click("Player1", 5, 0))
        self.assertIsNone(self.board.board[6][0])
        self.assertIsInstance(self.board.board[5][0], Pawn)

    @patch('pygame.draw.rect')
    @patch('piece.Piece.draw')
    def test_draw(self, mock_piece_draw, mock_draw_rect):
        """Проверка отрисовки доски"""
        mock_draw_rect.return_value = None
        window = MagicMock()

        self.board.draw(window, "Player1")

        self.assertTrue(window.blit.called)
        self.assertTrue(mock_piece_draw.called)


if __name__ == '__main__':
    unittest.main()
