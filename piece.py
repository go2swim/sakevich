from __future__ import annotations
import os
import pygame
import tkinter as tk
from concurrent.futures.thread import ThreadPoolExecutor

from constants import BLACK, PIECE_GREEN_BG, TILE_LENGTH
from utils import coordinate_builder_to_absolute_coord
from client import Client

selected_img = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "selected.png")),
    (TILE_LENGTH, TILE_LENGTH))

king_img_w = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "white_pieces", "white_king.png")),
    (TILE_LENGTH, TILE_LENGTH))
king_img_b = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "black_pieces", "black_king.png")),
    (TILE_LENGTH, TILE_LENGTH))

queen_img_w = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "white_pieces", "white_queen.png")),
    (TILE_LENGTH, TILE_LENGTH))
queen_img_b = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "black_pieces", "black_queen.png")),
    (TILE_LENGTH, TILE_LENGTH))

rook_img_w = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "white_pieces", "white_rook.png")),
    (TILE_LENGTH, TILE_LENGTH))
rook_img_b = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "black_pieces", "black_rook.png")),
    (TILE_LENGTH, TILE_LENGTH))

bishop_img_w = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "white_pieces", "white_bishop.png")),
    (TILE_LENGTH, TILE_LENGTH))
bishop_img_b = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "black_pieces", "black_bishop.png")),
    (TILE_LENGTH, TILE_LENGTH))

knight_img_w = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "white_pieces", "white_knight.png")),
    (TILE_LENGTH, TILE_LENGTH))
knight_img_b = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "black_pieces", "black_knight.png")),
    (TILE_LENGTH, TILE_LENGTH))

pawn_img_w = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "white_pieces", "white_pawn.png")),
    (TILE_LENGTH, TILE_LENGTH))
pawn_img_b = pygame.transform.scale(
    pygame.image.load(os.path.join("assets", "images", "black_pieces", "black_pawn.png")),
    (TILE_LENGTH, TILE_LENGTH))

valid_move_dot = pygame.transform.scale(pygame.image.load(os.path.join("assets", "images", "valid_move_dot.png")),
                                        (TILE_LENGTH, TILE_LENGTH))

images = {
    "king_w": king_img_w,
    "king_b": king_img_b,
    "queen_w": queen_img_w,
    "queen_b": queen_img_b,
    "rook_w": rook_img_w,
    "rook_b": rook_img_b,
    "bishop_w": bishop_img_w,
    "bishop_b": bishop_img_b,
    "knight_w": knight_img_w,
    "knight_b": knight_img_b,
    "pawn_w": pawn_img_w,
    "pawn_b": pawn_img_b,

    "selected": selected_img,
}


def create_piece(row: int, col: int, piece_name: str, color: str) -> Piece | None:
    match piece_name.lower():
        case "queen":
            return Queen(row, col, color, "queen")
        case "knight":
            return Knight(row, col, color, "knight")
        case "rook":
            return Rook(row, col, color, "rook")
        case "bishop":
            return Bishop(row, col, color, "bishop")

    return None


def get_piece(root: tk.Tk, piece_input: tk.Entry, row: int, col: int, color: str) -> Piece | None:
    piece = piece_input.get()

    match piece.lower():
        case "queen":
            root.destroy()
            return Queen(row, col, color, "queen")
        case "knight":
            root.destroy()
            return Knight(row, col, color, "knight")
        case "rook":
            root.destroy()
            return Rook(row, col, color, "rook")
        case "bishop":
            root.destroy()
            return Bishop(row, col, color, "bishop")

    return create_piece(row, col, piece, color)


