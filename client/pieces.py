from itertools import product
from enum import Enum
from fonctions import other_color, isInbounds
from square import Square, Move, Side


# forwards declaration
class Logic:
    pass


class Color(Enum):
    WHITE = 0
    BLACK = 1


class Piece:
    def __init__(self, color, square: Square):
        self.never_moved = True
        self.color: Color = color
        self.square: Square = square

    def set_coord_weird(self, i, j) -> None:
        self.i, self.j = i, j

    def almost_legal_moves(self, board: Logic) -> list[Move]:
        """Cette fonction est overriden pour chacune des pièces, elle renvoie les moves possible pour une pièce
        en prenant en compte les autres pièces de l'échequier mais sans prendre en compte les échecs au roi"""
        pass

    def legal_moves(self, logic: Logic) -> list[Move]:
        """ Returns the list of every almost legal move this piece has which means it does not care about checks,
        checks are handled in  legal_moves
         Format is (i, j, id) with id being 1 if it is a capture and ((2 if it is a check)) (else 0) """
        from logic import Logic
        returnlist = []
        if self.color != logic.turn:
            raise Exception(f"It is not this piece's turn, it is {logic.turn} turn\n"
                            f" and this piece is {self.color}\n"
                            f" and the piece is at {self.square}")
        for move in self.almost_legal_moves(logic):
            virtual = Logic(logic.get_fen())
            virtual.move(move)
            me_is_in_check = virtual.is_in_check(self.color)
            if not me_is_in_check:
                if virtual.is_in_check(other_color(self.color)):
                    move.is_check = True
                returnlist.append(move)
        return returnlist

    def attacking_squares(self, logic) -> list[Square]:
        """returns the list of every coordinates this piece is attacking/protecting, it is a bit different from
        almos_legal moves since a protected piece is not attacked """
        return [move.destination for move in self.almost_legal_moves(logic)]

    def moved(self, square: Square) -> None:
        """Updates the info the piece has about itself"""
        self.never_moved = False
        self.square = square

    def get_fen(self) -> str:
        """Returns the fen notation of the piece"""
        return self.abreviation if self.color == Color.WHITE else self.abreviation.lower()

    def __str__(self):
        s = f"{self.color} {self.abreviation} at {self.square}"
        return s


class Pawn(Piece):
    def __init__(self, color, square: Square):
        super().__init__(color, square)
        self.direction = 1 if self.color == Color.WHITE else -1
        self.abreviation = "P"

    def almost_legal_moves(self, board: Logic) -> list[Move]:
        piece_at = board.get_piece
        i, j = self.square.i, self.square.j
        dir = self.direction
        returnlist = []

        # move devant
        i1 = i + dir  # case devant le pion (relativement)
        if isInbounds(i1, j) and not piece_at(Square(i1, j)):
            returnlist.append(Move(self.square, Square(i1, j)))
            if self.square.i == (1 if self.color == Color.WHITE else 6):
                i2 = i1 + dir  # deux cases devant le pion
                if isInbounds(i2, j) and not piece_at(Square(i2, j)):
                    returnlist.append(Move(self.square, Square(i2, j)))

        # captures
        for ja in [j - 1, j + 1]:
            if 0 <= ja < 8:
                p = piece_at(Square(i1, ja))
                if isInbounds(i1, ja) and p and p.color != self.color:
                    returnlist.append(Move(self.square, Square(i1, ja), is_capture=True))

        # en croissant
        if board.en_passant_square:
            if board.en_passant_square.j in [j - 1, j + 1]:
                if board.en_passant_square.i == i + dir:
                    returnlist.append(Move(self.square, board.en_passant_square, is_capture=True))
        return returnlist

    def attacking_squares(self, logic) -> list[Square]:
        piece_at = logic.get_piece
        i, j = self.square.i, self.square.j
        dir = self.direction
        i1 = i + dir
        returnlist = []
        # attacked squares
        for ja in [j - 1, j + 1]:
            if isInbounds(i1, ja):
                returnlist.append(Square(i1, ja))

        return returnlist


class Bishop(Piece):
    def __init__(self, color, square: Square):
        super().__init__(color, square)
        self.abreviation = "B"

    def almost_legal_moves(self, board) -> list[Move]:
        piece_at = board.get_piece
        returnlist = []
        i, j = self.square.i, self.square.j

        for a, b in [[1, 1], [-1, 1], [1, -1], [-1, -1]]:
            i1, j1 = i + a, j + b
            while isInbounds(i1, j1):
                try:
                    piece = piece_at(Square(i1, j1))
                except IndexError:
                    break
                if not piece:
                    returnlist.append(Move(self.square, Square(i1, j1)))
                elif piece.color != self.color:
                    returnlist.append(Move(self.square, Square(i1, j1), is_capture=True))
                    break
                else:
                    break
                i1, j1 = i1 + a, j1 + b

        return returnlist


class Rook(Piece):
    def __init__(self, color, square: Square):
        super().__init__(color, square)
        self.abreviation = "R"

    def almost_legal_moves(self, board) -> list[Move]:
        piece_at = board.get_piece
        returnlist = []
        i, j = self.square.i, self.square.j

        # Check squares in each direction separately
        for a, b in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            i1, j1 = i + a, j + b
            while isInbounds(i1, j1):
                piece = piece_at(Square(i1, j1))
                if not piece:
                    returnlist.append(Move(self.square, Square(i1, j1)))
                    i1, j1 = i1 + a, j1 + b
                elif piece.color != self.color:
                    returnlist.append(Move(self.square, Square(i1, j1), is_capture=True))
                    break
                else:
                    break

        return returnlist


