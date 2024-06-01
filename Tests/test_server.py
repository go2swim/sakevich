import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from server import create_bot, send_remaining_time, client_thread, connection_sockets, client_names, boards, connection_count, lock, SERVER_ADDR

class TestServerFunctions(unittest.TestCase):

    @patch('server.HardBot')
    @patch('server.EasyBot')
    def test_create_bot(self, MockEasyBot, MockHardBot):
        # Test hard bot creation
        create_bot('Bot1', 'hard')
        MockHardBot.assert_called_once_with('Bot1', SERVER_ADDR)
        MockHardBot.return_value.play.assert_called_once()

        # Test easy bot creation
        create_bot('Bot2', 'easy')
        MockEasyBot.assert_called_once_with('Bot2', SERVER_ADDR)
        MockEasyBot.return_value.play.assert_called_once()

        # Test invalid difficulty
        with self.assertRaises(ValueError):
            create_bot('Bot3', 'invalid')

    @patch('server.socket.socket')
    def test_send_remaining_time(self, MockSocket):
        mock_socket = MockSocket.return_value
        send_remaining_time(mock_socket, 10)
        mock_socket.send.assert_called_once_with(b"TIME:10")

        # Test ConnectionResetError
        mock_socket.send.side_effect = ConnectionResetError
        send_remaining_time(mock_socket, 10)
        self.assertFalse(mock_socket.called) # Called again due to side effect


    def side_effect_for_create_bot(*args, **kwargs):
        raise MyException()

    @patch('threading.Thread', side_effect=side_effect_for_create_bot)
    @patch('server.send_remaining_time')
    @patch('server.pickle.dumps')
    @patch('server.Board')
    @patch('server.constants.WAIT_TIME', 5)
    def test_client_thread(self, MockBoard, mock_pickle_dumps, mock_send_remaining_time, mock_create_bot):
        client_socket = MagicMock()
        board = MockBoard.return_value
        connection_number = 0
        connection_sockets.clear()
        client_names.clear()
        boards.clear()

        client_socket.recv.return_value = b'add_easy_bot'

        try:
            client_thread(client_socket, board, connection_number)
        except MyException:
            pass

        client_socket.settimeout.assert_called()
        client_socket.recv.assert_called()
        mock_create_bot.assert_called()
        mock_send_remaining_time.assert_called()

if __name__ == '__main__':
    unittest.main()

class MyException(Exception):
    pass
