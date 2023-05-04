#include <iostream>
#include <cstdlib>
#include <cstring>
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <signal.h>
#include <pthread.h>

#include <cstring>

using namespace std;
#define PORT 5001
#define MAX_MSG_LEN 1024

int connect_to_server(const char *SERVER_IP)
{
    // Create client socket
    int client_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (client_socket == -1)
    {
        cerr << "Failed to create client socket" << endl;
        return EXIT_FAILURE;
    }

    // Connect to server
    struct sockaddr_in server_addr;
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = inet_addr(SERVER_IP);
    server_addr.sin_port = htons(PORT);
    if (connect(client_socket, (struct sockaddr *)&server_addr, sizeof(server_addr)) == -1)
    {
        cerr << "Failed to connect to server" << endl;
        return EXIT_FAILURE;
    }

    cout << "Connected to server at " << SERVER_IP << ":" << PORT << endl;

    return client_socket;
}

void *send_message(void *arg)
{
    int client_socket = *(int *)arg;
    char msg[MAX_MSG_LEN];
    while (true)
    {
        // Read message from stdin
        cout << "Enter move : ";
        cin.getline(msg, MAX_MSG_LEN);

        // Send message to server
        if (send(client_socket, msg, strlen(msg), 0) == -1)
        {
            cerr << "Failed to send message to server" << endl;
            return NULL;
        }

        // Receive message from server
        int bytes_received = recv(client_socket, msg, MAX_MSG_LEN, 0);
        if (bytes_received == -1)
        {
            cerr << "Failed to receive message from server" << endl;
            return NULL;
        }
        msg[bytes_received] = '\0';
        

        cout << "Server: " << msg << endl;
    }
}

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        cerr << "Usage: " << argv[0] << " <server_ip>" << endl;
        return EXIT_FAILURE;
    }

    const char *SERVER_IP = argv[1];
    int client_socket = connect_to_server(SERVER_IP);

    pthread_t thread;
    pthread_create(&thread, NULL, send_message, &client_socket);

    pthread_join(thread, NULL);
    // Close socket
    close(client_socket);

    return EXIT_SUCCESS;
}
