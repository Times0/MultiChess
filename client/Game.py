import threading
from board_ui import Board, get_x_y_w_h, pygame
from logic import Logic, Color, State, Square, Move
from constants import *
from tools.button import TextButton
from reseau import *


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

        self.socket = None
        self.server_thread = threading.Thread(target=self.listen_server)
        self.server_thread.start()
        self.last_retrieved_fen = self.logic.get_fen()

    def run(self):
        clock = pygame.time.Clock()
        while self.window_on:
            clock.tick(60)
            self.events()
            self.check_server()
            self.draw()

    def events(self):
        events = pygame.event.get()
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
        self.win.fill(BLACK)
        self.board.draw(self.win, self.current_piece_legal_moves, *get_x_y_w_h())
        for button in self.buttons:
            button.draw(self.win)
        pygame.display.flip()

    def select(self, pos):
        self.board.select(pos)


    def check_server(self):
        old_fen = self.logic.get_fen()
        new_fen = self.last_retrieved_fen
        if new_fen != old_fen:
            print(f"Updating fen from {old_fen} to {new_fen}")
            self.logic = Logic(new_fen)
            self.board.update(self.logic)
            self.current_piece_legal_moves = []
            
    def listen_server(self):
        import time
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while not self.socket.connect_ex((HOST, PORT)) == 0:
            print("Waiting for server...")
            if not self.window_on:
                return
            time.sleep(1)
        print("Connected to server")
        while True:
            data = self.socket.recv(1024)
            if not data:
                break
            if data.startswith(b"fen:"):
                data = data[4:]
                print(f"Recieved fen: {data.decode()}")
                self.last_retrieved_fen = data.decode()
            else:
                print(f"Received {data!r}")

