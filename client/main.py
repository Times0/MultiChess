import socket
import pygame
from game import Game
from constants import WIDTH, HEIGHT, STARTINGPOSFEN

HOST = "127.0.0.1"
PORT = 5000

# dpi awareness
try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.DOUBLEBUF, pygame.SCALED)
    pygame.display.set_caption("MultiChess")
    pygame.display.set_icon(pygame.image.load("assets/icon.png"))
    game = Game(win, STARTINGPOSFEN)
    game.run()
    pygame.quit()


if __name__ == "__main__":
    main()
