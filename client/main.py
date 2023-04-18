import socket
import pygame 
from Game import Game
from constants import WIDTH, HEIGHT, STARTINGPOSFEN

HOST = "127.0.0.1"
PORT = 5000

# with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#     s.connect((HOST, PORT))
#     s.sendall(b"Hello, world")
#     data = s.recv(1024)

# print(f"Received {data!r}")

def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE, pygame.FULLSCREEN)
    game = Game(win, STARTINGPOSFEN)
    game.run()
    pygame.quit()

    
if __name__ == "__main__":
    main()