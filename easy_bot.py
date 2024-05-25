from bot import Bot
import random


class EasyBot(Bot):
    def __init__(self, name: str, server_addr: tuple[str, int]):
        super().__init__(name, server_addr)

    def play(self) -> None:
        print()
        print("Easy bot started playing")
        print()
        while (True):
            self.receive(4096)
            self.board.update_valid_moves()
            move = self.make_random_move()
            self.send({
                "command": "move",
                "p_name": self.name,
                "pos_before": move[0],
                "pos_after": move[1],
                "replacement": None,
            })

    def make_random_move(self) -> list[tuple[int, int], tuple[int, int]]:
        """Делает рандомный ход в случае, если не нашлось фигуры соперника, которую можно съесть"""
        rows = [i for i in range(len(self.board.board))]
        cols = [j for j in range(len(self.board.board[0]))]
        random.shuffle(rows)
        random.shuffle(cols)
        for row in rows:
            for col in cols:
                piece = self.board.board[row][col]
                if piece:
                    if piece.color == 'b' and piece.valid_moves:
                        for move in piece.valid_moves:
                            piece.move(move[0], move[1], self.board.board)
                            self.board.update_valid_moves()
                            print()
                            print('Bot:' + "moved!", f'{(row, col)} -> {move}', '\n')
                            return [(row, col), move]