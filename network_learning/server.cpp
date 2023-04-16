#include <iostream>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define PORT 5000
#define MAX_MSG_LEN 1024
#define SERVER_IP "127.0.0.1"

int main()
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
    if (listen(server_socket, 5) == -1)
    {
        std::cerr << "Failed to listen for connections\n";
        return EXIT_FAILURE;
    }

    std::cout << "Server listening on port " << PORT << std::endl;

    // Accept incoming connections and exchange messages
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int client_socket = accept(server_socket, (struct sockaddr *)&client_addr, &client_len);
    if (client_socket == -1)
    {
        std::cerr << "Failed to accept client connection\n";
        return EXIT_FAILURE;
    }

    std::cout << "Client connected from " << inet_ntoa(client_addr.sin_addr) << std::endl;

    char msg[MAX_MSG_LEN];
    while (true)
    {
        // Receive message from client
        int msg_len = recv(client_socket, msg, MAX_MSG_LEN, 0);
        if (msg_len == -1)
        {
            std::cerr << "Failed to receive message from client\n";
            return EXIT_FAILURE;
        }
        else if (msg_len == 0)
        {
            std::cout << "Client disconnected\n";
            break;
        }

        msg[msg_len] = '\0';

        // Print received message
        std::cout << "Received message from client: " << msg << std::endl;

        // Send response back

        if (send(client_socket, msg, strlen(msg), 0) == -1)
        {
            std::cerr << "Failed to send response to client\n";
            return EXIT_FAILURE;
        }
    }

    // Close sockets
    close(client_socket);
    close(server_socket);

    return EXIT_SUCCESS;
}
