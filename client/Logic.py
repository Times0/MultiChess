from itertools import product
from random import shuffle

import numpy as np
from numpy import matrix, ndarray, sqrt

from fonctions import isInbounds, other_color

from typing import List, Tuple, Union

format_cr = "KQkq"


class Logic:
    """ a Logic instance is an independant chess board that has every fonction needed to play the game like isMate(
    color) or cases_attacked_by(color) and attributes such as turn, state, castle_rights etc"""

    def __init__(self, fen=None, data=None):
        if isinstance(data, type(None)):
            data = np.array(None)

        if data.size > 1:
            self.board = list()
            self.load_data(data)

        elif fen:
            # variables pour les privilèges de roquer
            self.castle_rights = "kqKQ"  # kingside, queenside
            # ["game_on","blackwins", "whitewins", "stalemate"]
            self.board = [[None for _ in range(8)] for _ in range(8)]
            self.turn = "white"
            self.load_fen(fen)
        else:
            raise ArithmeticError
        self.mark = list()  # en passant

        self.state = "game_on"

    def load_fen(self, fen) -> None:
        board = []
        i, j = 0, 0
        parts = fen.split(" ")
        # part 1
        for row in parts[0].split("/"):
            b_row = []
            for c in row:
                if c == " ":
                    break
                elif c.isnumeric():
                    b_row.extend([None] * int(c))
                    j += int(c)
                elif c.isalpha():
                    b_row.append(piece_from_abreviation(c, i, j))
                    if c.upper() == "P" and i != (1 if b_row[-1].color == "black" else 6):
                        b_row[-1].never_moved = False
                    j += 1
            board.append(b_row)
            i += 1
            j = 0

        for i, part in enumerate(parts[1:]):

            if i == 0:
                self.turn = "white" if part == "w" else "black"

            elif i == 1:
                self.castle_rights = part

        self.board = board.copy()

    def get_fen(self) -> str:
        """returns the fen of the current position"""
        i, j = 0, 0
        lines = list()
        while i < 8:
            line = ""
            while j < 8:
                # si on a un espace
                if not self.piece_at(i, j):
                    c = 0
                    while j < 8 and not self.piece_at(i, j):
                        c += 1
                        j += 1
                    line += str(c)
                else:
                    line += self.piece_at(i, j).abreviation
                    j += 1
            lines.append(line)
            i += 1
            j = 0

        board = "/".join(lines)
        turn = self.turn[0]
        castle_rights = f"{self.castle_rights}"

        returnfen = " ".join([board, turn, castle_rights])
        return returnfen

    def castle_rights_bit(self) -> ndarray:

        cr = self.castle_rights
        return np.array([1 if char in cr else 0 for char in format_cr])

    def get_data(self):
        L = np.array(
            [self.board[i][j].value
             if self.board[i][j] and self.board[i][j].color == "white"
             else self.board[i][j].value + 10 if self.board[i][j] else 0 for i in range(8) for j in range(8)],
            dtype=np.int8)
        L = np.append(L, (1 if self.turn == "white" else 0))
        cr = self.castle_rights_bit()
        L = np.concatenate((L, cr))
        return L

    def load_data(self, data):

        # print("\n\nSTART ")

        L = list()
        for i in range(8):

            L.append(
                [dico2[val - 10]("black", 0, 0)
                 if val > 10
                 else dico2[val]("white", 0, 0)
                if val != 0
                else dico2[val] for val in data[i * 8:i * 8 + 8]])

            for j in range(8):
                if L[i][j]:
                    L[i][j].set_coord_weird(i, j)
        self.board = L
        self.turn = "white" if data[64] == 1 else "black"
        self.castle_rights = "".join([format_cr[i] if data[65 + i] else "" for i in range(4)])

    def check(self):
        for i in range(8):
            for j in range(8):
                if self.piece_at(i, j):
                    if self.board[i][j].i != i or self.board[i][j].j != j:
                        print(i, j, self.board[i][j].i, self.board[i][j].j)
                        # return False
        return True

    def piece_at(self, i, j):
        return self.board[i][j]

    def cases_attacked_by(self, color: str) -> list:
        L = []
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color == color:
                    L.extend(piece.attacking_squares(self))
        return list(set(L))

    def legal_moves(self, color=""):
        color = self.turn if color == "" else color
        """origin, destination"""
        returnlist = []
        for i in range(8):
            for j in range(8):
                piece = self.piece_at(i, j)
                if piece and piece.color == color:
                    legals = piece.legal_moves(self)
                    if legals:
                        for legal in legals:
                            returnlist.append((i, j, legal[0], legal[1], legal[2]))
        return returnlist

    def ordered_legal_moves(self, color):
        lm = self.legal_moves(color)
        shuffle(lm)
        lm.sort(key=lambda tup: tup[4], reverse=True)
        return lm

    def hasLegalmoves(self, color):
        for i in range(8):
            for j in range(8):
                piece = self.piece_at(i, j)
                if piece and piece.color == color and piece.legal_moves(self):
                    return True
        return False

    def king_coord(self, color: str) -> tuple:

        for i in range(8):
            for j in range(8):
                if self.piece_at(i, j) and self.board[i][j].abreviation == ("K" if color == "white" else "k"):
                    return i, j

    def king(self, color: str):
        i, j = self.king_coord(color)
        return self.board[i][j]

    @staticmethod
    def isCapture(move) -> bool:
        return move[4] == 1

    @staticmethod
    def isCheck(move):
        return move[4] == 2

    def isIncheck(self, color: str) -> bool:
        i, j = self.king_coord(color)
        return (i, j) in self.cases_attacked_by(("white" if color == "black" else "black"))

    def isMate(self, color: str) -> bool:
        return self.isIncheck(color) and not self.hasLegalmoves(color)

    def isStalemate(self, color: str) -> bool:
        return not self.hasLegalmoves(color)

    def update_game_state(self, color: str):
        """ possible states : ["black wins","white wins","stalemate"]"""
        if self.isMate(color):
            self.state = "".join([other_color(color), "wins"])
        elif self.isStalemate(color):
            self.state = "draw"

    def move(self, move, switch_turn=True) -> None:
        i, j, dest_i, dest_j, _ = move
        piece = self.board[i][j]
        if not piece:
            print(f"{i,j=}")
            print(f"{self}")
            raise Exception
        self.mark = []

        # special moves
        # castle
        type = piece.abreviation.lower()
        if type == "k":
            self.remove_castle_rights(piece.color)
            if i == 0 and j == 4 and dest_i == 0 and dest_j == 2:
                self.move((0, 0, 0, 3, 0), False)
            elif i == 0 and j == 4 and dest_i == 0 and dest_j == 6:
                self.move((0, 7, 0, 5, 0), False)
            elif i == 7 and j == 4 and dest_i == 7 and dest_j == 2:
                self.move((7, 0, 7, 3, 0), False)
            elif i == 7 and j == 4 and dest_i == 7 and dest_j == 6:
                self.move((7, 7, 7, 5, 0), False)

        elif type == "r" and piece.never_moved and self.castle_rights:
            self.remove_castle_rights(piece.color, j)
        # promotion
        elif piece.abreviation.lower() == "p" and dest_i == (0 if piece.direction == -1 else 7):
            piece = Queen(piece.color, i, j)

        # en passant
        elif type == "p" and dest_i == i + 2 * piece.direction:
            self.mark = [(i + piece.direction, j)]
        elif type == 'p' and j != dest_j and not self.piece_at(dest_i, dest_j):
            self.capture(i, dest_j)

        self.board[i][j] = None
        self.board[dest_i][dest_j] = piece
        self.board[dest_i][dest_j].moved(dest_i, dest_j)
        if switch_turn:
            self.switch_turn()

    def real_move(self, move):
        """Only used in game.py, it is called once per move and not when calculating"""
        self.move(move)
        self.update_game_state(self.turn)

    def capture(self, i, j):
        self.board[i][j] = None

    def remove_castle_rights(self, color, j=None) -> None:
        if not self.castle_rights:
            return
        if j == 0:
            r = "q"
        elif j == 7:
            r = "k"
        else:
            r = "qk"
        if color == "white":
            r = r.upper()
        for char in r:
            self.castle_rights = self.castle_rights.replace(char, "")

    def switch_turn(self) -> None:
        self.turn = "white" if self.turn == "black" else "black"

    def get_score(self, color):
        score = 0
        for i in range(8):
            for j in range(8):
                piece = self.piece_at(i, j)
                if piece and piece.color == color:
                    score += values[piece.abreviation.lower()]
        return score

    def get_static_simple_eval(self):
        return self.get_score("white") - self.get_score("black")

    def get_static_eval(self):
        simple_eval = self.get_static_simple_eval()
        if self.nb_pieces_on_board() >= 4:
            return simple_eval

        if simple_eval < -5:
            loser = "white"
        elif simple_eval > 5:
            loser = "black"
        else:
            loser = "white"

        c_distance = self.distance_center_king(loser)
        k_distance = self.distance_between_kings()

        if loser == "white":
            return simple_eval - c_distance + k_distance
        elif loser == "black":
            return simple_eval + c_distance - k_distance
        else:
            return simple_eval

    def distance_between_kings(self):
        bk = self.king("black")
        wk = self.king("white")
        return sqrt((bk.i - wk.i) ** 2 + (bk.i - wk.i) ** 2)

    def distance_center_king(self, color):
        i, j = self.king_coord(color)
        return sqrt((i - 3) ** 2 + (j - 3) ** 2)

    def nb_pieces_on_board(self):
        return len([0 for i in range(8) for j in range(8) if self.board[i][j]])

    def __repr__(self) -> str:
        returnboard = [[" " for _ in range(8)] for _ in range(8)]
        for i in range(8):
            for j in range(8):
                if self.board[i][j]:
                    returnboard[i][j] = self.board[i][j].abreviation

        return str(matrix(returnboard))


