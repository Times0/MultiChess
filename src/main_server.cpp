#include "../include/jeu.hpp"
#include <iostream>

#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

using namespace std;

#define PORT 5206
#define MAX_MSG_LEN 1024
#define SERVER_IP "127.0.0.1"

#define CHK(expr)           \
    if (!(expr))            \
    {                       \
        perror(#expr);      \
        exit(EXIT_FAILURE); \
    }

int wait_for_clients(int nb_clients, int client_sockets[])
{
    // Create server socket
    int server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == -1)
    {
        std::cerr << "Failed to create server socket\n";
        return EXIT_FAILURE;
    }

    // Bind server socket to IP address and port
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);
    server_addr.sin_port = htons(PORT);
    if (bind(server_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
    {
        std::cerr << "Failed to bind server socket\n";
        return EXIT_FAILURE;
    }

    // Listen for incoming connections
    if (listen(server_socket, 0) == -1)
    {
        std::cerr << "Failed to listen for connections\n";
        return EXIT_FAILURE;
    }

    std::cout << "Server listening on " << SERVER_IP << ":" << PORT << "..." << std::endl;

    // Accept incoming connections and exchange messages
    struct sockaddr_in client_addrs[nb_clients];
    socklen_t client_len = sizeof(client_addrs[0]);
    for (int i = 0; i < nb_clients; i++)
    {
        cout << "Waiting for player (" << i << "/" << nb_clients << ")" << endl;
        client_sockets[i] = accept(server_socket, (struct sockaddr *)&client_addrs[i], &client_len);
        if (client_sockets[i] == -1)
        {
            std::cerr << "Failed to accept client connection\n";
            return EXIT_FAILURE;
        }

        std::cout << "Client connected from " << inet_ntoa(client_addrs[i].sin_addr) << std::endl;
    }

    cout << "All clients connected, game starting..." << endl;
    sleep(1);

    return EXIT_SUCCESS;
}

void close_clients(int nb_clients, int client_sockets[])
{
    cout << "Closing clients..." << endl;
    for (int i = 0; i < nb_clients; i++)
    {
        close(client_sockets[i]);
    }
}

int read_from_client(int client_socket, char buffer[MAX_MSG_LEN])
{
    cout << "Reading from client..." << endl;
    int bytes_read = recv(client_socket, buffer, MAX_MSG_LEN, 0);
    if (bytes_read == -1)
    {
        perror("recv");
        exit(EXIT_FAILURE);
    }
    else if (bytes_read == 0)
    {
        std::cout << "Client disconnected" << std::endl;
        return EXIT_FAILURE;
    }

    buffer[bytes_read] = '\0';

    return EXIT_SUCCESS;
}

string get_move_from_right_player(int client_socket)
{
    char buffer[MAX_MSG_LEN];
    if (read_from_client(client_socket, buffer) == EXIT_FAILURE)
    {
        cout << "Client disconnected, game over" << endl;
        exit(0);
    }

    string move_str(buffer);
    return move_str;
}

typedef struct
{
    int client_socket;
    Jeu *jeu;
} thread_args;

void *server_thread(void *arg)
{
    thread_args *args = (thread_args *)arg;
    int client_socket = args->client_socket;
    Jeu *jeu = args->jeu;

    char buffer[MAX_MSG_LEN];

    while (true)
    {
        if (read_from_client(client_socket, buffer) == EXIT_FAILURE)
        {
            break;
        }

        cout << "Received: " << buffer << endl;
        Play_result r = jeu->jouer(buffer);
        switch (r)
        {
        case GAME_OVER:
            send(client_socket, "GAME_OVER", 9, 0);
            break;
        case INVALID_MOVE:
            send(client_socket, "INVALID_MOVE", 12, 0);
            break;
        case VALID_MOVE:
            send(client_socket, "VALID_MOVE", 10, 0);
            break;
        }
    }

    return NULL;
}

int main()
{
    int nb_clients = 2;
    int client_sockets[nb_clients];
    wait_for_clients(nb_clients, client_sockets);
    Jeu monjeu;

    pthread_t threads[nb_clients];
    for (int i = 0; i < nb_clients; i++)
    {
        thread_args *args = (thread_args *)malloc(sizeof(thread_args));
        args->client_socket = client_sockets[i];
        args->jeu = &monjeu;
        pthread_create(&threads[i], NULL, server_thread, (void *)args);
    }
    
    cout << "Game starting..." << endl;
    map<Color, int> socket_map = {{WHITE, client_sockets[1]},
                                  {BLACK, client_sockets[0]}};

    // boucle de jeu, s'arrete à la fin de la partie
    bool game_is_on(true);
    do
    {
        monjeu.afficher();
        Color turn = monjeu.board->get_turn();

        string move;
        cin >> move;
        game_is_on = monjeu.jouer(move);

    } while (game_is_on);
    cout << endl;
    monjeu.afficher_position_canonique();

    close_clients(nb_clients, client_sockets);
    return 0;
}