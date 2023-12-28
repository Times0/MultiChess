import pygame
from pieces import Piece, isInbounds
from square import Move
from logic import Square
from constants import *
from typing import Tuple, Optional
from logic import Logic
from pygame import gfxdraw

PADDING_WIDTH = 125
PADDING_HEIGHT = 50


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
    def __init__(self, logic, perform_move: callable):
        self.logic: Logic = logic
        self.board_to_output = [[None for _ in range(8)] for _ in range(8)]

        self.clicked_piece_coord = None
        self.dragged_piece = None
        self.dragged_piece_coord = None

        self.dragging = False
        self.flipped = False

        self.current_piece_legal_moves = []
        self.rect = pygame.Rect(*get_x_y_w_h())

        self.play = perform_move

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

    def handle_event(self, event, dummy_mode=False):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if self.clicked(pos):
                piece = self.logic.get_piece(Square(*self.clicked_piece_coord))
                if self.logic.turn != piece.color:
                    return
                self.current_piece_legal_moves = piece.legal_moves(self.logic)
            else:
                self.current_piece_legal_moves.clear()
        if self.dragging:
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                pos = pygame.mouse.get_pos()
                dest_coord = self.drop(pos)
                move = Move(Square(*self.clicked_piece_coord), Square(*dest_coord))
                if move in self.current_piece_legal_moves and not dummy_mode:
                    self.current_piece_legal_moves.clear()
                    self.play(move)

    def draw(self, win):
        """Draws everything"""
        self.draw_board(win)
        self.draw_pieces(win)
        self.draw_dots(win, )
        self.draw_dragged_piece(win)

    def draw_dragged_piece(self, win):
        if self.dragging:
            _, _, w, _ = get_x_y_w_h()
            case_size = w // 8
            abbr = self.dragged_piece.get_fen()
            if abbr not in cache_img:
                cache_img[abbr] = pygame.transform.smoothscale(pieces_images[abbr], (case_size, case_size))

            img = cache_img[abbr]
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

    def draw_dots(self, win):
        x, y = self.rect.x, self.rect.y
        w = self.rect.w
        case_size = w // 8
        radius = case_size // 10

        for move in self.current_piece_legal_moves:
            i, j = move.destination.i, move.destination.j
            i, j = self._f(i, j)

            # Calculate the center of the circle
            center_x = x + j * case_size + case_size // 2
            center_y = y + i * case_size + case_size // 2

            # avoid aliasing on small circles
            gfxdraw.aacircle(win, center_x, center_y, radius, (100, 111, 64))
            gfxdraw.filled_circle(win, center_x, center_y, radius, (100, 111, 64))


cache_img = {}  # str: pygame.Surface
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