class Piece:
    def __init__(self, color, i, j):
        self.never_moved = True
        self.color = color
        self.i = i
        self.j = j
        self.abreviation = None
    
    def set_abreviation(self, name) -> None:
        inv_map = {v: k for k, v in dico.items()}
        abreviation = inv_map[name]
        if self.color == "white":
            abreviation = abreviation.upper()
        self.abreviation = abreviation

    def set_coord_weird(self, i, j) -> None:
        self.i, self.j = i, j

    def almost_legal_moves(self, board: Logic) -> list:
        """Cette fonction est overriden pour chacune des pièces, elle renvoie les moves possible pour une pièce
        en prenant en compte les autres pièces de l'échequier mais sans prendre en compte les échecs au roi"""
        pass

    def legal_moves(self, logic: Logic):
        """ Returns the list of every almost legal move this piece has which means it does not care about checks,
        checks are handled in  legal_moves
         Format is (i, j, id) with id being 1 if it is a capture and ((2 if it is a check)) (else 0) """

        returnlist = []
        if self.color != logic.turn:
            return []
        for move in self.almost_legal_moves(logic):
            virtual = Logic(fen=logic.get_fen())
            true_move = self.i, self.j, *move
            virtual.move(true_move)
            if not virtual.isIncheck(self.color):
                if virtual.isIncheck(other_color(self.color)):
                    returnlist.append((move[0], move[1], 2))
                else:
                    returnlist.append(move)

        return returnlist

    def attacking_squares(self, logic) -> list:
        """returns the list of every coordinates this piece is attacking/protecting, it is a bit different from
        almos_legal moves since a protected piece is not attacked """
        return [(e[0], e[1]) for e in self.almost_legal_moves(logic)]

    def moved(self, dest_i, dest_j) -> None:
        """Updates the info the piece has about itself"""
        self.i, self.j = dest_i, dest_j
        self.never_moved = False


