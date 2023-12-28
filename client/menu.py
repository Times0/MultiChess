import logging
import threading
import time

import pygame
from PygameUIKit import Group, button
from PygameUIKit.label import Label
from PygameUIKit.text_input import TextInput
from typing import Optional

from pygame import Color

from pieces import PieceColor

MENU_COLOR = (18, 18, 18)
MENU_BUTTON_COLOR = (50, 50, 50)
FONT_COLOR = (179, 179, 179)

FONT = pygame.font.SysFont("lucidafaxdemigras", 30)

CONNECTFONT = pygame.font.SysFont("lucidafaxdemigras", 40)


class MenuPart:
    def __init__(self, manager=None):
        self._name: str = ""
        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)
        self.name_label: Optional[Label] = None
        self.ui = Group()
        self.manager = manager

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if self._name != value:
            self._name = value
            self.name_label = Label(self._name.title().replace("_", ' '), font_color=FONT_COLOR, font=FONT)
            self.name_label.rect.midtop = self.rect.midtop

    def handle_events(self, events):
        pass

    def handle_event(self, event):
        self.ui.handle_event(event)

    def draw(self, win):
        self.rect.center = win.get_rect().center
        pygame.draw.rect(win, MENU_COLOR, self.rect, border_radius=10)

        if self.name_label:
            self.name_label.draw(win, *self.rect.move(10, 10).topleft)


class GameModeSelection(MenuPart):
    def __init__(self, start_local, start_bot, manager=None):
        super().__init__(manager)
        self.name = "mode_selection"
        self.rect = pygame.Rect(0, 0, 300, 300)
        params = {"rect_color": MENU_BUTTON_COLOR,
                  "font": FONT,
                  "font_color": FONT_COLOR,
                  "fixed_width": self.rect.w - 20,
                  "text_align": "center",
                  "ui_group": self.ui}
        self.btn_local = button.ButtonText("1v1 Local", **params, onclick_f=start_local)
        self.btn_online = button.ButtonText("1v1 Online", **params, onclick_f=lambda: self.manager.open("connection"))
        self.btn_bot = button.ButtonText("1vBot", **params,
                                         onclick_f=lambda: start_bot(PieceColor.BLACK))  # TODO: Add color selection

    def draw(self, win):
        super().draw(win)
        self.btn_local.draw(win, *self.rect.move(10, 75).topleft)
        self.btn_online.draw(win, *self.rect.move(10, 150).topleft)
        self.btn_bot.draw(win, *self.rect.move(10, 225).topleft)


class ServerConnection(MenuPart):
    def __init__(self, game_socket):
        super().__init__()
        self.name = "connection"
        self.rect = pygame.Rect(0, 0, 300, 400)
        self.server_thread = threading.Thread(target=self.thread_server_handler)

        params = {
            "font": FONT,
            "font_color": FONT_COLOR,
            "fixed_width": self.rect.w - 20,
            "ui_group": self.ui,
            "border_radius": 5,
        }
        self.text_input_ip = TextInput(text="127.0.0.1", placeholder="IP", **params)
        self.text_input_port = TextInput(text="5001", placeholder="Port", **params)
        self.btn_connect = button.ButtonThreadText(rect_color=Color((90, 170, 235)),
                                                   text_before="Connect",
                                                   text_during="Connecting...",
                                                   text_after="Connected",
                                                   onclick_f=lambda t=self.server_thread: t.start(),
                                                   border_radius=15,
                                                   ui_group=self.ui,
                                                   font=CONNECTFONT)

        self.socket = game_socket
        self.socket.settimeout(1)
        self.connected_to_server = False
        self.waiting_for_opponent = False
        self.btn_connect.thread = self.server_thread

    def handle_events(self, events):
        self.text_input_ip.handle_events(events)
        self.text_input_port.handle_events(events)
        self.btn_connect.check_thread(self.server_thread, self.connected_to_server)

    def draw(self, win):
        super().draw(win)
        self.text_input_ip.draw(win, *self.rect.move(10, 100).topleft)
        self.text_input_port.draw(win, *self.rect.move(10, 175).topleft)
        self.btn_connect.draw(win,
                              *self.btn_connect.surface.get_rect(midbottom=self.rect.midbottom).move(0, -30).topleft)

    def thread_server_handler(self):
        """
        Runs in a thread and listens to the server
        """
        logging.info("Starting server thread")
        max_attempts = 2
        delay = 1
        attempts = 0
        ip = str()
        port = int()
        while attempts < max_attempts:
            try:
                s = self.socket
                ip = self.text_input_ip.get_text()
                port = int(self.text_input_port.get_text())
                logging.info(f"Attempt {attempts + 1}/{max_attempts} to connect to {ip}:{port}")
                r = s.connect_ex((ip, port))
                if r != 0:
                    raise ConnectionError
                break  # Connection successful
            except ConnectionError:
                attempts += 1
                logging.error(f"Failed to connect to {ip}:{port}, retrying in {delay} seconds")
                time.sleep(delay)
                continue
        if attempts == max_attempts:
            logging.error(f"Failed to connect to {ip}:{port}, max attempts reached")
            return False
        logging.info(f"Conection to {ip}:{port} established")
        self.connected_to_server = True
        self.waiting_for_opponent = True

        self.moves_handler()


class Menu:
    def __init__(self):
        self.menus: dict[str, MenuPart] = dict()
        self.active_element: Optional[MenuPart] = None
        self.rect = pygame.display.get_surface().get_rect()

    def add_elements(self, elements: list[MenuPart]):
        if elements is None:
            return
        for element in elements:
            self.menus[element.name] = element

    def open(self, name):
        self.active_element = self.menus[name]

    def close(self):
        self.active_element = None

    def draw(self, win):
        if self.active_element:
            self.active_element.draw(win)

    def _handle_event(self, event):
        if self.active_element:
            self.active_element.handle_event(event)

    def handle_events(self, events):
        """ Text input needs to be handled separately """
        if self.active_element:
            self.active_element.handle_events(events)
        for event in events:
            self._handle_event(event)
