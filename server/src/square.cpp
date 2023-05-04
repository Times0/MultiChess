#include "../include/square.hpp"
#include <iostream>

using namespace std;

int Square::get_i()
{
    return i;
}

int Square::get_j()
{
    return j;
}

string Square::to_string()
{
    string s = "";
    s += (char)(j + 'a');
    s += (char)(i + '1');
    return s;
}

Square::Square(int v_i, int v_j)
{
    if (v_i < 0 || v_i > 7 || v_j < 0 || v_j > 7)
    {
        this->i = -1;
        this->j = -1;
        return;
    }
    this->i = v_i;
    this->j = v_j;
}

Square::Square(std::string s)
{
    this->j = s[0] - 'a';
    this->i = s[1] - '1';

    if (i < 0 || i > 7 || j < 0 || j > 7)
    {
        this->i = -1;
        this->j = -1;
    }
}

string Square::get_fen()
{
    string s = "";
    s += (char)(j + 'a');
    return s;
}

Square::~Square() {}
