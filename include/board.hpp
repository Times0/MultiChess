/**

    @file board.hpp
    @brief Header file for the Board class.
    */

#ifndef BOARD_HPP
#define BOARD_HPP

#include <vector>
#include <map>
#include "square.hpp"
#include "player.hpp"
#include "piece.hpp"

class Piece;

enum Side
{
    KING_SIDE,
    QUEEN_SIDE
};

enum State
{
    NORMAL,
    CHECKMATE,
    PAT
};

/**

    @class Board
    @brief Represents a chess board.
    The Board class stores the current state of the chess board, including the
    positions of all pieces, the current turn, and whether certain moves (e.g.
    castling or en passant) are legal or possible.
    */
class Board
{
private:
    Piece *board[8][8];                                      /*< The board as a 2D array of Piece pointers. */
    Color turn = WHITE;                                      /*< The current turn (either WHITE or BLACK). */
    Square en_passant_square = Square(-1, -1);               /*< The en passant square, if any. */
    std::map<Color, std::map<Side, bool>> castling_possible; /*< Whether castling is possible for each color and side. */
    int halfmove_clock = 0;                                  /*< The number of half-moves since the last capture or pawn move. */
    int fullmove_number = 1;                                 /*< The current full move number. */
    State state = NORMAL;                                    /**< The current game state (NORMAL, CHECKMATE, or PAT). */

public:
    /**
     * @brief Constructs a new, empty Board.
     */
    Board();

    /**
     * @brief Destroys the Board and all pieces on it.
     */
    ~Board();

    // Board Configuration

    /**
     * @brief Initializes the board to the starting position.
     */
    void init_position();

    /**
     * @brief Loads the board position from a FEN string.
     *
     * @param fen The FEN string to load.
     */
    void load_fen(std::string fen);

    /**
     * @brief Gets the current board position in FEN format.
     *
     * @return The FEN string representing the current board position.
     */
    std::string get_fen();

    /**
     * @brief Gets the current board position in canonique format.
     *
     * @return The canonique string representing the current board position.
     */
    std::string get_position_canonique();

    // Board Queries
    /**
     * @brief Determines whether a square is empty.
     *
     * @param square The square to check.
     * @return True if the square is empty, false otherwise.
     */
    bool is_empty(Square square);
    /**
     * @brief Gets the piece at a given square.
     *
     * @param square The square to check.
     * @return A pointer to the Piece object at the given square, or nullptr if there is no piece there.
     */
    Piece *get_piece(Square square);
    /**
     * @brief Gets the square containing the king of a given color.
     *
     * @param color The color of the king to find.
     * @return The square containing the king.
     */
    Square get_king_square(Color color);
    /**
     * @brief Determines whether a given color is in check.
     *
     * @param color The color to check.
     * @return True if the given color is in check, false otherwise.
     */
    bool is_in_check(Color color);
    /**
     * @brief Determines whether castling in a given direction is legal for a given color.
     *
     * @param color The color of the player attempting to castle.
     * @param side The direction of the castle (
     **/
    bool is_castling_legal(Color color, Side side);
    /**
     * @brief Determines whether castling in a given direction is possible for a given color.
     *
     * @param color The color of the player attempting to castle.
     * @param side The direction of the castle.
     * @return True if the given color can castle in the given direction, false otherwise.
     */
    bool is_castling_possible(Color color, Side side);
    /**
     * @brief Determines whether a given square is attacked by a given color.
     *
     * @param square The square to check.
     * @param color The color of the attacking pieces.
     * @return True if the given square is attacked by the given color, false otherwise.
     */
    bool is_square_attacked_by(Square square, Color color);

    // Board manipulation
    /*
    @brief Move a piece without swapping it with another piece on the destination square.
    @param orig The square where the piece is located.
    @param dest The square where the piece should be moved to.
    @return True if the move was successful, false otherwise.
    */
    bool move_no_swap(Square orig, Square dest);
    /**
        @brief Move a piece and swap it with another piece on the destination square.
        @param orig The square where the piece is located.
        @param dest The square where the piece should be moved to.
        @return The resulting state after the move.
        */
    State move(Square orig, Square dest);
    /**
        @brief Set the piece on a given square.
        @param square The square where the piece should be set.
        @param piece The piece to be set on the square.
        */
    void set_piece(Square square, Piece *piece);
    /**
        @brief Move a piece from one square to another without checking for any conditions such as check or checkmate.
        @param orig The square where the piece is located.
        @param dest The square where the piece should be moved to.
        */
    void move_piece_without_check(Square orig, Square dest);
    /**
        @brief Verify if a checkmate or stalemate has occurred for a given color.
        @param color The color to be verified.
        */
    void verify_checkmate_and_pat(Color color);
    // Board state manipulation
    /**
        @brief Swap the current turn between black and white.
        */
    void swap_turn() { turn = (turn == WHITE) ? BLACK : WHITE; }
    /**
        @brief Set the halfmove clock.
        @param halfmove_clock The value to be set as the halfmove clock.
        */
    void set_halfmove_clock(int halfmove_clock) { this->halfmove_clock = halfmove_clock; }
    /**
        @brief Increment the fullmove number.
        */
    void increment_fullmove_number() { fullmove_number++; }
    /**
        @brief Set the state of the board.
        @param state The state to be set for the board.
        */
    void set_state(State state) { this->state = state; }

    // Board state queries
    /**
        @brief Get the current turn.
        @return The color of the current turn.
        */
    Color get_turn() { return turn; }
    /**
        @brief Get the square where the en passant capture is possible.
        @return The square where the en passant capture is possible.
        */
    Square get_en_passant_square() { return en_passant_square; }
    /**
        @brief Get the current halfmove clock.
        @return The current value of the halfmove clock.
        */
    int get_halfmove_clock() { return halfmove_clock; }
    /**
        @brief Get the current fullmove number.
        @return The current value of the fullmove number.
        */
    int get_fullmove_number() { return fullmove_number; }
    /**
        @brief Get the current state of the board.
        @return The current state of the board.
        */
    State get_state() { return state; }

    // Board display
    /**
        @brief Print the board to standard output.
        */
    void afficher();

    Board *clone();
};

#endif
