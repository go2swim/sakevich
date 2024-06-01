import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call, PropertyMock
import pygame
import queue

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from board import Board
from client import Client
from constants import SCREEN_HEIGHT, FONT, BLACK, SERVER_ADDR
from window import draw_waiting, handle_promotion_click, update_timer_for_player
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

        draw_start_menu(self.window, "Player1", True, True)

        mock_sys_font.assert_called_once_with(FONT, SCREEN_HEIGHT // 10)
        self.assertTrue(mock_display_update.called)
        self.window.blit.assert_called()
        self.assertEqual(self.window.blit.call_count, 6)

    @patch('pygame.transform', return_value=None)
    @patch('pygame.image.load', return_value=None)
    @patch('pygame.display.update')
    @patch('pygame.font.SysFont')
    def test_draw_waiting(self, mock_sys_font, mock_display_update, mock_image, _):
        mock_font = MagicMock()
        mock_sys_font.return_value = mock_font

        draw_waiting(self.window, 10, True)

        mock_sys_font.assert_called_once_with(FONT, SCREEN_HEIGHT // 20)
        self.assertTrue(mock_display_update.called)
        self.window.blit.assert_called()
        self.assertEqual(self.window.blit.call_count, 8)
        mock_image.assert_called()


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

    @patch('threading.Thread.is_alive', side_effect=RuntimeError("Test exception"))
    @patch('window.create_client')
    @patch('pygame.event.get')
    @patch('pygame.quit')
    @patch('pygame.display.update')
    @patch('client.Client')
    @patch('threading.Thread.start')
    def test_menu_screen(self, mock_thread_start, MockClient, mock_pygame_display_update, mock_pygame_quit,
                         mock_pygame_event_get, mock_create_client, mock_chess_game):
        window = MagicMock()
        name = "TestPlayer"
        server_addr = ("localhost", 12345)
        key_event_queue = queue.Queue()

        # Simulate pressing the space key to start client creation
        mock_pygame_event_get.side_effect = [
            [MagicMock(type=pygame.KEYDOWN, key=pygame.K_SPACE)],
            []
        ]

        def mock_create_client_fn(name, server_addr, window, key_event_queue):
            key_event_queue.put(Client(name, server_addr, window, key_event_queue))

        mock_create_client.side_effect = mock_create_client_fn

        with self.assertRaises(RuntimeError):
            menu_screen(window, name)

        mock_chess_game.assert_called_once()
        mock_pygame_event_get.assert_has_calls([call(), call()])
        self.assertEqual(key_event_queue.qsize(), 0)


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

        with self.assertRaises(TestInterruptException):
            chess_game(self.window, self.client)

        # Проверка условий после вызова click
        self.assertTrue(mock_display_update.called)
        self.assertTrue(mock_thread.called)
        self.assertTrue(mock_board.draw.called)
        mock_board.click.assert_called_once_with(self.client.name, 1, 1,self.window) # Проверяем вызов click с координатами

    @patch('pygame.display.update', return_value=None)
    @patch('pygame.event.get')
    def test_menu_screen_quit(self, mock_pygame_event_get, _):
        window = MagicMock()
        name = "TestPlayer"
        key_event_queue = queue.Queue()

        mock_pygame_event_get.side_effect = [
            [MagicMock(type=pygame.QUIT)],
        ]

        with self.assertRaises(SystemExit):
            menu_screen(window, name)

        mock_pygame_event_get.assert_called()

    @patch('queue.Queue.put')
    @patch('pygame.display.update', return_value=None)
    @patch('pygame.event.get')
    def test_menu_screen_keydown(self, mock_pygame_event_get, _, mock_queue):
        window = MagicMock()
        name = "TestPlayer"
        key_event_queue = queue.Queue()

        def mock_side_effect(*args, **kwargs):
            raise TestInterruptException()

        mock_queue.side_effect = mock_side_effect

        mock_pygame_event_get.side_effect = [
            [MagicMock(type=pygame.KEYDOWN, key=pygame.K_1)],
        ]

        with self.assertRaises(TestInterruptException):
            menu_screen(window, name)

        self.assertTrue(key_event_queue.empty())


    def test_handle_promotion_click(self):
        buttons = [
            (pygame.Rect(0, 0, 50, 50), 'queen'),
            (pygame.Rect(60, 0, 50, 50), 'rook'),
            (pygame.Rect(120, 0, 50, 50), 'bishop'),
            (pygame.Rect(180, 0, 50, 50), 'knight'),
        ]
        mouse_pos = (30, 30)
        promo_window_pos = (0, 0)
        result = handle_promotion_click(buttons, mouse_pos, promo_window_pos)
        self.assertEqual(result, 'queen')

        mouse_pos = (70, 30)
        result = handle_promotion_click(buttons, mouse_pos, promo_window_pos)
        self.assertEqual(result, 'rook')

        mouse_pos = (130, 30)
        result = handle_promotion_click(buttons, mouse_pos, promo_window_pos)
        self.assertEqual(result, 'bishop')

        mouse_pos = (190, 30)
        result = handle_promotion_click(buttons, mouse_pos, promo_window_pos)
        self.assertEqual(result, 'knight')

        mouse_pos = (250, 30)
        result = handle_promotion_click(buttons, mouse_pos, promo_window_pos)
        self.assertIsNone(result)

    # @patch('pygame.font.SysFont')
    # @patch('pygame.display.update')
    # @patch('pygame.draw.circle')
    # @patch('pygame.Surface.fill')
    # @patch('pygame.Surface.blit')
    # def test_update_timer_for_player_white(self, mock_blit, mock_fill, mock_draw_circle, mock_display_update,
    #                                        mock_sys_font):
    #     mock_window = MagicMock()
    #     mock_font = MagicMock()
    #     mock_sys_font.return_value = mock_font
    #     white_timer = 150  # 2 minutes 30 seconds
    #     black_timer = 90  # 1 minute 30 seconds
    #     player_color = 'white'
    #
    #     update_timer_for_player(mock_window, white_timer, black_timer, player_color)
    #
    #     mock_fill.assert_has_calls([
    #         call(BLACK, (0, 0, SCREEN_HEIGHT // 2, 80)),
    #         call(BLACK, (SCREEN_HEIGHT // 2, 0, SCREEN_HEIGHT, 80))
    #     ])
    #
    #     white_time_text = mock_font.render(f'White: 02:30', True, pygame.Color("white"))
    #     black_time_text = mock_font.render(f'Black: 01:30', True, pygame.Color("black"))
    #
    #     mock_blit.assert_has_calls([
    #         call(white_time_text, (10, 10)),
    #         call(black_time_text, (SCREEN_HEIGHT // 2 + 10, 10))
    #     ])
    #
    #     mock_draw_circle.assert_called_once_with(mock_window, pygame.Color("white"), (5, 30), 5)
    #     mock_display_update.assert_called_once_with((0, 0, SCREEN_HEIGHT, 80))


    def tearDown(self):
        pygame.quit()

if __name__ == "__main__":
    unittest.main()

class TestInterruptException(Exception):
    pass