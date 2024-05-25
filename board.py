import os
import pygame
from collections import deque

from typing import Any
from copy import deepcopy

from constants import BLACK, BOARD_LENGTH, FONT, GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, BOARD_OFFSET, TILE_LENGTH
from piece import King, Queen, Rook, Bishop, Knight, Pawn, Piece

board_surface = pygame.transform.scale(pygame.image.load(os.path.join("assets", "images", "chess_board.png")),
                                       (BOARD_LENGTH, BOARD_LENGTH * 1.01538))

CONST1 = 1.5
class Board:
    def __init__(self, wp_name: str = None, bp_name: str = None) -> None:
        self.wp_name = wp_name  # имя пользователя играющего за белые
        self.bp_name = bp_name  # имя пользователя играющего за чёрные

        self.previous_move = None
        self.turn = wp_name  # имя ходящего

        self.selected = None

        self.is_ready = self.wp_name is not None \
                        and self.bp_name is not None \
                        and self.turn is not None
        self.winner = None

        self.is_check = False

        self.board = [[None for _ in range(8)] for _ in range(8)]

        self.log = deque(maxlen=40)
        self.turn_number = 1

        # Black 1st row
        self.board[0][0] = Rook(0, 0, "b", "rook")
        self.board[0][1] = Knight(0, 1, "b", "knight")
        self.board[0][2] = Bishop(0, 2, "b", "bishop")
        self.board[0][3] = Queen(0, 3, "b", "queen")
        self.board[0][4] = King(0, 4, "b", "king")
        self.board[0][5] = Bishop(0, 5, "b", "bishop")
        self.board[0][6] = Knight(0, 6, "b", "knight")
        self.board[0][7] = Rook(0, 7, "b", "rook")
        # Black pawn row
        self.board[1] = [Pawn(1, i, "b", "pawn") for i in range(8)]

        # White 1st row
        self.board[7][0] = Rook(7, 0, "w", "rook")
        self.board[7][1] = Knight(7, 1, "w", "knight")
        self.board[7][2] = Bishop(7, 2, "w", "bishop")
        self.board[7][3] = Queen(7, 3, "w", "queen")
        self.board[7][4] = King(7, 4, "w", "king")
        self.board[7][5] = Bishop(7, 5, "w", "bishop")
        self.board[7][6] = Knight(7, 6, "w", "knight")
        self.board[7][7] = Rook(7, 7, "w", "rook")
        # White pawn row
        self.board[6] = [Pawn(6, i, "w", "pawn") for i in range(8)]

        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                if self.board[row][col] is not None:
                    self.board[row][col].update_valid_moves(self.board)

    def set_name(self, p_name: str) -> None:
        if self.is_ready:
            return

        if not self.wp_name:
            self.wp_name = p_name
            self.turn = p_name
        elif not self.bp_name:
            self.bp_name = p_name

        self.update_is_ready()

    def update_is_ready(self) -> None:
        self.is_ready = self.wp_name is not None \
                        and self.bp_name is not None \
                        and self.turn is not None

    def command(self, command: dict[str, Any], window: pygame.Surface = None) -> None:
        if command.get("command") == "move":
            self.move(**command)

        if window is not None:
            self.draw(window, command.get("my_name"))

    def click(self, p_name: str, row: int, col: int, window: pygame.Surface = None, replacement: str = None,
              **_) -> bool:  # последний аргумент это игнор аргументов
        ret = False  # проверка валидно ли перемещение фигуры

        # проверяем корректность имени игрока p_name - текущий игрок
        if p_name != self.wp_name and p_name != self.bp_name:
            return ret

        # получаем текущий цвет фигуры
        p_color = "b" if p_name == self.bp_name else "w"

        # если нет выбраной фигуры и в клетке фигура правильного цвета то устанавливаем фигуру как выбраную
        if self.selected is None and self.board[row][col] is not None and self.board[row][col].color == p_color:
            self.selected = (row, col)
            self.board[row][col].select(window)
            return ret
        elif self.selected is None:
            return ret

        srow, scol = self.selected  # сохраняем координаты выбраной фигуры

        # проверка цвета выбраной фиугры
        if self.board[srow][scol] is not None and self.board[srow][scol].color != p_color:
            return ret
        # если фигуру не удалось передвинуть оттменяем выбор
        if not self.move(p_name, self.selected, (row, col), window, replacement):
            self.board[srow][scol].unselect(window)

            if self.board[row][col] is not None and self.board[row][col].color == p_color:
                self.selected = (row, col)
                self.board[row][col].select(window)
            else:
                self.selected = None
        # перемешение удалось возвращаем true и снимааем выделение
        else:
            self.selected = None
            ret = True
        # перерисовываем сцену
        if window is not None:
            self.draw(window, p_name)

        return ret

    def update_winner(self, winner: str) -> None:
        self.winner = winner

    def move(self, p_name: str, pos_before: tuple[int], pos_after: tuple[int], window: pygame.Surface = None,
             replacement: str = None, **_) -> bool:
        # проверяем началась ли игра и не закончилась ли
        if not self.is_ready or self.winner is not None:
            return False
        # проверяем правильность имени
        if p_name != self.wp_name and p_name != self.bp_name:
            return False

        bx, by = pos_before
        ax, ay = pos_after

        # определяем цвет игрока
        p_color = "w" if p_name == self.wp_name else "b"

        # если в начальной позиции нет фигуры не двигаем
        if self.board[bx][by] is None:
            return False

        piece_unicode = {
            "king": {"w": "♔", "b": "♚"},
            "queen": {"w": "♕", "b": "♛"},
            "rook": {"w": "♖", "b": "♜"},
            "bishop": {"w": "♗", "b": "♝"},
            "knight": {"w": "♘", "b": "♞"},
            "pawn": {"w": "♙", "b": "♟"}
        }

        # проверяем того ли цвета игрок двигает фигуру и тот ли игрок сейчас ходит
        if self.board[bx][by].color == p_color and p_name == self.turn:
            killed_piece = deepcopy(self.board[ax][ay])  # сохраняем фигуру перед удалением
            #сохраняем параметры фигуры до обновления(для лога)
            piece_move = self.board[bx][by]
            if piece_move.piece_name == 'king':
                rochade = piece_move.rochade
            # вызываем move уже у самой фигуры и проверяем правильность хода
            if self.board[bx][by].move(*pos_after, self.board, window, replacement):
                if killed_piece is not None:
                    if killed_piece.piece_name == "king":  # если убитая фигура король то объявляется победитель
                        self.update_winner(self.turn)

                def get_log_name(piece :Piece) -> str:
                    name = piece.piece_name
                    if name == 'knight': return 'N'
                    return name[:1].title()


                self.update_valid_moves()  # обновляем списко возможных ходов
                # Логирование хода
                # Жалко убирать с красивыми символами(console_log) в сраном пайгеме они не отображаются((
                console_log = f"{piece_unicode[piece_move.piece_name][piece_move.color]}{chr(ay + 97)}{8 - ax + 1}"
                if piece_move.piece_name == 'pawn':
                    move_log = f'{chr(ay + 97)}{8 - ax + 1}'
                else:
                    move_log = f'{get_log_name(piece_move)}{chr(ay + 97)}{8 - ax + 1}'
                if killed_piece is not None:
                    console_log += f"x{piece_unicode[killed_piece.piece_name][killed_piece.color]}"
                    if piece_move.piece_name != 'pawn':
                        move_log = f"{get_log_name(piece_move)}x{chr(ay + 97)}{8 - ax + 1}"
                    else:
                        move_log = f"{chr(by + 97)}{8 - bx + 1}x{chr(ay + 97)}{8 - ax + 1}"
                if self.is_check:
                    console_log += '+'
                    move_log +="+"
                if piece_move.piece_name == 'king' and (ax, ay) in rochade:
                    console_log = f'O-O-O' if ay < by else f'O-O'
                    move_log = 'K O-O-O' if ay < by else f'K O-O'
                self.log.append(f'{piece_move.color}{move_log}')
                #print(console_log)

                self.turn = self.bp_name if self.turn == self.wp_name else self.wp_name  # меняем цвет ходящего
                return True

        return False

    def update_valid_moves(self) -> None:
        check = set()
        # проходим по всем фигурам и обновляем возможные ходы для каждой фигуры
        for row in range(len(self.board)):
            for piece in self.board[row]:
                if piece is not None:
                    check.add(piece.update_valid_moves(self.board))

        self.is_check = True in check

    def draw(self, window: pygame.Surface, p_name: str = None) -> None:
        # чёрная заливка фона, теперь используем NEW_SCREEN_WIDTH
        pygame.draw.rect(window, BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        need_rotate = self.turn == self.bp_name

        # размещаем саму картинку доски, указывая центр по середине экрана
        board_rect = board_surface.get_rect()
        board_rect.left = (SCREEN_WIDTH - BOARD_LENGTH) // BOARD_OFFSET
        board_rect.top = (SCREEN_HEIGHT - BOARD_LENGTH) // 2
        window.blit(board_surface, board_rect)  # натягивает изображение на наш прямоугольник

        # инициализируем шрифт
        log_font = pygame.font.SysFont(FONT, SCREEN_WIDTH // 30)

        # создаём текст и красим его в зелёный в соответствии какой игрок ходит
        text_bp = log_font.render(self.bp_name, True, GREEN if self.turn == self.bp_name else WHITE)
        text_wp = log_font.render(self.wp_name, True, GREEN if self.turn == self.wp_name else WHITE)

        # координаты для текста
        text_bp_rect = text_bp.get_rect()
        text_bp_rect.centerx = board_rect.centerx
        text_bp_rect.centery = board_rect.top - (SCREEN_HEIGHT - BOARD_LENGTH) // 4
        text_wp_rect = text_wp.get_rect()
        text_wp_rect.centerx = board_rect.centerx
        text_wp_rect.centery = board_rect.bottom + (SCREEN_HEIGHT - BOARD_LENGTH) // 3

        # отрисовка прямоугольников с текстом
        window.blit(text_bp, text_bp_rect)
        window.blit(text_wp, text_wp_rect)

        # отображение имени игрока справа
        if p_name:
            text_you = log_font.render(f"You: {p_name}", True, WHITE)
            text_you = pygame.transform.rotate(text_you, -90)
            text_you_rect = text_you.get_rect()
            text_you_rect.center = (SCREEN_WIDTH - BOARD_LENGTH) // BOARD_OFFSET / 2, SCREEN_HEIGHT // 2
            window.blit(text_you, text_you_rect)

        # отображается текст Check при шахе
        if self.is_check:
            text = log_font.render("Check", True, RED)
            text = pygame.transform.rotate(text, 90)
            text_rect = text.get_rect()
            text_rect.centerx = (SCREEN_WIDTH - BOARD_LENGTH) // 8
            text_rect.centery = SCREEN_HEIGHT // 2
            window.blit(text, text_rect)

        # отрисовка фигур
        for row in range(len(self.board)):
            for piece in self.board[row]:
                if piece is not None:
                    piece.draw(window)

        # Отображение надписи если кто-то победил
        if self.winner is not None:
            log_font = pygame.font.SysFont(FONT, SCREEN_HEIGHT // 7)
            text = log_font.render(f"{self.winner} WON", True, GREEN)
            text_rect = text.get_rect()
            text_rect.center = board_rect.center
            window.blit(text, text_rect)

        # Отображение цифр слева
        font = pygame.font.SysFont(FONT, SCREEN_WIDTH // 30)
        square_size = BOARD_LENGTH // 8
        # Отображение цифр справа
        for i in range(8):
            num_text = font.render(str(8 - i), True, WHITE)
            num_text_rect = num_text.get_rect()
            num_text_rect.center = (board_rect.right + square_size / 4, board_rect.top + square_size * (i + 0.5))
            window.blit(num_text, num_text_rect)

        # Отображение букв снизу
        letters = 'abcdefgh'
        for i in range(8):
            letter_text = font.render(letters[i], True, WHITE)
            letter_text_rect = letter_text.get_rect()
            letter_text_rect.center = (board_rect.left + square_size * (i + 0.5), board_rect.bottom + square_size / 4)
            window.blit(letter_text, letter_text_rect)

        #отрисовка лога
        font = pygame.font.SysFont(FONT, SCREEN_WIDTH // 30)
        white_log_x = SCREEN_WIDTH - 335  # Позиция лога белых фигур по X
        black_log_x = SCREEN_WIDTH - 150  # Позиция лога черных фигур по X
        log_y = 50  # Начальная позиция лога по Y
        line_height = 40  # Высота строки в логе

        white_label = font.render("White", True, WHITE)
        black_label = font.render("Black", True, WHITE)
        window.blit(white_label, (white_log_x, log_y - line_height))
        window.blit(black_label, (black_log_x, log_y - line_height))

        white_moves = [move for move in self.log if move.startswith('w')]
        black_moves = [move for move in self.log if move.startswith('b')]

        offset_number = self.turn_number % 19 if self.turn_number // 19 >= 1 else 0

        for i, move in enumerate(white_moves):
            move_text = move[1:]  # Убираем префикс 'w'
            log_text = font.render(move_text, True, WHITE)
            turn_number_text = font.render(str(offset_number + i + 1), True, WHITE)
            window.blit(log_text, (white_log_x, log_y + i * line_height))
            window.blit(turn_number_text, (white_log_x - int(SCREEN_WIDTH // 30 + 5), log_y + i * line_height))

        for i, move in enumerate(black_moves):
            move_text = move[1:]  # Убираем префикс 'b'
            log_text = font.render(move_text, True, WHITE)
            window.blit(log_text, (black_log_x, log_y + i * line_height))

        if self.turn == self.wp_name:
            self.turn_number += 1