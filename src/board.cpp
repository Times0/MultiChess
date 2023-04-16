#include "../include/board.hpp"
#include <iostream>

using namespace std;

#define NBCOL 8
#define NBLIG 8

Piece *piece_from_fen(char c)
{
    switch (c)
    {
    case 'R':
        return new Rook(WHITE, Square(0, 0));
    case 'N':
        return new Knight(WHITE, Square(0, 0));
    case 'B':
        return new Bishop(WHITE, Square(0, 0));
    case 'Q':
        return new Queen(WHITE, Square(0, 0));
    case 'K':
        return new King(WHITE, Square(0, 0));
    case 'P':
        return new Pawn(WHITE, Square(0, 0));
    case 'r':
        return new Rook(BLACK, Square(0, 0));
    case 'n':
        return new Knight(BLACK, Square(0, 0));
    case 'b':
        return new Bishop(BLACK, Square(0, 0));
    case 'q':
        return new Queen(BLACK, Square(0, 0));
    case 'k':
        return new King(BLACK, Square(0, 0));
    case 'p':
        return new Pawn(BLACK, Square(0, 0));
    default:
        return nullptr;
    }
}

// constructeur
Board::Board()
{
    for (int i = 0; i < 8; i++)
    {
        for (int j = 0; j < 8; j++)
        {
            board[i][j] = nullptr;
        }
    }
    en_passant_square = Square(-1, -1);
    state = NORMAL;
    castling_possible = {
        {WHITE, {{KING_SIDE, false}, {QUEEN_SIDE, false}}},
        {BLACK, {{KING_SIDE, false}, {QUEEN_SIDE, false}}}};
}

void Board::init_position()
{
    // initialisation des pièces blanches
    // board[0][0] = new Rook(WHITE, Square(0, 0));
    board[0][0] = new Rook(WHITE, Square(0, 0));
    board[0][1] = new Knight(WHITE, Square(0, 1));
    board[0][2] = new Bishop(WHITE, Square(0, 2));
    board[0][3] = new Queen(WHITE, Square(0, 3));
    board[0][4] = new King(WHITE, Square(0, 4));
    board[0][5] = new Bishop(WHITE, Square(0, 5));
    board[0][6] = new Knight(WHITE, Square(0, 6));
    board[0][7] = new Rook(WHITE, Square(0, 7));
    for (int j = 0; j < 8; j++)
    {
        board[1][j] = new Pawn(WHITE, Square(1, j));
    }

    // initialisation des pièces noires
    board[7][0] = new Rook(BLACK, Square(7, 0));
    board[7][1] = new Knight(BLACK, Square(7, 1));
    board[7][2] = new Bishop(BLACK, Square(7, 2));
    board[7][3] = new Queen(BLACK, Square(7, 3));
    board[7][4] = new King(BLACK, Square(7, 4));
    board[7][5] = new Bishop(BLACK, Square(7, 5));
    board[7][6] = new Knight(BLACK, Square(7, 6));
    board[7][7] = new Rook(BLACK, Square(7, 7));
    for (int j = 0; j < 8; j++)
    {
        board[6][j] = new Pawn(BLACK, Square(6, j));
    }

    castling_possible = {
        {WHITE, {{KING_SIDE, true}, {QUEEN_SIDE, true}}},
        {BLACK, {{KING_SIDE, true}, {QUEEN_SIDE, true}}}};
}

void Board::afficher()
{

    string space5 = string(5, ' ');
    cout << endl;
    cout << "     a     b     c     d     e     f     g     h    " << endl;
    cout << "  +-----+-----+-----+-----+-----+-----+-----+-----+" << endl;
    for (int i(7); i >= 0; i--)
    {
        cout << i + 1 << " "; // numérotation ligne dans affichage
        for (int j(0); j < 8; j++)
        {
            cout << "|";
            if (board[i][j])
            {
                cout << "\u0020\u0020"; // U+0020 est un esapce utf-8 taille police
                board[i][j]->affiche();
                cout << "\u0020"
                     << " ";
            }
            else
                cout << space5; // 2 ascii spaces
        }
        cout << "|\n  +-----+-----+-----+-----+-----+-----+-----+-----+";
        cout << endl;
    }
    cout << "     a     b     c     d     e     f     g     h    " << endl;
}

