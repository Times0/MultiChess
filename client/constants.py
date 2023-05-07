import os

from pygame import image

# Colors
BLACK = 0, 0, 0
WHITE = 255, 255, 255
LIGHTBEIGE = 181, 136, 99
BROWN = 240, 217, 181
GREEN = 63, 123, 82
ORANGE = 253, 189, 89
RED = 250, 41, 76
GREY = 185, 199, 185
YELLOW = 252, 186, 64

BG_COLOR = BLACK

DARK_SQUARE_COLOR = BROWN
LIGHT_SQUARE_COLOR = LIGHTBEIGE

# Sizes
WIDTH, HEIGHT = 1920*0.6, 1080*0.8

# Pieces

dir = os.path.dirname(__file__)
P_image = image.load(fr"{dir}/assets/row-1-col-6.png")  # white
R_image = image.load(fr"{dir}/assets/row-1-col-5.png")  # white
N_image = image.load(fr"{dir}/assets/row-1-col-4.png")  # white
B_image = image.load(fr"{dir}/assets/row-1-col-3.png")  # white
Q_image = image.load(fr"{dir}/assets/row-1-col-2.png")  # white
K_image = image.load(fr"{dir}/assets/row-1-col-1.png")  # white

p_image = image.load(fr"{dir}/assets/row-2-col-6.png")  # black
r_image = image.load(fr"{dir}/assets/row-2-col-5.png")  # black
n_image = image.load(fr"{dir}/assets/row-2-col-4.png")  # black
b_image = image.load(fr"{dir}/assets/row-2-col-3.png")  # black
q_image = image.load(fr"{dir}/assets/row-2-col-2.png")  # black
k_image = image.load(fr"{dir}/assets/row-2-col-1.png")  # black

# other
STARTINGPOSFEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

fen1 = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
fencheck = "rnbqkbnr/pppppppp/5K2/8/8/8/PPPPPPPP/RNBQ1BNR w kq - 0 1"
fenmate = "r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1"
test = 'rn1qkb1r/pp2pppp/5n2/3p1b2/3P4/2N1P3/PP3PPP/R1BQKBNR w KQkq - 0 1 id "CCR01"; bm Qb3;'
endgame_fen = "2k5/8/8/8/2K5/8/3Q4/8 w - - 0 1"
castlefen = "r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R w KQkq - 0 1"
endgame = "8/8/3k4/8/3KQ3/8/8/8 w - - 4 3"
fenmate2 = ["6rk/pp3prp/4bQ1R/8/3p4/1PP2N1P/1P2q3/6RK w - - 0 29",
            "r1b1kb1r/3qn2p/p1Np1pn1/1p1P4/4Q2p/4R3/PPB2PPP/4R1K1 w kq - 0 24",
            "r1b2r2/pp4pp/1qnbpk2/3p2nQ/3P1N2/1P4PB/P4P1P/R1B2RK1 w - - 2 18",
            "2r4r/4p1k1/p5p1/q1p2nNp/1p3QPP/2nBBP2/PKP5/3R3R b - - 0 28",
            "r5k1/p5bp/5pp1/3prn2/1B1n4/2PP3P/PP1K1P2/R2Q3R b - - 1 23",
            "4r1k1/4q2p/1p1p4/p2P4/P2b1B2/1P3p1b/2Q2P1P/2R1R1K1 b - - 3 27",
            "r2q1r2/6R1/1pkpp3/p6Q/P1Pn4/B2P1P2/3K1P1P/8 w - - 15 28"]

fenmate3 = ["6B1/p1Q4p/2P2ppk/8/4P3/4qP2/1r4rP/2R2R1K b - - 3 29"]

testmate = "8/8/8/4k3/8/8/3Q4/2K5 w - - 0 1"

fen_pb = "r1bqkbnr/ppp2pp1/2n5/3p3p/2B1Pp2/5N2/PPPP2PP/RNBQR1K1 w kq - 0 7"