class Knight(Piece):
    def __init__(self, color, square: Square):
        super().__init__(color, square)
        self.abreviation = "N"

    def almost_legal_moves(self, board) -> list[Move]:
        piece_at = board.get_piece
        i, j = self.square.i, self.square.j
        returnlist = []

        # Iterate over each of the four possible moves
        for a, b in [(i - 1, j - 2), (i - 1, j + 2), (i + 1, j - 2), (i + 1, j + 2), (i - 2, j - 1), (i - 2, j + 1),
                     (i + 2, j - 1), (i + 2, j + 1)]:
            if isInbounds(a, b):
                piece = piece_at(Square(a, b))
                if not piece:
                    returnlist.append(Move(self.square, Square(a, b)))
                elif piece.color != self.color:
                    returnlist.append(Move(self.square, Square(a, b), is_capture=True))

        return returnlist


class Queen(Piece):
    def __init__(self, color, square: Square):
        super().__init__(color, square)
        self.abreviation = "Q"

    def almost_legal_moves(self, board):
        piece_at = board.get_piece
        returnlist = []
        i, j = self.square.i, self.square.j
        for a, b in [[1, 0], [-1, 0], [0, -1], [0, 1], [1, 1], [-1, 1], [1, -1], [-1, -1]]:
            for n in range(1, 8):  # on ne teste pas la case sur laquelle il y a déjà notre pièce
                i1, j1 = i + a * n, j + b * n
                if isInbounds(i1, j1):
                    piece = piece_at(Square(i1, j1))
                    if not piece:
                        returnlist.append(Move(self.square, Square(i1, j1)))
                    elif piece.color != self.color:
                        returnlist.append(Move(self.square, Square(i1, j1), is_capture=True))
                        break
                    else:
                        break  # rupture de la 'ligne' si une pièce y est présente
        return returnlist


class King(Piece):
    def __init__(self, color, square: Square):
        super().__init__(color, square)
        self.abreviation = "K"

    def almost_legal_moves(self, board: Logic):
        piece_at = board.get_piece
        returnlist = []

        i, j = self.square.i, self.square.j
        for a, b in [[-1, -1], [-1, 1], [-1, 0], [1, -1], [1, 1], [1, 0], [0, 1], [0, -1]]:
            i1, j1 = i + a, j + b
            if isInbounds(i1, j1):
                piece = piece_at(Square(i1, j1))
                if not piece:
                    returnlist.append(Move(self.square, Square(i1, j1)))
                elif piece.color != self.color:
                    returnlist.append(Move(self.square, Square(i1, j1), is_capture=True))

        # Castling
        a_s = board.squares_attacked_by(other_color(self.color))
        # KING SIDE
        if self.is_castling_still_available(board, Side.KING):
            if not piece_at(Square(i, j + 1)) and not piece_at(Square(i, j + 2)) \
                    and Square(i, j + 1) not in a_s and Square(i, j) not in a_s:
                returnlist.append(Move(self.square, Square(i, j + 2)))

        # QUEEN SIDE
        if self.is_castling_still_available(board, Side.QUEEN):
            if not piece_at(Square(i, j - 1)) and not piece_at(Square(i, j - 2)) and not piece_at(Square(i, j - 3)) \
                    and Square(i, j) not in a_s and Square(i, j - 1) not in a_s and Square(i, j - 2) not in a_s:
                returnlist.append(Move(self.square, Square(i, j - 2)))

        return returnlist

    def attacking_squares(self, logic):
        piece_at = logic.get_piece
        returnlist = []

        i, j = self.square.i, self.square.j
        for a, b in [[-1, -1], [-1, 1], [-1, 0], [1, -1], [1, 1], [1, 0], [0, 1], [0, -1]]:
            i1, j1 = i + a, j + b
            if not isInbounds(i1, j1):
                continue
            p = piece_at(Square(i1, j1))
            if isInbounds(i1, j1) and (not p or p.color != self.color):
                returnlist.append(Square(i1, j1))
        return returnlist

    def is_castling_still_available(self, logic: Logic, side: Side):
        color = self.color
        if color == Color.WHITE:
            if side == Side.KING:
                return logic.castle_rights_bit & 0b0001
            else:
                return logic.castle_rights_bit & 0b0010
        else:
            if side == Side.KING:
                return logic.castle_rights_bit & 0b0100
            else:
                return logic.castle_rights_bit & 0b1000


dico = {"p": Pawn, "r": Rook, "b": Bishop, "n": Knight, "q": Queen, "k": King}
dico2 = {0: None, 1: Pawn, 2: Bishop, 3: Rook, 4: Knight, 5: Queen, 6: King}


def piece_from_abreviation(abreviation, i, j):
    return dico[abreviation.lower()](Color.BLACK if abreviation.lower() == abreviation else Color.WHITE, Square(i, j))


piece_value = {"P": 1, "N": 3, "B": 3, "R": 5, "Q": 9, "K": 1000}