class Pawn(Piece):
    def __init__(self, color, i, j):
        super().__init__(color, i, j)
        self.set_abreviation(self.__class__)
        self.value = 1
        self.direction = -1 if self.color == 'white' else +1

    def almost_legal_moves(self, board: Logic) -> list:

        piece_at = board.piece_at
        i, j = self.i, self.j
        dir = self.direction
        returnlist = []

        # move devant
        i1 = i + dir  # case devant le pion (relativement)
        if isInbounds(i1, j) and not piece_at(i1, j):
            returnlist.append((i1, j, 0))
            if self.never_moved:
                i2 = i1 + dir  # deux cases devant le pion
                if isInbounds(i2, j) and not piece_at(i2, j):
                    returnlist.append((i2, j, 0))

        # captures
        for ja in [j - 1, j + 1]:
            if isInbounds(i1, ja) and piece_at(i1, ja) and piece_at(i1, ja).color != self.color:
                returnlist.append((i1, ja, 1))

        # en croissant
        if i == (3 if self.color == "white" else 4):
            for jb in [j - 1, j + 1]:
                if isInbounds(i1, jb) and (i1, jb) in board.mark:
                    returnlist.append((i1, jb, 1))

        return returnlist

    def attacking_squares(self, logic) -> list:
        piece_at = logic.piece_at
        i, j = self.i, self.j
        dir = self.direction
        i1 = i + dir
        returnlist = []
        # attacked squares
        for j in [j - 1, j + 1]:
            if isInbounds(i1, j) and (not piece_at(i1, j) or piece_at(i1, j).color != self.color):
                returnlist.append((i1, j))
        return returnlist


