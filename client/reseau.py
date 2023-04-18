import socket

HOST = "127.0.0.1"
PORT = 5001

def translate_coord(coord1, coord2):
    move_s = ""
    for coord in [coord1, coord2]:
        if coord[1] == 0:
            move_s += "a"
        elif coord[1] == 1:
            move_s += "b"
        elif coord[1] == 2:
            move_s += "c"
        elif coord[1] == 3:
            move_s += "d"
        elif coord[1] == 4:
            move_s += "e"
        elif coord[1] == 5:
            move_s += "f"
        elif coord[1] == 6:
            move_s += "g"
        elif coord[1] == 7:
            move_s += "h"
        move_s += str(8-coord[0])
    return move_s

def send_move_to_server(s,coord1, coord2):
    move_s = translate_coord(coord1, coord2)
    print(f"Sending {move_s} to server")
    s.sendall(move_s.encode())
