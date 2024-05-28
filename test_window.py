import unittest
from unittest.mock import patch, MagicMock, call, PropertyMock
import pygame
import queue
import threading
from board import Board
from client import Client
from constants import SCREEN_HEIGHT, FONT, BLACK, SERVER_ADDR
from sec_window import draw_waiting
from window import draw_start_menu, create_client, key_event_queue, menu_screen, chess_game


queue_values = ["tup_space", "key_1", Client]

class TestChessGame(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.window = MagicMock()
        self.client = MagicMock()


    @patch('pygame.display.update')
    @patch('pygame.font.SysFont')
    def test_draw_start_menu(self, mock_sys_font, mock_display_update):
        mock_font = MagicMock()
        mock_sys_font.return_value = mock_font

        draw_start_menu(self.window, "Player1")

        mock_sys_font.assert_called_once_with(FONT, SCREEN_HEIGHT // 10)
        self.assertTrue(mock_display_update.called)
        self.window.fill.assert_called_with(BLACK)
        self.window.blit.assert_called()
        self.assertEqual(self.window.blit.call_count, 3)

    @patch('pygame.display.update')
    @patch('pygame.font.SysFont')
    def test_draw_waiting(self, mock_sys_font, mock_display_update):
        mock_font = MagicMock()
        mock_sys_font.return_value = mock_font

        draw_waiting(self.window, 10)

        mock_sys_font.assert_called_once_with(FONT, SCREEN_HEIGHT // 20)
        self.assertTrue(mock_display_update.called)
        self.window.fill.assert_called_with(BLACK)
        self.window.blit.assert_called()
        self.assertEqual(self.window.blit.call_count, 5)


    @patch('client.Client.connect')
    @patch('client.Client.__init__', return_value=None)
    def test_create_client(self, mock_client_init, mock_connect):
        key_event_queue = queue.Queue()

        # Настраиваем возвращаемое значение мока метода connect
        mock_connect.return_value = Board()

        # Создаем экземпляр мока Client вручную, поскольку мы замокали __init__
        mock_client_instance = MagicMock(spec=Client)
        mock_client_instance.connect = mock_connect

        # Настраиваем возвращаемое значение mock_client_cls
        mock_client_init.return_value = None

        #вместо конструктора вызываем наш мок
        with patch('client.Client', return_value=mock_client_instance):
            create_client("Player1", SERVER_ADDR, self.window, key_event_queue)

        mock_client_init.assert_called_once_with("Player1", SERVER_ADDR, self.window, key_event_queue)
        #mock_connect.assert_called_once_with(self.window, key_event_queue)
        self.assertFalse(key_event_queue.empty())
        assert isinstance(key_event_queue.get(), Client)

    @patch('pygame.event.get', return_value=[])
    @patch('queue.Queue.get', side_effect=["tup_space", MagicMock(spec=Client)])
    @patch('window.draw_start_menu')
    @patch('pygame.display.update')
    @patch('threading.Thread')
    @patch.object(Client, 'connect', return_value=None)  # Мокируем метод connect
    def test_menu_screen(self, mock_connect, mock_thread, mock_display_update, mock_draw_menu, _, __):
        # Mock the methods
        mock_draw_menu.return_value = None
        mock_display_update.return_value = None

        mock_client_instance = MagicMock()
        mock_thread.return_value = mock_client_instance
        mock_thread.return_value.is_alive.side_effect = [True, False]

        key_event_queue = queue.Queue()
        key_event_queue.put("tup_space")
        key_event_queue.put(Client("Player1", ("localhost", 8080), self.window, key_event_queue))

        def mock_chess_game(*args, **kwargs):
            raise TestInterruptException

        with patch('window.chess_game', side_effect=mock_chess_game):
            with self.assertRaises(TestInterruptException):
                menu_screen(self.window, "Player1")

        # Perform assertions
        self.window.fill.assert_called_with(BLACK)
        self.assertEqual(self.window.blit.call_count, 3)
        self.assertTrue(mock_thread.called)
        mock_display_update.assert_called_once()
        mock_draw_menu.assert_called_once()

    @patch('pygame.mouse.get_pos')
    @patch('pygame.event.get')
    @patch('piece.get_piece')
    @patch('pygame.display.update')
    @patch('threading.Thread')
    def test_chess_game(self, mock_thread, mock_display_update, mock_get_piece, mock_event, mock_mouse):
        # Устанавливаем значения, которые будут возвращать моки
        mock_mouse.return_value = (150, 150)
        mock_event.return_value = [pygame.event.Event(pygame.MOUSEBUTTONDOWN)]

        # Создаем мок-объект для board и настраиваем его поведение
        mock_board = MagicMock()
        type(mock_board).winner = PropertyMock(return_value=None)  # Настраиваем board.winner возвращать None
        self.client.board = mock_board
        mock_thread.return_value = MagicMock()

        def mock_click(name, row, col, window):
            raise TestInterruptException

        # Настраиваем мок-объект для вызова mock_click вместо click
        mock_board.click.side_effect = mock_click

        with self.assertRaises(TestInterruptException):  # Ожидаем выброса TestInterruptException
            chess_game(self.window, self.client)

        # Проверка условий после вызова click
        self.window.fill.assert_called_with(BLACK)
        self.assertTrue(mock_display_update.called)
        self.assertTrue(mock_thread.called)
        self.assertTrue(mock_board.draw.called)
        mock_board.click.assert_called_once_with(self.client.name, 1, 1,self.window) # Проверяем вызов click с координатами

    def tearDown(self):
        pygame.quit()

if __name__ == "__main__":
    unittest.main()

class TestInterruptException(Exception):
    pass