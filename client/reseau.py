import socket

HOST = "127.0.0.1"
PORT = 5001



def send_move_to_server(socket,move):
    move_s = move
    print(f"Sending {move_s} to server")
    socket.sendall(move_s.encode())
