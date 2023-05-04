#include "../include/jeu.hpp"
#include <iostream>
using namespace std;

int main()
{
    Jeu monjeu;

    // boucle de jeu, s'arrete à la fin de la partie
    bool game_is_on(true);
    do
    {
        monjeu.afficher();
        game_is_on = monjeu.coup();
    } while (game_is_on);
    cout << endl;
    monjeu.afficher_position_canonique();
    return 0;
}