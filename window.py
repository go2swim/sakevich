import os
import threading
import time
import pygame
import tkinter as tk
import queue
import piece

import utils
from tkinter import messagebox
from client import Client
from piece import get_piece
from constants import BOARD_LENGTH, SCREEN_WIDTH, SCREEN_HEIGHT, SERVER_ADDR, FONT, TILE_LENGTH, WHITE, CAPTION, BLACK, \
    RED, TIME_TO_MOVE


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

def draw_waiting(window: pygame.Surface, remaining_time: float, mode: bool) -> None:
    window.fill(BLACK)

    if mode:
        alarm_img = pygame.transform.scale(
            pygame.image.load(os.path.join("assets", "images", "alarm_clock.png")),
            (TILE_LENGTH, TILE_LENGTH))
        alarm_rect = alarm_img.get_rect()
        alarm_rect.center = ((SCREEN_WIDTH - TILE_LENGTH), (SCREEN_HEIGHT - TILE_LENGTH))
        window.blit(alarm_img, alarm_rect)


    #аналогично рисуем экран ожидания
    font = pygame.font.SysFont(FONT, SCREEN_HEIGHT//20)
    text1 = font.render("Waiting for enemy...", True, WHITE)
    text2 = font.render(f"Bot will be added in {int(remaining_time)} seconds...", True, WHITE)
    text3 = font.render(f"Press :", True, WHITE)
    text4 = font.render(f"1 - if you want to add a easy bot", True, WHITE)
    text5 = font.render(f"2 - if you want to add a hard bot", True, WHITE)
    text6 = font.render(f"3 - blitz", True, WHITE)

    indentation_between_blocks = 60

    text_rect1 = text1.get_rect()
    text_rect1.center = (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - indentation_between_blocks * 5)

    text_rect2 = text2.get_rect()
    text_rect2.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - indentation_between_blocks * 2)

    text_rect3 = text3.get_rect()
    text_rect3.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)

    text_rect4 = text4.get_rect()
    text_rect4.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + indentation_between_blocks)

    text_rect5 = text5.get_rect()
    text_rect5.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + indentation_between_blocks * 2)

    text_rect6 = text6.get_rect()
    text_rect6.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + indentation_between_blocks * 3)

    window.blit(text1, text_rect1)
    window.blit(text2, text_rect2)
    window.blit(text3, text_rect3)
    window.blit(text4, text_rect4)
    window.blit(text5, text_rect5)
    window.blit(text6, text_rect6)

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
                elif event.key == pygame.K_1:
                    print("1 pressed")
                    key_event_queue.put("key_1")
                elif event.key == pygame.K_2:
                    print("2 pressed")
                    key_event_queue.put("key_2")
                elif event.key == pygame.K_3:
                    print('3 pressed')
                    key_event_queue.put("key_3")

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


PIECE_IMAGES = {
    "queen_w": piece.queen_img_w,
    "rook_w": piece.rook_img_w,
    "bishop_w": piece.bishop_img_w,
    "knight_w": piece.knight_img_w,
    "queen_b": piece.queen_img_b,
    "rook_b": piece.rook_img_b,
    "bishop_b": piece.bishop_img_b,
    "knight_b": piece.knight_img_b
}

def create_promotion_window(window, color):
    # Создание окна для выбора фигуры
    promotion_window = pygame.Surface((300, 100))
    promotion_window.fill(WHITE)  # Белый фон

    # Расположение изображений фигур
    piece_names = ["queen", "rook", "bishop", "knight"]
    buttons = []

    offset_between_images = 75
    for i, piece_name in enumerate(piece_names):
        img = PIECE_IMAGES[f"{piece_name}_{color}"]
        img_rect = img.get_rect(topleft=(i * offset_between_images, 0))
        promotion_window.blit(img, img_rect)
        buttons.append((img_rect, piece_name))

    return promotion_window, buttons

