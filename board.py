import os

from typing import Any
from copy import deepcopy

import pygame

from constants import BLACK, BOARD_LENGTH, FONT, GREEN, RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE
from piece import King, Queen, Rook, Bishop, Knight, Pawn

board_surface = pygame.transform.scale(pygame.image.load(os.path.join("assets", "images", "chess_board.png")),
                                       (BOARD_LENGTH, BOARD_LENGTH * 1.01538))


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

        # проверяем того ли цвета игрок двигает фигуру и тот ли игрок сейчас ходит
        if self.board[bx][by].color == p_color and p_name == self.turn:
            killed_piece = deepcopy(self.board[ax][ay])  # сохраняем фигуру перед удалением
            # вызываем move уже у самой фигуры и проверяем правильность хода
            if self.board[bx][by].move(*pos_after, self.board, window, replacement):
                if killed_piece is not None:
                    if killed_piece.piece_name == "king":  # если убитая фигура король то объявляется победитель
                        self.update_winner(self.turn)

                self.update_valid_moves()  # обновляем списко возможных ходов
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
        # чёрная заливка фона
        pygame.draw.rect(window, BLACK, (0, 0, (SCREEN_WIDTH - BOARD_LENGTH) / 2, SCREEN_HEIGHT))

        # размещаем саму картинку доски указывая центр по середине экрана
        board_rect = board_surface.get_rect()
        board_rect.left = (SCREEN_WIDTH - BOARD_LENGTH) / 2
        board_rect.top = (SCREEN_HEIGHT - BOARD_LENGTH) / 2
        window.blit(board_surface, board_rect)  # натягивает изображение на наш прямоугольник

        # инициализируем шрифт
        font = pygame.font.SysFont(FONT, SCREEN_WIDTH // 15)

        # создаём текст и красим его в зелёный в соответствии какой игрок ходит
        text_bp = font.render(self.bp_name, True, GREEN if self.turn == self.bp_name else WHITE)
        text_wp = font.render(self.wp_name, True, GREEN if self.turn == self.wp_name else WHITE)
        text_bp_rect = text_bp.get_rect()
        # координаты для текста
        text_bp_rect.centerx = SCREEN_WIDTH / 2
        text_bp_rect.centery = (SCREEN_HEIGHT - BOARD_LENGTH) / 4
        text_wp_rect = text_wp.get_rect()
        text_wp_rect.centerx = SCREEN_WIDTH / 2
        text_wp_rect.centery = SCREEN_HEIGHT - (SCREEN_HEIGHT - BOARD_LENGTH) / 4
        # отрисовка прямоугольников с текстом
        window.blit(text_bp, text_bp_rect)
        window.blit(text_wp, text_wp_rect)

        # отображение имени игрока справа
        if p_name:
            text_you = font.render(f"You: {p_name}", True, WHITE)
            text_you = pygame.transform.rotate(text_you, -90)
            text_you_rect = text_you.get_rect()
            text_you_rect.center = SCREEN_WIDTH - (SCREEN_WIDTH - BOARD_LENGTH) / 4, SCREEN_HEIGHT / 2
            window.blit(text_you, text_you_rect)

        # отображается текст Check при шахе
        if self.is_check:
            text = font.render("Check", True, RED)
            text = pygame.transform.rotate(text, 90)
            text_rect = text.get_rect()
            text_rect.centerx = (SCREEN_WIDTH - BOARD_LENGTH) / 4
            text_rect.centery = SCREEN_HEIGHT / 2
            window.blit(text, text_rect)

        # отрисовка фигур
        for row in range(len(self.board)):
            for piece in self.board[row]:
                if piece is not None:
                    piece.draw(window)

        # Отображение надписи если кто то победил
        if self.winner is not None:
            font = pygame.font.SysFont(FONT, SCREEN_HEIGHT // 7)
            text = font.render(f"{self.winner} WON", True, GREEN)
            text_rect = text.get_rect()
            text_rect.center = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
            window.blit(text, text_rect)
