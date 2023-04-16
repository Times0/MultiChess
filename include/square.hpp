#ifndef SQUARE
#define SQUARE

#include <string>
class Square
{
private:
    int i;
    int j;

public:
    Square(int i, int j);
    Square(std::string s);

    int get_i();
    int get_j();

    std::string to_string();

    // equality operator
    bool operator==(const Square &other) const
    {
        return (i == other.i && j == other.j);
    }

    // inequality operator
    bool operator!=(const Square &other) const
    {
        return !(*this == other);
    }

    std::string get_fen();
    ~Square();
};

#endif
