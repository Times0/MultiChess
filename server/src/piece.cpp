#include "../include/piece.hpp"
#include <iostream>
#include <string>
#include <map>

using namespace std;

map<string, string> lookup = {
    {"white Rook", "♜"},
    {"white Knight", "♞"},
    {"white Bishop", "♝"},
    {"white Queen", "♛"},
    {"white King", "♚"},
    {"white Pawn", "♟"},
    {"black Rook", "♖"},
    {"black Knight", "♘"},
    {"black Bishop", "♗"},
    {"black Queen", "♕"},
    {"black King", "♔"},
    {"black Pawn", "♙"},
};

Piece::Piece(Color color, Square square)
{
    this->color = color;
    this->i = square.get_i();
    this->j = square.get_j();
}

void Piece::affiche()
{
    string color = (this->color == 0) ? "white" : "black";
    type_t type = get_type();
    string type_str = (type == ROOK)     ? "Rook"
                      : (type == KNIGHT) ? "Knight"
                      : (type == BISHOP) ? "Bishop"
                      : (type == QUEEN)  ? "Queen"
                      : (type == KING)   ? "King"
                      : (type == PAWN)   ? "Pawn"
                                         : "Error (Piece::affiche())";
    string key = color + " " + type_str;

    cout << lookup[key];
}

void Piece::set_position(Square dest)
{
    this->i = dest.get_i();
    this->j = dest.get_j();
}

bool Piece::is_move_possible(Square dest, Board board)
{
    vector<Square> moves = this->get_possible_moves(board);
    for (size_t i = 0; i < moves.size(); i++)
    {
        if (dest == moves[i])
        {
            return true;
        }
    }
    return false;
}

bool Piece::can_move_to(Square dest, Board board)
{
    vector<Square> moves = this->get_possible_moves(board);
    for (size_t i = 0; i < moves.size(); i++)
    {
        // cout << "moves[i]: " << moves[i].get_i() << ", " << moves[i].get_j() << endl;

        if (dest == moves[i])
        {
            return true;
        }
    }
    return false;
}

vector<Square> Rook::get_possible_moves(Board board)
{
    vector<Square> moves;
    int i = this->get_i(), j = this->get_j();
    int color = this->get_color();

    int dirs[4][2] = {{1, 0}, {-1, 0}, {0, -1}, {0, 1}};
    for (int k = 0; k < 4; k++)
    {
        int x = i + dirs[k][0], y = j + dirs[k][1];
        for (int l = 1; l < 8; l++)
        {
            if (x < 0 || x > 7 || y < 0 || y > 7)
                break;
            Square square = Square(x, y);
            if (!board.is_empty(square))
            {
                if (board.get_piece(square)->get_color() != color)
                    moves.push_back({x, y});
                break;
            }
            moves.push_back({x, y});
            x += dirs[k][0];
            y += dirs[k][1];
        }
    }

    return moves;
}

vector<Square> Bishop::get_possible_moves(Board board)
{
    vector<Square> moves;
    int i = this->get_i(), j = this->get_j();
    int color = this->get_color();

    int dirs[4][2] = {{1, 1}, {-1, -1}, {1, -1}, {-1, 1}};
    for (int k = 0; k < 4; k++)
    {
        int x = i + dirs[k][0], y = j + dirs[k][1];
        for (int l = 1; l < 8; l++)
        {
            if (x < 0 || x > 7 || y < 0 || y > 7)
                break;
            Square square = Square(x, y);
            if (!board.is_empty(square))
            {
                if (board.get_piece(square)->get_color() != color)
                    moves.push_back({x, y});
                break;
            }
            moves.push_back({x, y});
            x += dirs[k][0];
            y += dirs[k][1];
        }
    }

    return moves;
}

vector<Square> Queen::get_possible_moves(Board board)
{
    vector<Square> moves;

    Rook shallow_rook = Rook(this->get_color(), Square(this->get_i(), this->get_j()));
    Bishop shallow_bishop = Bishop(this->get_color(), Square(this->get_i(), this->get_j()));

    vector<Square> rook_moves = shallow_rook.get_possible_moves(board);
    vector<Square> bishop_moves = shallow_bishop.get_possible_moves(board);

    moves.insert(moves.end(), rook_moves.begin(), rook_moves.end());
    moves.insert(moves.end(), bishop_moves.begin(), bishop_moves.end());

    return moves;
}

vector<Square> King::get_possible_moves(Board board)
{
    vector<Square> moves;
    int i = this->get_i(), j = this->get_j();
    int color = this->get_color();

    int dirs[8][2] = {{1, 0}, {-1, 0}, {0, -1}, {0, 1}, {1, 1}, {-1, -1}, {1, -1}, {-1, 1}};
    for (int k = 0; k < 8; k++)
    {
        int x = i + dirs[k][0], y = j + dirs[k][1];
        if (x < 0 || x > 7 || y < 0 || y > 7)
            continue;
        Square square = Square(x, y);
        if (!board.is_empty(square))
        {
            if (board.get_piece(square)->get_color() != color)
                moves.push_back({x, y});
            continue;
        }
        moves.push_back({x, y});
    }

    // Castling
    if (color == WHITE)
    {
        if (board.is_castling_legal(WHITE, KING_SIDE))
            moves.push_back({i, j + 2});
        if (board.is_castling_legal(WHITE, QUEEN_SIDE))
            moves.push_back({i, j - 2});
    }
    else
    {
        if (board.is_castling_legal(BLACK, KING_SIDE))
            moves.push_back({i, j + 2});
        if (board.is_castling_legal(BLACK, QUEEN_SIDE))
            moves.push_back({i, j - 2});
    }

    return moves;
}

