import pygame

from constants import *
from typing import Tuple

class Board:
    def __init__(self, size):
        self.size = size
        self.case_size = int(self.size // 8)
        self.x = 0  # coordonnées en pixel par rapport à la fenetre
        self.y = 0
        self.board_to_output = [[None for _ in range(8)] for _ in
                                range(8)]  # board shown on screen which can have "gone" for somme coords
        boardstates = ["idle", "dragging"]
        self.state = "idle"

        self.clicked_piece_coord = None
        self.dragged_piece = None
        self.dragged_piece_coord = None  # i,j
        self.dragged_piece_pos = None

        self.legal_moves_to_output = []

        self.attacked_cases = []

    def set_to_gone(self, x, y):
        i, j = self.coord_from_pos(x, y)
        self.dragged_piece = self.piece_at_coord(i, j)
        self.board_to_output[i][j] = "gone"
        self.dragged_piece_pos = x, y
        self.dragged_piece_coord = i, j
        self.clicked_piece_coord = i, j

    def set_to_not_gone(self):
        i, j = self.dragged_piece_coord
        self.board_to_output[i][j] = self.dragged_piece
        self.dragged_piece = None
        self.dragged_piece_coord = None
        self.dragged_piece_pos = None

    def coord_from_pos(self, x, y) -> Tuple[int, int]:
        """
        Fait le lien entre les pixels et les coordonnées de la matrice
        :param x:
        :param y:
        :return: Retourne i,j les coordonnées de la matrice de Board
        """
        j = (x - BOARDTOPLEFTPOS[0]) // self.case_size
        i = (y - BOARDTOPLEFTPOS[1]) // self.case_size
        return int(i), int(j)

    def pos_from_coord(self, i, j):
        return self.x + j * self.case_size, self.y + i * self.case_size

    def piece_at_coord(self, i, j):
        return self.board_to_output[i][j]

    def isNotempty(self, i, j):
        return (self.board_to_output[i][j]) is not None

    def update(self, logic):
        for i in range(8):
            for j in range(8):
                self.board_to_output[i][j] = logic.board[i][j]

    # affichage

    def draw(self, win, x, y):
        """Draws everything"""
        self.draw_board(win, x, y)
        # self.draw_attacked_cases(win)
        self.draw_pieces(win)
        self.draw_dots(win)

    def draw_board(self, win, x, y):
        self.x = x
        self.y = y
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    color = CASECOLOR1
                else:
                    color = CASECOLOR2

                pygame.draw.rect(win, color,
                                 (x + self.case_size * i, y + self.case_size * j, self.case_size, self.case_size))

    def draw_pieces(self, win):
        board = self.board_to_output
        for i in range(8):
            for j in range(8):
                if board[i][j] == "gone":
                    image = globals()[f"{self.dragged_piece.abreviation}_image"]
                    image = pygame.transform.smoothscale(image, (self.case_size, self.case_size))
                    win.blit(image,
                             (self.dragged_piece_pos[0] - self.case_size // 2,
                              self.dragged_piece_pos[1] - self.case_size // 2))
                elif (board[i][j]) is not None:
                    image = globals()[f"{board[i][j].abreviation}_image"]
                    image = pygame.transform.smoothscale(image, (self.case_size, self.case_size))
                    win.blit(image, (self.x + self.case_size * j, self.y + self.case_size * i))

    def draw_dots(self, win):
        for legal_move in self.legal_moves_to_output:
            i, j = legal_move[0], legal_move[1]

            color = GREEN if not self.piece_at_coord(i, j) else ORANGE

            pygame.draw.rect(win, color, (
                self.pos_from_coord(i, j)[0] + self.case_size // 2 - 5,
                self.pos_from_coord(i, j)[1] + self.case_size // 2 - 5,
                10, 10))

    def draw_attacked_cases(self, win):
        for case in self.attacked_cases:
            i, j = case[0], case[1]
            pygame.draw.rect(win, RED, (
                self.pos_from_coord(i, j)[0],
                self.pos_from_coord(i, j)[1],
                self.case_size, self.case_size))

    def __repr__(self):  # useless

        returnboard = [[None for _ in range(8)] for _ in range(8)]
        for i in range(8):
            for j in range(8):
                if self.board_to_output[i][j] is not None:
                    returnboard[i][j] = self.board_to_output[i][j].abreviation
        return str(returnboard)
