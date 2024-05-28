import datetime
import math
import random
import copy
from constants import DEPTH_FOR_HARD_BOT
import time

from bot import Bot
from board import Board


def get_child_positions(position: Board, color: str) -> list[tuple[tuple[int, int], tuple[int, int], Board]]:
    """Функция для получения дочерних позиций."""
    childs = []
    for row in range(8):
        for col in range(8):
            piece = position.board[row][col]
            if not piece or not piece.valid_moves or piece.color != color:
                continue

            for move in piece.valid_moves:
                temp = copy.deepcopy(position)
                temp.board[row][col].move(move[0], move[1], temp.board)
                temp.update_valid_moves()
                childs.append(((row, col), move, temp))
    return childs


def evaluate_position(board: Board) -> float:
    """Функция для оценки позиции исключительно на основе веса фигур"""
    evaluation = 0.0
    for row in range(8):
        for col in range(8):
            piece = board.board[row][col]
            if not piece:
                continue
            evaluation = (evaluation + piece.get_value() if piece.color == 'w'
                          else evaluation - piece.get_value())
    return evaluation


class HardBot(Bot):
    def __init__(self, name: str, server_addr: tuple[str, int]):
        super().__init__(name, server_addr)
        self.current_best_move = None


    def play(self) -> None:
        print()
        print("Hard bot started playing")
        print()
        while (True):
            command = self.receive(4096)
            # обновляем доску у бота, делая ход, переданный от игрока (костыль)
            self.board.move(**command)
            self.board.update_valid_moves()
            self.board.print_board()

            t = time.time()
            print("Evaluating...")
            self.minimax(self.board, DEPTH_FOR_HARD_BOT, -math.inf, math.inf, False)
            print(time.time() - t)
            if not self.current_best_move:
                self.current_best_move = self.make_random_move()

            self.board.move(self.name, self.current_best_move[0], self.current_best_move[1])

            print('Bot ' + "moved!", f'{self.current_best_move[0]} -> {self.current_best_move[1]}', '\n')
            self.board.update_valid_moves()
            self.send({
                "command": "move",
                "p_name": self.name,
                "pos_before": self.current_best_move[0],
                "pos_after": self.current_best_move[1],
                "replacement": None,
            })

            self.current_best_move = None

    def minimax(self, position: Board, depth: int, alpha, beta, maximizing_player: bool):
        """Функция для получения наилучшей возможной оценки на данной позиции."""
        if depth == 0:
            return evaluate_position(position)

        if maximizing_player:
            max_eval = -math.inf
            child_positions = get_child_positions(position, "w")
            for child_position in child_positions:
                eval = self.minimax(child_position[2], depth - 1, alpha, beta, False)
                if eval >= max_eval:
                    max_eval = eval
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = math.inf
            child_positions = get_child_positions(position, "b")
            for child_position in child_positions:
                eval = self.minimax(child_position[2], depth - 1, alpha, beta, True)
                if eval <= min_eval:
                    min_eval = eval
                    self.current_best_move = (child_position[0], child_position[1])
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval

    def make_random_move(self) -> list[tuple[int, int], tuple[int, int]]:
        """Делает рандомный ход."""
        rows = [i for i in range(len(self.board.board))]
        cols = [j for j in range(len(self.board.board[0]))]
        random.shuffle(rows)
        random.shuffle(cols)
        for row in rows:
            for col in cols:
                piece = self.board.board[row][col]
                if piece:
                    if piece.color == 'b' and piece.valid_moves:
                        piece.is_selected = True
                        for move in piece.valid_moves:
                            print("Random move!")
                            return [(row, col), move]