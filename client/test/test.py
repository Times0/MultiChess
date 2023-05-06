import unittest
from logic import Logic, Color
from constants import *
from logic import State, Square, Move

import logging


class TestMovement(unittest.TestCase):
    def test_move(self):
        logic = Logic(STARTINGPOSFEN)
        self.assertEqual(logic.get_fen(), STARTINGPOSFEN)


class TestFen(unittest.TestCase):
    def test_load_fen(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        logic = Logic(fen)
        self.assertEqual(logic.turn, Color.WHITE)
        self.assertEqual(logic.castle_rights_bit, 0b1111)

    def test_get_fen(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        logic = Logic(fen)
        expected_fen = fen
        self.assertEqual(logic.get_fen(), expected_fen)

    def test_complcated_fen(self):
        fen = "r1b2r2/pp4pp/1qnbpk2/3p2nQ/3P1N2/1P4PB/P4P1P/R1B2RK1 w - - 2 18"
        logic = Logic(fen)
        expected_fen = fen
        self.assertEqual(logic.get_fen(), expected_fen)

    def test_fen_with_en_passant(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq e3 0 1"
        logic = Logic(fen)
        expected_fen = fen
        self.assertEqual(logic.get_fen(), expected_fen)
        self.assertEqual(logic.en_passant_square, Square("e3"))


class TestCastling(unittest.TestCase):
    def test_basic_kingside_no_check(self):
        fen = "rnbqk2r/ppppbppp/5n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        logic = Logic(fen)
        self.assertEqual(logic.castle_rights_bit, 0b1111)

        lm = logic.legal_moves(Color.WHITE)
        self.assertIn(Move(Square("e1"), Square("g1")), lm)
        self.assertNotIn(Move(Square("e1"), Square("c1")), lm)
        logic.real_move(Move(Square("e1"), Square("g1")))
        self.assertEqual(logic.castle_rights_bit, 0b1100)

    def test_advanced(self):
        fen = "rnbqk2r/ppppbppp/8/4p2n/2B1P1P1/5N2/PPPP1P1P/RNBQ1RK1 b kq - 0 5"
        logic = Logic(fen)
        self.assertEqual(logic.castle_rights_bit, 0b1100)
        self.assertIn(Move(Square("e8"), Square("g8")), logic.legal_moves(Color.BLACK))

        logic.real_move(Move(Square("f7"), Square("f5")))
        self.assertEqual(logic.castle_rights_bit, 0b1100)

        logic.real_move(Move(Square("h2"), Square("h3")))
        self.assertEqual(logic.castle_rights_bit, 0b1100)

        self.assertNotIn(Move(Square("e8"), Square("g8")), logic.legal_moves(Color.BLACK))


class TestPromotion(unittest.TestCase):
    def test(self):
        fen = "rnb1k2r/pp1p2Pp/3b2P1/q1p1p2n/7P/8/PPPP1P2/RNBQKBNR w KQkq - 1 9"
        logic = Logic(fen)
        self.assertEqual(logic.get_fen(), fen)

        logic.real_move(Move(Square("g7"), Square("g8")))

        new_fen = "rnb1k1Qr/pp1p3p/3b2P1/q1p1p2n/7P/8/PPPP1P2/RNBQKBNR b KQkq - 0 9"
        self.assertEqual(logic.get_fen(), new_fen)



if __name__ == '__main__':
    unittest.main()
