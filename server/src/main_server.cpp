#include "../include/jeu.hpp"
#include <iostream>

#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <signal.h>

using namespace std;

#define PORT 5001
#define MAX_MSG_LEN 1024
#define SERVER_IP "172.27.126.6"

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
            perror("accept");
            exit(EXIT_FAILURE);
        }

        cout << "Client connected from " << inet_ntoa(client_addrs[i].sin_addr) << endl;
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
    int bytes_read = recv(client_socket, buffer, MAX_MSG_LEN, 0);
    if (bytes_read == -1)
    {
        perror("recv");
        exit(EXIT_FAILURE);
    }
    else if (bytes_read == 0)
    {
        cout << "Client disconnected" << endl;
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
    int *client_sockets;
    int nb_clients;
    int num_socket;
    Jeu *jeu;
    Color color_to_play;
    pthread_cond_t *cond;
    pthread_mutex_t *mutex;
    int *stop;

} thread_args;

void my_send(string msg, int socket)
{
    if (send(socket, msg.c_str(), msg.length(), 0) == -1)
    {
        perror("send");
        exit(EXIT_FAILURE);
    }
}

void *server_thread(void *arg)
{
    thread_args *args = (thread_args *)arg;
    Jeu *jeu = args->jeu;
    int nb_clients = args->nb_clients;
    Color player = args->color_to_play;
    pthread_cond_t *cond = args->cond;
    pthread_mutex_t *mutex = args->mutex;
    int client_socket = args->client_sockets[args->num_socket];
    char buffer[MAX_MSG_LEN];

    // send to client the color he will play
    string color_str = "color:";
    color_str += player == WHITE ? "white" : "black";
    color_str += '\n';
    my_send(color_str, client_socket);

    string init_fen = jeu->board->get_fen();
    my_send("fen:" + init_fen + "", client_socket);

    while (true)
    {
        if (*args->stop)
        {
            break;
        }

        if (read_from_client(client_socket, buffer) == EXIT_FAILURE)
        {
            return NULL;
        }

        if (player != jeu->board->get_turn())
        {
            if (send(client_socket, "NOT_YOUR_TURN", 13, 0) == -1)
            {
                perror("send");
                exit(EXIT_FAILURE);
            }

            continue;
        }
        Play_result r = jeu->jouer(buffer);
        cout << "Play result: " << r << endl;

        string fen = jeu->board->get_fen();
        string to_send = "fen:" + fen + "\n";

        pthread_cond_signal(cond);

        // send to all clients the new fen representing the board
        for (int i = 0; i < nb_clients; i++)
        {
            my_send(to_send, args->client_sockets[i]);
            if (r == GAME_OVER)
            {
                my_send("info: SERVER STOP\n", args->client_sockets[i]);
            }
        }

        if (r == GAME_OVER)
        {
            cout << "Game is over, terminating server thread nb " << args->num_socket << endl;
            *args->stop = 1;
            break;
        }
    }

    return NULL;
}

typedef struct
{
    Jeu *jeu;
    pthread_cond_t *cond;
    pthread_mutex_t *mutex;
} display_args;

void *display_thread(void *arg)
{
    cout << "Display thread started" << endl;
    display_args *args = (display_args *)arg;
    Jeu *jeu = args->jeu;
    pthread_cond_t *cond = args->cond;
    pthread_mutex_t *mutex = args->mutex;

    while (true)
    {
        jeu->afficher();
        pthread_cond_wait(cond, mutex);
    }

    pthread_mutex_unlock(mutex);

    return NULL;
}

int main()
{
    int nb_clients = 2;
    int client_sockets[nb_clients];

    wait_for_clients(nb_clients, client_sockets);
    Jeu monjeu;

    pthread_cond_t cond = PTHREAD_COND_INITIALIZER;
    pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
    pthread_t threads[nb_clients];
    int stop = 0;

    for (int i = 0; i < nb_clients; i++)
    {
        thread_args *args = (thread_args *)malloc(sizeof(thread_args));
        args->client_sockets = client_sockets;
        args->nb_clients = nb_clients;
        args->num_socket = i;
        args->jeu = &monjeu;
        args->color_to_play = (i == 1) ? WHITE : BLACK;
        args->cond = &cond;
        args->mutex = &mutex;
        args->stop = &stop;
        pthread_create(&threads[i], NULL, server_thread, (void *)args);
    }

    cout << "Game starting..." << endl;
    map<Color, int> socket_map = {{WHITE, client_sockets[1]},
                                  {BLACK, client_sockets[0]}};

    pthread_t display;
    display_args *args = (display_args *)malloc(sizeof(display_args));
    args->jeu = &monjeu;
    args->cond = &cond;
    args->mutex = &mutex;
    pthread_create(&display, NULL, display_thread, (void *)args);

    for (int i = 0; i < nb_clients; i++)
    {
        pthread_join(threads[i], NULL);
    }

    free(args);

    pthread_kill(display, 0);
    cout << "Game over, closing" << endl;
    close_clients(nb_clients, client_sockets);
    return 0;
}