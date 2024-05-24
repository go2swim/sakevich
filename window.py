import os
import queue
import threading
import time
import pygame
import tkinter as tk
import queue

import utils
from client import Client
from piece import get_piece
from constants import BOARD_LENGTH, SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_ADDR, FONT, TILE_LENGTH, WHITE, CAPTION, BLACK, RED



def draw_start_menu(window: pygame.Surface, name: str, connection_lost: bool=False, connection_refused: bool=False) -> None:
    #делаем фон окошка чёрным
    window.fill(BLACK)  # TODO: load bg image

    #устанавливаем шрифт и создаём текст
    font = pygame.font.SysFont(FONT, SCREEN_HEIGHT//10)
    text1 = font.render("Press space key", True, WHITE)
    text2 = font.render("to enter a game", True, WHITE)
    text3 = font.render(name, True, WHITE)

    #вывод сообщения если клиент не подключ  к серверу
    if connection_refused:
        conn_text = font.render("(connection refused)", True, RED)
        conn_text_rect = conn_text.get_rect()
        conn_text_rect.centerx = SCREEN_WIDTH/2
        window.blit(conn_text, conn_text_rect)

    #вывод сообщения если сервер отпал
    if connection_lost:
        conn_text = font.render("(connection lost)", True, RED)
        conn_text_rect = conn_text.get_rect()
        conn_text_rect.centerx = SCREEN_WIDTH/2
        window.blit(conn_text, conn_text_rect)

    #создаём прямоугольники для текста
    text1_rect = text1.get_rect()
    text1_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - SCREEN_HEIGHT//10)
    text2_rect = text2.get_rect()
    text2_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    text3_rect = text3.get_rect()
    text3_rect.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + SCREEN_HEIGHT//10)

    #натягиваем текст на прямоугольник
    window.blit(text1, text1_rect)
    window.blit(text2, text2_rect)
    window.blit(text3, text3_rect)

    pygame.display.update()

def draw_waiting(window: pygame.Surface, remaining_time: float) -> None:
    window.fill(BLACK)

    #аналогично рисуем экран ожидания
    font = pygame.font.SysFont(FONT, SCREEN_HEIGHT//20)
    text1 = font.render("Waiting for enemy...", True, WHITE)
    text2 = font.render(f"Bot will be added in {int(remaining_time)} seconds...", True, WHITE)
    text3 = font.render(f"Press the space if you want to add a bot", True, WHITE)

    text_rect1 = text1.get_rect()
    text_rect1.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60)

    text_rect2 = text2.get_rect()
    text_rect2.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    text_rect3 = text3.get_rect()
    text_rect3.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60)

    window.blit(text1, text_rect1)
    window.blit(text2, text_rect2)
    window.blit(text3, text_rect3)

    pygame.display.update()



key_event_queue = queue.Queue()

def create_client(name: str, server_addr: tuple[str, int], window: pygame.Surface, key_event_queue: queue.Queue):
    try:
        new_client = Client(name, server_addr, window, key_event_queue)
        key_event_queue.put(new_client)  # Передаём созданного клиента в очередь
    except ConnectionRefusedError:
        key_event_queue.put(None)  # Передаём None в очередь, если соединение не удалось

def menu_screen(window: pygame.Surface, name: str, connection_lost: bool=False) -> None:
    draw_start_menu(window, name, connection_lost)

    client_thread = None
    new_client = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("tup")
                    key_event_queue.put("tup_space")

        if client_thread is None:
            if not key_event_queue.empty():
                event = key_event_queue.get()
                if event == "tup_space":
                    client_thread = threading.Thread(target=create_client, args=(name, SERVER_ADDR, window, key_event_queue))
                    client_thread.start()
        else:
            if not client_thread.is_alive():
                if not key_event_queue.empty():
                    while new_client is None:
                        message = key_event_queue.get()
                        if isinstance(message, Client):
                            new_client = message
                        elif key_event_queue.empty():
                            raise ValueError("there is no client in the queue")
                            # draw_start_menu(window, name, connection_refused=True)
                            # client_thread = None  # Сбросить поток, чтобы можно было попытаться снова

                        chess_game(window, new_client)
                        break

        pygame.display.update()

