import numpy as np

from client.constants import STARTINGPOSFEN
from pieces import Square, Move, PieceColor, piece_from_abbreviation, other_color, Side, Piece, Queen, King
import enum


class State(enum.Enum):
    GAMEON = 0
    BLACKWINS = 1
    WHITEWINS = 2
    DRAW = 3  # 50 moves rule, stalemate


class Logic:
    def __init__(self, fen=STARTINGPOSFEN):
        self.board = np.empty((8, 8), dtype=Piece)
        self.state = State.GAMEON
        self.turn: PieceColor = PieceColor.WHITE
        self.castle_rights_bit = 0
        self.full_move_number = int()
        self.half_move_clock = int()
        self.en_passant_square = str()
        self.load_fen(fen)
        self.move_history = []
        self.fen_history = []
        self.king_square = {PieceColor.WHITE: self.get_king_square(PieceColor.WHITE),
                            PieceColor.BLACK: self.get_king_square(PieceColor.BLACK)}

    def load_fen(self, fen) -> None:
        """loads a fen into the board"""
        self.board = np.empty((8, 8), dtype=Piece)
        fen = fen.split(" ")
        fen_board = fen[0].split("/")
        for i in range(8):
            j = 0
            for char in fen_board[i]:
                if char.isdigit():
                    j += int(char)
                else:
                    self.set_piece(Square(7 - i, j), piece_from_abbreviation(char, 7 - i, j))
                    j += 1
        self.turn = PieceColor.WHITE if fen[1] == "w" else PieceColor.BLACK
        str_castle_rights = fen[2]
        self.castle_rights_bit = 0b0000
        if "K" in str_castle_rights:
            self.castle_rights_bit |= 0b0001
        if "Q" in str_castle_rights:
            self.castle_rights_bit |= 0b0010
        if "k" in str_castle_rights:
            self.castle_rights_bit |= 0b0100
        if "q" in str_castle_rights:
            self.castle_rights_bit |= 0b1000

        self.en_passant_square = Square(fen[3]) if fen[3] != "-" else None
        self.half_move_clock = int(fen[4])
        self.full_move_number = int(fen[5])

    def get_fen(self) -> str:
        """returns the fen of the current position"""
        fen = ""
        empty = 0
        for i in range(7, -1, -1):
            for j in range(8):
                piece = self.get_piece(Square(i, j))
                if piece:
                    if empty:
                        fen += str(empty)
                        empty = 0
                    fen += piece.get_fen()
                else:
                    empty += 1
            if empty:
                fen += str(empty)
                empty = 0
            if i != 0:
                fen += "/"
        fen += f" {'w' if self.turn == PieceColor.WHITE else 'b'}"
        str_castle_rights = ""
        if self.castle_rights_bit & 0b0001:
            str_castle_rights += "K"
        if self.castle_rights_bit & 0b0010:
            str_castle_rights += "Q"
        if self.castle_rights_bit & 0b0100:
            str_castle_rights += "k"
        if self.castle_rights_bit & 0b1000:
            str_castle_rights += "q"

        fen += f" {str_castle_rights if str_castle_rights else '-'}"
        fen += f" {self.en_passant_square if self.en_passant_square else '-'}"
        fen += f" {self.half_move_clock} {self.full_move_number}"
        return fen

    def get_piece(self, square: Square) -> Piece or None:
        return self.board[square.i][square.j]

    def set_piece(self, square: Square, piece: Piece | None) -> None:
        self.board[square.i][square.j] = piece

    def squares_attacked_by(self, color: PieceColor) -> list[Square]:
        L = set()
        for i in range(8):
            for j in range(8):
                piece = self.get_piece(Square(i, j))
                if piece and piece.color == color:
                    L.update(piece.attacking_squares(self))
        return list(L)

    def legal_moves(self, color) -> list[Move]:
        color = self.turn if color is None else color
        return_list = []
        for i in range(8):
            for j in range(8):
                piece = self.get_piece(Square(i, j))
                if piece and piece.color == color:
                    legal_moves = piece.legal_moves(self)
                    return_list.extend(legal_moves)
        return return_list

    def get_legal_moves_piece(self, square: Square):
        piece = self.get_piece(square)

        if piece is None:
            raise Exception("No piece at this square")
        elif piece.color != self.turn:
            raise Exception("Piece is not the right color")
        else:
            return piece.legal_moves(self)

    def ordered_legal_moves(self, color: PieceColor):
        """Returns a list of legal moves where the checks are first then captures then the rest"""
        legal_moves = self.legal_moves(color)
        checks = []
        captures = []
        rest = []
        for move in legal_moves:
            if move.is_check:
                checks.append(move)
            elif move.is_capture:
                captures.append(move)
            else:
                rest.append(move)
        return checks + captures + rest

    def get_king_square(self, color: PieceColor) -> Square:
        for i in range(8):
            for j in range(8):
                p = self.get_piece(Square(i, j))
                if p and p.color == color and p.__class__ == King:
                    return Square(i, j)
        raise Exception(f"No king found for {color}\n {self}")

    def is_in_check(self, color: PieceColor) -> bool:
        s = self.king_square[color]
        squares_attacked = self.squares_attacked_by(other_color(color))
        return s in squares_attacked

    def update_game_state(self, debug=False):
        for i in range(8):
            for j in range(8):
                p = self.get_piece(Square(i, j))
                if p and p.color == self.turn and p.legal_moves(self):
                    if debug:
                        print(f"{self.turn} has legal moves : {p.legal_moves(self)}")
                    self.state = State.GAMEON
                    return

        if self.is_in_check(self.turn):
            self.state = State.WHITEWINS if self.turn == PieceColor.BLACK else State.BLACKWINS
        else:
            self.state = State.DRAW

    def move(self, move: Move) -> None:
        piece = self.get_piece(move.origin)
        if not piece:
            raise Exception(f"Tried to do the move {move} but there is no piece at {move.origin}\n{self}")
        if piece.color != self.turn:
            raise Exception(f"it's not {piece.color}'s turn")
        self.en_passant_square = None

        if piece and piece.abbreviation.lower() == "p" or move.is_capture:
            self.half_move_clock = 0
        else:
            self.half_move_clock += 1

        # castle
        piece_type = piece.abbreviation.lower()
        if piece_type == "k":
            self.king_square[piece.color] = move.destination
            if abs(move.origin.j - move.destination.j) == 2:
                rook_square = Square(move.origin.i, 7 if move.origin.j < move.destination.j else 0)
                rook = self.get_piece(rook_square)
                self.set_piece(rook_square, None)
                self.set_piece(Square(move.origin.i, 5 if move.origin.j < move.destination.j else 3), rook)
                rook.moved(Square(move.origin.i, 5 if move.origin.j < move.destination.j else 3))
            self.remove_castle_rights(piece.color, Side.KING)
            self.remove_castle_rights(piece.color, Side.QUEEN)

        elif piece_type == "r" and piece.never_moved:
            side = Side.KING if piece.square.j < move.destination.j else Side.QUEEN
            self.remove_castle_rights(piece.color, side)
        elif piece_type == "p" and move.destination.i == (7 if piece.direction == 1 else 0):
            self.set_piece(move.origin, None)
            q: Piece = Queen(piece.color, move.destination)
            self.set_piece(move.destination, q)
            return

            # en passant square
        if piece_type == "p" and move.destination.i == (3 if piece.direction == 1 else 4):
            self.en_passant_square = Square(move.origin.i + piece.direction, move.destination.j)
        elif piece_type == "p" and not self.get_piece(move.destination) and move.destination.j != move.origin.j:
            self.set_piece(Square(move.destination.i - piece.direction, move.destination.j), None)

        self.set_piece(move.origin, None)
        self.set_piece(move.destination, piece)
        piece.moved(move.destination)

    def real_move(self, move: Move) -> None:
        """
        Called once the move is validated, updates the game state, switches the turn and increments the halfmove
        clock
        """
        self.move_history.append(move)
        self.fen_history.append(self.get_fen())
        self.move(move)
        self.switch_turn()

        if self.turn == PieceColor.WHITE:
            self.full_move_number += 1

        self.update_game_state()

    def remove_castle_rights(self, color: PieceColor, side: Side) -> None:
        """
        Removes the castle rights for the given color and side 1110 means no castle rights for white king and
        KINGSIDE
        """
        if color == PieceColor.WHITE:
            if side == Side.KING:
                self.castle_rights_bit &= 0b1110
            else:
                self.castle_rights_bit &= 0b1101
        else:
            if side == Side.KING:
                self.castle_rights_bit &= 0b1011
            else:
                self.castle_rights_bit &= 0b0111

    def switch_turn(self) -> None:
        self.turn = PieceColor.WHITE if self.turn == PieceColor.BLACK else PieceColor.BLACK

    def reset(self):
        self.load_fen(STARTINGPOSFEN)
        self.move_history = []
        self.fen_history = []

    def __repr__(self):
        s = ""
        for i in range(8, 0, -1):
            s += str(i) + " "
            for j in "abcdefgh":
                piece = self.get_piece(Square(j + str(i)))
                if piece:
                    s += piece.abbreviation + " "
                else:
                    s += "~ "
            s += "\n"
        s += "____________________\n"
        s += "  a b c d e f g h"
        return s
