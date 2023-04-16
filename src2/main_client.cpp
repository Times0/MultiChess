#include <iostream>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>

#define PORT 5201
#define MAX_MSG_LEN 1024

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        std::cerr << "Usage: " << argv[0] << " <server_ip>\n";
        return EXIT_FAILURE;
    }

    const char *SERVER_IP = argv[1];

    // Create client socket
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket == -1)
    {
        std::cerr << "Failed to create client socket\n";
        return EXIT_FAILURE;
    }

    // Connect to server
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);
    server_addr.sin_port = htons(PORT);
    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
    {
        std::cerr << "Failed to connect to server\n";
        return EXIT_FAILURE;
    }

    std::cout << "Connected to server at " << SERVER_IP << ":" << PORT << std::endl;

    // Exchange messages with server
    char msg[MAX_MSG_LEN];
    while (true)
    {
        // Read message from console
        std::cout << "Enter message: ";
        std::cin.getline(msg, MAX_MSG_LEN);

        // Send message to server
        if (send(client_socket, msg, strlen(msg), 0) == -1)
        {
            std::cerr << "Failed to send message to server\n";
            return EXIT_FAILURE;
        }

        // Receive response from server
        int msg_len = recv(client_socket, msg, MAX_MSG_LEN, 0);
        if (msg_len == -1)
        {
            std::cerr << "Failed to receive response from server\n";
            return EXIT_FAILURE;
        }
        else if (msg_len == 0)
        {
            std::cout << "Server disconnected\n";
            break;
        }

        // Print received message
        msg[msg_len] = '\0';
        std::cout << "Received response from server: " << msg << std::endl;
    }

    // Close socket
    close(client_socket);

    return EXIT_SUCCESS;
}
