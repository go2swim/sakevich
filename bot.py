import time

from client import Client
from queue import Queue
import pickle
import pygame
import threading
import time




class Bot(Client):
    def __init__(self, name: str, server_addr: tuple[str, int]):
        #сюда окно с очередью ивентов не передаём т.к тут нам рисовать окно не нужно
        super().__init__(name, server_addr, None, None)
        # play_thread = threading.Thread(target=self.play())
        # play_thread.start()

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
            self.send({
                "command": "move",
                "p_name": self.name,
                "pos_before": (1, 1),
                "pos_after": (1, 1),
                "replacement": None,
            })

