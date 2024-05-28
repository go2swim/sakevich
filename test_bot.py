import unittest
import pickle

from unittest.mock import patch, MagicMock
from board import Board
from bot import Bot



class TestBot(unittest.TestCase):

    @patch.object(Bot, 'connect', return_value=Board())
    def test_bot_init(self, mock_client_init):
        name = "TestBot"
        server_addr = ("localhost", 12345)

        bot = Bot(name, server_addr)

        mock_client_init.assert_called_once_with(None, None)
        self.assertEqual(bot.name, name)
        self.assertEqual(bot.server_addr, server_addr)

    @patch('bot.pickle.loads')
    @patch('socket.socket')
    def test_bot_connect(self, mock_socket_class, mock_pickle_loads):
        name = "TestBot"
        server_addr = ("localhost", 12345)

        mock_socket_instance = mock_socket_class.return_value
        mock_socket_instance.recv = MagicMock(side_effect=[
            b"BOARD:" + pickle.dumps("board_data"),
            b'\nGET:',
            b'incorrect_data'
        ])

        bot = Bot(name, server_addr)

        with self.assertRaises(ValueError):
            bot.connect()

        mock_socket_instance.connect.assert_called_with(server_addr)
        self.assertEqual(mock_socket_instance.recv.call_count, 3)
        self.assertEqual(mock_pickle_loads.call_count, 2)

    @patch('bot.pickle.loads')
    @patch('socket.socket')
    def test_bot_connect_get_board(self, mock_socket_class, mock_pickle_loads):
        name = "TestBot"
        server_addr = ("localhost", 12345)

        mock_socket_instance = mock_socket_class.return_value
        board_data = "board_data"
        mock_socket_instance.recv = MagicMock(side_effect=[
            b"BOARD:" + pickle.dumps(board_data),
        ])
        mock_pickle_loads.return_value = board_data

        bot = Bot(name, server_addr)

        mock_socket_instance.connect.assert_called_once_with(server_addr)
        self.assertEqual(bot.board, board_data)
        mock_pickle_loads.assert_called_with(pickle.dumps(board_data))


if __name__ == '__main__':
    unittest.main()
