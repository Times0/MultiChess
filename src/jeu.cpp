#include "../include/jeu.hpp"
#include <iostream>
#include <map>
#include <regex>

#include "jeu.hpp"

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
    system("clear");
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
    return jouer(mouvement);
}

bool Jeu::jouer(string mouvement)
{
    if (mouvement == "/quit")
        return false;

    else if (mouvement == "/turn")
    {
        cout << "Tour : " << nbCoups / 2 + 1 << endl;
        return true;
    }

    else if (mouvement == "/fen")
    {
        afficher_position_fen();
        return true;
    }

    else if (mouvement == "/canonique")
    {
        afficher_position_canonique();
        return true;
    }

    else if (mouvement == "/halfmove")
    {
        cout << "The halfmove clock is used to determine if a draw can be claimed under the fifty-move rule. The halfmove clock is reset to zero when a pawn is moved, a piece is captured, or a king is moved. It is incremented after each black move. " << endl;
        cout << "Halfmove clock : " << board->get_halfmove_clock() << endl;
        return true;
    }

    else if (mouvement == "/help")
    {
        cout << "Commandes disponibles : " << endl;
        cout << "/quit : quitter la partie" << endl;
        cout << "/turn : afficher le tour" << endl;
        cout << "/fen : afficher la position au format FEN" << endl;
        cout << "/canonique : afficher la position au format canonique" << endl;
        cout << "/help : afficher les commandes disponibles" << endl;
        return true;
    }

    else

        if (saisie_correcte(mouvement))
        board->move(Square(mouvement.substr(0, 2)), Square(mouvement.substr(2, 2)));

    else if (saisie_correcte_petitroque(mouvement))
    {
        if (board->get_turn() == WHITE)
            board->move(Square("e1"), Square("g1"));
        else
            board->move(Square("e8"), Square("g8"));
    }

    else if (saisie_correcte_grandroque(mouvement))
    {
        if (board->get_turn() == WHITE)
            board->move(Square("e1"), Square("c1"));
        else
            board->move(Square("e8"), Square("c8"));
    }

    else
        cout << "Saisie incorrecte" << endl;

    // The state of the game is updated inside the move function
    State state = board->get_state();
    if (state == NORMAL)
    {
        return true;
    }
    else if (state == CHECKMATE)
    {
        cout << "Echec et mat" << endl;
        return false;
    }
    else if (state == PAT)
    {
        cout << "Pat" << endl;
        return false;
    }
    return true;
}

void Jeu::afficher_position_canonique()
{
    string result = "?-?";
    if (board->get_state() == CHECKMATE)
    {
        if (board->get_turn() == BLACK)
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