class Piece:
    def __init__(self, row: int, col: int, color: str, piece_name: str) -> None:
        # координаты
        self.row = row
        self.col = col

        # кому принадлежит
        self.color = color

        self.piece_name = piece_name
        self.img_name = f"{piece_name}_{color}"
        self.is_selected = False

        # набор возможных ходов (обновляем каждый ход для каждой фигуры)
        self.valid_moves = set()

        self.first_move = True

    def select(self, window: pygame.Surface = None) -> None:
        self.is_selected = True

        if window is not None:
            self.draw(window)

    def unselect(self, window: pygame.Surface = None) -> None:
        self.is_selected = False
        if window is not None:
            self.draw(window)

    def one_direction(self, board: list[list[Piece, None]], candidates: set, row_change: int, col_change: int,
                      check: set) -> None:
        row, col = self.row, self.col

        # пробегаем по всей доске и добавляем клетки в candidates
        while row >= 0 and col < len(board[row]):
            row += row_change
            col += col_change

            if row < 0 or row >= len(board) or col < 0 or col >= len(board[row]):
                return

            # добавляем фигуру в check если клетка не пуста и там не стоит фигура того же цвета
            if board[row][col] is None:
                candidates.add((row, col))
                if board[row][col] is not None and board[row][col].piece_name == "king":
                    check.add(True)
            elif board[row][col].color != self.color:
                candidates.add((row, col))
                if board[row][col] is not None and board[row][col].piece_name == "king":
                    check.add(True)
                return
            elif board[row][col].color == self.color:  # если фигура того же цвета то клетка не подходит
                return

    def update_valid_moves(self, board: list[list[Piece, None]]) -> bool:
        self.valid_moves, check = self.all_valid_moves(board)

        # в check хранится флаг, который показывает поставлен ли шах
        return check

    def move(self, row: int, col: int, board: list[list[Piece, None]], window: pygame.Surface = None,
             replacement: str = None) -> bool:
        # координаты куда перемещаем фигуру
        if (row, col) not in self.valid_moves:
            return False

        self.first_move = False

        # перемещаем фигуру на новые координаты (все проверки координат выполняются в board)
        board[row][col] = board[self.row][self.col]
        board[self.row][self.col] = None  # убираем фигуру со старого места

        self.row = row
        self.col = col

        self.is_selected = False

        # обработка той ситуации когда пешка доходит до края доски
        if replacement:
            board[self.row][self.col] = create_piece(self.row, self.col, replacement, self.color)
            board[self.row][self.col].first_move = False

        # перерисовываем доску в переданом окне после перемещений
        if window is not None:
            board[self.row][self.col].draw(window)

        return True

    def draw(self, window: pygame.Surface) -> tuple[int]:
        # координаты левого верхнего угла
        x, y = coordinate_builder_to_absolute_coord(self.row, self.col)

        # если фигура выбрана, то отрисовываем по особому
        if not self.is_selected:
            img = images.get(self.img_name)
        else:
            img = images.get("selected")

            # отрисовываем все возможные ходы если фигура выбрана
            for row, col in self.valid_moves:
                # строим прямоугольник соответствующий клеточке и в центре рисуем круг
                dotx, doty = coordinate_builder_to_absolute_coord(row, col)

                dot_rect = valid_move_dot.get_rect()
                dot_rect.left = dotx
                dot_rect.top = doty

                window.blit(valid_move_dot, dot_rect)

        # рисуем фигуру
        img_rect = img.get_rect()
        img_rect.left = x
        img_rect.top = y

        window.blit(img, img_rect)


class King(Piece):
    def __init__(self, row: int, col: int, color: str, piece_name: str) -> None:
        super().__init__(row, col, color, piece_name)

        # клетки для рокировки
        self.rochade = set()

    def move(self, row: int, col: int, board: list[list[Piece, None]], window: pygame.Surface = None,
             replacement: str = None) -> bool:
        # проверка на рокировку
        if (row, col) in self.rochade:
            if col < self.col:
                # длинная рокировка, вызываем у ладьи метод перестановки
                board[self.row][0].move(self.row, self.col - 1, board, window, replacement)
            if col > self.col:
                # короткая рокировка
                board[self.row][7].move(self.row, self.col + 1, board, window, replacement)

        # передвигаем как обычную фигуру
        return super().move(row, col, board, window, replacement)

    def all_valid_moves(self, board: list[list[Piece, None]]) -> tuple[set, bool]:
        candidates = set()
        self.rochade = set()
        check = False

        for x in range(self.row - 1, self.row + 2):
            for y in range(self.col - 1, self.col + 2):
                # проверяем все клетки вокруг лежат ли на доске, пусты ли они и если не пусты то должна стоять фигура противника
                if x < len(board) and y < len(board[x]) and (x, y) != (self.row, self.col) and (
                        board[x][y] is None or board[x][y].color != self.color):
                    if 0 <= x <= 7 and 0 <= y <= 7:
                        candidates.add((x, y))
                        # выводим check если шаханули чужого короля (бред)
                        if board[x][y] is not None and board[x][y].piece_name == "king":
                            check = True

        # check for rochade
        # проверяем клетки для рокировки (должны быть пусты), проверяем не ходил ли король и проверяем наличие ладьи
        if self.first_move and board[self.row][0] is not None and board[self.row][0].first_move:
            if board[self.row][self.col - 3] is None and board[self.row][self.col - 2] is None and board[self.row][
                self.col - 1] is None:
                candidates.add((self.row, self.col - 2))
                self.rochade.add((self.row, self.col - 2))
        if self.first_move and board[self.row][7] is not None and board[self.row][7].first_move:
            if board[self.row][self.col + 2] is None and board[self.row][self.col + 1] is None:
                candidates.add((self.row, self.col + 2))
                self.rochade.add((self.row, self.col + 2))

        return candidates, check


