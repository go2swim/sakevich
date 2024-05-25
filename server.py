import queue
import socket
import pickle
import threading
import time
from threading import Thread, Lock
from easy_bot import EasyBot
from hard_bot import HardBot

import constants
from constants import SERVER_ADDR
from board import Board

# создаём сервер с протоколом TCP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDR)  # присваиваем ему адресс
server_socket.listen()  # и прослушиваем его

# храним все запущеные сессии
boards = []
connection_sockets = []
client_names = []
connection_count = 0
lock = Lock()
condition = threading.Condition()


def create_bot(name: str, difficult: str) -> None:
    if difficult == 'hard':
        bot = HardBot(name, SERVER_ADDR)
    elif difficult == 'easy':
        bot = EasyBot(name, SERVER_ADDR)
    else:
        raise ValueError("incorrect request to create a bot")

    bot.play()


def send_remaining_time(client_socket, remaining_time):
    try:
        client_socket.send(f"TIME:{remaining_time}".encode("utf-8"))
    except (ConnectionResetError, ConnectionAbortedError):
        pass


# передаём для каждого клента socket, который осуществляет передачу данных, свой экземпляр доски и порядковый номер подключения
def client_thread(client_socket: socket.socket, board: Board, connection_number: int) -> None:
    global connection_count

    # замораживаемся на проверке пришёл ли напарник и разморозимся когда человек зайдёт и пополнит список клиентов
    if connection_number % 2 == 0:
        communicating_client_num = connection_number + 1  # если у пользователя чётный номер то у напарника следующий
        # таймер
        start_time = time.time()
        while communicating_client_num >= len(connection_sockets):
            elapsed_time = time.time() - start_time
            remaining_time = constants.WAIT_TIME - elapsed_time
            if remaining_time <= 0:
                with lock:
                    # кидаем создание и поддерживание бота в отдельный поток
                    bot_thread = threading.Thread(target=create_bot, args=(f"Bot {connection_number + 1}", 'hard'))
                    bot_thread.start()
                    break

            send_remaining_time(client_socket, remaining_time)

            # Проверяем входящие сообщения от клиента
            try:
                client_socket.settimeout(1)
                data = client_socket.recv(1024)

                try:
                    response = data.decode("utf-8")
                except UnicodeDecodeError:
                    raise UnicodeDecodeError("incorrect message format from the client")

                #если отправили одновреммено две команды то просто смотрим первую
                message = response.split('|')[0]

                if message == 'add_easy_bot':
                    print("add_easy_bot")
                    with lock:
                        bot_thread = threading.Thread(target=create_bot, args=(f"Bot {connection_number + 1}", 'easy'))
                        bot_thread.start()
                        break
                elif message == 'add_hard_bot':
                    with lock:
                        bot_thread = threading.Thread(target=create_bot, args=(f"Bot {connection_number + 1}", 'hard'))
                        bot_thread.start()
                        break
                else:
                    raise ValueError(f'incorrect request format from client: {message}')

            except socket.timeout:
                continue  # Игнорируем таймауты и продолжаем ожидание
            except Exception as e:
                print(f"Error while waiting for opponent: {e}")
                client_socket.close()
                connection_count -= 1
                return
    else:
        communicating_client_num = connection_number - 1

    # после того как пара образовалась начинаем опрашивать имена
    try:
        client_socket.send('\nGET:need_name'.encode("utf-8"))
    except Exception:
        raise TimeoutError

    try:
        client_name = client_socket.recv(1024).decode("utf-8")  # получаем по каналу 1024 байта и декодируем в имя
    except Exception as e:
        print(f"Error while receiving client name: {e}")
        client_socket.close()
        connection_count -= 1
        return

    client_names.append(client_name)
    board.set_name(client_name)

    # Ожидаем, пока оба клиента не установят свои имена
    while len(client_names) % 2 != 0:
        try:
            continue
        except socket.timeout:
            continue

    # если имя уже есть на сервере то отключаем соеденение
    if client_names[connection_number] == client_names[communicating_client_num]:
        client_socket.close()
        print("[LOST] connection to a client")
        connection_count -= 1
        return

    # сереализуем и отправляем по каналу нашу доску
    client_socket.send(b"BOARD:" + pickle.dumps(board))

    client_socket.settimeout(100)

    # ждём пока не получим доску оппонента
    while True:
        try:
            # ожидаем формочку доски от оппонента
            print(f'{threading.current_thread().name}: request {client_names[connection_sockets.index(client_socket)]}')

            command = client_socket.recv(4096)

            print(f'{threading.current_thread().name}: get from {client_names[connection_sockets.index(client_socket)]}')

            board.command(pickle.loads(command))  # десериализуем словарь и отправляем доске
            # сделали изменения на доске в соответсвии с командой, изменили команду и отсылаем обратно оппоненту
            connection_sockets[communicating_client_num].send(command)

            print(f'{threading.current_thread().name}: send to {client_names[communicating_client_num]}')
        # сервер прекратил передачу, поток завершил сам клиент, проблемы при передаче
        except (ConnectionResetError, ConnectionAbortedError, EOFError):
            # убираем клиента с сервера
            client_socket.close()
            print("[LOST] connection to a client")
            connection_sockets[communicating_client_num].close()
            print("[LOST] connection to a client")
            connection_count -= 1
            return


if __name__ == "__main__":
    print("[WAITING] for incoming connections")

    while True:
        # ждём нового подключения
        client_socket, addr = server_socket.accept()
        connection_sockets.append(client_socket)
        connection_count += 1

        print(f"[CONNECTION] total: {connection_count}")

        # проверяем нужна ли новая доска
        if (len(connection_sockets) - 1) // 2 >= len(boards):
            boards.append(Board())  # создаём новую доску если кол-во клиентов чётно
            print(f"[CREATED] new board, total: {len(boards)}")

        # создаём поток для нового клиента и передаём аргументы которые попадут в метод client_thread
        # передаём socket для передачи данных, доску на которой будет игра и порядковый номер клиента
        thread = Thread(target=client_thread, args=(client_socket, boards[-1], len(connection_sockets) - 1))
        thread.start()

