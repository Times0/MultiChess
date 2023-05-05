import threading
from board_ui import Board, get_x_y_w_h, pygame
from logic import Logic, Color, State, Square, Move
from constants import *
from tools.button import TextButton
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
        self.board = Board(BOARDSIZE)
        self.board.update(self.logic)

        self.current_piece_legal_moves = []
        self.game_on = True
        self.window_on = True

        # Buttons
        self.buttons = []
        self.btn_new_game = TextButton("New Game", 10, 50, WHITE)
        self.btn_flip_board = TextButton("Flip Board", 10, 100, WHITE)
        self.btn_retry_connection = TextButton("Retry Connection", 10, 150, WHITE)
        self.buttons.extend(
            (self.btn_new_game, self.btn_flip_board, self.btn_retry_connection)
        )

        # Entry
        self.entry_ip = text_input.InputBox(text="127.0.0.1", width=None)
        self.entry_port = text_input.InputBox(text="5001", width=100)

        # Labels
        self.label_enter_ip = pygame.font.SysFont("None", 25).render(
            f"server IP : ", True, WHITE
        )
        self.label_enter_port = pygame.font.SysFont("None", 25).render(
            f"server port : ", True, WHITE
        )

        # Server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = None
        self.port = None
        self.server_thread = threading.Thread(target=self.thread_srver_handler)
        self.server_thread.start()
        self.last_retrieved_fen = self.logic.get_fen()
        self.color = None
        self.connected_to_server = False

        self.waiting_for_opponent = False
        self.is_my_turn = False

        self.color_zougou = (0, 85, 170)

    def run(self):
        clock = pygame.time.Clock()
        while self.window_on:
            clock.tick(60)
            print("FPS : ", clock.get_fps(), end="\r")
            self.events()
            self.update_board_if_new_info()
            self.draw()

    def events(self):
        events = pygame.event.get()
        self.entry_ip.handle_event(events)
        self.entry_port.handle_event(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.window_on = False
                self.game_on = False
                self.connected_to_server = False
                self.socket.close()

            self.check_buttons(events)
            if not self.game_on:
                continue
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                if self.board.clicked(pos):
                    if (
                        self.logic.turn
                        != self.logic.get_piece(
                            Square(*self.board.clicked_piece_coord)
                        ).color
                    ):
                        continue
                    self.current_piece_legal_moves = self.logic.get_legal_moves_piece(
                        Square(*self.board.clicked_piece_coord)
                    )
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
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_new_game.tick():
                    exit()
                    self.bot_is_thinking = False
                    self.logic = Logic(STARTINGPOSFEN)
                    self.board.update(self.logic)
                    self.game_on = True
                    self.current_piece_legal_moves = []
                if self.btn_flip_board.tick():
                    self.board.flip_board()
                if self.btn_retry_connection.tick():
                    self.server_thread = threading.Thread(target=self.thread_srver_handler)
                    self.server_thread.start()

    def check_end(self):
        if self.logic.state != State.GAMEON:
            logging.info(self.logic.state)
            self.game_on = False

    def draw(self):
        x, y, w, h = get_x_y_w_h()
        W, H = pygame.display.get_surface().get_size()
        self.color_zougou = [
            (c + random.randint(0, 3)) % 255 for c in self.color_zougou
        ]
        self.win.fill(BLACK)
        self.board.draw(self.win, self.current_piece_legal_moves, *(x, y, w, h))
        for button in self.buttons:
            button.draw(self.win)

        s = ""
        if self.color is None:
            s = "Not connected"
        elif self.color == Color.WHITE:
            s = "Playing as white"
        elif self.color == Color.BLACK:
            s = "Playing as black"

        if self.color is None and not self.waiting_for_opponent:
            self.win.blit(self.label_enter_ip, (10, H - 60))
            self.win.blit(self.label_enter_port, (10, H - 30))

            self.entry_ip.draw(self.win, 10 + self.label_enter_ip.get_width(), H - 60)
            self.entry_port.draw(
                self.win, 10 + self.label_enter_port.get_width(), H - 30
            )

        if self.waiting_for_opponent:
            label = pygame.font.SysFont("Arial", 50).render(
                f"Waiting for opponent", True, self.color_zougou
            )
            self.win.blit(label, label.get_rect(center=(W / 2, H / 2)))

        pygame.display.flip()

    def select(self, pos):
        self.board.select(pos)

    def update_board_if_new_info(self):
        old_fen = self.logic.get_fen()
        new_fen = self.last_retrieved_fen
        if new_fen != old_fen:
            logging.debug(f"Updating fen from {old_fen} to {new_fen}")
            self.logic = Logic(new_fen)
            self.board.update(self.logic)
            self.current_piece_legal_moves = []

    def thread_srver_handler(self):
        """
        Runs in a thread and listens to the server
        """
        max_attempts = 10
        delay = 2
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        attempts = 0
        while attempts < max_attempts:
            if not self.window_on:
                self.socket.close()
                return
            try:
                s = self.socket
                ip = self.entry_ip.get_text()
                port = int(self.entry_port.get_text())
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
                    elif color == "black":
                        self.color = Color.BLACK
                        self.board.flipped = True
                    else:
                        logging.error("Invalid color")
                        exit()
                    self.waiting_for_opponent = False
                    self.connected_to_server = True
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

        self.clear()

    def clear(self):
        logging.info("Clearing")
        self.socket.close()
        self.connected_to_server = False
        self.waiting_for_opponent = False
        self.color = None
