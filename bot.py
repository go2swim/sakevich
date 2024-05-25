import collections
import dataclasses
import random
import time

from client import Client
from queue import Queue
import pickle
import pygame
import threading
import time

from sakevich.piece import Piece


@dataclasses.dataclass
class Move:
    piece: Piece
    current_position: tuple[int, int]
    new_position: tuple[int, int]


class Bot(Client):
    def __init__(self, name: str, server_addr: tuple[str, int]):
        #сюда окно с очередью ивентов не передаём т.к тут нам рисовать окно не нужно
        super().__init__(name, server_addr, None, None)
        play_thread = threading.Thread(target=self.play())
        play_thread.start()

    def connect(self, window: pygame.Surface = None, key_event_queue: Queue = None):
        self.socket.connect(self.server_addr)
        while(True):
            data = self.socket.recv(4096 * 8)
            if data.startswith(b"BOARD:"):
                a = pickle.loads(data[6:])
                return pickle.loads(data[6:])
            elif data.startswith(b'\nGET:'):
                self.send(bytes(self.name, "utf-8"), dump_pickle=False)
            else:
                raise ValueError("incorrect request for the bot")


    def play(self):
        print("Сделай меня, Артём")
        while(True):
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
                            print("moved!", f'{(row, col)} -> {move}', '\n')
                            return [(row, col), move]













