import threading
from board_ui import Board, get_x_y_w_h, pygame
from logic import Logic, Color, State, Square, Move
from constants import *
from tools.button import ButtonRect, ButtonImage, ButtonThread
from tools.label import Label
from reseau import *
import tools.text_input as text_input
import random
import time
import logging

logging.basicConfig(level=logging.INFO)

COLOR_CHANGING = (0, 85, 170)


class Game:
    def __init__(self, win, fen):
        self.win = win
        self.logic = Logic(fen)
        self.board = Board()
        self.board.update(self.logic)

        self.current_piece_legal_moves = []
        self.game_on = True
        self.window_on = True

        # Server
        self.socket = None
        self.server_thread = None
        self.last_retrieved_fen = self.logic.get_fen()
        self.color = None
        self.connected_to_server = False
        self.waiting_for_opponent = False

        # # # Assets
        # button to quit
        self.btn_quit = ButtonRect(15, 15, RED)
        self.btn_minimize = ButtonRect(15, 15, YELLOW)

        # button to flip the board
        img_flip = pygame.image.load(os.path.join("assets", "other", "flip.png")).convert_alpha()
        self.btn_flip_board = ButtonImage(img_flip)

        # # surface for connection to server
        self.surface_connection = pygame.Surface((320, 440))
        # label title connection
        self.lbl_title = Label("Connection", WHITE, font=pygame.font.SysFont("Inter", 70))
        # label waiting
        self.lbl_waiting = Label("Waiting for an opponent...", WHITE, font=pygame.font.SysFont("None", 20))
        # text input for ip
        self.text_input_ip = text_input.InputBox("127.0.0.1", width=150)
        self.text_input_port = text_input.InputBox("5000", width=70)
        self.lbl_ip = Label("Server IP :", WHITE)
        self.lbl_port = Label("Port :", WHITE)
        # button to connect to server
        image_connect_1 = pygame.image.load(os.path.join("assets", "other", "connect", "idle.png")).convert_alpha()
        image_connect_1 = pygame.transform.scale(image_connect_1, (200, 80))
        image_connect_2 = pygame.image.load(os.path.join("assets", "other", "connect", "working.png")).convert_alpha()
        image_connect_2 = pygame.transform.scale(image_connect_2, (200, 80))
        image_connect_3 = pygame.image.load(os.path.join("assets", "other", "connect", "hover.png")).convert_alpha()
        image_connect_3 = pygame.transform.scale(image_connect_3, (200, 80))
        image_connect_4 = pygame.image.load(os.path.join("assets", "other", "connect", "connected.png")).convert_alpha()
        image_connect_4 = pygame.transform.scale(image_connect_4, (200, 80))
        self.btn_connect = ButtonThread(image_connect_1, image_connect_2, image_connect_3, image_connect_4)

        self.objects_in_connection_surface = [self.lbl_title, self.text_input_ip, self.text_input_port, self.lbl_ip,
                                              self.lbl_port, self.btn_connect, self.lbl_waiting]

    def run(self):
        clock = pygame.time.Clock()
        while self.window_on:
            clock.tick(60)
            print("FPS : ", clock.get_fps(), end="\r")
            self.events()
            self.update_board_if_new_info()
            self.draw()

    def events_connection(self, events):
        self.text_input_ip.handle_event(events)
        self.text_input_port.handle_event(events)
        self.btn_connect.handle_events(events)
        if self.server_thread:
            self.btn_connect.check_thread(self.server_thread, self.connected_to_server)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if self.surface_connection.get_rect().collidepoint(pos):
                    pos = (pos[0] - self.surface_connection.get_rect().x,
                           pos[1] - self.surface_connection.get_rect().y)
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pos = pygame.mouse.get_pos()
                if self.btn_connect.tick(pos) and not self.btn_connect.isSucces and not self.btn_connect.isWorking:
                    self.server_thread = threading.Thread(target=self.thread_server_handler)
                    self.server_thread.start()

    def events(self):
        events = pygame.event.get()
        if not self.connected_to_server or self.waiting_for_opponent:
            self.events_connection(events)
        self.check_buttons(events)

        for event in events:
            if event.type == pygame.QUIT:
                self.window_on = False
                self.game_on = False
                self.connected_to_server = False
                try:
                    self.socket.close()
                except AttributeError:
                    pass
            if not self.game_on:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if self.board.clicked(pos):
                    if self.logic.turn != self.logic.get_piece(Square(*self.board.clicked_piece_coord)).color:
                        continue
                    self.current_piece_legal_moves = self.logic.get_legal_moves_piece(
                        Square(*self.board.clicked_piece_coord))
            if self.board.dragging:
                if event.type == pygame.MOUSEMOTION:
                    pos = pygame.mouse.get_pos()
                    self.board.drag(pos)

                if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    dest_coord = self.board.drop(pos)
                    move = Move(
                        Square(*self.board.clicked_piece_coord), Square(*dest_coord)
                    )

                    for m in self.current_piece_legal_moves:
                        if m == move:
                            self.current_piece_legal_moves = []
                            self.play(m)
                            break

    def play(self, move):
        if not self.connected_to_server:
            return
        logging.info(f"Sending move: {move.get_uci()} to server")
        send_move_to_server(self.socket, move.get_uci())

    def check_buttons(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.btn_quit.tick(event.pos):
                    self.game_on = False
                    self.socket.close()
                    pygame.quit()
                    exit()
                elif self.btn_flip_board.tick(event.pos):
                    self.board.flip()
                elif self.btn_minimize.tick(event.pos):
                    pygame.display.iconify()

    def check_end(self):
        if self.logic.state != State.GAMEON:
            logging.info(self.logic.state)
            self.game_on = False

    def draw(self):
        x, y, w, h = get_x_y_w_h()
        W, H = pygame.display.get_surface().get_size()
        self.win.fill((39, 35, 35))
        self.board.draw(self.win, self.current_piece_legal_moves, *(x, y, w, h))
        self.btn_flip_board.draw(self.win, x + w - 25, y + h + 10)
        self.btn_quit.draw(self.win, W - 50, 25)
        self.btn_minimize.draw(self.win, W - 100, 25)

        if not self.connected_to_server or self.waiting_for_opponent:
            self.draw_connection()

        pygame.display.flip()

    def draw_connection(self):
        self.surface_connection.fill((72, 61, 61))
        self.surface_connection.set_alpha(250)  # transparency value 0 -> transparent, 255 -> opaque
        x, y = self.surface_connection.get_size()
        self.lbl_title.draw(self.surface_connection, x // 2, 60, center=True)
        self.lbl_ip.draw(self.surface_connection, 42, 179)
        self.text_input_ip.draw(self.surface_connection, 150, 177)
        self.lbl_port.draw(self.surface_connection, 42, 235)
        self.text_input_port.draw(self.surface_connection, 150, 233)
        self.btn_connect.draw(self.surface_connection, 62, 308)
        if self.btn_connect.isSucces:
            # draw label saying waiting for opponent
            self.lbl_waiting.draw(self.surface_connection, x // 2, 400, center=True)

        W, H = pygame.display.get_surface().get_size()
        x1, y1 = (W // 2 - self.surface_connection.get_width() // 2,
                  H // 2 - self.surface_connection.get_height() // 2)
        for obj in self.objects_in_connection_surface:
            obj.update_pos(x1, y1)
        # draw the surface in the center of the screen
        self.win.blit(self.surface_connection, (x1, y1))

    def update_board_if_new_info(self):
        old_fen = self.logic.get_fen()
        new_fen = self.last_retrieved_fen
        if new_fen != old_fen:
            logging.debug(f"Updating fen from {old_fen} to {new_fen}")
            self.logic = Logic(new_fen)
            self.board.update(self.logic)
            self.current_piece_legal_moves = []

    def thread_server_handler(self):
        """
        Runs in a thread and listens to the server
        """
        max_attempts = 2
        delay = 1
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attempts = 0
        ip = str()
        port = int()
        while attempts < max_attempts:
            if not self.window_on:
                self.socket.close()
                return
            try:
                s = self.socket
                ip = self.text_input_ip.get_text()
                port = int(self.text_input_port.get_text())
                logging.info(f"Trying to connect to {ip}:{port}")
                r = s.connect_ex((ip, port))
                if r != 0:
                    raise Exception("Connection failed")
                break  # exit the function after a successful connection
            except Exception as e:
                attempts += 1
                logging.debug(f"Attempt {attempts} failed: {e}")
                time.sleep(delay)
        if attempts == max_attempts:
            logging.error(f"Failed to connect to {ip}:{port}, max attempts reached")
            return
        logging.info(f"Conection to {ip}:{port} established")
        self.connected_to_server = True
        self.waiting_for_opponent = True

        self.moves_handler()

    def moves_handler(self):
        should_run = True
        while should_run:
            try:
                data = self.socket.recv(1024)
            except Exception as e:
                logging.error(f"Error while receiving data: {e}")
                should_run = False
                break
            data = data.decode()
            if not data:
                logging.error("No data received")
                should_run = False
                break
            liste = data.split("\n")
            for line in liste:
                if line.startswith("color:"):
                    color = line[6:]
                    logging.debug(f"Recieved color: {color}")
                    if color == "white":
                        self.color = Color.WHITE
                        self.board.flipped = False
                        self.waiting_for_opponent = False

                    elif color == "black":
                        self.color = Color.BLACK
                        self.board.flipped = True
                        self.waiting_for_opponent = False

                    else:
                        logging.error("Invalid color")
                        exit()
                elif line.startswith("fen:"):
                    fen_str = line[4:]
                    self.last_retrieved_fen = fen_str.strip()
                elif line.startswith("info:"):
                    type_info = line[5:].strip()
                    if type_info == "SERVER STOP":
                        logging.info("Server stopped")
                        should_run = False
                        break
                else:
                    logging.error(f"Received <<{line!r}>> which was not understood")

        self.clean()

    def clean(self):
        logging.info("Cleaning up")
        self.socket.close()
        self.connected_to_server = False
        self.waiting_for_opponent = False
        self.color = None