// returns true if the move was performed, false otherwise
bool Board::move_no_swap(Square orig, Square dest)
{
    Square origine = orig;
    Square destination = dest;

    if (origine.get_i() == -1 || origine.get_j() == -1 || destination.get_i() == -1 || destination.get_j() == -1)
    {
        cout << "Les cases d'origine ou de destination ne sont pas valides" << endl;
        return false;
    }

    int i_orig = origine.get_i();
    int j_orig = origine.get_j();

    // vérification que la case d'origine contient une pièce de la bonne couleur
    Square square = Square(i_orig, j_orig);
    Piece *piece;
    if (is_empty(origine))
    {
        cout << "La case d'origine ne contient pas de pièce" << endl;
        return false;
    }

    if ((piece = get_piece(square))->get_color() != turn)
    {
        cout << "La pièce n'est pas de la bonne couleur" << endl;
        return false;
    }

    // vérification que la pièce peut se déplacer sur la case de destination
    if (!piece->can_move_to(destination, *this))
    {
        cout << "La pièce ne peut pas se déplacer sur la case de destination" << endl;
        return false;
    }

    // vérification que le roi n'est pas mis en échec
    if (!piece->is_legal_move(destination, *this))
    {
        cout << "Le roi est en échec" << endl;
        return false;
    }

    // halfmove clock
    if (piece->get_type() == PAWN || !is_empty(destination))
    {
        halfmove_clock = 0;
    }
    else
    {
        halfmove_clock++;
    }

    // En passant
    if (piece->get_type() == PAWN && abs(i_orig - destination.get_i()) == 2)
    {

        int i_en_passant = (i_orig + destination.get_i()) / 2;
        Square en_passant_square = Square(i_en_passant, j_orig);
        this->en_passant_square = en_passant_square;
    }
    else
        this->en_passant_square = Square(-1, -1);

    // en passant capture
    if (piece->get_type() == PAWN && abs(j_orig - destination.get_j()) == 1 && is_empty(destination))
    {
        Square en_passant_square = Square(orig.get_i(), destination.get_j());
        set_piece(en_passant_square, nullptr);
    }

    // castling
    if (piece->get_type() == KING && abs(j_orig - destination.get_j()) == 2)
    {
        int j_rook;
        if (j_orig < destination.get_j())
            j_rook = 7;
        else
            j_rook = 0;
        Square rook_square = Square(i_orig, j_rook);
        Piece *rook = get_piece(rook_square);
        int j_rook_dest;
        if (j_orig < destination.get_j())
            j_rook_dest = 5;
        else
            j_rook_dest = 3;
        Square rook_dest_square = Square(i_orig, j_rook_dest);
        set_piece(rook_dest_square, rook);
        set_piece(rook_square, nullptr);
        rook->set_position(rook_dest_square);
    }

    if (piece->get_type() == KING)
    {
        castling_possible[turn][KING_SIDE] = false;
        castling_possible[turn][QUEEN_SIDE] = false;
    }
    else if (piece->get_type() == ROOK)
    {
        if (orig == Square(0, 0))
            castling_possible[WHITE][QUEEN_SIDE] = false;
        else if (orig == Square(0, 7))
            castling_possible[WHITE][KING_SIDE] = false;
        else if (orig == Square(7, 0))
            castling_possible[BLACK][QUEEN_SIDE] = false;
        else if (orig == Square(7, 7))
            castling_possible[BLACK][KING_SIDE] = false;
    }

    // promotion
    if (piece->get_type() == PAWN && (destination.get_i() == 0 || destination.get_i() == 7))
    {
        cout << "Promotion de la pièce en : " << endl;
        cout << "Q. Reine" << endl;
        cout << "B. Fou" << endl;
        cout << "N. Cavalier" << endl;
        cout << "R. Tour" << endl;
        char choice;
        cin >> choice;

        Piece *new_piece;
        switch (choice)
        {
        case 'Q':
            new_piece = new Queen(piece->get_color(), destination);
            break;
        case 'B':
            new_piece = new Bishop(piece->get_color(), destination);
            break;
        case 'N':
            new_piece = new Knight(piece->get_color(), destination);
            break;
        case 'R':
            new_piece = new Rook(piece->get_color(), destination);
            break;
        default:
            cout << "Choix invalide" << endl;
            break;
        }
        new_piece->set_position(destination);
        set_piece(destination, new_piece);
        set_piece(origine, nullptr);
        return true;
    }

    // modification de la position de la pièce
    piece->set_position(destination);

    // déplacement de la pièce sur l'échiquier
    set_piece(destination, piece);
    set_piece(origine, nullptr);

    return true;
}

