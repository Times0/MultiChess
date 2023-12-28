import pygame
from client.pieces import Piece
from logic import Square
from constants import *
from typing import Tuple, Optional
from logic import Logic
from fonctions import isInbounds

PADDING_WIDTH = 150
PADDING_HEIGHT = 75


def get_x_y_w_h():
    """
    :return: Retourne x,y,w,h les coordonnées du plateau de jeu
    """
    W, H = pygame.display.get_surface().get_size()
    m = min(W - 2 * PADDING_WIDTH, H - 2 * PADDING_HEIGHT)
    x = (W - m) // 2
    y = (H - m) // 2
    return x, y, m, m


def coord_from_pos(coord_x, coord_y) -> Tuple[int, int]:
    """
    Fait le lien entre les pixels et les coordonnées de la matrice
    :return: Retourne i,j les coordonnées de la matrice de Board
    """
    x, y, w, h = get_x_y_w_h()
    i = (coord_y - y) // (h // 8)
    j = (coord_x - x) // (w // 8)
    return i, j


class Board:
    def __init__(self):
        self.board_to_output = [[None for _ in range(8)] for _ in range(8)]

        self.clicked_piece_coord = None
        self.dragged_piece = None
        self.dragged_piece_coord = None

        self.dragging = False
        self.flipped = False

        self.rect = pygame.Rect(*get_x_y_w_h())

    def set_to_gone(self, i, j):
        self.dragged_piece = self._get_piece_at(i, j)
        if not self.dragged_piece:
            return
        self.dragging = True
        self.clicked_piece_coord = i, j

    def _f(self, i, j):
        if self.flipped:
            return i, 7 - j
        else:
            return 7 - i, j

    def set_to_not_gone(self):
        self.dragged_piece = None
        self.dragged_piece_coord = None
        self.dragging = False

    def _get_piece_at(self, i, j) -> Optional[Piece]:
        return self.board_to_output[i][j]

    def set_pos_from_logic(self, logic: Logic):
        for i in range(8):
            for j in range(8):
                self._set_piece(i, j, logic.get_piece(Square(i, j)))

    def _set_piece(self, i, j, piece):
        self.board_to_output[i][j] = piece

    def clicked(self, pos) -> bool:
        """Called when the mouse is clicked return True if there is a piece at the position"""
        i, j = self._f(*coord_from_pos(*pos))
        if not isInbounds(i, j):
            return False
        if self._get_piece_at(i, j) is not None:
            self.set_to_gone(i, j)
            return True
        return False

    def drop(self, pos) -> Tuple[int, int]:
        """Called when a piece is already being dragged and the mouse is released"""
        i, j = self._f(*coord_from_pos(*pos))
        self.set_to_not_gone()
        return i, j

    def flip_board(self):
        self.flipped = not self.flipped

    def draw(self, win, dots):
        """Draws everything"""
        self.draw_board(win)
        self.draw_pieces(win)
        self.draw_dots(win, dots)
        self.draw_dragged_piece(win)

    def draw_dragged_piece(self, win):
        if self.dragging:
            _, _, w, _ = get_x_y_w_h()
            case_size = w // 8
            img = pygame.transform.smoothscale(pieces_images[self.dragged_piece.get_fen()],
                                               (case_size * 1.1, case_size * 1.1))
            x, y = pygame.mouse.get_pos()
            win.blit(img, img.get_rect(center=(x, y)))

    def draw_board(self, win):
        case_size = self.rect.w // 8
        x = self.rect.x
        y = self.rect.y
        for i in range(8):
            for j in range(8):
                if (i + j) % 2 == 0:
                    color = DARK_SQUARE_COLOR
                else:
                    color = LIGHT_SQUARE_COLOR
                pygame.draw.rect(win, color, (x + j * case_size, y + i * case_size, case_size, case_size))

    def draw_pieces(self, win):
        x, y = self.rect.x, self.rect.y
        w = self.rect.w
        case_size = w // 8
        for i in range(8):
            itab = 7 - i if not self.flipped else i
            for j in range(8):
                jtab = j if not self.flipped else 7 - j
                if self.dragging and (itab, jtab) == self.clicked_piece_coord:
                    continue
                piece = self._get_piece_at(itab, jtab)
                if piece is not None:
                    img = pygame.transform.smoothscale(pieces_images[piece.get_fen()], (case_size, case_size))
                    win.blit(img, (x + j * case_size, y + i * case_size))

    def draw_dots(self, win, moves):
        x, y = self.rect.x, self.rect.y
        w = self.rect.w
        case_size = w // 8
        for move in moves:
            i, j = move.destination.i, move.destination.j
            i, j = self._f(i, j)
            pygame.draw.circle(win, RED, (x + j * case_size + case_size // 2, y + i * case_size + case_size // 2), 5)


pieces_images = {
    'P': P_image,
    'R': R_image,
    'N': N_image,
    'B': B_image,
    'Q': Q_image,
    'K': K_image,
    'p': p_image,
    'r': r_image,
    'n': n_image,
    'b': b_image,
    'q': q_image,
    'k': k_image
}
