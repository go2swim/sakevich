import unittest
from unittest.mock import patch, MagicMock, call
from queue import Queue
import socket
import pickle
import pygame

from board import Board
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


if __name__ == '__main__':
    unittest.main()