#основной метод, тут происходит вся игра
def chess_game(window: pygame.Surface, client: Client) -> None:
    #отрисовываем задник
    window.fill(BLACK)
    board = client.board
    board.draw(window, client.name)
    pygame.display.update()

    #метод для опроса сервера, вынесен в отдельный метод чтобы запустить в отдельном потоке
    def receive_move(client, command_queue):
        while True:
            try:
                #ожидаем пока сервер ответит, из за этого окно зависало
                command = client.receive(4096)
                command_queue.put(command)
            except ConnectionResetError:
                command_queue.put("connection_lost")
                break

    #в очередь будем складывать все команды которые прилетают с сервера
    command_queue = queue.Queue()
    receive_thread = threading.Thread(target=receive_move, args=(client, command_queue))
    #обозначаем поток как фоновый
    receive_thread.daemon = True
    #запускаем receive_move в отдельном потоке11
    receive_thread.start()

    while True:
        if board.winner is not None:
            time.sleep(5)
            menu_screen(window, client.name)

        try:
            #извлекаем элемент из очереди, если нет элемента то выкидываем ошибку (обычный get ждёт пока элемент не появится)
            command = command_queue.get_nowait()
            if command == "connection_lost":
                menu_screen(window, client.name, connection_lost=True)
            else:
                command["window"] = window
                command["my_name"] = client.name
                #даём доске обработать входящюю команду и обновится
                #в обработку входит и отрисовка на нашем окне
                board.command(command, window)
                print('get command')
        except queue.Empty:
            pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                client.disconnect()
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()

                #переходим в систему координат доски
                col, row = utils.coordinate_builder_to_tile_coord(x, y)

                if not 0 <= row <= 7 or not 0 <= col <= 7:
                    continue

                selected = board.selected

                #обращаемся к доске, и проверяем валидность клика
                if board.click(client.name, row, col, window):
                    replacement = None

                    #если пешка дошла до края, то вызываем ущербное окно
                    if board.board[row][col].piece_name == "pawn" and (
                            row == 0 and board.board[row][col].color == "w" or
                            row == 7 and board.board[row][col].color == "b"):
                        new_piece = []

                        root = tk.Tk()
                        tk.Label(root, text="Enter the piece you want to replace your pawn with").grid(row=0)
                        piece_input = tk.Entry(root)
                        piece_input.grid(row=1)
                        tk.Button(root, text="Enter", command=lambda: new_piece.append(get_piece(root, piece_input, row, col, board.board[row][col].color))).grid(row=2, pady=4)

                        root.mainloop()

                        board.board[row][col] = new_piece[-1]
                        board.update_valid_moves()
                        board.board[row][col].draw(window)

                        replacement = new_piece[-1].piece_name

                    #отправляем оппоненту данные о перестановке, чтобы он обновил доску и начал ход
                    try:
                        client.send({
                            "command": "move",
                            "p_name": client.name,
                            "pos_before": selected,
                            "pos_after": (row, col),
                            "replacement": replacement,
                        })
                        print('send')
                    except Exception:
                        print('didnt send')

        pygame.display.update()


def main() -> None:
    pygame.init()

    #создаём формочку для ввода имени
    def submit():
        name.set(entry.get())
        root.destroy()

    root = tk.Tk()
    root.title("Enter Name")

    tk.Label(root, text="Enter your name:").pack(pady=10)
    entry = tk.Entry(root)
    entry.pack(pady=10)

    name = tk.StringVar()
    tk.Button(root, text="Submit", command=submit).pack(pady=10)
    root.geometry("400x200")
    root.mainloop()

    inter_name = name.get()


    #задаём параметры окна
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    #назавание окна в шапке и картинка
    pygame.display.set_caption(CAPTION)
    pygame.display.set_icon(pygame.image.load(os.path.join("assets", "images", "window_icon.png")))

    #отрисовываем менюшку и ждём нажатие пробела
    menu_screen(window, inter_name)


if __name__ == "__main__": main()