vector<Square> Knight::get_possible_moves(Board board)
{
    vector<Square> moves;
    int i = this->get_i(), j = this->get_j();
    int color = this->get_color();
    int dirs[8][2] = {{1, 2}, {-1, 2}, {1, -2}, {-1, -2}, {2, 1}, {-2, 1}, {2, -1}, {-2, -1}};

    for (int k = 0; k < 8; k++)
    {
        int x = i + dirs[k][0], y = j + dirs[k][1];
        if (x < 0 || x > 7 || y < 0 || y > 7)
            continue;
        Square square = Square(x, y);
        if (!board.is_empty(square))
        {
            if (board.get_piece(square)->get_color() != color)
                moves.push_back({x, y});
            continue;
        }
        moves.push_back({x, y});
    }

    return moves;
}

vector<Square> Pawn::get_possible_moves(Board board)
{
    vector<Square> moves;
    int i = this->get_i(), j = this->get_j();
    int color = this->get_color();

    int dir = color == WHITE ? 1 : -1;
    int x = i + dir, y = j;
    if (x >= 0 && x <= 7)
    {
        // Normal move
        Square square = Square(x, y);
        if (board.is_empty(square))
            moves.push_back({x, y});

        // Capture moves to the left
        if (j > 0 && board.get_piece(Square(x, y - 1)) && board.get_piece(Square(x, y - 1))->get_color() != color)
            moves.push_back({x, y - 1});

        // Capture moves to the right
        if (j < 7 && board.get_piece(Square(x, y + 1)) && board.get_piece(Square(x, y + 1))->get_color() != color)
            moves.push_back({x, y + 1});
    }

    // Pawn double move (for pawn's initial move only)
    if ((color == WHITE && i == 1) || (color == BLACK && i == 6))
    {
        x = i + 2 * dir;
        if (board.is_empty(Square(x, y)))
        {
            moves.push_back({x, y});
        }
    }

    // En passant
    if (board.get_en_passant_square() != Square(-1, -1))
    {
        Square en_passant_square = board.get_en_passant_square();
        if (en_passant_square.get_i() == i + dir && abs(en_passant_square.get_j() - j) == 1)
            moves.push_back(en_passant_square);
    }
    return moves;
}

vector<Square> Piece::get_legal_moves(Board board)
{
    vector<Square> moves = this->get_possible_moves(board);
    vector<Square> legal_moves;

    for (Square move : moves)
    {
        Board *new_board = board.clone();
        new_board->move_piece_without_check(this->get_square(), move);
        if (!new_board->is_in_check(this->get_color()))
            legal_moves.push_back(move);
    }

    return legal_moves;
}

Piece *Piece::clone()
{
    switch (this->get_type())
    {
    case PAWN:
        return new Pawn(this->get_color(), this->get_square());
    case KNIGHT:
        return new Knight(this->get_color(), this->get_square());
    case BISHOP:
        return new Bishop(this->get_color(), this->get_square());
    case ROOK:
        return new Rook(this->get_color(), this->get_square());
    case QUEEN:
        return new Queen(this->get_color(), this->get_square());
    case KING:
        return new King(this->get_color(), this->get_square());
    case NONE:
        return nullptr;
    }

    return nullptr;
}

bool Piece::is_legal_move(Square dest, Board board)
{
    vector<Square> legal_moves = this->get_legal_moves(board);
    for (Square move : legal_moves)
        if (move == dest)
            return true;
    return false;
}

vector<Square> Rook::get_attacking_squares(Board board)
{
    return this->get_possible_moves(board);
}

vector<Square> Bishop::get_attacking_squares(Board board)
{
    return this->get_possible_moves(board);
}

vector<Square> Queen::get_attacking_squares(Board board)
{
    return this->get_possible_moves(board);
}

vector<Square> Knight::get_attacking_squares(Board board)
{
    return this->get_possible_moves(board);
}

vector<Square> Pawn::get_attacking_squares(Board board)
{
    (void)board;
    vector<Square> moves;
    int i = this->get_i(), j = this->get_j();
    int color = this->get_color();

    int dir = color == WHITE ? 1 : -1;
    int x = i + dir, y = j;
    if (x >= 0 && x <= 7)
    {
        // Capture moves to the left
        if (j > 0)
            moves.push_back({x, y - 1});

        // Capture moves to the right
        if (j < 7)
            moves.push_back({x, y + 1});
    }

    return moves;
}

vector<Square> King::get_attacking_squares(Board board)
{
    (void)board;
    vector<Square> moves;
    int i = this->get_i(), j = this->get_j();
    int dirs[8][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}, {1, 1}, {-1, -1}, {1, -1}, {-1, 1}};

    for (int k = 0; k < 8; k++)
    {
        int x = i + dirs[k][0], y = j + dirs[k][1];
        if (x < 0 || x > 7 || y < 0 || y > 7)
            continue;
        moves.push_back({x, y});
    }

    return moves;
}

bool Piece::is_attacking(Square square, Board board)
{
    vector<Square> attacking_squares = this->get_attacking_squares(board);
    for (Square attacking_square : attacking_squares)
        if (attacking_square == square)
            return true;
    return false;
}

/*
@brief Returns the name of the piece in format color + type (e.g. "wP" for white pawn)
*/
string Piece::get_pgn_name_bs()
{
    string name = "";
    switch (color)
    {
    case WHITE:
        name += "w";
        break;
    case BLACK:
        name += "b";
        break;
    }

    switch (this->get_type())
    {
    case PAWN:
        name += "P";
        break;
    case KNIGHT:
        name += "N";
        break;
    case BISHOP:
        name += "B";
        break;
    case ROOK:
        name += "R";
        break;
    case QUEEN:
        name += "Q";
        break;
    case KING:
        name += "K";
        break;
    case NONE:
        name += " ";
        break;
    }

    return name;
}

Piece::~Piece() {}