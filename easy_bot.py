import copy
import random

from bot import Bot
from board import Board


class EasyBot(Bot):
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
            possible_player_moves = self.get_possible_player_moves()
            move = self.take_piece(possible_player_moves)
            move = self.take_care(possible_player_moves) if not move else move
            move = self.make_random_move() if not move else move
            self.board.board[move[0][0]][move[0][1]].move(move[1][0], move[1][1], self.board.board)

            print('Bot ' + "moved!", f'{move[0]} -> {move[1]}', '\n')
            self.board.update_valid_moves()
            self.send({
                "command": "move",
                "p_name": self.name,
                "pos_before": move[0],
                "pos_after": move[1],
                "replacement": None,
            })

    def make_random_move(self) -> list[tuple[int, int], tuple[int, int]]:
        """Делает рандомный ход в случае, если не нашлось фигуры соперника, которую можно съесть."""
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

    def take_piece(self, possible_player_moves: list) -> list[tuple[int, int], tuple[int, int]] or None:
        """Ищет самую сладенькую фигуру для взятия."""
        best_move = []
        best_value = 0

        for row in range(8):
            for col in range(8):
                piece = self.board.board[row][col]
                if not piece or not piece.valid_moves or piece.color != 'b':
                    continue
                bots_piece_value = piece.get_value()
                for move in piece.valid_moves:
                    piece_to_take = self.board.board[move[0]][move[1]]
                    if not piece_to_take:
                        continue
                    players_piece_value = piece_to_take.get_value()
                    if players_piece_value < best_value:
                        continue
                    if bots_piece_value <= players_piece_value:
                        best_move = [(row, col), move]
                        best_value = players_piece_value
                        continue
                    temp = self.test_one_move_ahead(self.board, (row, col), move)
                    if move not in temp.get_possible_player_moves():
                        best_move = [(row, col), move]
                        best_value = players_piece_value
                        continue
        if best_move:
            print("Piece taken!")
        return best_move

    def test_one_move_ahead(self, board: Board, pos_before: tuple[int, int], pos_after: tuple[int, int]) -> Board:
        """Создаёт копию доски и делает ход.
        Нужно для расчёта на один ход вперёд."""
        temp = copy.deepcopy(board)
        temp.board[pos_before[0]][pos_before[1]].move(pos_after[0], pos_after[1], temp.board)
        temp.update_valid_moves()
        return temp

    def take_care(self, possible_player_moves: list) -> list[tuple[int, int], tuple[int, int]] or None:
        """Если у бота есть фигура под боем, он её жадно спасёт,
        если ценность фигуры выше ценности фигуры соперника."""
        best_move = None
        best_value = 0

        for row in range(len(self.board.board)):
            for col in range(len(self.board.board[0])):
                piece = self.board.board[row][col]
                if not piece or not piece.valid_moves:
                    continue
                value = piece.get_value()
                for i in range(8):
                    for j in range(8):
                        players_piece = self.board.board[i][j]
                        if (not players_piece or not players_piece.valid_moves
                                or (row, col) not in players_piece.valid_moves
                                or players_piece.get_value() >= value
                                or best_value >= value):
                            print("Continued")
                            continue
                        for move in piece.valid_moves:
                            if move not in players_piece.valid_moves:
                                best_move = [(row, col), move]
                                best_value = value
        if best_move:
            print("Took care!")
        return best_move

    def get_possible_player_moves(self):
        """Возвращает список всех возможных ходов игрока."""
        possible_player_moves = []
        for row in range(len(self.board.board)):
            for col in range(len(self.board.board[0])):
                piece = self.board.board[row][col]
                if not piece or not piece.valid_moves or piece.color != 'w':
                    continue
                possible_player_moves += piece.valid_moves
                # print(possible_player_moves)
        return possible_player_moves