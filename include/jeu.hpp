#pragma once

#include <string>
#include "board.hpp"
#include "piece.hpp"

/**
 * @brief The Jeu class represents a game of chess.
 */
class Jeu
{
private:
    int nbCoups;         /**< An integer that represents the number of moves made in the game. */
    Color currentPlayer; /**< A Color enumeration that represents the player who is currently making a move. */
public:
    Board *board; /**< A pointer to a Board object that represents the current state of the chess board. */

public:
    /**
     * @brief The Jeu constructor initializes the game.
     */
    Jeu();

    /**
     * @brief The afficher function displays the current state of the chess board on the console.
     */
    void afficher();

    /**
     * @brief The coup function prompts the current player to enter a move and then applies that move to the chess board.
     * @return true if the move was applied successfully, false otherwise.
     */
    bool coup();

    bool jouer(std::string mouvement);

    /**
     * @brief The swap_player function swaps the current player.
     */
    void swap_player();

    /**
     * @brief The afficher_position_canonique function displays the current state of the chess board in the PGN format.
     */
    void afficher_position_canonique();

    /**
     * @brief The afficher_position_fen function displays the current state of the chess board in the fen format.
     */
    void afficher_position_fen();

    /**
     * @brief The saisie_correcte function checks whether a given move is valid.
     * @param mouvement A string representing the move to check.
     * @return true if the move is valid, false otherwise.
     */
    bool saisie_correcte(std::string mouvement);

    /**
     * @brief The saisie_correcte_petitroque function checks whether a given castling move is valid.
     * @param mouvement A string representing the castling move to check.
     * @return true if the move is valid, false otherwise.
     */
    bool saisie_correcte_petitroque(std::string mouvement);

    /**
     * @brief The saisie_correcte_grandroque function checks whether a given castling move is valid.
     * @param mouvement A string representing the castling move to check.
     * @return true if the move is valid, false otherwise.
     */
    bool saisie_correcte_grandroque(std::string mouvement);

    /**
     * @brief The Jeu destructor frees the memory used by the Board object.
     */
    ~Jeu();
};
