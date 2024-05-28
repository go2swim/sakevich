from queue import Queue
import socket
import pickle

import pygame
from typing import Any


class Client:
    def __init__(self, name: str, server_addr: tuple[str, int], window: pygame.Surface, key_event_queue: Queue) -> None:
        self.name = name
        self.server_addr = server_addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.board = self.connect(window, key_event_queue)

    def connect(self, window: pygame.Surface, key_event_queue: Queue) -> bytes:
        # конектим сокет к серверу по адресу и порту, далее можно обмениваться с помощью него данными
        self.socket.connect(self.server_addr)
        mode = False

        while True:
            try:
                data = self.socket.recv(4096 * 8)  # Ждём ответа от сервера
                # если пришла доска, значит присоеденился реальный игрок
                if data.startswith(b"BOARD:"):
                    board_data = pickle.loads(data[6:])
                    return board_data
                else:
                    data = data.decode("utf-8").split('\n')
                    if data[0].startswith("TIME:"):
                        remaining_time = float(data[0][5:])

                        from window import draw_waiting
                        draw_waiting(window, remaining_time, mode)

                        # Проверяем очередь сообщений на команду добавления бота
                        if not key_event_queue.empty():
                            command = key_event_queue.get()
                            if command == "key_1":
                                # Отсылаем на сервер, что бот добавлен
                                self.send(b'add_easy_bot|', dump_pickle=False)
                                print('send request 1')
                            elif command == "key_2":
                                self.send(b'add_hard_bot|', dump_pickle=False)
                                print('send request 2')
                            elif command == "key_3":
                                self.send(b'blitz|', dump_pickle=False)
                                mode = not mode
                                print('send request blitz')
                            elif command == 'tup_space':
                                pass
                            else:
                                raise ValueError(f'Incorrect command in queue: {command}')

                    if len(data) > 1 and data[1].startswith("GET:"):
                        message = data[1][4:]
                        if message == "need_name":
                            self.send(bytes(self.name, "utf-8"), dump_pickle=False)
            except Exception as e:
                raise e

    def disconnect(self) -> None:
        self.socket.close()

    def send(self, content: Any, dump_pickle: bool = True) -> None:
        # берём объект, сериализуем (в зависимости от флага) и отправляем на сервер
        if dump_pickle:
            content = pickle.dumps(content)

        self.socket.send(content)

    def receive(self, bufsize: int, load_pickle: bool = True) -> Any:
        # ожидаем ответа от сервера, десериализуем (в зависимости от флага) и возвращаем
        result = self.socket.recv(bufsize)

        if load_pickle:
            result = pickle.loads(result)

        return result