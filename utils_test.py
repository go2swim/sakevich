import unittest

from constants import SCREEN_WIDTH, BOARD_LENGTH, BOARD_OFFSET, SCREEN_HEIGHT, TILE_LENGTH
from utils import coordinate_builder_to_absolute_coord, coordinate_builder_to_tile_coord


class TestCoordinateFunctions(unittest.TestCase):

    def test_coordinate_builder_to_absolute_coord(self):
        # Example test cases
        row, col = 0, 0
        expected_x = (SCREEN_WIDTH - BOARD_LENGTH) / BOARD_OFFSET
        expected_y = (SCREEN_HEIGHT - BOARD_LENGTH) / 2
        self.assertEqual(coordinate_builder_to_absolute_coord(row, col), (expected_x, expected_y))

        row, col = 1, 1
        expected_x = (SCREEN_WIDTH - BOARD_LENGTH) / BOARD_OFFSET + TILE_LENGTH
        expected_y = (SCREEN_HEIGHT - BOARD_LENGTH) / 2 + TILE_LENGTH
        self.assertEqual(coordinate_builder_to_absolute_coord(row, col), (expected_x, expected_y))

        # Additional test cases
        row, col = 5, 5
        expected_x = (SCREEN_WIDTH - BOARD_LENGTH) / BOARD_OFFSET + 5 * TILE_LENGTH
        expected_y = (SCREEN_HEIGHT - BOARD_LENGTH) / 2 + 5 * TILE_LENGTH
        self.assertEqual(coordinate_builder_to_absolute_coord(row, col), (expected_x, expected_y))

    def test_coordinate_builder_to_tile_coord(self):
        # Example test cases
        x, y = (SCREEN_WIDTH - BOARD_LENGTH) / BOARD_OFFSET, (SCREEN_HEIGHT - BOARD_LENGTH) / 2
        expected_row, expected_col = 0, 0
        self.assertEqual(coordinate_builder_to_tile_coord(x, y), (expected_row, expected_col))

        x, y = (SCREEN_WIDTH - BOARD_LENGTH) / BOARD_OFFSET + TILE_LENGTH, (SCREEN_HEIGHT - BOARD_LENGTH) / 2 + TILE_LENGTH
        expected_row, expected_col = 1, 1
        self.assertEqual(coordinate_builder_to_tile_coord(x, y), (expected_row, expected_col))

        # Additional test cases
        x, y = (SCREEN_WIDTH - BOARD_LENGTH) / BOARD_OFFSET + 5 * TILE_LENGTH, (SCREEN_HEIGHT - BOARD_LENGTH) / 2 + 5 * TILE_LENGTH
        expected_row, expected_col = 5, 5
        self.assertEqual(coordinate_builder_to_tile_coord(x, y), (expected_row, expected_col))

if __name__ == '__main__':
    unittest.main()