def handle_promotion_click(buttons, mouse_pos, promo_window_pos):
    #переходим в систему координат нового окна
    relative_mouse_pos = (mouse_pos[0] - promo_window_pos[0], mouse_pos[1] - promo_window_pos[1])
    for rect, piece_name in buttons:
        print(f'mouse_pos == {relative_mouse_pos}')
        #функция проверяет лежат ли координаты в прямоугольнике
        if rect.collidepoint(relative_mouse_pos):
            return piece_name
    return None


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
    lock = threading.Lock()

    def update_timer():
        print(f'timer start working')

        last_update_time = time.perf_counter()

        def update_timer_for_player(name: str):
            nonlocal last_update_time
            current_time = time.perf_counter()
            elapsed_time = current_time - last_update_time
            if elapsed_time >= 1:
                time_in_board = board.timers[name]
                update_time = time_in_board - int(elapsed_time)
                if update_time <= 0:
                    board.update_winner = client.name
                    return

                board.timers[name] = update_time
                print(f'time:{board.timers[name]}')

                with lock:
                    board.update_time_in_board(window)

                last_update_time = current_time

                client.send(f'TIME:{board.timers[name]}')

        while True:
            if board.turn.startswith('Bot') or board.turn == client.name:
                update_timer_for_player(board.turn)
            else:
                # Сброс времени последнего обновления, чтобы время не уменьшалось, пока другой игрок ходит
                last_update_time = time.perf_counter()

            time.sleep(0.01)


    if board.mode == 'blitz':
        board.timers[client.name] = TIME_TO_MOVE
        timer_thread = threading.Thread(target=update_timer)
        timer_thread.start()

    while True:
        if board.winner is not None:
            time.sleep(5)
            menu_screen(window, client.name)

        try:
            #извлекаем элемент из очереди, если нет элемента то выкидываем ошибку (обычный get ждёт пока элемент не появится)
            command = command_queue.get_nowait()
            if command == "connection_lost":
                menu_screen(window, client.name, connection_lost=True)
            elif isinstance(command, dict):
                command["window"] = window
                command["my_name"] = client.name
                #даём доске обработать входящюю команду и обновится
                #в обработку входит и отрисовка на нашем окне
                board.command(command, window)
                print('get command')
            elif isinstance(command, str) and command.startswith('TIME:'):
                with lock:
                    board.timers[board.turn] = int(command[5:])
                    board.update_time_in_board(window)
            else:
                raise ValueError(f"Incorrect request{command}")
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

                    #если пешка дошла до края, то вызываем окно
                    if board.board[row][col].piece_name == "pawn" and (
                            row == 0 and board.board[row][col].color == "w" or
                            row == 7 and board.board[row][col].color == "b"):
                        promotion_window, buttons = create_promotion_window(window, board.board[row][col].color)
                        promo_window_pos = (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 50)
                        while True:
                            for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                    pygame.quit()
                                    exit()
                                elif event.type == pygame.MOUSEBUTTONDOWN:
                                    mouse_pos = pygame.mouse.get_pos()
                                    piece_name = handle_promotion_click(buttons, mouse_pos, promo_window_pos)
                                    if piece_name:
                                        new_piece = get_piece(piece_name, row, col, board.board[row][col].color)
                                        board.board[row][col] = new_piece
                                        board.update_valid_moves()
                                        board.board[row][col].draw(window)
                                        replacement = new_piece.piece_name
                                        break
                            if replacement:
                                break
                            window.blit(promotion_window, promo_window_pos)
                            pygame.display.update()
                        # Убираем окно после выбора фигуры
                        window.fill(BLACK)
                        board.draw(window, client.name)
                        pygame.display.update()

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

    while True:
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
        if inter_name:
            break
        else:
            messagebox.showwarning("Invalid input", "Name cannot be empty. Please enter a valid name.")


    #задаём параметры окна
    window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    #назавание окна в шапке и картинка
    pygame.display.set_caption(CAPTION)
    pygame.display.set_icon(pygame.image.load(os.path.join("assets", "images", "window_icon.png")))

    #отрисовываем менюшку и ждём нажатие пробела
    menu_screen(window, inter_name)


if __name__ == "__main__": main()