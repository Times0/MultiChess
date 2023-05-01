import socket
import pygame 
from game import Game
from constants import WIDTH, HEIGHT, STARTINGPOSFEN

HOST = "127.0.0.1"
PORT = 5000


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE, pygame.FULLSCREEN)
    game = Game(win, STARTINGPOSFEN)
    game.run()
    pygame.quit()

    
if __name__ == "__main__":
    main()