import os
import threading
from typing import Optional

from PygameUIKit import Group, button
from PygameUIKit.label import Label
from PygameUIKit.utilis import load_image
from pygame import Color

from board_ui import Board, get_x_y_w_h, pygame
from logic import Logic, State
from PygameUIKit.button import ButtonPngIcon
from reseau import *
import time
import logging

logging.basicConfig(level=logging.INFO)

BACKGROUND_COLOR = (22, 21, 18)
COLOR_CHANGING = (0, 85, 170)

FONT = pygame.font.SysFont("lucidafaxdemigras", 30)
SERVER_MODE = False


class Game:
    def __init__(self, win, fen):
        self.win = win
        self.logic = Logic(fen)
        self.board = Board(self.logic, self.play)
        self.board.set_pos_from_logic(self.logic)

        self.game_on = True
        self.window_on = True

        # Menus
        self.menu = Menu()
        self.menu.open("game_selection")

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
        self.ui.add(self.menu)
        self.btn_flip_board = ButtonPngIcon(img_flip, self.flip_board, ui_group=self.ui)

    def run(self):
        clock = pygame.time.Clock()
        while self.window_on:
            clock.tick(60)
            self.events()
            # self.update_board_if_new_info()
            self.draw()

    def events(self):
        events = pygame.event.get()
        for event in events:
            self.ui.handle_event(event)
            self.board.handle_event(event)
            if event.type == pygame.QUIT:
                self.window_on = False
                self.game_on = False
                self.connected_to_server = False
                try:
                    self.socket.close()
                except AttributeError:
                    pass
            if event.type == pygame.WINDOWRESIZED:
                self.board.rect = pygame.Rect(get_x_y_w_h())

    def draw(self):
        x, y, w, h = get_x_y_w_h()
        self.win.fill(BACKGROUND_COLOR)
        self.board.draw(self.win)
        self.btn_flip_board.draw(self.win, x + w - 25, y + h + 10)
        self.menu.draw(self.win)
        pygame.display.flip()

    def play(self, move):
        if SERVER_MODE:
            logging.info(f"Sending move: {move.get_uci()} to server")
            send_move_to_server(self.socket, move.get_uci())
        else:
            logging.info(f"Playing move: {move.get_uci()}")
            self.logic.real_move(move)
            self.board.set_pos_from_logic(self.logic)

    def check_end(self):
        if self.logic.state != State.GAMEON:
            self.game_on = False

    def update_board_if_new_info(self):
        old_fen = self.logic.get_fen()
        new_fen = self.last_retrieved_fen
        if new_fen != old_fen:
            logging.debug(f"Updating fen from {old_fen} to {new_fen}")
            self.logic = Logic(new_fen)
            self.board.set_pos_from_logic(self.logic)
            # self.current_piece_legal_moves = []

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

    def connect_to_server(self):
        print("Connecting to server")
        self.server_thread = threading.Thread(target=self.thread_server_handler)
        self.server_thread.start()

    def flip_board(self):
        self.board.flipped = not self.board.flipped


class MenuPart:
    def __init__(self):
        self._name: str = ""
        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.name_label: Optional[Label] = None
        self.ui = Group()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.name_label = Label(self._name.title().replace("_",' '), font_color=Color("black"), font=FONT)
            self.name_label.rect.midtop = self.rect.midtop

    def handle_event(self, event):
        self.ui.handle_event(event)

    def draw(self, win):
        self.rect.center = win.get_rect().center
        pygame.draw.rect(win, Color("gray"), self.rect)

        if self.name_label:
            self.name_label.draw(win, *self.rect.move(10, 10).topleft)


class GameModeSelection(MenuPart):
    def __init__(self):
        super().__init__()
        self.name = "mode_selection"
        self.rect = pygame.Rect(0, 0, 300, 300)

        params = {"rect_color": (199, 201, 207),
                  "font": FONT,
                  "fixed_width": self.rect.w - 20,
                  "text_align": "center",
                  "ui_group": self.ui}
        self.btn_local = button.ButtonText("1v1 Local", **params)
        self.btn_online = button.ButtonText("1v1 Online", **params)
        self.btn_bot = button.ButtonText("1vBot", **params)

    def draw(self, win):
        super().draw(win)
        self.btn_local.draw(win, *self.rect.move(10, 75).topleft)
        self.btn_online.draw(win, *self.rect.move(10, 150).topleft)
        self.btn_bot.draw(win, *self.rect.move(10, 225).topleft)


class Menu:
    def __init__(self):
        self.menus: dict[str, MenuPart] = {"game_selection": GameModeSelection()}
        self.active_element: Optional[MenuPart] = None
        self.rect = pygame.display.get_surface().get_rect()

    def add_elements(self, elements: list[MenuPart]):
        if elements is None:
            return
        for element in elements:
            self.menus[element.name] = element

    def open(self, name):
        self.active_element = self.menus[name]

    def draw(self, win):
        if self.active_element:
            self.active_element.draw(win)

    def handle_event(self, event):
        if self.active_element:
            self.active_element.handle_event(event)
