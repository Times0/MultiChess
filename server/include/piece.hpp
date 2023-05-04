#pragma once
#include <string>
#include <vector>

#include "square.hpp"

class Board;

#include "board.hpp"

enum type_t
{
    ROOK,
    KNIGHT,
    BISHOP,
    QUEEN,
    KING,
    PAWN,
    NONE
};

class Piece
{
public:
    Piece();
    Piece(Color color, Square square);
    virtual ~Piece();

    int get_i() { return i; };
    int get_j() { return j; };
    Square get_square() { return Square(i, j); };
    Color get_color() { return color; };

    void set_i(int i);
    void set_j(int j);
    void set_position(Square dest);

    void affiche();
    virtual type_t get_type() { return NONE; }

    bool can_move_to(Square dest, Board board);
    bool is_legal_move(Square dest, Board board);
    virtual std::vector<Square> get_possible_moves(Board board) = 0;
    virtual std::vector<Square> get_attacking_squares(Board board) = 0;
    std::vector<Square> get_legal_moves(Board board);

    virtual std::string get_fen() { return " "; }
    Piece *clone();
    void set_has_moved() { has_moved = true; }
    bool is_first_move() { return !has_moved; }
    bool is_move_possible(Square dest, Board board);
    bool is_attacking(Square dest, Board board);

    std::string get_pgn_name_bs();

private:
    int i;
    int j;
    Color color;
    bool has_moved = false;
};

class Rook : public Piece
{
public:
    Rook(Color color, Square square) : Piece(color, square) {}
    virtual type_t get_type() { return ROOK; }
    virtual std::vector<Square> get_possible_moves(Board board);
    virtual std::vector<Square> get_attacking_squares(Board board);
    virtual std::string get_fen() { return (get_color() == WHITE) ? "R" : "r"; }

private:
};

class Bishop : public Piece
{
public:
    Bishop(Color color, Square square) : Piece(color, square) {}
    virtual type_t get_type() { return BISHOP; }
    virtual std::vector<Square> get_possible_moves(Board board);
    virtual std::string get_fen() { return (get_color() == WHITE) ? "B" : "b"; }
    virtual std::vector<Square> get_attacking_squares(Board board);

private:
};

class Knight : public Piece
{
public:
    Knight(Color color, Square square) : Piece(color, square) {}
    virtual type_t get_type() { return KNIGHT; }
    virtual std::vector<Square> get_possible_moves(Board board);
    virtual std::string get_fen() { return (get_color() == WHITE) ? "N" : "n"; }
    virtual std::vector<Square> get_attacking_squares(Board board);

private:
};

class Queen : public Piece
{
public:
    Queen(Color color, Square square) : Piece(color, square) {}
    virtual type_t get_type() { return QUEEN; }
    virtual std::vector<Square> get_possible_moves(Board board);
    virtual std::string get_fen() { return (get_color() == WHITE) ? "Q" : "q"; }
    virtual std::vector<Square> get_attacking_squares(Board board);

private:
};

class King : public Piece
{
public:
    King(Color color, Square square) : Piece(color, square) {}
    virtual type_t get_type() { return KING; }
    virtual std::vector<Square> get_possible_moves(Board board);
    virtual std::string get_fen() { return (get_color() == WHITE) ? "K" : "k"; }
    virtual std::vector<Square> get_attacking_squares(Board board);

private:
    bool has_moved = false;
};

class Pawn : public Piece
{
public:
    Pawn(Color color, Square square) : Piece(color, square) {}
    virtual type_t get_type() { return PAWN; }
    virtual std::vector<Square> get_possible_moves(Board board);
    virtual std::string get_fen() { return (get_color() == WHITE) ? "P" : "p"; }
    virtual std::vector<Square> get_attacking_squares(Board board);

private:
};
