#include "../include/jeu.hpp"
#include <iostream>
#include <map>
#include <regex>


using namespace std;

const string init_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

Jeu::Jeu()
{
    nbCoups = 0;
    board = new Board();
    board->load_fen(init_fen);
}

void Jeu::afficher()
{
    //system("clear");
    string color = (board->get_turn() == WHITE) ? "white" : "black";
    cout << "Tour : " << color << endl;
    board->afficher();
}

// return true if the game continues and false if it ends
bool Jeu::coup()
{
    string mouvement;
    cout << "(" << board->get_fullmove_number() << ")"
         << "Entrez le coup : ";
    cin >> mouvement;
    Play_result result = jouer(mouvement);
    return result != GAME_OVER;
}

Play_result Jeu::jouer(string mouvement)
{

    if (mouvement.substr(0, 1) == "/")
    {
        if (mouvement == "/quit")
            return GAME_OVER;

        else if (mouvement == "/turn")
        {
            cout << "Tour : " << nbCoups / 2 + 1 << endl;
            return VALID_COMMAND;
        }

        else if (mouvement == "/fen")
        {
            afficher_position_fen();
            return VALID_COMMAND;
        }

        else if (mouvement == "/canonique")
        {
            afficher_position_canonique();
            return VALID_COMMAND;
        }

        else if (mouvement == "/halfmove")
        {
            cout << "The halfmove clock is used to determine if a draw can be claimed under the fifty-move rule. The halfmove clock is reset to zero when a pawn is moved, a piece is captured, or a king is moved. It is incremented after each black move. " << endl;
            cout << "Halfmove clock : " << board->get_halfmove_clock() << endl;
            return VALID_COMMAND;
        }

        else if (mouvement == "/help")
        {
            cout << "Commandes disponibles : " << endl;
            cout << "/quit : quitter la partie" << endl;
            cout << "/turn : afficher le tour" << endl;
            cout << "/fen : afficher la position au format FEN" << endl;
            cout << "/canonique : afficher la position au format canonique" << endl;
            cout << "/help : afficher les commandes disponibles" << endl;
            return VALID_COMMAND;
        }

        else
        {
            cout << "Commande inconnue" << endl;
            return INVALID_COMMAND;
        }
    }

    bool was_move_played = false;
    if (saisie_correcte(mouvement))
        was_move_played = board->move(Square(mouvement.substr(0, 2)), Square(mouvement.substr(2, 2)));

    else if (saisie_correcte_petitroque(mouvement))
    {
        if (board->get_turn() == WHITE)
            was_move_played = board->move(Square("e1"), Square("g1"));
        else
            was_move_played = board->move(Square("e8"), Square("g8"));
    }

    else if (saisie_correcte_grandroque(mouvement))
    {
        if (board->get_turn() == WHITE)
            was_move_played = board->move(Square("e1"), Square("c1"));
        else
            was_move_played = board->move(Square("e8"), Square("c8"));
    }

    else
    {
        cout << "Saisie incorrecte" << endl;
        return INVALID_COMMAND;
    }

    // The state of the game is updated inside the move function
    State state = board->get_state();
    if (state == CHECKMATE)
    {
        cout << "Echec et mat" << endl;
        return GAME_OVER;
    }
    else if (state == PAT)
    {
        cout << "Pat" << endl;
        return GAME_OVER;
    }
    else
    {
        if (was_move_played)
            return VALID_MOVE;
        else
            return INVALID_MOVE;
    }
}

void Jeu::afficher_position_canonique()
{
    string result = "?-?";
    if (board->get_state() == CHECKMATE)
    {
        if (board->get_turn() == WHITE)
            result = "0-1";
        else
            result = "1-0";
    }
    else if (board->get_state() == PAT)
        result = "1/2-1/2";
    cout << board->get_position_canonique() << " " << result << endl;
}

void Jeu::afficher_position_fen()
{
    cout << board->get_fen() << endl;
}

bool Jeu::saisie_correcte(string cmd)
{
    regex mouvmtpattern("[a-h][1-8][a-h][1-8]");
    return regex_match(cmd, mouvmtpattern);
}

bool Jeu::saisie_correcte_petitroque(string cmd)
{
    regex mouvmtpattern("(O|o|0)-(O|o|0)");
    return regex_match(cmd, mouvmtpattern);
}

bool Jeu::saisie_correcte_grandroque(string cmd)
{
    regex mouvmtpattern("(O|o|0)-(O|o|0)-(O|o|0)");
    return regex_match(cmd, mouvmtpattern);
}

Jeu::~Jeu()
{
    delete board;
}