import threading
from board_ui import Board, get_x_y_w_h, pygame
from logic import Logic, Color, State, Square, Move
from constants import *
from tools.button import TextButton
from reseau import *
import tools.text_input as text_input
import random


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
        self.btn_new_game = TextButton("New Game", 10, 50, pygame.font.SysFont("Arial", 32), WHITE)
        self.btn_flip_board = TextButton("Flip Board", 10, 100, pygame.font.SysFont("Arial", 32), WHITE)
        self.buttons.extend((self.btn_new_game, self.btn_flip_board))

        # Entry
        self.entry_ip = text_input.InputBox(text = "127.0.01")
        self.entry_port = text_input.InputBox(text = "5001")
        

        # Server
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = None
        self.port = None
        self.server_thread = threading.Thread(target=self.listen_server)
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
            print(f"Fps: {clock.get_fps()}", end="\r")
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
                self.socket.close()

            self.check_buttons(events)
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
                    move = Move(Square(*self.board.clicked_piece_coord), Square(*dest_coord))
                    
                    for m in self.current_piece_legal_moves:
                        if m == move:
                            self.current_piece_legal_moves = []
                            self.play(m)
                            break

    def play(self, move):
        if not self.connected_to_server:
            return
        print(f"Sending move: {move.get_uci()} to server")
        send_move_to_server(self.socket,move.get_uci())

    def check_buttons(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.btn_new_game.tick():
                    exit()
                    print("New game")
                    self.bot_is_thinking = False
                    self.logic = Logic(STARTINGPOSFEN)
                    self.board.update(self.logic)
                    self.game_on = True
                    self.current_piece_legal_moves = []
                if self.btn_flip_board.tick():
                    self.board.flip_board()

    def check_end(self):
        if self.logic.state != State.GAMEON:
            print(self.logic.state)
            self.game_on = False

    def draw(self):
        x,y,w,h = get_x_y_w_h()
        W,H = pygame.display.get_surface().get_size()
        self.color_zougou = [(c+random.randint(0,3))%255 for c in self.color_zougou]
        self.win.fill(BLACK)
        self.board.draw(self.win, self.current_piece_legal_moves, *(x,y,w,h))
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
            label_enter_ip = pygame.font.SysFont("Arial", 15).render(f"Enter server IP : ", True, WHITE)
            label_enter_port = pygame.font.SysFont("Arial", 15).render(f"Enter server port : ", True, WHITE)
            self.win.blit(label_enter_ip, (10, H - 60))
            self.win.blit(label_enter_port, (10, H - 30))

            self.entry_ip.draw(self.win, *(10 + label_enter_ip.get_width(), H - 60))
            self.entry_port.draw(self.win, *(10 + label_enter_port.get_width(), H - 30))
        
        if self.waiting_for_opponent:
            label = pygame.font.SysFont("Arial", 50).render(f"Waiting for opponent", True, self.color_zougou)
            self.win.blit(label, label.get_rect(center=(W/2, H/2)))

        pygame.display.flip()

    def select(self, pos):
        self.board.select(pos)

    def update_board_if_new_info(self):
        old_fen = self.logic.get_fen()
        new_fen = self.last_retrieved_fen
        if new_fen != old_fen:
            print(f"Updating fen from {old_fen} to {new_fen}")
            self.logic = Logic(new_fen)
            self.board.update(self.logic)
            self.current_piece_legal_moves = []
            
    def listen_server(self):
        import time
        should_run = True

        while should_run:
            time.sleep(2)
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            while True:
                self.ip = self.entry_ip.text
                try:
                    self.port = int(self.entry_port.text)
                except:
                    self.port = 0
                if self.ip == "" or self.port == 0:
                    continue # no ip or port no need to try to connect
                try:
                    print(f"Trying to connect to {self.ip}:{self.port}...")
                    r= self.socket.connect_ex((self.ip, self.port))
                    if r == 0:
                        break
                except:
                    pass
                if not self.window_on:
                    return
                time.sleep(5)
            
            print("Connected to server")
            self.waiting_for_opponent = True
            
            server_on = True
            while server_on:
                data = self.socket.recv(1024)
                if not data:
                    should_run = False
                    server_on = False
                    break
                
                data = data.decode()
                liste = data.split("\n")

                for line in liste:
                    if line.startswith("color:"):
                        color = line[6:]
                        print(f"Recieved color: {color}")
                        if color == "white":
                            self.color = Color.WHITE
                            self.board.flipped = False
                        elif color == "black":
                            self.color = Color.BLACK
                            self.board.flipped = True
                        else:
                            print("Invalid color")
                            exit()
                        self.waiting_for_opponent = False
                        self.connected_to_server = True
                    elif line.startswith("fen:"):
                        fen_str = line[4:]
                        self.last_retrieved_fen = fen_str.strip()
                    elif line.startswith("info:"):
                        type_info = line[5:].strip()
                        if type_info == "SERVER STOP":
                            self.color = None
                            self.connected_to_server = False
                            self.waiting_for_opponent = False
                            server_on = False
                            self.socket.close()
                        print(f"ALERT {line}")
                    else:
                        print(f"Received {line!r}")

