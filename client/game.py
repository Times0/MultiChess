import threading

from PygameUIKit import Group
from PygameUIKit.utilis import load_image

from board_ui import Board, get_x_y_w_h, pygame
from logic import Logic, Color, State, Square, Move
from constants import *
from PygameUIKit.button import ButtonPngIcon
from reseau import *
import time
import logging

logging.basicConfig(level=logging.INFO)

COLOR_CHANGING = (0, 85, 170)


class Game:
    def __init__(self, win, fen):
        self.win = win
        self.logic = Logic(fen)
        self.board = Board()
        self.board.set_pos_from_logic(self.logic)

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

        # button to flip the board
        img_flip = load_image(os.path.join("assets", "other", "flip.png"), (25, 25))
        self.ui = Group()
        self.btn_flip_board = ButtonPngIcon(img_flip, self.flip_board, ui_group=self.ui)

    def run(self):
        clock = pygame.time.Clock()
        while self.window_on:
            clock.tick(60)
            self.events()
            self.update_board_if_new_info()
            self.draw()

    def events(self):
        events = pygame.event.get()
        for event in events:
            self.ui.handle_event(event)
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
            if event.type == pygame.WINDOWRESIZED:
                self.board.rect = pygame.Rect(get_x_y_w_h())
            if self.board.dragging:
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

    def check_end(self):
        if self.logic.state != State.GAMEON:
            logging.info(self.logic.state)
            self.game_on = False

    def draw(self):
        x, y, w, h = get_x_y_w_h()
        self.win.fill((39, 35, 35))
        self.board.draw(self.win, self.current_piece_legal_moves)
        self.btn_flip_board.draw(self.win, x + w - 25, y + h + 10)
        pygame.display.flip()

    def update_board_if_new_info(self):
        old_fen = self.logic.get_fen()
        new_fen = self.last_retrieved_fen
        if new_fen != old_fen:
            logging.debug(f"Updating fen from {old_fen} to {new_fen}")
            self.logic = Logic(new_fen)
            self.board.set_pos_from_logic(self.logic)
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
        try:
            self.socket.close()
        except AttributeError:
            pass
        self.connected_to_server = False
        self.waiting_for_opponent = False
        self.color = None

    # button functions

    def connect_to_server(self):
        print("Connecting to server")
        self.server_thread = threading.Thread(target=self.thread_server_handler)
        self.server_thread.start()

    def flip_board(self):
        self.board.flipped = not self.board.flipped
