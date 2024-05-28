import datetime
import math
import random
import copy
from constants import DEPTH_FOR_HARD_BOT
import time

from bot import Bot
from sakevich.board import Board


def get_child_positions(position: Board, color: str) -> list[Board]:
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
                childs.append(temp)
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

    def play(self) -> None:
        print()
        print("Easy bot started playing")
        print()
        while (True):
            command = self.receive(4096)
            # обновляем доску у бота, делая ход, переданный от игрока (костыль)
            self.board.board[command["pos_before"][0]][command["pos_before"][1]].move(
                command["pos_after"][0], command["pos_after"][1], self.board.board
            )
            self.board.update_valid_moves()
            move = self.make_random_move()

            t = time.time()
            self.board.print_board()
            print("Evaluating...")
            print(self.minimax(self.board, DEPTH_FOR_HARD_BOT, -math.inf, math.inf, False))
            print(time.time() - t)

            self.board.board[move[0][0]][move[0][1]].move(move[1][0], move[1][1], self.board.board)
            print('Bot ' + "moved!", f'{move[0]} -> {move[1]}', '\n')
            print(evaluate_position(self.board))
            self.board.update_valid_moves()
            self.send({
                "command": "move",
                "p_name": self.name,
                "pos_before": move[0],
                "pos_after": move[1],
                "replacement": None,
            })

    def minimax(self, position: Board, depth: int, alpha, beta, maximizing_player: bool):
        """Функция для получения наилучшей возможной оценки на данной позиции."""
        if depth == 0:
            return evaluate_position(position)
        print(depth)

        if maximizing_player:
            max_eval = -math.inf
            child_positions = get_child_positions(position, "w")
            for child_position in child_positions:
                eval = self.minimax(child_position, depth - 1, alpha, beta, False)
                max_eval = max(eval, max_eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval

        else:
            min_eval = math.inf
            child_positions = get_child_positions(position, "b")
            for child_position in child_positions:
                eval = self.minimax(child_position, depth - 1, alpha, beta, True)
                min_eval = min(eval, min_eval)
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
                        # print(piece.valid_moves)
                        for move in piece.valid_moves:
                            print("Random move!")
                            return [(row, col), move]


