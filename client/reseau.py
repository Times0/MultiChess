import socket

HOST = "127.0.0.1"
PORT = 5001

def translate_coord(coord1, coord2):
    move_s = ""
    for coord in [coord1, coord2]:
        if coord[0] == 0:
            move_s += "a"
        elif coord[0] == 1:
            move_s += "b"
        elif coord[0] == 2:
            move_s += "c"
        elif coord[0] == 3:
            move_s += "d"
        elif coord[0] == 4:
            move_s += "e"
        elif coord[0] == 5:
            move_s += "f"
        elif coord[0] == 6:
            move_s += "g"
        elif coord[0] == 7:
            move_s += "h"
        move_s += str(coord[1] + 1)
    return move_s

def send_move_to_server(s,coord1, coord2):
    move_s = translate_coord(coord1, coord2)
    s.sendall(move_s.encode())
    data = s.recv(1024)
    print(f"Received {data!r}")