import os
import queue
import socket
import threading
from enum import Enum
from typing import Optional

from PygameUIKit import Group
from PygameUIKit.label import Label
from PygameUIKit.utilis import load_image
from pygame import Color

from board_ui import Board, get_x_y_w_h, pygame
from ai import PlayerType, Bot
from pieces import PieceColor
from logic import Logic, State
from PygameUIKit.button import ButtonPngIcon

from menu import Menu, ServerConnection, GameModeSelection
from reseau import *
import time
import logging

logging.basicConfig(level=logging.INFO)

BACKGROUND_COLOR = (0, 0, 0)

FONT = pygame.font.SysFont("lucidafaxdemigras", 30)
SERVER_MODE = False


class GameMode(Enum):
    Local = 0
    Online = 1
    Bot = 2


FONT_LABEL_COLOR = (97, 175, 239)


class Game:
    def __init__(self, win, fen):
        self.win = win
        self.logic = Logic(fen)
        self.board = Board(self.logic, self.play)
        self.board.set_pos_from_logic(self.logic)

        self.game_on = True
        self.window_on = True

        # Server
        self.socket = None
        self.server_thread = None
        self.last_retrieved_fen = self.logic.get_fen()
        self.color = None
        self.connected_to_server = False
        self.waiting_for_opponent = False

        # UI
        img_flip = load_image(os.path.join("assets", "other", "flip.png"), (25, 25))
        img_settings = load_image(os.path.join("assets", "other", "settings.png"), (50, 50))

        self.ui = Group()
        self.btn_flip_board = ButtonPngIcon(img_flip, self.flip_board, ui_group=self.ui)
        self.btn_settings = ButtonPngIcon(img_settings, lambda: self.menu.open("mode_selection"), ui_group=self.ui)
        self.players = {PieceColor.WHITE: None,
                        PieceColor.BLACK: None}

        self.player_label = Label("X to play", font_color=FONT_LABEL_COLOR, font=FONT)

        # May not be used
        self.bot_is_thinking = False
        self.queue: queue.Queue = queue.Queue()
        self.thread_bot: Optional[threading.Thread] = None

        self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Menus
        self.menu = Menu()
        game_selection = GameModeSelection(self.start_local_game, self.start_vs_bot, manager=self.menu)
        server_selection = ServerConnection(game_socket=self.socket)
        self.menu.add_elements([game_selection, server_selection])
        self.menu.open("mode_selection")
        self.mode: Optional[GameMode] = None

    def clean(self):
        if self.thread_bot:
            self.thread_bot.join()
        if self.server_thread:
            self.server_thread.join()

        self.queue = queue.Queue()
        self.thread_bot = None
        self.server_thread = None

    def start_local_game(self):
        self.menu.close()
        self.clean()
        self.mode = GameMode.Local
        self.players = {PieceColor.WHITE: PlayerType.HUMAN,
                        PieceColor.BLACK: PlayerType.HUMAN}
        self.logic.reset()
        self.board.set_pos_from_logic(self.logic)

    def start_vs_bot(self, bot_color: PieceColor):
        self.menu.close()
        self.clean()
        self.mode = GameMode.Bot
        if bot_color == PieceColor.WHITE:
            self.board.flipped = True
            self.players = {PieceColor.WHITE: PlayerType.BOT,
                            PieceColor.BLACK: PlayerType.HUMAN}
        else:
            self.board.flipped = False
            self.players = {PieceColor.WHITE: PlayerType.HUMAN,
                            PieceColor.BLACK: PlayerType.BOT}
        self.logic.reset()
        self.board.set_pos_from_logic(self.logic)

    def start_online_game(self, client_color: PieceColor):
        self.menu.close()
        self.clean()
        self.mode = GameMode.Online

        if client_color == PieceColor.WHITE:
            self.board.flipped = True
            self.players = {PieceColor.WHITE: PlayerType.HUMAN,
                            PieceColor.BLACK: PlayerType.ONLINE}
        else:
            self.board.flipped = False
            self.players = {PieceColor.WHITE: PlayerType.ONLINE,
                            PieceColor.BLACK: PlayerType.HUMAN}
        self.logic.reset()
        self.board.set_pos_from_logic(self.logic)

    def server_listner(self):
        should_run = True
        while should_run:
            try:
                data = self.socket.recv(1024)
            except Exception as e:
                logging.error(f"Error while receiving data: {e}")
                break
            data = data.decode()
            if not data:
                logging.error("No data received")
                break
            liste = data.split("\n")
            for line in liste:
                if line.startswith("color:"):
                    color = line[6:]
                    logging.debug(f"Recieved color: {color}")
                    if color == "white":
                        self.color = PieceColor.WHITE
                        self.board.flipped = False
                        self.waiting_for_opponent = False

                    elif color == "black":
                        self.color = PieceColor.BLACK
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

    def run(self):
        clock = pygame.time.Clock()
        while self.window_on:
            clock.tick(60)
            self.events()
            if self.mode == GameMode.Bot:
                self.bot_events()
            elif self.mode == GameMode.Online:
                if self.connected_to_server and not self.server_thread:
                    self.server_thread = threading.Thread(target=self.server_listner)
                    self.server_thread.start()
            self.draw()

    def bot_events(self):
        if not self.queue.empty():
            evaluation, move = self.queue.get()
            self.play(move)
            self.bot_is_thinking = False

    def events(self):
        events = pygame.event.get()
        self.menu.handle_events(events)
        for event in events:
            self.ui.handle_event(event)
            if self.mode == GameMode.Local:
                self.board.handle_event(event, dummy_mode=self.mode is None)
            elif self.mode == GameMode.Bot:
                if self.players.get(self.logic.turn) == PlayerType.HUMAN:
                    self.board.handle_event(event)
                else:
                    if not self.bot_is_thinking:
                        self.bot_is_thinking = True
                        self.thread_bot = threading.Thread(target=Bot().play, args=(self.logic, self.queue))
                        self.thread_bot.start()

            elif self.mode == GameMode.Online:
                pass

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
        self.btn_settings.draw(self.win, self.win.get_width() - 60, 10)
        if self.logic.turn == PieceColor.WHITE:
            self.player_label.text = "White to play"
        else:
            self.player_label.text = "Black to play"
        self.player_label.draw(self.win,
                               self.win.get_width() // 2 - self.player_label.rect.w // 2, self.win.get_height() - 50)
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

    def flip_board(self):
        self.board.flipped = not self.board.flipped