State Board::move(Square orig, Square dest)
{
    if (move_no_swap(orig, dest))
    {
        Piece *piece = get_piece(dest);
        piece->set_has_moved();
        verify_checkmate_and_pat(turn == WHITE ? BLACK : WHITE);

        if (state == CHECKMATE)
        {
            return CHECKMATE;
        }
        else if (state == PAT)
        {
            return PAT;
        }

        if (turn == BLACK)
        {
            increment_fullmove_number();
        }

        if (halfmove_clock >= 100)
        {
            return PAT;
        }

        turn = (Color)(WHITE + BLACK - turn);
    }
    return NORMAL;
}

void Board::set_piece(Square square, Piece *piece)
{
    int i = square.get_i();
    int j = square.get_j();
    board[i][j] = piece;
}

bool Board::is_empty(Square square)
{
    int i = square.get_i();
    int j = square.get_j();
    return (board[i][j] == nullptr);
}

Piece *Board::get_piece(Square square)
{
    int i = square.get_i();
    int j = square.get_j();
    return this->board[i][j];
}

bool Board::is_in_check(Color color)
{
    Square king_square = get_king_square(color);
    return is_square_attacked_by(king_square, (Color)(WHITE + BLACK - color));
}

Square Board::get_king_square(Color color)
{
    for (int i = 0; i < 8; i++)
    {
        for (int j = 0; j < 8; j++)
        {
            if (!is_empty(Square(i, j)) && get_piece(Square(i, j))->get_type() == KING && get_piece(Square(i, j))->get_color() == color)
            {
                return Square(i, j);
            }
        }
    }
    cerr << "Le roi n'a pas été trouvé" << endl;
    exit(1);
}

void Board::move_piece_without_check(Square orig, Square dest)
{
    Piece *piece = get_piece(orig);
    set_piece(dest, piece);
    set_piece(orig, nullptr);

    piece->set_position(dest);
}

Board *Board::clone()
{
    Board *board = new Board();
    for (int i = 0; i < 8; i++)
    {
        for (int j = 0; j < 8; j++)
        {
            if (this->board[i][j])
            {
                board->board[i][j] = this->board[i][j]->clone();
            }
        }
    }
    return board;
}

bool Board::is_castling_possible(Color color, Side side)
{
    return castling_possible[color][side];
}

string Board::get_fen()
{
    string fen = "";
    int empty_count = 0;
    for (int i = 7; i > -1; i--)
    {
        for (int j = 0; j < 8; j++)
        {
            if (board[i][j])
            {
                if (empty_count > 0)
                {
                    fen += to_string(empty_count);
                    empty_count = 0;
                }
                fen += board[i][j]->get_fen();
            }
            else
            {
                empty_count++;
            }
        }
        if (empty_count > 0)
        {
            fen += to_string(empty_count);
            empty_count = 0;
        }
        if (i > 0)
        {
            fen += "/";
        }
    }

    if (turn == WHITE)
    {
        fen += " w ";
    }
    else
    {
        fen += " b ";
    }

    if (castling_possible[WHITE][KING_SIDE] || castling_possible[WHITE][QUEEN_SIDE] || castling_possible[BLACK][KING_SIDE] || castling_possible[BLACK][QUEEN_SIDE])
    {
        if (castling_possible[WHITE][KING_SIDE])
        {
            fen += "K";
        }
        if (castling_possible[WHITE][QUEEN_SIDE])
        {
            fen += "Q";
        }
        if (castling_possible[BLACK][KING_SIDE])
        {
            fen += "k";
        }
        if (castling_possible[BLACK][QUEEN_SIDE])
        {
            fen += "q";
        }
    }
    else
    {
        fen += "-";
    }

    if (en_passant_square.get_i() != -1)
    {
        fen += " " + en_passant_square.to_string() + " ";
    }
    else
    {
        fen += " - ";
    }

    fen += to_string(halfmove_clock) + " " + to_string(fullmove_number);

    return fen;
}