class Bishop(Piece):
    def __init__(self, color, i, j):
        super().__init__(color, i, j)
        self.set_abreviation(self.__class__)
        self.value = 2
        # self.image = globals()[f"{self.abreviation}_image"]

    def almost_legal_moves(self, board):
        piece_at = board.piece_at
        returnlist = []
        i, j = self.i, self.j
        for a, b in [[1, 1], [-1, 1], [1, -1], [-1, -1]]:
            for n in range(1, 8):  # on ne teste pas la case sur laquelle il y a déjà notre pièce
                i1, j1 = i + a * n, j + b * n
                if isInbounds(i1, j1):
                    piece = piece_at(i1, j1)
                    if not piece:
                        returnlist.append((i1, j1, 0))
                    elif piece.color != self.color:
                        returnlist.append((i1, j1, 1))
                    if piece:
                        break  # c'est cette ligne qui traduit la rupture de la 'ligne' si une pièce y est présente
        return returnlist


class Rook(Piece):
    def __init__(self, color, i, j):
        super().__init__(color, i, j)
        self.set_abreviation(self.__class__)
        self.value = 3
        # self.image = globals()[f"{self.abreviation}_image"]

    def almost_legal_moves(self, board):
        piece_at = board.piece_at
        returnlist = []
        i, j = self.i, self.j
        for a, b in [[1, 0], [-1, 0], [0, -1], [0, 1]]:
            for n in range(1, 8):  # on ne teste pas la case sur laquelle il y a déjà notre pièce
                i1, j1 = i + a * n, j + b * n
                if isInbounds(i1, j1):
                    piece = piece_at(i1, j1)
                    if not piece:
                        returnlist.append((i1, j1, 0))
                    elif piece.color != self.color:
                        returnlist.append((i1, j1, 1))
                    if piece:
                        break  # rupture de la 'ligne' si une pièce y est présente
        return returnlist


class Knight(Piece):
    def __init__(self, color, i, j):
        super().__init__(color, i, j)
        self.set_abreviation(self.__class__)
        self.value = 4
        # self.image = globals()[f"{self.abreviation}_image"]

    def almost_legal_moves(self, board):
        piece_at = board.piece_at
        i, j = self.i, self.j
        returnlist = []
        moves = list(product([i - 1, i + 1], [j - 2, j + 2])) + list(product([i - 2, i + 2], [j - 1, j + 1]))
        # return [move for move in moves if
        #         isInbounds(*move) and (not piece_at(*move) or piece_at(*move).color != self.color)]
        for i1, j1 in moves:
            if isInbounds(i1, j1):
                piece = piece_at(i1, j1)
                if not piece:
                    returnlist.append((i1, j1, 0))
                elif piece.color != self.color:
                    returnlist.append((i1, j1, 1))
        return returnlist