class Queen(Piece):
    def all_valid_moves(self, board: list[list[Piece, None]]) -> tuple[set, bool]:
        candidates = set()
        check = set()

        change = [-1, 0]

        # отправляем в 4 потока
        with ThreadPoolExecutor(max_workers=4) as executor:
            # получаем все направление по кругу и чекаем их в каждом потоке с помощью метода one direction
            for i in range(4):
                # инвертирует ненулевое значение и возвращает пары по типу диагональ: [1, 1], лево: [-1, 1] и т.д
                change[int(i != 0)] *= -1

                # ставим на выполнение
                executor.submit(self.one_direction, board, candidates, *change, check)

                change[int(i != 0)] *= -1

                executor.submit(self.one_direction, board, candidates, *change, check)

                if i == 0:
                    change = change[::-1]
                if i == 1:
                    change[0] = -1

                change[0] *= -1

        return candidates, True in check


class Rook(Piece):
    def all_valid_moves(self, board: list[list[Piece, None]]) -> tuple[set, bool]:
        candidates = set()
        check = set()

        change = [1, 0]

        with ThreadPoolExecutor(max_workers=4) as executor:
            for i in range(1, 5):
                executor.submit(self.one_direction, board, candidates, *change, check)

                change = change[::-1]
                if i % 2 == 0:
                    change[0] *= -1

        return candidates, True in check


class Bishop(Piece):
    def all_valid_moves(self, board: list[list[Piece, None]]) -> tuple[set, bool]:
        candidates = set()
        check = set()

        change = [1, 1]

        with ThreadPoolExecutor(max_workers=4) as executor:
            for i in range(1, 5):
                executor.submit(self.one_direction, board, candidates, *change, check)

                change[1] *= -1
                if i % 2 == 0:
                    change[0] *= -1

        return candidates, True in check


class Knight(Piece):
    def all_valid_moves(self, board: list[list[Piece, None]]) -> tuple[set, bool]:
        candidates = set()
        check = False

        change = [1, -2]

        for i in range(8):
            if i % 2 == 0:
                change = change[::-1]
            if i % 4 == 0:
                change[0] *= -1

            x = self.row + change[0]
            y = self.col + change[1]

            if x >= 0 and x < len(board) and y >= 0 and y < len(board[x]):
                if board[x][y] is None or board[x][y].color != self.color:
                    candidates.add((x, y))
                    if board[x][y] is not None and board[x][y].piece_name == "king":
                        check = True

            change[int(i % 4 in (0, 1))] *= -1

        return candidates, check


class Pawn(Piece):
    def all_valid_moves(self, board: list[list[Piece, None]]) -> tuple[set, bool]:
        candidates = set()
        check = False

        direction = -1 if self.color == "w" else 1

        # в зависмисости от того первый или последующий ход чекаем клетку
        for i in range(1, 2 + int(self.first_move)):  # going forward
            if self.row + i * direction >= 0 and self.row + i * direction < len(board):
                if board[self.row + i * direction][self.col] is None:
                    candidates.add((self.row + i * direction, self.col))
            else:
                break

        # замена фигуры вроде как
        if self.row + 1 * direction < 0 or self.row + i * direction >= len(board):
            return candidates, check

        # diagonal kill
        if self.col + 1 < len(board[self.row + 1 * direction]) and board[self.row + 1 * direction][
            self.col + 1] is not None and board[self.row + 1 * direction][self.col + 1].color != self.color:
            candidates.add((self.row + 1 * direction, self.col + 1))
            if board[self.row + 1 * direction][self.col + 1] is not None and board[self.row + 1 * direction][
                self.col + 1].piece_name == "king":
                check = True
        if self.col - 1 >= 0 and board[self.row + 1 * direction][self.col - 1] is not None and \
                board[self.row + 1 * direction][self.col - 1].color != self.color:
            candidates.add((self.row + 1 * direction, self.col - 1))
            if board[self.row + 1 * direction][self.col - 1] is not None and board[self.row + 1 * direction][
                self.col - 1].piece_name == "king":
                check = True

        return candidates, check

