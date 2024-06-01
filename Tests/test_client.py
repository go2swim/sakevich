import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
from queue import Queue
import pickle
import pygame

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from client import Client


class TestClient(unittest.TestCase):

    @patch.object(Client, 'connect', return_value=None)
    def get_ready_client_without_connect(self, _=None):
        return Client("Player1", ("localhost", 8080), MagicMock(spec=pygame.Surface), Queue())

    @patch('socket.socket.__init__', return_value=None)
    @patch('client.Client.connect', return_value=None)
    def test_init(self, mock_connect, mock_socket_connect):
        window = MagicMock(spec=pygame.Surface)
        key_event_queue = Queue()

        client = Client("Player1", ("localhost", 8080), window, key_event_queue)

        self.assertEqual(client.name, "Player1")
        self.assertEqual(client.server_addr, ("localhost", 8080))
        mock_socket_connect.assert_called_once()
        mock_connect.assert_called_once_with(window, key_event_queue)

    @patch('socket.socket.connect')
    @patch('socket.socket.recv', return_value=b'BOARD:' + pickle.dumps('board_data'))
    @patch('client.Client.send')
    @patch('window.draw_waiting')
    def test_connect(self, mock_draw_waiting, mock_send, mock_recv, mock_socket_connect):
        window = MagicMock(spec=pygame.Surface)
        key_event_queue = Queue()
        key_event_queue.put("key_1")

        client = Client("Player1", ("localhost", 8080), window, key_event_queue)

        mock_socket_connect.assert_called_once_with(("localhost", 8080))
        mock_recv.assert_called()
        self.assertEqual(client.board, "board_data")


    @patch('socket.socket.close')
    def test_disconnect(self, mock_socket_close):
        client = self.get_ready_client_without_connect()
        client.disconnect()
        mock_socket_close.assert_called_once()

    @patch('socket.socket.send')
    def test_send(self, mock_socket_send):
        client = self.get_ready_client_without_connect()
        data = {"key": "value"}
        serialized_data = pickle.dumps(data)

        client.send(data)

        mock_socket_send.assert_called_once_with(serialized_data)

    @patch('socket.socket.recv', return_value=pickle.dumps({"key": "value"}))
    def test_receive(self, mock_socket_recv):
        client = self.get_ready_client_without_connect()

        result = client.receive(1024)

        mock_socket_recv.assert_called_once_with(1024)
        self.assertEqual(result, {"key": "value"})

    @patch('window.draw_waiting', return_value=None)
    @patch('client.socket.socket')
    @patch('client.pygame.Surface')
    @patch('client.Queue')
    def test_connect_time_condition(self, MockQueue, MockSurface, MockSocket, mock_draw_waiting):
        # Mock socket and its methods
        mock_socket = MockSocket.return_value
        mock_socket.recv = MagicMock(side_effect=[
            b"TIME:30.0\n",  # First recv call returns "TIME:" condition
        ])

        # Mock the key event queue
        mock_queue = MockQueue.return_value
        mock_queue.empty = MagicMock(return_value=False)
        mock_queue.get = MagicMock(return_value="key_1")

        with self.assertRaises(Exception) as context:
            client = Client("test_user", ("localhost", 8080), MockSurface, mock_queue)

        mock_socket.connect.assert_called_once_with(("localhost", 8080))
        mock_draw_waiting.assert_called_once_with(MockSurface, 30.0, False)
        mock_queue.empty.assert_called_once()
        mock_queue.get.assert_called_once()

    @patch('window.draw_waiting', return_value=None)
    @patch('client.socket.socket')
    @patch('client.pygame.Surface')
    @patch('client.Queue')
    def test_connect_get_condition(self, MockQueue, MockSurface, MockSocket, _):
        # Mock socket and its methods
        mock_socket = MockSocket.return_value
        mock_socket.recv = MagicMock(side_effect=[
            b"INFO:\nGET:need_name",  # First recv call returns "GET:" condition
        ])

        # Mock the key event queue
        mock_queue = MockQueue.return_value
        mock_queue.empty = MagicMock(return_value=True)


        with self.assertRaises(Exception) as context:
            client = Client("test_user", ("localhost", 8080), MockSurface, mock_queue)

        mock_socket.connect.assert_called_once_with(("localhost", 8080))



if __name__ == '__main__':
    unittest.main()