void Board::load_fen(string fen)
{
    for (int i = 0; i < 8; i++)
    {
        for (int j = 0; j < 8; j++)
        {
            board[i][j] = nullptr;
        }
    }
    state = NORMAL;
    int i = 7;
    int j = 0;
    int k;
    for (k = 0; k < (int)fen.length(); k++)
    {
        char c = fen[k];
        if (c == ' ')
        {
            break;
        }
        else if (c == '/')
        {
            i--;
            j = 0;
        }
        else if (c >= '1' && c <= '8')
        {
            j += c - '0';
        }
        else
        {
            Piece *piece = piece_from_fen(c);
            piece->set_position(Square(i, j));
            set_piece(Square(i, j), piece);
            j++;
        }
    }

    k++;
    if (fen[k] == 'w')
    {
        turn = WHITE;
    }
    else
    {
        turn = BLACK;
    }

    k += 2;
    while (fen[k] != ' ')
    {
        if (fen[k] == 'K')
        {
            castling_possible[WHITE][KING_SIDE] = true;
        }
        else if (fen[k] == 'Q')
        {
            castling_possible[WHITE][QUEEN_SIDE] = true;
        }
        else if (fen[k] == 'k')
        {
            castling_possible[BLACK][KING_SIDE] = true;
        }
        else if (fen[k] == 'q')
        {
            castling_possible[BLACK][QUEEN_SIDE] = true;
        }
        k++;
    }

    k++;
    if (fen[k] != '-')
    {
        en_passant_square = Square(fen.substr(k, 2));
    }

    k += 3;
    halfmove_clock = stoi(fen.substr(k - 1, fen.find(" ", k) - k + 1));

    k = fen.find(" ", k) + 1;
    fullmove_number = stoi(fen.substr(k));
}

bool Board::is_castling_legal(Color color, Side side)
{
    if (!is_castling_possible(color, side))
    {
        return false;
    }
    if (color == WHITE)
    {
        if (side == KING_SIDE)
        {
            if (!is_empty(Square(0, 5)) || !is_empty(Square(0, 6)))
            {
                return false;
            }

            if (is_square_attacked_by(Square(0, 5), BLACK) || is_square_attacked_by(Square(0, 6), BLACK))
            {
                return false;
            }
        }
        else
        {
            if (!is_empty(Square(0, 3)) || !is_empty(Square(0, 2)) || !is_empty(Square(0, 1)))
            {
                return false;
            }
            if (is_square_attacked_by(Square(0, 3), BLACK) || is_square_attacked_by(Square(0, 2), BLACK) || is_square_attacked_by(Square(0, 1), BLACK))
            {
                return false;
            }
        }
    }
    else
    {
        if (side == KING_SIDE)
        {
            if (!is_empty(Square(7, 5)) || !is_empty(Square(7, 6)))
            {
                return false;
            }
            if (is_square_attacked_by(Square(7, 5), WHITE) || is_square_attacked_by(Square(7, 6), WHITE))
            {
                return false;
            }
        }
        else
        {

            if (!is_empty(Square(7, 3)) || !is_empty(Square(7, 2)) || !is_empty(Square(7, 1)))
            {
                return false;
            }
            if (is_square_attacked_by(Square(7, 3), WHITE) || is_square_attacked_by(Square(7, 2), WHITE) || is_square_attacked_by(Square(7, 1), WHITE))
            {
                return false;
            }
        }
    }

    return true;
}

bool Board::is_square_attacked_by(Square square, Color color)
{
    for (int i = 0; i < 8; i++)
    {
        for (int j = 0; j < 8; j++)
        {
            if (!is_empty(Square(i, j)) && get_piece(Square(i, j))->get_color() == color)
            {
                if (get_piece(Square(i, j))->is_attacking(square, *this))
                {
                    return true;
                }
            }
        }
    }
    return false;
}

void Board::verify_checkmate_and_pat(Color color)
{
    for (int i = 0; i < 8; i++)
    {
        for (int j = 0; j < 8; j++)
        {
            if (!is_empty(Square(i, j)) && get_piece(Square(i, j))->get_color() == color)
            {
                vector<Square> moves = get_piece(Square(i, j))->get_legal_moves(*this);
                if (moves.size() > 0)
                {
                    return;
                }
            }
        }
    }
    if (!is_in_check(color))
    {
        state = PAT;
    }
    else
    {
        state = CHECKMATE;
    }
}

string Board::get_position_canonique()
{
    string output;
    for (size_t row(1); row <= 8; row++)
    {
        for (char col('a'); col <= 'h'; col++)
        {
            Square square(col + to_string(row));
            if (!is_empty(square))
                // get pieces with theit PGN names,
                // true -> with P for pawns, true -> w/b for colors.
                output += get_piece(square)->get_pgn_name_bs();
            output += ",";
        }
    }
    return output;
}

Board::~Board()
{
}