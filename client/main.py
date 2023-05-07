import socket
import pygame
from game import Game
from constants import WIDTH, HEIGHT, STARTINGPOSFEN

HOST = "127.0.0.1"
PORT = 5000


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    # name window
    pygame.display.set_caption("MultiChess")
    pygame.display.set_icon(pygame.image.load("assets/icon.png"))
    game = Game(win, STARTINGPOSFEN)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
