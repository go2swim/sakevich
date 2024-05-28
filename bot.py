import threading
from typing import Any

from client import Client
from queue import Queue
import pickle
import pygame


class Bot(Client):
    def __init__(self, name: str, server_addr: tuple[str, int]):
        # сюда окно с очередью ивентов не передаём т.к тут нам рисовать окно не нужно
        super().__init__(name, server_addr, None, None)

    def connect(self, window: pygame.Surface = None, key_event_queue: Queue = None) -> None:
        self.socket.connect(self.server_addr)
        while (True):
            data = self.socket.recv(4096 * 8)
            if data.startswith(b"BOARD:"):
                return pickle.loads(data[6:])
            elif data.startswith(b'\nGET:'):
                self.send(bytes(self.name, "utf-8"), dump_pickle=False)
            else:
                raise ValueError("incorrect request for the bot")

    def play(self) -> None:
        pass