class Queen(Piece):
    def __init__(self, color, i, j):
        super().__init__(color, i, j)
        self.set_abreviation(self.__class__)
        self.value = 5
        # self.image = globals()[f"{self.abreviation}_image"]

    def almost_legal_moves(self, board):
        piece_at = board.piece_at
        returnlist = []
        i, j = self.i, self.j
        for a, b in [[1, 0], [-1, 0], [0, -1], [0, 1], [1, 1], [-1, 1], [1, -1], [-1, -1]]:
            for n in range(1, 8):  # on ne teste pas la case sur laquelle il y a déjà notre pièce
                i1, j1 = i + a * n, j + b * n
                if isInbounds(i1, j1):
                    piece = piece_at(i1, j1)
                    if not piece:
                        returnlist.append((i1, j1, 0))
                    elif piece.color != self.color:
                        returnlist.append((i1, j1, 1))
                    if piece:
                        break  # rupture de la 'ligne' si une pièce y est présente
        return returnlist


class King(Piece):
    def __init__(self, color, i, j):
        super().__init__(color, i, j)
        self.set_abreviation(self.__class__)
        self.value = 6
        # self.image = globals()[f"{self.abreviation}_image"]

    def almost_legal_moves(self, board):
        piece_at = board.piece_at
        returnlist = []

        i, j = self.i, self.j
        for a, b in [[-1, -1], [-1, 1], [-1, 0], [1, -1], [1, 1], [1, 0], [0, 1], [0, -1]]:
            i1, j1 = i + a, j + b
            if isInbounds(i1, j1):
                piece = piece_at(i1, j1)
                if not piece:
                    returnlist.append((i1, j1, 0))
                elif piece.color != self.color:
                    returnlist.append((i1, j1, 1))

        castle_rights = board.castle_rights
        if self.color == "white":
            rights = str([char for char in castle_rights if char.upper() == char])
        else:
            rights = str([char for char in castle_rights if char.lower() == char])
        if rights:
            i, j = (0, 4) if self.color == "black" else (7, 4)
            if "k" in rights.lower():
                if not piece_at(i, j + 1) and not piece_at(i, j + 2):
                    attacked_cases = board.cases_attacked_by(other_color(self.color))
                    if (i, j) not in attacked_cases and (i, j + 1) not in attacked_cases and (
                            i, j + 2) not in attacked_cases and piece_at(i, 7):
                        returnlist.append((i, j + 2, 0))
            if "q" in rights.lower():
                if not piece_at(i, j - 1) and not piece_at(i, j - 2) and not piece_at(i, j - 3):
                    attacked_cases = board.cases_attacked_by(other_color(self.color))
                    if (i, j) not in attacked_cases and (i, j - 1) not in attacked_cases and (
                            i, j - 2) not in attacked_cases and piece_at(i, 0):
                        returnlist.append((i, j - 2, 0))
        return returnlist

    def attacking_squares(self, logic):
        piece_at = logic.piece_at
        returnlist = []

        i, j = self.i, self.j
        for a, b in [[-1, -1], [-1, 1], [-1, 0], [1, -1], [1, 1], [1, 0], [0, 1], [0, -1]]:
            i1, j1 = i + a, j + b
            if isInbounds(i1, j1) and (not piece_at(i1, j1) or piece_at(i1, j1).color != self.color):
                returnlist.append((i1, j1))
        return returnlist


dico = {"p": Pawn, "r": Rook, "b": Bishop, "n": Knight, "q": Queen, "k": King}
dico2 = {0: None, 1: Pawn, 2: Bishop, 3: Rook, 4: Knight, 5: Queen, 6: King}
values = {"p": 1, "r": 5, "b": 3, "n": 3, "q": 9, "k": 0}


def piece_from_abreviation(abreviation, i, j):
    return dico[abreviation.lower()]("black" if abreviation.lower() == abreviation else "white", i, j)
