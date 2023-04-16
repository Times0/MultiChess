#include "../include/jeu.hpp"
#include <iostream>
#include <map>

#include <regex>
#include "jeu.hpp"

using namespace std;

string init_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

Jeu::Jeu()
{
    nbCoups = 0;
    board = new Board();
    board->load_fen(init_fen);
}

void Jeu::afficher()
{
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
    if (mouvement == "/quit")
        return false;

    else if (mouvement == "/tour")
    {
        cout << "Tour : " << nbCoups / 2 + 1 << endl;
        return true;
    }

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

    // We update the game state inside the move function
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