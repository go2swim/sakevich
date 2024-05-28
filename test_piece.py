import os
import unittest
from unittest.mock import MagicMock, patch, call
from piece import Piece, King, Queen, Rook, Bishop, Knight, Pawn, create_piece, get_piece


class TestChessPieces(unittest.TestCase):

    def setUp(self):
        self.empty_board = [[None for _ in range(8)] for _ in range(8)]

    @patch('piece.Knight')
    @patch('piece.Bishop')
    @patch('piece.Rook')
    @patch('piece.Queen')
    def test_create_piece(self, mock_queen, mock_rook, mock_bishop, mock_knight):
        # Test create_piece function
        piece = create_piece(0, 0, 'queen', 'w')
        mock_queen.assert_called_once_with(0, 0, 'w', 'queen')

        piece = create_piece(0, 0, 'knight', 'w')
        mock_knight.assert_called_once_with(0, 0, 'w', 'knight')

        piece = create_piece(0, 0, 'rook', 'w')
        mock_rook.assert_called_once_with(0, 0, 'w', 'rook')

        piece = create_piece(0, 0, 'bishop', 'w')
        mock_bishop.assert_called_once_with(0, 0, 'w', 'bishop')

    @patch('piece.Knight')
    @patch('piece.Bishop')
    @patch('piece.Rook')
    @patch('piece.Queen')
    def test_get_piece(self, mock_queen, mock_rook, mock_bishop, mock_knight):
        # Test get_piece function
        piece = get_piece('queen', 0, 0, 'w')
        mock_queen.assert_called_once_with(0, 0, 'w', 'queen')

        piece = get_piece('knight', 0, 0, 'w')
        mock_knight.assert_called_once_with(0, 0, 'w', 'knight')

        piece = get_piece('rook', 0, 0, 'w')
        mock_rook.assert_called_once_with(0, 0, 'w', 'rook')

        piece = get_piece('bishop', 0, 0, 'w')
        mock_bishop.assert_called_once_with(0, 0, 'w', 'bishop')

    @patch('piece.Piece.draw')
    def test_piece_select(self, mock_draw):
        # Test select method in Piece class
        piece = Piece(0, 0, 'w', 'pawn')
        window = MagicMock()

        piece.select(window)
        self.assertTrue(piece.is_selected)
        mock_draw.assert_called_once_with(window)

    @patch('piece.Piece.draw')
    def test_piece_unselect(self, mock_draw):
        # Test unselect method in Piece class
        piece = Piece(0, 0, 'w', 'pawn')
        window = MagicMock()

        piece.unselect(window)
        self.assertFalse(piece.is_selected)
        mock_draw.assert_called_once_with(window)

    @patch('piece.Piece.one_direction')
    def test_piece_one_direction(self, mock_one_direction):
        # Test one_direction method in Piece class
        piece = Piece(0, 0, 'w', 'bishop')
        board = [[None] * 8 for _ in range(8)]
        candidates = set()
        check = set()

        piece.one_direction(board, candidates, 1, 1, check)
        mock_one_direction.assert_called_once_with(board, candidates, 1, 1, check)

    @patch('piece.Piece.draw')
    def test_piece_move(self, mock_draw):
        # Test move method in Piece class
        piece = Piece(0, 0, 'w', 'pawn')
        board = [[None] * 8 for _ in range(8)]
        window = MagicMock()
        piece.valid_moves = {(1, 0)}

        board[0][0] = piece
        piece.move(1, 0, board, window)
        self.assertEqual(piece.row, 1)
        self.assertEqual(piece.col, 0)
        self.assertFalse(piece.is_selected)
        mock_draw.assert_called_once_with(window)

    @patch('piece.coordinate_builder_to_absolute_coord')
    @patch('piece.images')
    def test_piece_draw(self, mock_images, mock_coordinate_builder_to_absolute_coord):
        # Test draw method in Piece class
        piece = Piece(0, 0, 'w', 'pawn')
        window = MagicMock()
        mock_coordinate_builder_to_absolute_coord.return_value = (0, 0)
        img_mock = MagicMock()
        mock_images.get.return_value = img_mock

        piece.draw(window)
        mock_coordinate_builder_to_absolute_coord.assert_called_once_with(0, 0)
        mock_images.get.assert_called_once_with(piece.img_name)
        window.blit.assert_called_once_with(img_mock, img_mock.get_rect.return_value)

    def test_piece_get_value(self):
        # Test get_value method in Piece class
        piece_values = {
            'king': 99,
            'queen': 9,
            'rook': 5,
            'bishop': 3,
            'knight': 3,
            'pawn': 1
        }

        for piece_name, value in piece_values.items():
            piece = Piece(0, 0, 'w', piece_name)
            self.assertEqual(piece.get_value(), value)

    def test_piece_str_repr(self):
        # Test __str__ and __repr__ methods in Piece class
        piece = Piece(0, 0, 'w', 'queen')
        self.assertEqual(str(piece), 'queen')
        self.assertEqual(repr(piece), 'queen')

    def test_piece_copy(self):
        # Test __copy__ method in Piece class
        piece = Piece(0, 0, 'w', 'queen')
        piece_copy = piece.__copy__()

        self.assertEqual(piece_copy.row, piece.row)
        self.assertEqual(piece_copy.col, piece.col)
        self.assertEqual(piece_copy.color, piece.color)
        self.assertEqual(piece_copy.piece_name, piece.piece_name)
        self.assertEqual(piece_copy.img_name, piece.img_name)
        self.assertEqual(piece_copy.is_selected, piece.is_selected)
        self.assertEqual(piece_copy.valid_moves, piece.valid_moves)
        self.assertEqual(piece_copy.first_move, piece.first_move)

    def test_king_moves(self):
        board = self.empty_board
        king = King(4, 4, 'w', 'king')
        board[4][4] = king
        valid_moves, _ = king.all_valid_moves(board)

        expected_moves = {(3, 3), (3, 4), (3, 5), (4, 3), (4, 5), (5, 3), (5, 4), (5, 5)}
        self.assertEqual(valid_moves, expected_moves)

    def test_rook_moves(self):
        board = self.empty_board
        rook = Rook(4, 4, 'w', 'rook')
        board[4][4] = rook
        valid_moves, _ = rook.all_valid_moves(board)

        expected_moves = set()
        for i in range(8):
            if i != 4:
                expected_moves.add((i, 4))
                expected_moves.add((4, i))

        self.assertEqual(valid_moves, expected_moves)

    def test_bishop_moves(self):
        board = self.empty_board
        bishop = Bishop(4, 4, 'w', 'bishop')
        board[4][4] = bishop
        valid_moves, _ = bishop.all_valid_moves(board)

        expected_moves = {(0, 0), (1, 1), (1, 7), (2, 2), (2, 6), (3, 3), (3, 5), (5, 3), (5, 5), (6, 2), (6, 6),
                          (7, 1), (7, 7)}

        self.assertEqual(valid_moves, expected_moves)

    def test_knight_moves(self):
        board = self.empty_board
        knight = Knight(4, 4, 'w', 'knight')
        board[4][4] = knight
        valid_moves, _ = knight.all_valid_moves(board)

        expected_moves = {(2, 3), (2, 5), (3, 2), (3, 6), (5, 2), (5, 6), (6, 3), (6, 5)}
        self.assertEqual(valid_moves, expected_moves)

    def test_pawn_moves(self):
        board = self.empty_board
        pawn = Pawn(1, 4, 'w', 'pawn')
        board[1][4] = pawn
        valid_moves, _ = pawn.all_valid_moves(board)

        expected_moves = {(0, 4)}
        self.assertEqual(valid_moves, expected_moves)


if __name__ == '__main__':
    unittest.main()
