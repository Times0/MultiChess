import cProfile
import multiprocessing
import pstats

import Button
import bot
from Board import *
from Logic import Logic
from fonctions import *


class Game:
    def __init__(self, win, fen):
        self.win = win
        self.logic = Logic(fen=fen)
        self.board = Board(BOARDSIZE)
        self.board.update(self.logic)
        self.players = {"white": "human", "black": "human"}  # MODIFY HERE
        botw = bot.Edouard("white")
        botb = bot.Edouard("black")
        self.bots = {"white": botw, "black": botb}
        self.playertextlabel = {"white": f'white : {self.players["white"]}',
                                "black": f'black : {self.players["black"]}'}

        self.buttons = [Button.Button(BLACK, GREY, WIDTH * 0.95, 15, 40, 40, pygame.quit, "X"),
                        Button.Button(BLACK, BLACK, 15, MIDH, 150, 40, lambda: self.swap("white"),
                                      self.playertextlabel['white'], textcolor=WHITE),
                        Button.Button(BLACK, BLACK, 15, MIDH + 50, 150, 40, lambda: self.swap("black"),
                                      self.playertextlabel['black'], textcolor=WHITE),
                        Button.Button(BLACK, GREY, 15, HEIGHT * 0.9, 180, 40, self.restart, "New game")

                        ]

        # multiprocessing
        manager = multiprocessing.Manager()
        self.the_list = manager.list()
        self.the_list.append(None)
        self.bot_process = multiprocessing.Process(target=pygame.quit)

        # bot
        self.hasToThink = True

        # game
        self.game_on = True

    def run(self):
        win_running = True
        _move_info = False
        clock = pygame.time.Clock()

        while win_running:
            clock.tick(60)
            self.win.fill(BG_COLOR)
            # gestion des évènements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:  # si on appuie sur la croix
                    self.game_on = False
                # buttons
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for button in self.buttons:
                        if button.isMouseon(event.pos):
                            button.onclick()

                    for button in self.buttons:
                        if button.isMouseon(event.pos):
                            button.hover()
                        else:
                            button.default()

                if "human" in self.players.values():
                    # si on clique sur l'echequier
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and \
                            isInrectangle(event.pos, BOARDTOPLEFTPOS, BOARDSIZE, BOARDSIZE):

                        previous_coord = self.board.clicked_piece_coord

                        if previous_coord:
                            move = *previous_coord, *self.board.coord_from_pos(*event.pos)
                        legal_moves = self.logic.legal_moves()
                        legal_moves_reduced = [(e[0], e[1], e[2], e[3]) for e in legal_moves]

                        # si on clique sur une case qui est un legal move, on effectue le move
                        if self.board.legal_moves_to_output and move in legal_moves_reduced:
                            i = legal_moves_reduced.index(move)
                            _move_info = True
                            actual_move = legal_moves[i]
                            self.board.legal_moves_to_output = []
                            self.board.clicked_piece_coord = None
                        # si on clique sur une piece
                        elif self.board.isNotempty(*self.board.coord_from_pos(*event.pos)):
                            self.board.set_to_gone(*event.pos)
                            self.board.state = "dragging"
                            i, j = self.board.coord_from_pos(*event.pos)
                            moves = self.logic.board[i][j].legal_moves(self.logic)
                            self.board.legal_moves_to_output = moves

                        # si on clique sur une case vide
                        else:
                            self.board.legal_moves_to_output = []
                        # si on lache la piece

                    # si on lache le clique et qu'on draggait
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.board.state == "dragging":
                        legal_moves = self.logic.legal_moves()
                        legal_moves_reduced = [(e[0], e[1], e[2], e[3]) for e in legal_moves]
                        previous_coord = self.board.clicked_piece_coord
                        if previous_coord:
                            move = *previous_coord, *self.board.coord_from_pos(*event.pos)

                        # on effectue le move
                        if move in legal_moves_reduced:
                            i = legal_moves_reduced.index(move)
                            _move_info = True
                            actual_move = legal_moves[i]
                            self.board.set_to_not_gone()
                            self.board.legal_moves_to_output = []
                        else:
                            self.board.set_to_not_gone()
                        self.board.state = "idle"
                    # si on bouge la souris avec une pièce en main
                    elif self.board.state == "dragging" and event.type == pygame.MOUSEMOTION:
                        self.board.dragged_piece_pos = event.pos

            if self.game_on:
                if self.players[self.logic.turn] == "human":
                    if _move_info:
                        self.logic.real_move(actual_move)
                        self.board.update(self.logic)
                        self.board.attacked_cases = self.logic.cases_attacked_by('white')
                        if self.logic.state != "game_on":
                            self.game_on = False  # on arrete la boucle du jeu

                elif self.players[self.logic.turn] == "bot":
                    if self.hasToThink:
                        print("\nStarted thinking")

                        # FIND WHAT TAKES TIME
                        # with cProfile.Profile() as pr:
                        #     self.bots[self.logic.turn].play(self.logic, self.the_list)
                        #     stats = pstats.Stats(pr)
                        #     stats.sort_stats(pstats.SortKey.TIME)
                        #     stats.print_stats()

                        self.bot_process = multiprocessing.Process(target=self.bots[self.logic.turn].play,
                                                                   args=(self.logic, self.the_list))
                        self.bot_process.start()

                        self.hasToThink = False
                    if self.the_list[0]:
                        print(f"Found the move {self.the_list[0]}")
                        genius_move = self.the_list[0]
                        self.the_list[0] = None
                        self.hasToThink = True
                        move = genius_move[1]
                        self.logic.real_move(move)
                        # self.logic.update_game_state(self.logic.turn)
                        self.board.update(self.logic)
                        if self.logic.state != "game_on":
                            self.game_on = False  # on arrete la boucle du jeu
            _move_info = False
            actual_move = None

            self.draw_everything()
            pygame.display.flip()  # update l'affichage
        pygame.quit()

    def draw_everything(self):
        self.board.draw(self.win, *BOARDTOPLEFTPOS)
        for button in self.buttons:
            button.draw(self.win)
        self.draw_labels()

    def draw_labels(self):
        font = pygame.font.SysFont("monospace", 25)
        label_state = font.render(f"Game state : {self.logic.state}", True, WHITE)
        label_turn = font.render(f"Turn : {self.logic.turn}", True, WHITE)
        self.win.blit(label_state, (15, HEIGHT * 0.1))
        self.win.blit(label_turn, (15, HEIGHT * 0.1 + HEIGHT // 15))

    def restart(self):
        try:
            self.bot_process.terminate()
        except:
            pass

        self.__init__(self.win, STARTINGPOSFEN)

    def swap(self, color):
        yes = "human" if self.players[color] == "bot" else "bot"
        self.players[color] = yes
        self.buttons[1 if color == "white" else 2].text = f"{color} : {yes}"
